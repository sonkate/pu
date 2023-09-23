from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.schema.login import Login
from src.helper.encrypt_password import check_password
from src.helper.roles import get_role_by_email
from src.config import config
from src.connect import session
from src.models.user import Users
from sqlalchemy import update, select
from src.lib.authentication import JsonWebToken
import json
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
MAX_LOGIN_ATTEMPTS = 5
FAILED_LOGIN_PREFIX = "failed_login: "
from src.connect import redis
class Login(HTTPEndpoint):
    @executor(form_data = Login)
    async def post(self,form_data):
        email = form_data['email']
        # check password
        check_pw, user_created =  await check_password(email, form_data['password'])
        if not user_created:
            raise BadRequest(errors="Please regist an account")
        # check if the account is locked
        result = await session.execute(select(Users).filter_by(**{'email' : email}))
        result = result.fetchall()
        item = result[0]
        dict_item = item[0].as_dict
        if not dict_item['is_active']:
            raise BadRequest(errors="This account is locked")
        else:
            redis.delete(FAILED_LOGIN_PREFIX + email)
        if not check_pw:
            login_attempts = redis.incr(FAILED_LOGIN_PREFIX + email)
            if login_attempts >= MAX_LOGIN_ATTEMPTS:
                await session.execute(update(Users).
                                where(Users.email == email).
                                values(is_active = False))
                await session.commit()
                raise BadRequest(errors="Maximum login attempts exceeded. Account locked.")
            else:
                raise BadRequest(errors="Wrong password")
        # login success
        redis.delete(FAILED_LOGIN_PREFIX + email)
        role = await get_role_by_email(email)
        token = login_require.create_token(payload_data={'email': email, 'role': role})
        _token = json.dumps(token)
        redis.set(email, _token)
        return 'success'