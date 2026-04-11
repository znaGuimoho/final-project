from app.services.auth_helper import require_admin
from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Router ───────────────────────────────────────────────────────────────────


def admin_dashboard(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/admin/review")
    async def get_review(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await require_admin(request, db)
        if not user_info:
            # don't reveal it exists — return 404 not 403
            raise HTTPException(status_code=404)

        result = await db.execute(
            text("""
            SELECT 
                u.user_id, u.user_name, u.email, u.phone_number,
                u.country, u.city, u.email_verified, u.id_verified,
                u.account_verified, u.agreed_at,
                hv.id_photo_urls, hv.selfie_photo_url,
                hv.host_role, hv.proof_doc_url, hv.submitted_at
            FROM users u
            LEFT JOIN host_verifications hv ON hv.user_id = u.user_id
            WHERE u.account_verified = 'pending'
            ORDER BY hv.submitted_at ASC
        """)
        )
        applicants = [dict(row._mapping) for row in result.fetchall()]

        approved = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE account_verified = 'approved'")
        )
        rejected = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE account_verified = 'rejected'")
        )
        total = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE is_host = TRUE")
        )

        return templates.TemplateResponse(
            "adminReview.html",
            {
                "request": request,
                "user_info": user_info,
                "applicants": applicants,
                "approved_count": approved.scalar(),
                "rejected_count": rejected.scalar(),
                "total_hosts": total.scalar(),
            },
        )

    @app.post("/admin/review/{user_id}/approve")
    async def approve_host(
        user_id: int, request: Request, db: AsyncSession = Depends(get_db)
    ):
        user_info = await require_admin(request, db)
        if not user_info:
            raise HTTPException(status_code=404)

        await db.execute(
            text("""
                UPDATE users
                SET account_verified = 'approved',
                    is_host = TRUE
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        )
        await db.commit()
        return RedirectResponse("/admin/review", status_code=303)

    @app.post("/admin/review/{user_id}/reject")
    async def reject_host(
        user_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
        reason: str = Form(""),
    ):
        user_info = await require_admin(request, db)
        if not user_info:
            raise HTTPException(status_code=404)

        await db.execute(
            text("""
                UPDATE users
                SET account_verified = 'rejected'
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        )
        await db.execute(
            text("""
                UPDATE host_verifications
                SET notes = :reason, reviewed_at = NOW(), reviewed_by = :admin_id
                WHERE user_id = :user_id
            """),
            {"reason": reason, "admin_id": user_info["user_id"], "user_id": user_id},
        )
        await db.commit()
        return RedirectResponse("/admin/review", status_code=303)

    @app.get("/super_admin")
    async def get_super_admin(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await require_admin(request, db)
        return {"superadmin": "hello admin"}
