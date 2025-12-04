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
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import redis.asyncio as aioredis

##########################################################################
################## Load environment variables from .env ##################
##########################################################################
load_dotenv()

#############################################################
################## this is socketio set up ##################
#############################################################
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=['http://127.0.0.1:8000', 'http://localhost:8000', 'http://127.0.0.1', 'http://localhost'],
    cors_credentials=True,
    logger=True,  # Enable logging to see what's happening
    engineio_logger=True
)

#############################################################
################## this is FastAPI set up ##################
#############################################################
app = FastAPI()

# Add CORS middleware BEFORE mounting Socket.IO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute paths that work in Docker environments
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

#without docker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")

# Create directories if they don't exist
os.makedirs(FRONTEND_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Only mount static files if directories exist
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
    
    # Mount subdirectories only if they exist
    css_dir = os.path.join(FRONTEND_DIR, "css")
    script_dir = os.path.join(FRONTEND_DIR, "script") 
    imgs_dir = os.path.join(FRONTEND_DIR, "imgs")
    
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(script_dir):
        app.mount("/script", StaticFiles(directory=script_dir), name="script")
    if os.path.exists(imgs_dir):
        app.mount("/imgs", StaticFiles(directory=imgs_dir), name="imgs")

if os.path.exists(UPLOADS_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Create ASGI app with Socket.IO - SINGLE DEFINITION
app_sio = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path="socket.io"  # No leading slash
)

templates = Jinja2Templates(directory=FRONTEND_DIR if os.path.exists(FRONTEND_DIR) else BASE_DIR)

#######################################################################
################## Database setup (Async PostgreSQL) ##################
#######################################################################

#for docker
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/houserent_db"  # Use Docker service name
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

# ------------------------
# Redis connection
# ------------------------
redis = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True
)

#######################################################################
################## Function that returns variables ####################
#######################################################################

def create_app():
    """
    Returns the FastAPI + Socket.IO application instance.
    """
    # Return the already-created app_sio instead of creating a new one
    return app_sio, sio, app, get_db, templates, redis