# Modified:    2021-08-24
# Description: The api's entry point

import uvicorn
from config import settings

# start the server
if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
