"""
utils.py

Core utility functions for session management, database queries,
email delivery, and data encryption used across the HouseRent API.
"""

import os
import smtplib
import uuid
from email.mime.text import MIMEText

from app.config import AsyncSessionLocal
from colorama import Fore, Style
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import HTTPException, Request, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()


# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------


async def set_user_data(
    request: Request, response: Response, email: str, db: AsyncSession
) -> dict:
    """
    Create a new session for a verified, non-banned user and set a session cookie.

    Uses INSERT ... SELECT to atomically look up the user and create the session
    in a single query, avoiding race conditions.

    Args:
        request:  The incoming FastAPI request (reserved for future middleware use).
        response: The outgoing FastAPI response used to attach the session cookie.
        email:    The email address of the user attempting to log in.
        db:       An active async SQLAlchemy session.

    Returns:
        A dict containing `session_id` and `user_id` for the newly created session.

    Raises:
        HTTPException(401): If the email doesn't match any active, non-banned user.
    """
    # Generate a unique session identifier
    session_id = str(uuid.uuid4())

    # Insert the session only if the user exists and is not banned.
    # RETURNING user_id lets us confirm the insert succeeded without a second query.
    query = text("""
        INSERT INTO sessions (session_id, user_id, created_at, expires_at)
        SELECT :session_id, user_id, NOW(), NOW() + INTERVAL '1 hour'
        FROM users
        WHERE email = :email AND banned = false
        RETURNING user_id
    """)

    result = await db.execute(query, {"session_id": session_id, "email": email})
    user_id = result.scalar_one_or_none()

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or banned user")

    await db.commit()

    # Attach the session cookie — HttpOnly prevents JS access (XSS mitigation)
    response.set_cookie(
        key="session_id",
        value=session_id,
        path="/",
        httponly=True,
        samesite="lax",
        max_age=3600,  # 1 hour, matching the DB expiry
    )

    return {"session_id": session_id, "user_id": user_id}


async def get_user_data(request: Request, db: AsyncSession) -> dict:
    """
    Validate the session cookie and return the associated user's full profile.

    Also slides the session expiry forward by 1 hour on each successful call,
    implementing a rolling-window session strategy.

    Args:
        request: The incoming FastAPI request containing the session cookie.
        db:      An active async SQLAlchemy session.

    Returns:
        A dict with user profile fields plus any host-verification details.

    Raises:
        HTTPException(401): If no cookie is present, the session has expired,
                            or the user has been banned.
    """
    # Pull session_id from the cookie jar
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Session not found")

    # Join sessions → users → host_verifications in one round-trip.
    # expires_at > NOW() rejects expired sessions server-side.
    query = text("""
        SELECT
            s.session_id,
            u.user_id,
            u.user_name,
            u.email,
            u.phone_number,
            u.nationality,
            u.country,
            u.city,
            u.email_verified,
            u.phone_verified,
            u.id_verified,
            u.account_verified,
            u.is_host,
            u.is_admin,
            u.is_super_admin,
            hv.id_photo_urls,
            hv.selfie_photo_url,
            hv.auth_type,
            hv.auth_doc_urls,
            hv.auth_verified,
            hv.submitted_at
        FROM sessions s
        JOIN users u ON s.user_id = u.user_id
        LEFT JOIN host_verifications hv ON hv.user_id = u.user_id
        WHERE s.session_id = :session_id
          AND s.expires_at > NOW()
          AND u.banned = false
        LIMIT 1
    """)

    result = await db.execute(query, {"session_id": session_id})
    user_data = result.mappings().first()

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Extend the session expiry window ("sliding expiration")
    await db.execute(
        text("""
            UPDATE sessions
            SET expires_at = NOW() + INTERVAL '1 hour'
            WHERE session_id = :session_id
        """),
        {"session_id": session_id},
    )
    await db.commit()

    return {
        # --- Session ---
        "session_id": str(user_data["session_id"]),
        # --- Core profile ---
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"],
        "email": user_data["email"],
        "phone_number": user_data["phone_number"],
        "nationality": user_data["nationality"],
        "country": user_data["country"],
        "city": user_data["city"],
        # --- Verification flags ---
        "email_verified": user_data["email_verified"],
        "phone_verified": user_data["phone_verified"],
        "id_verified": user_data["id_verified"],  # source of truth for KYC
        "account_verified": user_data["account_verified"],
        "is_host": user_data["is_host"],
        # --- Host verification details (None if not a host applicant) ---
        "id_photo_urls": user_data["id_photo_urls"],
        "selfie_photo_url": user_data["selfie_photo_url"],
        "auth_type": user_data["auth_type"],
        "auth_doc_urls": user_data["auth_doc_urls"],
        "auth_verified": user_data["auth_verified"],
        "submitted_at": user_data["submitted_at"],
        # --- is user admin ---
        "is_admin": user_data["is_admin"],
        "is_super_admin": user_data["is_super_admin"],
    }


# ---------------------------------------------------------------------------
# Database Search
# ---------------------------------------------------------------------------


async def search_in_database(user_inp: str, db: AsyncSession) -> list[dict]:
    """
    Full-text search over the `house_details` JSONB field in the houses table.

    Uses ILIKE for case-insensitive substring matching. Consider a full-text
    index (tsvector) or pg_trgm if performance becomes a concern at scale.

    Args:
        user_inp: The search string provided by the user.
        db:       An active async SQLAlchemy session.

    Returns:
        A list of dicts with `id` and `details` for up to 10 matching houses.
    """
    query = text("""
        SELECT id, details->>'house_details' AS house_details
        FROM houses
        WHERE details->>'house_details' ILIKE '%' || :user_input || '%'
        LIMIT 10;
    """)

    result = await db.execute(query, {"user_input": user_inp})
    rows = result.fetchall()

    return [{"id": row.id, "details": row.house_details} for row in rows]


# ---------------------------------------------------------------------------
# WSGI / WebSocket Cookie Helper
# ---------------------------------------------------------------------------


async def get_user_id_from_cookie(environ: dict) -> int | None:
    """
    Extract and validate a session_id from a raw WSGI environ dict.

    Intended for WebSocket or ASGI middleware contexts where FastAPI's
    dependency injection is not available.

    Args:
        environ: A WSGI-style environ dict containing HTTP headers.

    Returns:
        The integer user_id if the session is valid and unexpired,
        or None if the cookie is missing, malformed, or expired.
    """
    cookie_header = environ.get("HTTP_COOKIE")

    if not cookie_header:
        print(f"{Fore.RED}No cookie header found in request{Style.RESET_ALL}")
        return None

    print(f"{Fore.GREEN}✓ Cookie header found: {cookie_header}{Style.RESET_ALL}")

    # Parse "key=value; key2=value2" into a plain dict
    cookies = dict(
        cookie.strip().split("=", 1)
        for cookie in cookie_header.split(";")
        if "=" in cookie
    )

    print(f"{Fore.GREEN}Parsed cookies: {list(cookies.keys())}{Style.RESET_ALL}")

    session_id = cookies.get("session_id")
    if not session_id:
        print(
            f"{Fore.RED}No 'session_id' cookie found. "
            f"Available cookies: {list(cookies.keys())}{Style.RESET_ALL}"
        )
        return None

    print(f"{Fore.GREEN}✓ Session ID found: {session_id}{Style.RESET_ALL}")

    # Open a fresh DB connection — this function runs outside normal request scope
    async with AsyncSessionLocal() as db:
        query = text("""
            SELECT user_id
            FROM sessions
            WHERE session_id = :session_id
              AND expires_at > NOW()
        """)
        result = await db.execute(query, {"session_id": session_id})
        row = result.fetchone()

    if row:
        print(f"{Fore.GREEN}✓ User authenticated: user_id={row[0]}{Style.RESET_ALL}")
        return row[0]

    print(
        f"{Fore.RED}Session not found or expired for session_id: "
        f"{session_id}{Style.RESET_ALL}"
    )
    return None


# ---------------------------------------------------------------------------
# Email Delivery
# ---------------------------------------------------------------------------


def send_email(to_email: str, verify_link: str) -> None:
    """
    Send an email verification link to the given address.

    Currently connects to a local MailHog/MailPit SMTP stub on port 1025.
    Swap the SMTP host/port and add credentials for production use.

    Args:
        to_email:    Recipient email address.
        verify_link: The time-limited verification URL to include in the body.
    """
    print(Fore.RED + "Sending verification email…" + Style.RESET_ALL)

    msg = MIMEText(f"""Hi,

Click the link below to verify your email address:
{verify_link}

This link expires in 1 hour.

— HouseRent Team""")

    msg["Subject"] = "Verify your email — HouseRent"
    msg["From"] = "noreply@houserent.dev"
    msg["To"] = to_email

    # Port 1025 = local dev SMTP server (e.g. MailHog / MailPit)
    with smtplib.SMTP("localhost", 1025) as smtp:
        smtp.send_message(msg)


# ---------------------------------------------------------------------------
# Encryption Helpers
# ---------------------------------------------------------------------------

# Load the Fernet symmetric key from the environment.
# The key must be a URL-safe base64-encoded 32-byte value generated via
# `Fernet.generate_key()`. Store it securely (e.g. in a secrets manager).
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt(value: str) -> str:
    """
    Encrypt a plaintext string using the Fernet symmetric cipher.

    Args:
        value: The plaintext string to encrypt.

    Returns:
        A URL-safe base64-encoded ciphertext string.
    """
    return fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    """
    Decrypt a Fernet-encrypted string back to plaintext.

    Args:
        value: A base64-encoded ciphertext string produced by `encrypt()`.

    Returns:
        The original plaintext string.

    Raises:
        cryptography.fernet.InvalidToken: If the token is invalid or tampered with.
    """
    return fernet.decrypt(value.encode()).decode()
