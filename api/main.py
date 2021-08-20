# Modified:    2021-08-20
# Description: The api's entry point

import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from .controllers import player_router, game_router


# create the app
app = FastAPI()

# start the server
if __name__ == '__main__':
    uvicorn.run(
        "main: app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG_MODE,
    )

    # attach attach API endpoints
    # app.include_router(game_router, tags=["game"], prefix="/game")
    # app.include_router(move_router, tags=["move"], prefix="/move")
    app.include_router(player_router, tags=["player"], prefix="/player")

    # open an asynchronous database connection on startup
    @app.on_event("startup")
    async def open_mongodb_connection():
        app.client = AsyncIOMotorClient(settings.MONGODB_URI)
        app.db = app.client[settings.DB_NAME]

    # close the asynchronous database connection on shutdown
    @app.on_event("shutdown")
    async def close_mongodb_connection():
        app.client.close()
