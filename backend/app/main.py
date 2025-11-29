from app.config import create_app
from app.routers.auth import auth_rout
from app.routers.hoster import hosting
from app.routers.home import home
from app.routers.more import more

#---------------------------------------------------
#----------GET THE VARIBLES FROM config.py----------
#---------------------------------------------------
app_sio, sio, app, get_db, templates = create_app()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_sio, host="0.0.0.0", port=8000)