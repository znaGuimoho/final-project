# app/events/contact_events.py
from sqlalchemy import text
from datetime import datetime
from socketio import AsyncServer
from app.config import AsyncSessionLocal
from app.services.user_service import get_user_id_from_cookie
from app.services.redis_db import get_messages, save_message
from colorama import Fore, Style
import json

def register_socketio_handelers(app, templates, get_db, app_sio, sio: AsyncServer):
    user_sessions = {}
    
    @sio.event
    async def connect(sid, environ, auth=None):
        try:
            print(">>> SOCKET CONNECT attempt:", sid)

            cookie_header = environ.get("HTTP_COOKIE")
            print("COOKIE HEADER:", cookie_header)

            user_id = await get_user_id_from_cookie(environ)

            if not user_id:
                print(f"Unauthorized connection from {sid}")
                return False

            user_sessions[sid] = user_id

            print(f"Client {sid} authenticated as user {user_id}")
            return True

        except Exception as e:
            print("Exception in connect handler:", repr(e))
            return False

    
    @sio.event
    async def join_room(sid, data):
        """Join a room"""
        room = data.get('room')
        
        if not room:
            await sio.emit('error_message', {'message': 'No room code provided'}, to=sid)
            return
        
        current_user_id = user_sessions.get(sid)
        
        if not current_user_id:
            await sio.emit('error_message', {'message': 'Not authenticated'}, to=sid)
            return
        
        async with AsyncSessionLocal() as db:
            try:
                query = "SELECT user_id, hoster_id FROM contact_history WHERE room_name = :room"
                result = await db.execute(text(query), {"room": room})
                room_data = result.fetchone()
                
                if not room_data:
                    await sio.emit('error_message', {'message': 'Invalid room code'}, to=sid)
                    return
                
                user_id, hoster_id = room_data[0], room_data[1]
                
                if current_user_id not in [user_id, hoster_id]:
                    await sio.emit('error_message', {'message': 'Unauthorized'}, to=sid)
                    print(f"{Fore.RED}User {current_user_id} unauthorized for room {room}{Style.RESET_ALL}")
                    return
                
                await sio.enter_room(sid, room)
                await sio.emit('joined_room', {'room': room}, to=sid)
                print(f"{Fore.GREEN}User {current_user_id} joined room {room}{Style.RESET_ALL}")
                
                # Notify others
                role = "hoster" if current_user_id == hoster_id else "client"
                await sio.emit('user_joined', {
                    'message': f'The {role} has joined the chat'
                }, room=room, skip_sid=sid)
                
            except Exception as e:
                print(f"{Fore.RED}Error in join_room: {e}{Style.RESET_ALL}")
                await sio.emit('error_message', {'message': 'Server error'}, to=sid)
    
    @sio.event
    async def send_message(sid, data):
        room = data.get('room')
        message = data.get('message')

        if not room or not message:
            return

        current_user_id = user_sessions.get(sid)

        async with AsyncSessionLocal() as db:
            query = """SELECT user_id, hoster_id 
                    FROM contact_history 
                    WHERE room_name = :room"""
            result = await db.execute(text(query), {"room": room})
            user_id, hoster_id = result.fetchone()

        await save_message(
            room=room,
            sender_id=str(current_user_id),
            hoster=str(hoster_id),
            client=str(user_id),
            message=message,
            timestamp=datetime.now().isoformat()
        )

        sender_role = "hoster" if current_user_id == hoster_id else "client"

        QUERY = await db.execute(text("SELECT user_name FROM users WHERE user_id = :id"), {"id": current_user_id})
        row = QUERY.fetchone()
        name = row[0] if row else "Unknown"

        print(f"{Fore.GREEN}Message sent in room {room} by {name} ({sender_role}){Style.RESET_ALL}")

        await sio.emit('receive_message', {
            "message": message,
            "sender_id": current_user_id,
            "sender_role": sender_role,
            "sender_name": name,
            "timestamp": datetime.now().isoformat()
        }, room=room)

    
    @sio.event
    async def disconnect(sid):
        user_id = user_sessions.pop(sid, None)
        print(f"{Fore.GREEN}Client {sid} (user: {user_id}) disconnected{Style.RESET_ALL}")