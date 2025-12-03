import random
from sqlalchemy.ext.asyncio import AsyncSession
from string import ascii_uppercase
from sqlalchemy import text

async def generate_unique_code(length: int, db: AsyncSession):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length * 3))
        result = await db.execute(
            text("SELECT 1 FROM contact_history WHERE room_name = :code"),
            {"code": code}
        )
        row = result.first()
        if not row:
            break
    return code