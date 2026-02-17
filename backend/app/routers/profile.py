import secrets

from app.services.user_service import get_user_data
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def profile(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/profile")
    async def get_profile(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_data = await get_user_data(request, db)
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

        user_id = user_data["user_id"]

        result = await db.execute(
            text(
                "SELECT email, phone_number, nationality FROM users WHERE user_id = :user_id"
            ),
            {"user_id": user_id},
        )

        user_info = result.fetchone()

        if user_info:
            user_data["email"] = user_info.email

            if user_info.phone_number:
                user_data["phone_number"] = user_info.phone_number

            if user_info.nationality:
                user_data["nationality"] = user_info.nationality
        else:
            raise HTTPException(status_code=404, detail="User not found")

        csrf_token = secrets.token_urlsafe(32)

        return templates.TemplateResponse(
            "myprofile.html",
            {"request": request, "user_data": user_data, "csrf_token": csrf_token},
        )

    @app.post("/profile")
    async def post_profile(
        request: Request,
        db: AsyncSession = Depends(get_db),
        name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(None),  # Optional
        nationality: str = Form(None),  # Optional
    ):
        try:
            # Get current user
            user_data = await get_user_data(request, db)
            user_id = user_data["user_id"]

            # Validate email format (basic validation)
            if "@" not in email or "." not in email:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "Invalid email format"},
                )

            # Update user in database
            update_query = text("""
                UPDATE users 
                SET user_name = :name, 
                    email = :email, 
                    phone_number = :phone, 
                    nationality = :nationality
                WHERE user_id = :user_id
            """)

            await db.execute(
                update_query,
                {
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "nationality": nationality,
                },
            )

            # Commit the changes
            await db.commit()

            # Return success response
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Profile updated successfully",
                    "data": {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "nationality": nationality,
                    },
                },
            )

        except HTTPException as e:
            if e.status_code == 401:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "message": "Unauthorized"},
                )
            raise

        except Exception as e:
            print(f"Error updating profile: {e}")
            await db.rollback()
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Failed to update profile"},
            )

