###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||   this is the hoster.py file where I make my login and register routes||##########################################
##########################################||                                                                       ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from app.services.Hash_password import hash_password, verify_password
from app.services.user_service import get_user_data
import base64
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from uuid import uuid4
import os
import json
from pathlib import Path

def hosting(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    
    BASE_DIR = Path(__file__).resolve().parents[2]   # finalProject/
    UPLOAD_DIR = BASE_DIR / "app" / "static" / "uploads"

    print(BASE_DIR)
    print(UPLOAD_DIR)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    @app.get("/host", response_class=HTMLResponse)
    async def get_host(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        return templates.TemplateResponse("host.html", {"request": request})
    
    @app.post("/host")
    async def upload_with_data(
        request: Request,
        image: UploadFile = File(...),
        category: str = Form(...),
        price: float = Form(...),
        locationText: str = Form(...),
        details: str = Form(...),
        lat: str = Form(None),
        lng: str = Form(None),
        db: AsyncSession = Depends(get_db),
    ):
        try:
            filename = f"{datetime.utcnow().timestamp()}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            # Save file to disk
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())

            img_url = f"/uploads/{filename}"

            location_url = None
            if lat and lng:
                location_url = f"https://www.google.com/maps?q={lat},{lng}"

            user_info = await get_user_data(request, db)

            JSdetails = {
                "hoster_id": user_info["user_id"],
                "hoster_name": user_info["user_name"],
                "house_details": details
            }

            query = text("""
                INSERT INTO houses (category, price, location_name, location_url, details, img_url)
                VALUES (:category, :price, :location_name, :location_url, :details, :img_url)
            """)

            result = await db.execute(query, {
                "category": category,
                "price": price,
                "location_name": locationText,
                "location_url": location_url,
                "details": json.dumps(JSdetails),
                "img_url": img_url
            })
            await db.commit()

            return RedirectResponse(url="/sucsessUp")
        except Exception as e:
            print("Error while uploading:", e)
            return templates.TemplateResponse(
                "host.html",
                {"request": request, "error": "An error occurred while uploading."}
            )
    

    @app.get("/sucsessUp")
    async def get_sucsess(request: Request):
        return templates.TemplateResponse("uploadSucsess.html", {"request": request})