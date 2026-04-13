from app.services.user_service import get_user_data
from fastapi import (
    HTTPException,
    Request,
)
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


# ── admin requirement ─────────────────────────────────────────────────────────────
async def require_admin(request: Request, db: AsyncSession):
    user_info = await _get_user_or_redirect(request, db)
    if not user_info:
        return None
    if not user_info.get("is_admin"):
        return None
    return user_info


# ── super admin requirement ─────────────────────────────────────────────────────────────
async def require_super_admin(request: Request, db: AsyncSession):
    user_info = await _get_user_or_redirect(request, db)
    if not user_info:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not user_info.get("is_super_admin"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_info
