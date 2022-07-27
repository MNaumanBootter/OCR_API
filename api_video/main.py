from fastapi import FastAPI
from database import engine, Base
from routers.video_router import router as video_router
from routers.index_router import router as index_router
from config import app_config
import uvicorn


# declaring FastAPI app
app = FastAPI()

# create all tables for first time
Base.metadata.create_all(bind=engine)

# routers
app.include_router(video_router)
app.include_router(index_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=app_config.API_PORT_DOCKER)
