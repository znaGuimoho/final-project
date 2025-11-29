from fastapi import Request, Response, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

async def set_user_data(request: Request, response: Response, email: str, db: AsyncSession):
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
        max_age=3600
    )

    return {"session_id": session_id, "user_id": user_id}


async def get_user_data(request: Request, db: AsyncSession):
    # 1. Get session_id from cookies
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Session not found")

    # 2. Query to join sessions and users
    query = text("""
        SELECT s.session_id, u.user_id, u.user_name
        FROM sessions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.session_id = :session_id
          AND s.expires_at > NOW()
          AND u.banned = false
        LIMIT 1
    """)

    result = await db.execute(query, {"session_id": session_id})
    user_data = result.mappings().first()  # returns dict-like row

    # 3. Validate session
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # 4. Optionally refresh session expiration
    refresh_query = text("""
        UPDATE sessions
        SET expires_at = NOW() + INTERVAL '1 hour'
        WHERE session_id = :session_id
    """)
    await db.execute(refresh_query, {"session_id": session_id})
    await db.commit()

    # 5. Return user data as dict
    return {
        "session_id": str(user_data["session_id"]),
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"]
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

    return [
        {"id": row.id, "details": row.house_details}
        for row in rows
    ]
