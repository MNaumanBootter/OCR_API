from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL as sqlalchemy_engine_URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import app_config


engine = create_engine(
    sqlalchemy_engine_URL.create(
        drivername=app_config.DB_DRIVER,  # e.g "mysql" or "pymsql+mysql"
        username=app_config.DB_USER,  # e.g. "my-database-user"
        password=app_config.DB_PASSWORD,  # e.g. "my-database-password"
        host=app_config.DB_HOST,  # e.g. "127.0.0.1"
        port=app_config.DB_PORT,  # e.g. 3306
        database=app_config.DATABASE_NAME,  # e.g. "my-database-name"

    )
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
