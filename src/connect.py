from src.lib.postgres import Postgres
from src.config import config
import redis
db = Postgres(url=config.POSTGRES_URI)
session = db._make_session() # using session execute query

redis = redis.Redis(config.REDIS_URI)