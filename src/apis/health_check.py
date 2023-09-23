from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.connect import session
from src.models.test import Test
from sqlalchemy import select


class HealthCheck(HTTPEndpoint):

    @executor()
    async def get(self):
        return "health check"