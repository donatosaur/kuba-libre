# Modified:    2021-09-05
# Description: Defines the FastAPI app
#
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.controllers import game_controller, player_controller
from api.db import db
from api.config import settings

# create the app
app = FastAPI()


# attach CORS middleware; current settings are only appropriate for development environments
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# attach attach API endpoints
app.include_router(game_controller.router, tags=["game"], prefix="/game")
app.include_router(player_controller.router, tags=["player"], prefix="/player")


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
