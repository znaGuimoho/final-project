###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||       this is the home.py file where I have my home page at           ||##########################################
##########################################||                                                                       ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from app.services.user_service import get_user_data, search_in_database
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def home(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/")
    @app.get("/home")
    async def get_home(
        request: Request, responce: Response, db: AsyncSession = Depends(get_db)
    ):
        # Execute query
        result = await db.execute(text("SELECT * FROM houses"))

        houses = [dict(row._mapping) for row in result.fetchall()]

        try:
            user_info = await get_user_data(request, db)
        except HTTPException:
            user_info = None

        if user_info:
            user_id = user_info["user_id"]

            query = "SELECT * from myfavorite where user_id = :user_id"
            result1 = await db.execute(text(query), {"user_id": user_id})
            favorite_ids = {row.house_id for row in result1.fetchall()}

            for house in houses:
                house["is_favorite"] = house["id"] in favorite_ids
        else:
            for house in houses:
                house["is_favorite"] = False

        return templates.TemplateResponse(
            "home.html", {"request": request, "houses": houses, "user_info": user_info}
        )

    @app.get("/house/{house_id}")
    async def get_house(
        house_id: int, request: Request, db: AsyncSession = Depends(get_db)
    ):
        result = await db.execute(
            text("SELECT * FROM houses WHERE id = :id"), {"id": house_id}
        )

        row = result.fetchone()

        if not row:
            return templates.TemplateResponse(
                "house.html", {"request": request, "error": "couldn't get the house ID"}
            )

        house = dict(row._mapping)

        return templates.TemplateResponse(
            "house.html", {"request": request, "house": house}
        )

    @app.get("/api/search")
    async def api_search(
        query: str, request: Request, db: AsyncSession = Depends(get_db)
    ):
        result = await search_in_database(query, db)

        return {"results": result}
