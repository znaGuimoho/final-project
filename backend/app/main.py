from app.config import create_app
from app.routers.auth import auth_rout
from app.routers.hoster import hosting
from app.routers.home import home
from app.routers.more import more
from app.routers.contact import contuct
from app.events.contact_events import register_socketio_handelers

#---------------------------------------------------
#----------GET THE VARIBLES FROM config.py----------
#---------------------------------------------------
app_sio, sio, app, get_db, templates, redis = create_app()

#-----------------------------------------------------------------
#----------THE ROUTED FOR THE login and register auth.py----------
#-----------------------------------------------------------------
auth_rout(app, templates, get_db, sio)

#-----------------------------------------------------------------
#----------TTHE ROUTED FOR hosters and simular tasks -------------
#-----------------------------------------------------------------
hosting(app, templates, get_db, sio)

#-----------------------------------------------------------------
#----------TTHE ROUTED FOR home pages-----------------------------
#-----------------------------------------------------------------
home(app, templates, get_db, sio)

#-----------------------------------------------------------------
#----------TTHE ROUTED FOR more options---------------------------
#-----------------------------------------------------------------
more(app, templates, get_db, sio)

#-----------------------------------------------------------------
#----------TTHE ROUTED FOR contact the hoster --------------------
#-----------------------------------------------------------------
contuct(app, templates, get_db, sio)

register_socketio_handelers(app, templates, get_db, app_sio, sio)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app_sio", host="0.0.0.0", port=8000, reload=True)