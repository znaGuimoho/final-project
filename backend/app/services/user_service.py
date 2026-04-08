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


async def set_user_data(
    request: Request, response: Response, email: str, db: AsyncSession
):
    # 1. Generate session_id
    session_id = str(uuid.uuid4())

    # 2. Insert session using INSERT ... SELECT
    query = text("""
        INSERT INTO sessions (session_id, user_id, created_at, expires_at)
        SELECT :session_id, user_id, NOW(), NOW() + INTERVAL '1 hour'
        FROM users
        WHERE email = :email AND banned = false
        RETURNING user_id
    """)

    # Execute the query
    result = await db.execute(query, {"session_id": session_id, "email": email})
    user_id = result.scalar_one_or_none()  # fetch RETURNING value

    # 3. Check result
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or banned user")

    # 4. Commit transaction
    await db.commit()

    # 5. Set cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        path="/",
        httponly=True,
        samesite="lax",
        max_age=3600,
    )

    return {"session_id": session_id, "user_id": user_id}


async def get_user_data(request: Request, db: AsyncSession):
    # 1. Get session_id from cookies
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Session not found")

    # 2. Query to join sessions and users — fetch all user fields
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

    # 3. Validate session
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # 4. Refresh session expiration
    await db.execute(
        text("""
            UPDATE sessions
            SET expires_at = NOW() + INTERVAL '1 hour'
            WHERE session_id = :session_id
        """),
        {"session_id": session_id},
    )
    await db.commit()

    # 5. Return all user data as dict
    return {
        "session_id": str(user_data["session_id"]),
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"],
        "email": user_data["email"],
        "phone_number": user_data["phone_number"],
        "nationality": user_data["nationality"],
        "country": user_data["country"],
        "city": user_data["city"],
        "email_verified": user_data["email_verified"],
        "phone_verified": user_data["phone_verified"],
        "id_verified": user_data["id_verified"],  # source of truth
        "account_verified": user_data["account_verified"],
        "is_host": user_data["is_host"],
        # host verification details
        "id_photo_urls": user_data["id_photo_urls"],
        "selfie_photo_url": user_data["selfie_photo_url"],
        "auth_type": user_data["auth_type"],
        "auth_doc_urls": user_data["auth_doc_urls"],
        "auth_verified": user_data["auth_verified"],
        "submitted_at": user_data["submitted_at"],
    }


async def search_in_database(user_inp: str, db: AsyncSession):
    query = text("""
        SELECT id, details->>'house_details' AS house_details
        FROM houses
        WHERE details->>'house_details' ILIKE '%' || :user_input || '%'
        LIMIT 10;
    """)

    result = await db.execute(query, {"user_input": user_inp})
    rows = result.fetchall()

    return [{"id": row.id, "details": row.house_details} for row in rows]


async def get_user_id_from_cookie(environ):
    cookie_header = environ.get("HTTP_COOKIE")

    if not cookie_header:
        print(f"{Fore.RED}No cookie header found in request{Style.RESET_ALL}")
        return None

    print(f"{Fore.GREEN}✓ Cookie header found: {cookie_header}{Style.RESET_ALL}")

    cookies = dict(
        cookie.strip().split("=", 1)
        for cookie in cookie_header.split(";")
        if "=" in cookie
    )

    print(f"{Fore.GREEN}Parsed cookies: {list(cookies.keys())}{Style.RESET_ALL}")

    session_id = cookies.get("session_id")

    if not session_id:
        print(
            f"{Fore.RED}No 'session_id' cookie found. Available cookies: {list(cookies.keys())}{Style.RESET_ALL}"
        )
        return None

    print(f"{Fore.GREEN}✓ Session ID found: {session_id}{Style.RESET_ALL}")

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
            print(
                f"{Fore.GREEN}✓ User authenticated: user_id={row[0]}{Style.RESET_ALL}"
            )
            return row[0]
        else:
            print(
                f"{Fore.RED}Session not found or expired for session_id: {session_id}{Style.RESET_ALL}"
            )
            return None


def send_email(to_email: str, verify_link: str):
    print(Fore.RED + "trying to send the email" + Style.RESET_ALL)
    msg = MIMEText(f"""Hi,

Click the link below to verify your email address:
{verify_link}

This link expires in 1 hour.

— HouseRent Team""")
    msg["Subject"] = "Verify your email — HouseRent"
    msg["From"] = "noreply@houserent.dev"
    msg["To"] = to_email

    with smtplib.SMTP("localhost", 1025) as smtp:
        smtp.send_message(msg)


ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
