import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _get_stats(db: AsyncSession) -> dict:
    total_users = await db.scalar(text("SELECT COUNT(*) FROM users"))
    banned_users = await db.scalar(
        text("SELECT COUNT(*) FROM users WHERE banned = TRUE")
    )
    total_admins = await db.scalar(
        text("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
    )
    active_houses = await db.scalar(text("SELECT COUNT(*) FROM houses"))

    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)

    return {
        "total_users": total_users or 0,
        "banned_users": banned_users or 0,
        "total_admins": total_admins or 0,
        "active_houses": active_houses or 0,
    }
