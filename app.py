from fastapi import FastAPI
from database import engine, Base
from routers.auth_router import router as auth_router
from routers.ocr_router import router as ocr_router
from routers.index_router import router as index_router
from config import settings
import uvicorn


# declaring FastAPI app
app = FastAPI()

# create all tables for first time
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth_router)
app.include_router(ocr_router)
app.include_router(index_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
