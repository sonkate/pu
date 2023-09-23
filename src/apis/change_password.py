from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.schema.reset_password import ResetPassword
from src.schema.change_password import ChangePassword, ModifyPassword

from src.helper.encrypt_password import check_password, hash_password
from src.helper.validate_password import validate_password
from src.helper.roles import check_role_constraint, get_role_by_email
from sqlalchemy import update, insert
from src.connect import session
from src.models.user import Users
from src.models.approve_request import ApproveRequests
from src.config import config
from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
from src.tasks import task
from src.lib.request_type import RequestType
from src.lib.roles import Role
import json
class ChangePassword(HTTPEndpoint):
    @executor(login_require=login_require, form_data=ChangePassword)
    async def post(self, user, form_data):
        check_pw, _ =  await check_password(user['email'], form_data['current_password'])
        if not check_pw:
            raise  BadRequest(errors="Wrong password")
        else:
            if not validate_password(form_data['new_password']):
                raise  BadRequest(errors="Please check password constraint")
            if form_data['new_password'] != form_data['confirm_password']:
                raise  BadRequest(errors="confirm password is not correct")
            else:
                new_password = hash_password(form_data['new_password'])
                await session.execute(
                    update(Users).
                    where(Users.email == user['email']).
                    values(password = new_password))
                await session.commit()
                # send notification email
                message = 'Your password has been changed. This is your new password {}'.format(form_data['new_password'])
                task.send_task('worker.send_mail', ("customer_email", user['email'], message), queue = 'send_mail')
                return 'change password successfully'

    @executor(login_require=login_require, form_data=ModifyPassword)
    async def put(self, user, form_data):
        modifier_role = user.get('role')
        user_role = form_data['role']
        if not check_role_constraint(modifier_role, user_role):
            raise BadRequest(errors="Invalid role constraint")
        if not validate_password(form_data['new_password']):
            raise BadRequest(errors="Please check password constraint")
        if form_data['new_password'] != form_data['confirm_password']:
            raise BadRequest(errors="confirm password is not correct")

        new_password = hash_password(form_data['new_password'])
        # store data to approve request table if creater is maker and user is merchant
        if modifier_role == Role.MAKER.value and user_role == Role.MERCHANT.value:
            request_data = {'new_password': new_password, 'request_type': RequestType.CHANGE_PASSWORD.value}
            await session.execute(insert(ApproveRequests)
                            .values(request_data = json.dumps(request_data), email = form_data['email']))
            await session.commit()

        await session.execute(
            update(Users).
            where(Users.email == form_data['email']).
            values(password = new_password))
        await session.commit()
        return 'success'