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
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

def contuct(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/contact")
    async def get_contact(request: Request):
        return templates.TemplateResponse("contact.html", {"request": request})