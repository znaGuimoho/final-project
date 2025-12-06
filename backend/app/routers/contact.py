###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||       this is the contact.py file where the user will conatact the    ||##########################################
##########################################||                              hoster                                   ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form, Depends, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.services.user_service import get_user_data
from app.services.contact_services import generate_unique_code
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from colorama import Fore, Style
from app.services.redis_db import get_messages

def contuct(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/contact")
    async def get_contact(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)
            user_id = user_info["user_id"]
            
            history_query = """
                SELECT DISTINCT 
                    ch.room_name,
                    ch.house_id,
                    u.user_name as hoster_name
                FROM contact_history ch
                LEFT JOIN users u ON ch.hoster_id = u.user_id
                WHERE ch.user_id = :user_id OR ch.hoster_id = :user_id
                ORDER BY ch.room_name
            """
            history = await db.execute(text(history_query), {"user_id": user_id})
            rooms = history.fetchall()
            
            return templates.TemplateResponse("contact.html", {
                "request": request, 
                "user": user_info,
                "history": rooms
            })
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise
    
    @app.get("/contact/{house_id}")
    async def get_contact_hoster(request: Request, house_id: int, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)

            user_id = user_info["user_id"]
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise
        
        house_query = "SELECT details->>'hoster_id' as hoster_id FROM houses WHERE id = :house_id"
        house_result = await db.execute(text(house_query), {"house_id": house_id})
        house_row = house_result.fetchone()
        
        if not house_row:
            raise HTTPException(status_code=404, detail="House not found")
        
        hoster_id = int(house_row[0])
        
        query = """
            SELECT room_name FROM contact_history 
            WHERE (user_id = :user_id AND hoster_id = :hoster_id)
            OR (user_id = :hoster_id AND hoster_id = :user_id)
            LIMIT 1
        """
        result = await db.execute(
            text(query), 
            {"user_id": user_info["user_id"], "hoster_id": hoster_id}
        )
        row = result.fetchone()
        
        if not row:
            code = await generate_unique_code(4, db)
            insert_query = """
                INSERT INTO contact_history (room_name, house_id, user_id, hoster_id) 
                VALUES (:code, :house_id, :user_id, :hoster_id)
            """
            try:
                await db.execute(
                    text(insert_query), 
                    {"code": code, "house_id": house_id, "user_id": user_info["user_id"], "hoster_id": hoster_id}
                )
                await db.commit()
            except IntegrityError:
                await db.rollback()
                raise HTTPException(status_code=400, detail="Database error")
        else:
            code = row[0]

        messages = await get_messages(code)

        hoster_result = await db.execute(
            text("SELECT user_name FROM users WHERE user_id = :hoster_id"),
            {"hoster_id": hoster_id}
        )
        hoster_row = hoster_result.fetchone()
        hoster_name = hoster_row[0] if hoster_row else "Unknown"

        history_query = """
                SELECT DISTINCT 
                    ch.room_name,
                    ch.house_id,
                    u.user_name as hoster_name
                FROM contact_history ch
                LEFT JOIN users u ON ch.hoster_id = u.user_id
                WHERE ch.user_id = :user_id OR ch.hoster_id = :user_id
                ORDER BY ch.room_name
            """
        history = await db.execute(text(history_query), {"user_id": user_id})
        rooms = history.fetchall()
        
        return templates.TemplateResponse("contact.html", {"request": request, "code": code, "messages": messages, "hoster_name": hoster_name, "history": rooms})
