# Modified:    2021-10-19
# Description: Defines the FastAPI app
#
import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.controllers import game_controller, player_controller
from api.db import db
from api.config import settings

# create the app
app = FastAPI()

# find the absolute path to static_content
static_content_dir = os.path.dirname(os.path.abspath(__file__)) + "/static_content/"

# attach CORS middleware; current settings are only appropriate for development environments
origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# attach attach API endpoints
app.include_router(game_controller.router, tags=["game"], prefix="/api/game")
app.include_router(player_controller.router, tags=["player"], prefix="/api/player")
app.mount("/", StaticFiles(directory=static_content_dir, html=True), name="static")


# open an asynchronous database connection on startup
@app.on_event("startup")
async def open_mongodb_connection():
    print("Connecting to MongoDB client...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    await db.index()  # index the db for faster lookups and to enforce uniqueness
    print("Connection successful" if db.client else "Connection failed")


# close the asynchronous database connection on shutdown
@app.on_event("shutdown")
async def close_mongodb_connection():
    print("Closing connection to MongoDB client...")
    db.client.close()
