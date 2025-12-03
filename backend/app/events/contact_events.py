from sqlalchemy import text
from datetime import datetime
from socketio import AsyncServer
import os
from werkzeug.utils import secure_filename
from app.services.user_service import get_user_data

SESSION_COOKIE = "session_id"

def register_socketio_handelers(app, templates, get_db, app_sio, sio: AsyncServer):
    @sio.event
    async def connect(environ):
        user_data = await get_user_data()

        if not user_data or not user_data["user_name"]:
            return False
        
        name = user_data["user_name"]
        
                

        