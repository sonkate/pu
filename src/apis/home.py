from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.config import config
from src.helper.register import is_exists_user_maker
from src.lib.roles import Role
from src.helper.encrypt_password import generate_hased_password
from src.models.user import Users

from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)

from src.connect import redis, session
from sqlalchemy import insert
class Home(HTTPEndpoint):
    @executor()
    async def get(self):
        if not await is_exists_user_maker():
            (password, b_pasword) = generate_hased_password(6)
            await session.execute(
                insert(Users).
                values(email = 'admin', role = Role.CHECKER.value, password = b_pasword, is_active = True)
            )
            await session.commit()
            return 'This is password of admin: {}'.format(password)
        return 'success'