from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
SQLALCHEMY_DATABASE_URL = f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_USER_PASSWORD}@{settings.DB_DOCKER_SERVICE}/{settings.APP_DATABASE}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()
