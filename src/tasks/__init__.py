from src.config import config
from celery import Celery
task = Celery(__name__, broker=config.BROKER_URL, backend=config.BROKER_URL)