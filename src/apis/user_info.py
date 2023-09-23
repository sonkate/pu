from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.config import config
from src.connect import session
from src.models.user import Users
from src.models.approve_request import ApproveRequests
from src.helper.roles import Role, check_role_constraint
from src.helper.validate_password import validate_password
from src.helper.register import is_exists_email, is_exists_tax
from src.lib.request_type import RequestType
from sqlalchemy import select, insert, update, delete, or_
from src.schema.modify_user import EmailRoleModifyAccount, ModifyAccount
from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
import json
class UserInfo(HTTPEndpoint):
    @executor(login_require=login_require, allow_roles=[Role.CHECKER.value, Role.MAKER.value, Role.MERCHANT.value])
    async def get(self, user):
        user_role = user.get('role')
        if user_role == Role.MAKER.value or user_role == Role.CHECKER.value:
            result = await session.execute(select(Users).filter_by(or_(**{'role': Role.MERCHANT.value, 'role': Role.SUB_MERCHANT.value})))
            result = result.fetchall()
        if user_role == Role.MERCHANT.value:
            result = await session.execute(select(Users).filter_by(**{'role': Role.SUB_MERCHANT.value}))
            result = result.fetchall()
        list_item = []
        for item in result:
            dict_item = item[0].as_dict
            list_item.append(dict_item)
        return list_item
    # update account
    @executor(login_require=login_require, form_data=ModifyAccount, allow_roles=[Role.CHECKER.value, Role.MAKER.value, Role.MERCHANT.value])
    async def post(self, form_data, user):
        modifier_role = user.get('role')
        user_role = form_data['role']
        if not check_role_constraint(modifier_role, user_role):
            raise BadRequest(errors="Invalid role constraint")
        # check Email and tax
        if await is_exists_email(form_data['email']):
            raise BadRequest(errors="Email exists")
        if form_data['tax'] and await is_exists_tax(int(form_data['tax'])) and user_role == Role.MERCHANT.value:
            raise BadRequest(errors="Tax exists")
        # user_email - email of the user who will be modified
        user_email = form_data['user_email']
        del form_data['user_email']
        # store data to approve request table if creater is maker and user is merchant
        if modifier_role == Role.MAKER.value and user_role == Role.MERCHANT.value:
            form_data['request_type'] = RequestType.UPDATE_ACCOUNT.value
            await session.execute(insert(ApproveRequests)
                            .values(request_data = json.dumps(dict(form_data)), email = user_email))
            await session.commit()
        else:
            await session.execute(
                        update(Users).
                        where(Users.email == user_email).
                        values(form_data))
            await session.commit()
        return 'success'
    # delete account
    @executor(login_require=login_require, form_data=EmailRoleModifyAccount)
    async def delete(self, form_data, user):
        modifier_role = user.get('role')
        user_role = form_data['role']
        if not check_role_constraint(modifier_role, user_role):
            raise BadRequest(errors="Invalid role constraint")

        # store data to approve request table if creater is maker and user is merchant
        if modifier_role == Role.MAKER.value and user_role == Role.MERCHANT.value:
            form_data['request_type'] = RequestType.DELETE_ACCOUNT.value
            await session.execute(insert(ApproveRequests)
                            .values(request_data = json.dumps(dict(form_data))), email = form_data['email'])
            await session.commit()
        else:
            await session.execute(
                delete(Users).
                where(Users.email == form_data['email'])
            )
            await session.commit()
        return 'success'