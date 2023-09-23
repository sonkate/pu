from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.schema.reset_password import ResetPassword, VerifyResetPassword, ChangeResetPassword

from sqlalchemy import select, update
from src.connect import session, redis
from src.models.user import Users
from src.config import config
from src.tasks import task
from src.helper.encrypt_password import hash_password
from src.helper.validate_password import validate_password
from src.helper.register import is_exists_email
import jwt
from src.lib.authentication import JsonWebToken
reset_pw_token = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
class ResetPassword(HTTPEndpoint):
    @executor(form_data=ResetPassword)
    async def post(self, form_data):
        email = form_data.get('email')
        if await is_exists_email(email):
            temp = reset_pw_token.create_token(email)
            token = temp.get('token')
            redis.set(email, token)
            # Send email with link to verify token
            message = 'Please click this link to verify your token: {}?token={}'.format(config.BASE_URL_RESET_PW, token)
            task.send_task('worker.send_mail', ("customer_email", email, message), queue = 'send_mail')
            return "success"
        else:
            # email does not exist
            raise BadRequest(errors="user does not exist")
    @executor(query_params=VerifyResetPassword)
    async def get(self, query_params):
        token = query_params['token']
        _decode = jwt.decode(token, key=config.KEY_JWT,
                                    algorithms=[config.ALGORITHM_HASH_TOKEN])
        email = _decode.get('payload')
        stored_token = redis.get(email).decode()
        if stored_token == token:
            # let user change password
            return "success"
        else:
            raise BadRequest(errors="Token does not match")

    @executor(form_data=ChangeResetPassword, query_params=VerifyResetPassword)
    async def put(self, form_data, query_params):
        token = query_params['token']
        _decode = jwt.decode(token, key=config.KEY_JWT,
                                    algorithms=[config.ALGORITHM_HASH_TOKEN])
        email = _decode.get('payload')
        if not validate_password(form_data['new_password']):
            raise BadRequest(errors="please check password constraint")
        elif form_data['new_password'] != form_data['confirm_password']:
            raise BadRequest(errors="confirm password is not correct")
        else:
            new_password = hash_password(form_data['new_password'])
            await session.execute(
                update(Users).
                where(Users.email == email).
                values(password = new_password))
            await session.commit()
            return "success"