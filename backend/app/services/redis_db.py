import json
from app.config import redis

async def save_message(room: str, sender_id: str, hoster: str, client: str, message: str, timestamp: str):
    sender_role = "hoster" if sender_id == hoster else "client"

    data = {
        "sender_id": sender_id,
        "sender_role": sender_role,
        "hoster": hoster,
        "client": client,
        "message": message,
        "timestamp": timestamp
    }

    await redis.rpush(f"room:{room}:messages", json.dumps(data))

async def get_messages(room: str, limit: int = 50):
    raw_messages = await redis.lrange(f"room:{room}:messages", -limit, -1)
    return [json.loads(m) for m in raw_messages]

async def delete_all_messages(room: str):
    """Delete all messages in a room"""
    await redis.delete(f"room:{room}:messages")
