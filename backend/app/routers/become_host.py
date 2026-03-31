import secrets

from app.services.user_service import get_user_data, send_email
from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def become_host(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/become-host")
    async def get_become_host(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_info = await get_user_data(request, db)

            verif_query = """
                SELECT email, phone_number, email_verified, phone_verified, id_verified, account_verified, is_host
                FROM users
                WHERE user_id = :user_id            
            """
            verif_result = await db.execute(
                text(verif_query), {"user_id": user_info["user_id"]}
            )
            row = verif_result.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="User not found")

            info = dict(row._mapping)

            if info["is_host"]:
                return RedirectResponse("/host", status_code=303)

            return templates.TemplateResponse(
                "becomeHost.html",
                {"request": request, "user_info": user_info, "info": info},
            )
        except HTTPException as e:
            if e.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise

    # @app.get("/become-host/step1")
    # async def get_step1(request: Request, db: AsyncSession = Depends(get_db)):
    #     user_info = await get_user_data(request, db)
    #     email_verified = user_info.get("email_verified", False)
    #     return templates.TemplateResponse(
    #         "becomeHost.html",
    #         {
    #             "request": request,
    #             "user_info": user_info,
    #             "email_verified": email_verified,
    #         },
    #     )

    @app.post("/become-host/step1")
    async def post_become_host(
        request: Request,
        db: AsyncSession = Depends(get_db),
        phone_number: str = Form(...),
        country: str = Form(...),
        city: str = Form(...),
    ):
        user_info = await get_user_data(request, db)

        await db.execute(
            text("""
                UPDATE users
                SET phone_number = :phone,
                    country = :country,
                    city = :city
                WHERE user_id = :user_id
            """),
            {
                "phone": phone_number,
                "country": country,
                "city": city,
                "user_id": user_info["user_id"],
            },
        )
        await db.commit()
        return RedirectResponse("/become-host/step2", status_code=303)

    @app.post("/verify-email/send")
    async def send_verification_email(
        request: Request,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
    ):
        try:
            user_info = await get_user_data(request, db)
        except HTTPException:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        get_mail_query = "SELECT email FROM users WHERE user_id = :user_id"
        get_mail_result = await db.execute(
            text(get_mail_query), {"user_id": user_info["user_id"]}
        )
        email = get_mail_result.fetchone()

        if email:
            user_info["email"] = email[0]
        else:
            user_info["email"] = None  # or handle error

        # Generate a secure token
        token = secrets.token_urlsafe(32)

        # Save token to DB with expiry
        await db.execute(
            text("""
                UPDATE users
                SET email_verify_token = :token,
                    email_verify_expires = NOW() + INTERVAL '1 hour'
                WHERE user_id = :user_id
            """),
            {"token": token, "user_id": user_info["user_id"]},
        )
        await db.commit()

        # Send email in background so the response is instant
        verify_link = f"{request.base_url}verify-email/confirm?token={token}"
        background_tasks.add_task(send_email, user_info["email"], verify_link)

        return JSONResponse({"message": "Email sent"})

    @app.get("/verify-email/confirm")
    async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            text("""
                SELECT user_id FROM users
                WHERE email_verify_token = :token
                  AND email_verify_expires > NOW()
            """),
            {"token": token},
        )
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        await db.execute(
            text("""
                UPDATE users
                SET email_verified = TRUE,
                    email_verify_token = NULL,
                    email_verify_expires = NULL
                WHERE user_id = :user_id
            """),
            {"user_id": row.user_id},
        )
        await db.commit()
        return RedirectResponse("/become-host/step1", status_code=303)
