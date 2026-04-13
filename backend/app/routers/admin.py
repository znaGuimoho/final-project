from app.services.auth_helper import require_admin, require_super_admin
from app.services.stats import _get_stats
from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Router ───────────────────────────────────────────────────────────────────


def admin_dashboard(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    print("called")

    @app.get("/admin/review")
    async def get_review(request: Request, db: AsyncSession = Depends(get_db)):
        print("called")
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
            "admin_dir/adminReview.html",
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

    @app.get("/super_admin", response_class=HTMLResponse)
    async def super_admin_dashboard(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        user = await require_super_admin(request, db)
        stats = await _get_stats(db)

        return templates.TemplateResponse(
            "/admin_dir/superAdmin.html",
            {
                "request": request,
                "user": user,
                "stats": stats,
            },
        )

    @app.get("/super_admin/api/stats")
    async def super_admin_stats(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        """JSON — for live dashboard refresh via fetch()."""
        await require_super_admin(request, db)
        return await _get_stats(db)

    # ── Admin management ─────────────────────────────────────────────────────────
    @app.get("/super_admin/admins")
    async def get_admins(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await require_super_admin(request, db)

        result = await db.execute(text("SELECT * FROM users WHERE is_admin = true"))
        admins = [
            dict(row._mapping) for row in result.fetchall()
        ]  # ← same as your adminReview

        return templates.TemplateResponse(
            "/admin_dir/admins.html",
            {"request": request, "user_info": user_info, "admins": admins},
        )

    @app.post("/super_admin/admins/promote/{user_id}")
    async def promote_to_admin(
        user_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)

        await db.execute(
            text("UPDATE users SET is_admin = TRUE WHERE id = :id"), {"id": user_id}
        )
        await db.commit()
        return {"detail": f"User {user_id} promoted to admin"}

    @app.post("/super_admin/admins/demote/{user_id}")
    async def demote_admin(
        user_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)

        await db.execute(
            text("UPDATE users SET is_admin = FALSE WHERE id = :id"), {"id": user_id}
        )
        await db.commit()
        return {"detail": f"User {user_id} demoted"}

    # ── User management ──────────────────────────────────────────────────────────
    @app.get("/super_admin/users")
    async def get_users(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await require_super_admin(request, db)

        result = await db.execute(
            text("""
                SELECT user_id, user_name, email, phone_number,
                       country, city, email_verified, is_host,
                       banned, is_admin
                FROM users
                WHERE is_admin = FALSE AND is_super_admin = FALSE
            """)
        )
        users = [dict(row._mapping) for row in result.fetchall()]

        # counts for the stats strip
        total_count = len(users)
        verified_count = sum(1 for u in users if u["email_verified"])
        host_count = sum(1 for u in users if u["is_host"])
        banned_count = sum(1 for u in users if u["banned"])

        return templates.TemplateResponse(
            "/admin_dir/users.html",
            {
                "request": request,
                "user_info": user_info,
                "users": users,
                "total_count": total_count,
                "verified_count": verified_count,
                "host_count": host_count,
                "banned_count": banned_count,
            },
        )

    @app.post("/super_admin/users/ban/{user_id}")
    async def ban_user(
        user_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)

        await db.execute(
            text("UPDATE users SET is_banned = TRUE WHERE id = :id"), {"id": user_id}
        )
        await db.commit()
        return {"detail": f"User {user_id} banned"}

    @app.post("/super_admin/users/unban/{user_id}")
    async def unban_user(
        user_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)

        await db.execute(
            text("UPDATE users SET is_banned = FALSE WHERE id = :id"), {"id": user_id}
        )
        await db.commit()
        return {"detail": f"User {user_id} unbanned"}

    # ── Listing management ───────────────────────────────────────────────────────
    @app.get("/super_admin/listings")
    async def get_listings(request: Request, db: AsyncSession = Depends(get_db)):
        user_info = await require_super_admin(request, db)

        result = await db.execute(
            text("""
                SELECT
                    id,
                    category,
                    price,
                    location_name,
                    location_url,
                    img_url,
                    details,
                    details->>'hoster_id'     AS hoster_id,
                    details->>'hoster_name'   AS hoster_name,
                    details->>'house_details' AS house_details
                FROM houses
                ORDER BY id DESC
            """)
        )
        listings = [dict(row._mapping) for row in result.fetchall()]

        total_count = len(listings)
        house_count = sum(1 for l in listings if l["category"] == "house")
        hotel_count = sum(1 for l in listings if l["category"] == "hotel")
        hostel_count = sum(1 for l in listings if l["category"] == "hostel")

        return templates.TemplateResponse(
            "/admin_dir/listings.html",
            {
                "request": request,
                "user_info": user_info,
                "listings": listings,
                "total_count": total_count,
                "house_count": house_count,
                "hotel_count": hotel_count,
                "hostel_count": hostel_count,
            },
        )

    @app.delete("/super_admin/listings/{house_id}")
    async def delete_listing(
        house_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)

        # delete dependent rows first, then the house
        await db.execute(
            text("DELETE FROM contact_history WHERE house_id = :id"), {"id": house_id}
        )
        await db.execute(
            text("DELETE FROM myfavorite WHERE house_id = :id"), {"id": house_id}
        )
        await db.execute(text("DELETE FROM houses WHERE id = :id"), {"id": house_id})
        await db.commit()
        return {"detail": f"Listing {house_id} deleted"}

    # ── Platform settings ────────────────────────────────────────────────────────

    class PlatformSettings(BaseModel):
        platform_fee_percent: float | None = None
        max_listings_per_user: int | None = None
        allow_new_registrations: bool | None = None

    @app.patch("/super_admin/settings")
    async def update_settings(
        settings: PlatformSettings,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        await require_super_admin(request, db)
        # Persist to a platform_settings table or a config file — adapt as needed
        return {
            "detail": "Settings updated",
            "applied": settings.dict(exclude_none=True),
        }
