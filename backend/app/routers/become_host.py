import os
import secrets
from pathlib import Path
from typing import List

from app.services.user_service import encrypt, get_user_data, send_email
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Auth helper ─────────────────────────────────────────────────────────────


async def _get_user_or_redirect(request: Request, db: AsyncSession):
    """Returns user_info or None if unauthenticated."""
    try:
        return await get_user_data(request, db)
    except HTTPException as e:
        if e.status_code == 401:
            return None
        raise


# ── Router ───────────────────────────────────────────────────────────────────


def become_host(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    BASE_DIR = Path(__file__).resolve().parents[2]  # finalProject/
    HOSTERS_INFO_DIR = BASE_DIR / "static" / "hosters-info"
    PROOF_DIR = BASE_DIR / "static" / "proof-doc"

    os.makedirs(HOSTERS_INFO_DIR, exist_ok=True)
    os.makedirs(PROOF_DIR, exist_ok=True)
    # ── Entry point ──────────────────────────────────────────────────────────

    @app.get("/become-host")
    async def get_become_host(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        # Already a host — send them to the listing page
        if user_info.get("is_host"):
            return RedirectResponse("/host", status_code=303)

        # Resume from wherever they left off
        step = _get_resume_step(user_info)
        return RedirectResponse(f"/become-host/step{step}", status_code=303)

    # ── Step 1 – Basic information ───────────────────────────────────────────

    @app.get("/become-host/step1")
    async def get_step1(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        if user_info.get("phone_number") and user_info.get("email_verified"):
            return RedirectResponse("/become-host/step2", status_code=303)

        # fetch full verification info
        result = await db.execute(
            text("""
                SELECT email, phone_number, email_verified,
                       phone_verified, id_verified, account_verified
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": user_info["user_id"]},
        )
        row = result.fetchone()
        info = dict(row._mapping) if row else {}

        return templates.TemplateResponse(
            "step1.html",
            {
                "request": request,
                "user_info": user_info,
                "info": info,
            },
        )

    @app.post("/become-host/step1")
    async def post_step1(
        request: Request,
        db: AsyncSession = Depends(get_db),
        phone_number: str = Form(...),
        country: str = Form(...),
        city: str = Form(...),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        await db.execute(
            text("""
                UPDATE users
                SET phone_number = :phone,
                    country      = :country,
                    city         = :city
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

    # ── Step 2 – Identity verification ──────────────────────────────────────

    @app.get("/become-host/step2")
    async def get_step2(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "step2.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    @app.post("/become-host/step2")
    async def post_step2(
        request: Request,
        db: AsyncSession = Depends(get_db),
        id_photo: List[UploadFile] = File(...),
        selfie_photo: UploadFile = File(...),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        try:
            id_photos_url = []
            for img in id_photo:
                filename = f"{user_info['user_name']}-id_photo-{img.filename}"
                file_path = os.path.join(HOSTERS_INFO_DIR, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await img.read())
                id_photos_url.append(f"/hosters-info/{filename}")

            selfie_name = (
                f"{user_info['user_name']}-selfie_photo-{selfie_photo.filename}"
            )
            selfie_path = os.path.join(HOSTERS_INFO_DIR, selfie_name)
            with open(selfie_path, "wb") as buffer:
                buffer.write(await selfie_photo.read())
            selfie_url = f"/hosters-info/{selfie_name}"

            # Insert or update if they're resubmitting
            await db.execute(
                text("""
                    INSERT INTO host_verifications (user_id, id_photo_urls, selfie_photo_url)
                    VALUES (:user_id, :id_photos, :selfie)
                    ON CONFLICT (user_id) DO UPDATE
                        SET id_photo_urls    = EXCLUDED.id_photo_urls,
                            selfie_photo_url = EXCLUDED.selfie_photo_url,
                            submitted_at     = NOW()
                """),
                {
                    "user_id": user_info["user_id"],
                    "id_photos": id_photos_url,
                    "selfie": selfie_url,
                },
            )
            await db.commit()

        except Exception as e:
            print("Error while uploading:", e)
            return templates.TemplateResponse(
                "become_host/step2.html",
                {
                    "request": request,
                    "user_info": user_info,
                    "error": "Upload failed, please try again.",
                },
            )

        return RedirectResponse("/become-host/step3", status_code=303)

    # ── Step 3 – Property authorization ─────────────────────────────────────

    @app.get("/become-host/step3")
    async def get_step3(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "step3.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    @app.post("/become-host/step3")
    async def post_step3(
        request: Request,
        db: AsyncSession = Depends(get_db),
        host_role: str = Form(...),  # 'owner', 'manager', 'subletter'
        proof_document: UploadFile = File(...),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        try:
            filename = f"{user_info['user_name']}-proof_doc-{proof_document.filename}"
            file_path = os.path.join(PROOF_DIR, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await proof_document.read())
            proof_doc_url = f"/proof-doc/{filename}"

            await db.execute(
                text("""
                    INSERT INTO host_verifications (user_id, host_role, proof_doc_url)
                    VALUES (:user_id, :host_role, :proof_doc_url)
                    ON CONFLICT (user_id) DO UPDATE
                        SET host_role     = EXCLUDED.host_role,
                            proof_doc_url = EXCLUDED.proof_doc_url
                """),
                {
                    "user_id": user_info["user_id"],
                    "host_role": host_role,
                    "proof_doc_url": proof_doc_url,
                },
            )
            await db.commit()

        except Exception as e:
            print("Error while uploading proof document:", e)
            return templates.TemplateResponse(
                "become_host/step3.html",
                {
                    "request": request,
                    "user_info": user_info,
                    "error": "Upload failed, please try again.",
                },
            )

        return RedirectResponse("/become-host/step4", status_code=303)

    # ── Step 4 – Property listing details ───────────────────────────────────

    @app.get("/become-host/step4")
    async def get_step4(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "step4.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    @app.post("/become-host/step4")
    async def post_step4(
        request: Request,
        db: AsyncSession = Depends(get_db),
        property_type: str = Form(...),
        country: str = Form(...),
        city: str = Form(...),
        address: str = Form(...),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        query = """
            INSERT INTO listings (property_type, country, city, address)
            VALUES (:property_type, :country, :city, :address)
        """
        await db.execute(
            text(query),
            {
                "property_type": property_type,
                "country": country,
                "city": city,
                "address": address,
            },
        )
        db.commit()

        return RedirectResponse("/become-host/step5", status_code=303)

    # ── Step 5 – Payment setup ───────────────────────────────────────────────

    @app.get("/become-host/step5")
    async def get_step5(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "step5.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    @app.post("/become-host/step5")
    async def post_step5(
        request: Request,
        db: AsyncSession = Depends(get_db),
        account_name: str = Form(...),
        bank_name: str = Form(...),
        account_number: str = Form(...),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        try:
            # Only encrypt the sensitive field
            encrypted_account_number = encrypt(account_number)

            await db.execute(
                text("""
                    INSERT INTO host_payment_info
                        (user_id, account_name, bank_name, account_number)
                    VALUES
                        (:user_id, :account_name, :bank_name, :account_number)
                    ON CONFLICT (user_id) DO UPDATE
                        SET account_name   = EXCLUDED.account_name,
                            bank_name      = EXCLUDED.bank_name,
                            account_number = EXCLUDED.account_number,
                            updated_at     = NOW()
                """),
                {
                    "user_id": user_info["user_id"],
                    "account_name": account_name,
                    "bank_name": bank_name,
                    "account_number": encrypted_account_number,
                },
            )
            await db.commit()

        except Exception as e:
            print("Error saving payment info:", e)
            return templates.TemplateResponse(
                "become_host/step5.html",
                {
                    "request": request,
                    "user_info": user_info,
                    "error": "Could not save payment info. Please try again.",
                },
            )

        return RedirectResponse("/become-host/step6", status_code=303)

    # ── Step 6 – Terms & confirmation ────────────────────────────────────────

    @app.get("/become-host/step6")
    async def get_step6(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "step6.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    @app.post("/become-host/step6")
    async def post_step6(
        request: Request,
        db: AsyncSession = Depends(get_db),
        terms_agreed: str = Form(...),
        legal_right_confirmed: str = Form(...),  # ← add this
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        if terms_agreed and legal_right_confirmed:
            await db.execute(
                text("""
                UPDATE users
                SET agreed_terms          = TRUE,
                    legal_right_confirmed = TRUE,
                    agreed_at             = NOW(),
                    account_verified      = 'pending'
                WHERE user_id = :user_id
            """),
                {"user_id": user_info["user_id"]},
            )
            await db.commit()
            return RedirectResponse("/become-host/pending", status_code=303)

        return templates.TemplateResponse(
            "step6.html",
            {
                "error": "You can't continue withou agreed at the terms and conditions",
            },
        )

    # ── Pending approval page ────────────────────────────────────────────────

    @app.get("/become-host/pending")
    async def get_pending(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "pending.html",
            {
                "request": request,
                "user_info": user_info,
            },
        )

    # ── Email verification ───────────────────────────────────────────────────

    @app.post("/verify-email/send")
    async def send_verification_email(
        request: Request,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
    ):
        user_info = await _get_user_or_redirect(request, db)
        if not user_info:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        # Fetch email from DB (in case get_user_data doesn't include it)
        result = await db.execute(
            text("SELECT email FROM users WHERE user_id = :user_id"),
            {"user_id": user_info["user_id"]},
        )
        row = result.fetchone()
        if not row:
            return JSONResponse({"error": "User not found"}, status_code=404)

        email = row[0]
        token = secrets.token_urlsafe(32)

        await db.execute(
            text("""
                UPDATE users
                SET email_verify_token   = :token,
                    email_verify_expires = NOW() + INTERVAL '1 hour'
                WHERE user_id = :user_id
            """),
            {"token": token, "user_id": user_info["user_id"]},
        )
        await db.commit()

        verify_link = f"{request.base_url}verify-email/confirm?token={token}"
        background_tasks.add_task(send_email, email, verify_link)

        return JSONResponse({"message": "Email sent"})

    @app.get("/verify-email/confirm")
    async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            text("""
                SELECT user_id FROM users
                WHERE email_verify_token   = :token
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
                SET email_verified       = TRUE,
                    email_verify_token   = NULL,
                    email_verify_expires = NULL
                WHERE user_id = :user_id
            """),
            {"user_id": row.user_id},
        )
        await db.commit()
        return RedirectResponse("/become-host/step1", status_code=303)


# ── Resume helper ────────────────────────────────────────────────────────────


def _get_resume_step(user_info: dict) -> int:
    """Return the step number the user should resume from."""
    if not user_info.get("phone_number") or not user_info.get("email_verified"):
        return 1
    if not user_info.get("id_verified"):
        return 2
    if not user_info.get("property_authorized"):
        return 3
    if not user_info.get("listing_created"):
        return 4
    if not user_info.get("payment_setup"):
        return 5
    if not user_info.get("agreed_terms"):
        return 6
    return 6
