from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    HASH_ALGORITHM: str
    DB_USER: str
    DB_USER_PASSWORD: str
    API_PORT: int
    DB_PORT: int
    APP_DATABASE: str
    DB_DRIVER: str
    DB_DOCKER_SERVICE: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    # SQLALCHEMY_DATABASE_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_USER_PASSWORD}@{DB_DOCKER_SERVICE}/{APP_DATABASE}"
    # ALEMBIC_DATABASE_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_USER_PASSWORD}@127.0.0.1:{DB_PORT}/{APP_DATABASE}"

settings = Settings()
