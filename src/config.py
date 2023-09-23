from pydantic_settings import BaseSettings
import typing

class Config(BaseSettings):
    class Config:
        env_file = ".env"

    PROJECT_NAME: str = 'portal-user'
    POSTGRES_URI: str
    REDIS_URI: str
    PORT: typing.Optional[int]
    BROKER_URL: str
    CELERY_ROUTES: dict = {
        'worker.send_mail': {'queue': 'send_mail'},
    }
    BASE_URL_RESET_PW: str
    CELERY_IMPORTS: list = ['src.tasks']
    CELERY_RESULT_BACKEND:str = 'rpc://'
    CELERY_TRACK_STARTED:bool = True
    CELERY_RESULT_PERSISTENT:bool = True
    KEY_JWT: str
    ALGORITHM_HASH_TOKEN: str = "HS256"
config = Config()