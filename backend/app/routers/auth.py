###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||   this is the auth.py file where I make my login and register routes  ||##########################################
##########################################||                                                                       ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from app.services.Hash_password import hash_password, verify_password
import base64
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.user_service import set_user_data

def auth_rout(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/register", response_class=HTMLResponse)
    async def get_login(request: Request):
        return templates.TemplateResponse("register.html", {"request": request, "name": "", "gmail": "", "passw": "", "pass1": "", "title": "Chat App"})
    
    @app.post("/register", response_class=HTMLResponse)
    async def post_login(
        request: Request,
        name: str = Form(...),
        gmail: str = Form(...),
        passw: str = Form(...),
        pass1: str = Form(...),
        db: AsyncSession = Depends(get_db)
        ):
        #chec that the user enter evrything
        if not name or not gmail or not passw or not pass1:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Fill all the fields please!"}
            )
        
        #chec the password maches
        if passw != pass1:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "The passwords don't match!"}
            )
        
        #chec is the username alredy exist
        result = await db.execute(text("SELECT 1 FROM users WHERE user_name = :name"), {"name": name})
        if result.first():
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "User name already exists."}
            )
        
        #hash password
        salt, hashed_password = hash_password(passw)
        hashed_password_str = base64.b64encode(hashed_password).decode("utf-8")
        salt_str = base64.b64encode(salt).decode("utf-8")

        try:
            await db.execute(
                text(
                    "INSERT INTO users (user_name, email, hashed_password, banned, salt) "
                    "VALUES (:name, :email, :hashed_password, false, :salt)"
                ),
                {
                    "name": name,
                    "email": gmail,
                    "hashed_password": hashed_password_str,
                    "salt": salt_str
                }
            )
            await db.commit()
        except IntegrityError:
            # Email already exists or constraint violation
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "This email is already registered."}
            )
        
        return RedirectResponse(
            url=f"/login",
            status_code=303
        )
    
    @app.get("/login")
    async def get_login(request: Request):
        return templates.TemplateResponse("login.html", {"request": request,})
    
    @app.post("/login")
    async def post_login(
        request: Request,
        response: Response,
        gmail: str = Form(...),
        passw: str = Form(...),
        db: AsyncSession = Depends(get_db)
    ):
        result = await db.execute(
            text("SELECT user_id, user_name, hashed_password, salt, banned FROM users WHERE email = :email"),
            {"email": gmail}
        )
        user = result.fetchone()

        if not user:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid email or password"}
            )
        
        if user.banned:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "This account is banned"}
            )

        # Try verifying
        ok = verify_password(passw, user.salt, user.hashed_password)

        if not ok:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid email or password"}
            )
        
        result = await set_user_data(request, response, gmail, db)

        return RedirectResponse(
            url=f"/home",
            status_code=303,
            headers=response.headers
        )