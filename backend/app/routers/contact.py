from app.services.contact_services import generate_unique_code
from app.services.redis_db import get_messages
from app.services.user_service import get_user_data
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HISTORY_QUERY = """
    SELECT DISTINCT
        ch.room_name,
        ch.house_id,
        u1.user_name AS user_name,
        u2.user_name AS hoster_name
    FROM contact_history ch
    LEFT JOIN users u1 ON ch.user_id = u1.user_id
    LEFT JOIN users u2 ON ch.hoster_id = u2.user_id
    WHERE ch.user_id = :user_id OR ch.hoster_id = :user_id
    ORDER BY ch.room_name
"""


async def _get_rooms(user_id: int, db: AsyncSession):
    """Return all chat rooms the current user is part of."""
    result = await db.execute(text(HISTORY_QUERY), {"user_id": user_id})
    return result.fetchall()


async def _get_or_create_room(
    user_id: int, hoster_id: int, house_id: int, db: AsyncSession
) -> str:
    """Return an existing room code for this pair, or create a new one."""
    query = """
        SELECT room_name FROM contact_history
        WHERE (user_id = :user_id AND hoster_id = :hoster_id)
           OR (user_id = :hoster_id AND hoster_id = :user_id)
        LIMIT 1
    """
    result = await db.execute(text(query), {"user_id": user_id, "hoster_id": hoster_id})
    row = result.fetchone()

    if row:
        return row[0]

    # No existing room — create one
    code = await generate_unique_code(4, db)
    insert_query = """
        INSERT INTO contact_history (room_name, house_id, user_id, hoster_id)
        VALUES (:code, :house_id, :user_id, :hoster_id)
    """
    try:
        await db.execute(
            text(insert_query),
            {
                "code": code,
                "house_id": house_id,
                "user_id": user_id,
                "hoster_id": hoster_id,
            },
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail="Database error while creating room"
        )

    return code


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


def contact(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/contact")
    async def get_contact(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        rooms = await _get_rooms(user_info["user_id"], db)

        return templates.TemplateResponse(
            "contact.html",
            {
                "request": request,
                "user": user_info,
                "current_user": user_info["user_name"],
                "history": rooms,
            },
        )

    # Separate path prefix avoids collision with /contact/{room_code}
    @app.get("/contact/house/{house_id}")
    async def get_contact_hoster(
        request: Request, house_id: int, db: AsyncSession = Depends(get_db)
    ):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        # Look up the house hoster
        house_result = await db.execute(
            text(
                "SELECT details->>'hoster_id' AS hoster_id FROM houses WHERE id = :house_id"
            ),
            {"house_id": house_id},
        )
        house_row = house_result.fetchone()

        if not house_row:
            raise HTTPException(status_code=404, detail="House not found")

        hoster_id = int(house_row[0])

        code = await _get_or_create_room(
            user_id=user_info["user_id"],
            hoster_id=hoster_id,
            house_id=house_id,
            db=db,
        )

        # 303 See Other is correct after a write operation
        return RedirectResponse(f"/contact/{code}", status_code=303)

    @app.get("/contact/{room_code}")
    async def get_room(
        request: Request, room_code: str, db: AsyncSession = Depends(get_db)
    ):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        user_id = user_info["user_id"]

        # Validate room and membership
        room_result = await db.execute(
            text(
                "SELECT user_id, hoster_id FROM contact_history WHERE room_name = :room_code"
            ),
            {"room_code": room_code},
        )
        room_row = room_result.fetchone()

        if room_row is None:
            return RedirectResponse("/home", status_code=302)

        if user_id not in (room_row.user_id, room_row.hoster_id):
            return RedirectResponse("/home", status_code=302)

        # The "other" person in the conversation
        other_user_id = (
            room_row.hoster_id if user_id == room_row.user_id else room_row.user_id
        )

        hoster_result = await db.execute(
            text("SELECT user_name FROM users WHERE user_id = :other_user_id"),
            {"other_user_id": other_user_id},
        )
        hoster_row = hoster_result.fetchone()
        hoster_name = hoster_row[0] if hoster_row else "Unknown"

        messages = await get_messages(room_code)
        rooms = await _get_rooms(user_id, db)

        return templates.TemplateResponse(
            "contact.html",
            {
                "request": request,
                "user": user_info,
                "current_user": user_info["user_name"],
                "code": room_code,
                "messages": messages,
                "hoster_name": hoster_name,
                "history": rooms,
            },
        )
