# Modified:    2022-06-01
# Description: Defines the FastAPI app
#
import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from controllers import game_controller, player_controller
from db import db
from config import settings

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


class ReactStaticFiles(StaticFiles):
    """Extends StaticFiles to allow React SPA to handle 404s"""
    async def get_response(self, path, scope):
        res = await super().get_response(path, scope)
        if res.status_code == 404:
            # funnel 404s back to React App: source https://stackoverflow.com/a/68363904
            res = await super().get_response('.', scope)
        return res


# attach API endpoints
app.include_router(game_controller.router, tags=["game"], prefix="/api/game")
app.include_router(player_controller.router, tags=["player"], prefix="/api/player")
app.mount("/", ReactStaticFiles(directory=static_content_dir, html=True), name="static")


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
