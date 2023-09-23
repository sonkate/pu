from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.connect import session
from src.models.user import Users
from src.models.approve_request import ApproveRequests
from src.schema.register import Register
from sqlalchemy import select, insert
from src.helper.register import is_exists_email, is_exists_tax
from src.helper.encrypt_password import generate_hased_password
from src.helper.roles import check_role_constraint
from src.tasks import task
from src.config import config
from src.lib.roles import Role
from src.lib.request_type import RequestType
from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
import json
class Register(HTTPEndpoint):

    @executor(form_data = Register, login_require = login_require, allow_roles=[Role.CHECKER.value, Role.MERCHANT.value, Role.MAKER.value])
    async def post(self, form_data, user):
        # check role constraint
        creater_email = user.get('email')
        creater_role = user.get('role')
        user_role = form_data['role']
        if not check_role_constraint(creater_role, user_role):
            raise BadRequest(errors="Invalid role constraint")
        # check Email and tax
        if await is_exists_email(form_data['email']):
            raise BadRequest(errors="Email exists")
        if form_data['tax'] and await is_exists_tax(int(form_data['tax'])) and user_role == Role.MERCHANT.value:
            raise BadRequest(errors="Tax exists")
        # store data to approve request table if creater is maker and user is merchant
        if creater_role == Role.MAKER.value and user_role == Role.MERCHANT.value:
            form_data['request_type'] = RequestType.CREATE_ACCOUNT.value
            # add request to table
            await session.execute(insert(ApproveRequests)
                            .values(request_data = json.dumps(dict(form_data))), email = form_data.get('email'))
            await session.commit()
            return 'success'
        if user_role == Role.SUB_MERCHANT.value:
            result = await session.execute(select(Users).filter_by(**{'email' : creater_email}))
            result = result.fetchall()
            item = result[0]
            dict_item = item[0].as_dict
            form_data['parent_tax'] = dict_item['tax']
        # store data of user to posgreSQL
        (password, b_pasword) = generate_hased_password(12)
        form_data['password'] = b_pasword
        await session.execute(
            insert(Users).
            values(form_data)
        )
        await session.commit()
        # send email notification
        message = 'This is your password {}'.format(password)
        task.send_task('worker.send_mail', ("customer_email", form_data['email'], message), queue = 'send_mail')
        return "success"