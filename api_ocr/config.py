from os import path
from decouple import config

try:
    basedir = path.abspath(path.dirname(__file__))
except:
    pass

TEMP_ENV = config('ENV')

class Config:
    """Base config."""
    pass

    DATABASE_NAME = config('DB_NAME')


class DevConfig(Config):
    ENV = 'development'
    DEBUG = True
    TESTING = True
    API_PORT_DOCKER = config('API_PORT_DOCKER', cast=int)
    DB_HOST = config('DB_HOST')
    DB_PORT = config('DB_PORT', cast=int)
    DB_USER = "root"
    DB_PASSWORD = config('DB_PASSWORD')
    HASH_ALGORITHM = config('HASH_ALGORITHM')
    DB_DRIVER = config('DB_DRIVER')
    ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)
    SECRET_KEY = config('SECRET_KEY')
    CELERY_BROKER_URL = config('CELERY_BROKER_URL')
    CELERY_RESULT_URL = config('CELERY_RESULT_URL')


class TestConfig(Config):
    ENV = 'testing'
    DEBUG = False
    TESTING = False


class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False


def get_env():
    if TEMP_ENV == 'development':
        app_config = DevConfig()
        return app_config
    elif TEMP_ENV == 'testing':
        app_config = TestConfig()
        return app_config
    elif TEMP_ENV == 'production':
        app_config = ProdConfig()
        return app_config
    else:
        raise Exception("Invalid  ENV environment variable value")


app_config = get_env()
