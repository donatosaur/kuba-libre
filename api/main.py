import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from fastapi import FastAPI


# create the app
app = FastAPI()
app.client = None

# start the server
if __name__ == '__main__':
    uvicorn.run(
        "main: app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG_MODE,
    )

    # open an asynchronous database connection
    @app.on_event("startup")
    async def open_mongodb_connection():
        app.client = AsyncIOMotorClient(settings.MONGODB_URI)
        app.db = app.client[settings.DB_NAME]

    @app.on_event("shutdown")
    async def close_mongodb_connection():
        app.client.close()
