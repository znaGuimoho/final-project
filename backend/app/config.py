###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||   this is the config.py file where I set all of my configs that       ||##########################################
##########################################||               I'll need in the entire project                         ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################
import os
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

##########################################################################
################## Load environment variables from .env ##################
##########################################################################
load_dotenv()


#############################################################
################## this is socketio set up ##################
#############################################################
sio = socketio.AsyncServer (
    async_mode = "asgi",
    cors_allowed_origins = "*"
)

#############################################################
################## this is FastAPI set up ##################
#############################################################
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "backend", "app", "static", "uploads")

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/script", StaticFiles(directory=os.path.join(FRONTEND_DIR, "script")), name="script")
app.mount("/imgs", StaticFiles(directory=os.path.join(FRONTEND_DIR, "imgs")), name="imgs")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app_sio = socketio.ASGIApp(sio, app)
templates = Jinja2Templates(directory=FRONTEND_DIR)

#######################################################################
################## Database setup (Async PostgreSQL) ##################
#######################################################################
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:M123%40moha_fg@localhost:5432/houserent_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


#################################################################################################################################################
############################## this is the fuction that retuns the varibles that I'LL weork with in the other files ##############################
#################################################################################################################################################

def create_app():
    """
    Returns the FastAPI + Socket.IO application instance.
    """
    app_sio = socketio.ASGIApp(sio, app)
    return app_sio, sio, app, get_db, templates