###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||   this is the more.py file where I have my about us, available houses,||##########################################
##########################################||         Renting tips, contact us FAQs Terms and conditions            ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from services.Hash_password import hash_password, verify_password
from services.user_service import get_user_data
import base64
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from uuid import uuid4
import os
import json
from services.user_service import search_in_database

def more(app: FastAPI, templates: Jinja2Templates, get_db, sio):

    @app.get("/about")
    async def get_about_us(request: Request):
        return templates.TemplateResponse("aboutUs.html", {"request": request})
    
    @app.get("/renting-tips")
    async def get_about_us(request: Request):
        return templates.TemplateResponse("rentalTips.html", {"request": request})
    
    @app.get("/terms")
    async def get_terms(request: Request):
        return templates.TemplateResponse("termsAndConditions.html", {"request": request})