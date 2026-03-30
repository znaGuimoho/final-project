from app.config import create_app
from app.events.contact_events import register_socketio_handelers
from app.routers.auth import auth_rout
from app.routers.contact import contact
from app.routers.favorites import favorite
from app.routers.home import home
from app.routers.hoster import hosting
from app.routers.more import more
from app.routers.profile import profile

# ── App setup ──────────────────────────────────────────────────────────────
app_sio, sio, app, get_db, templates, redis = create_app()

# ── Register routers ───────────────────────────────────────────────────────
routers = [
    auth_rout,
    hosting,
    home,
    more,
    contact,
    favorite,
    profile,
]

for router in routers:
    router(app, templates, get_db, sio)

# ── Socket.IO handlers ─────────────────────────────────────────────────────
register_socketio_handelers(app, templates, get_db, app_sio, sio)

# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app_sio", host="0.0.0.0", port=8000, reload=True)
