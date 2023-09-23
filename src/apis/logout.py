from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.config import config
from src.connect import redis
from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)

class Logout(HTTPEndpoint):
    @executor(login_require=login_require)
    async def post(self, user):
        email = user.get('email')
        redis.delete(email)
        return 'success'