###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||       this is the favorite.py file where the user will select his     ||##########################################
##########################################||                              favorite house                           ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from app.services.user_service import get_user_data
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def favorite(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.post("/favorite")
    async def post_favorite(
        request: Request, data: dict, db: AsyncSession = Depends(get_db)
    ):
        house_id = int(data["house_id"])
        favorite = bool(data["favorite"])

        user_info = await get_user_data(request, db)
        user_id = user_info["user_id"]

        if favorite:
            query = text("""
                INSERT INTO myfavorite (house_id, user_id)
                VALUES (:house_id, :user_id)
                ON CONFLICT (house_id, user_id) DO NOTHING
            """)
        else:
            query = text("""
                DELETE FROM myfavorite
                WHERE user_id = :user_id
                AND house_id = :house_id
            """)

        await db.execute(query, {"house_id": house_id, "user_id": user_id})
        await db.commit()

        return {"ok"}

    @app.get("/favorites_page")
    async def get_my_favorites(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        user_id = user_info["user_id"]

        query = """
        SELECT h.*
        FROM houses h
        JOIN myfavorite f
            ON h.id = f.house_id
        WHERE f.user_id = :user_id;
        """

        result = await db.execute(text(query), {"user_id": user_id})
        houses = [dict(row._mapping) for row in result.fetchall()]

        return templates.TemplateResponse(
            "favorites.html", {"request": request, "houses": houses}
        )
