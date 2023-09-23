from starlette.endpoints import HTTPEndpoint
from src.lib.executor import executor
from src.schema.approve_request import RequestEmail
from src.helper.encrypt_password import generate_hased_password
from sqlalchemy import select, insert, update, delete
from src.connect import session
from src.models.approve_request import ApproveRequests
from src.models.user import Users
from src.config import config
from src.helper.roles import get_role_by_email, Role
from src.tasks import task
from src.lib.request_type import RequestType
from src.lib.authentication import JsonWebToken
login_require = JsonWebToken(config.KEY_JWT, config.ALGORITHM_HASH_TOKEN)
from src.lib.exception import BadRequest
import json
class AllApproveRequest(HTTPEndpoint):
    @executor(login_require=login_require, allow_roles=[Role.CHECKER.value])
    async def get(self):
        list_data = []
        result = await session.execute(select(ApproveRequests))
        result = result.fetchall()
        for item in result:
            dict_item = item[0].as_dict
            list_data.append(dict_item)
        return list_data
class ApproveRequest(HTTPEndpoint):
    @executor(login_require=login_require, query_params=RequestEmail, allow_roles=[Role.CHECKER.value])
    async def get(self, query_params):
        request_email = query_params['email']
        result = await session.execute(select(ApproveRequests).filter_by(**{'email' : request_email}))
        result = result.fetchall()
        if not len(result):
            raise BadRequest(errors='user not found')
        item = result[0]
        dict_item = item[0].as_dict
        request_data = json.loads(dict_item['request_data'])
        return {
                'request_type': request_data['request_type'],
                'tax': request_data['tax'],
                'merchant_name': request_data['merchant_name'],
                'address': request_data['address'],
                'legal_representative:': request_data['legal_representative'],
                'email': request_data['email'],
                'is_active': request_data['is_active']
                }
    # accept request
    @executor(login_require=login_require, form_data=RequestEmail, allow_roles=[Role.CHECKER.value])
    async def post(self, form_data):
        request_email = form_data['email']
        result = await session.execute(select(ApproveRequests).filter_by(**{'email' : request_email}))
        result = result.fetchall()
        item = result[0]
        dict_item = item[0].as_dict
        request_data = json.loads(dict_item['request_data'])
        request_data['status'] = True
        if request_data['request_type'] == RequestType.CHANGE_PASSWORD:
            # update status of Approve Request table
            await session.execute(
                update(ApproveRequests).
                where(ApproveRequests.email == request_email).
                values(**{'request_data': json.dumps(request_data)})
            )
            await session.execute(
                update(Users).
                where(Users.email == request_email).
                values(password = request_data['new_password'])
            )
            await session.commit()
        if request_data['request_type'] == RequestType.UPDATE_ACCOUNT:
            # update status of Approve Request table
            await session.execute(
                update(ApproveRequests).
                where(ApproveRequests.email == request_email).
                values(**{'email': request_data['email'], 'request_data': json.dumps(request_data)})
            )
            del request_data['status']
            del request_data['request_type']
            await session.execute(
                update(Users).
                where(Users.email == request_email).
                values(**request_data)
            )
            await session.commit()
        if request_data['request_type'] == RequestType.DELETE_ACCOUNT:
            await session.execute(
                update(ApproveRequests).
                where(ApproveRequests.email == request_email).
                values(**{'request_data': json.dumps(request_data)})
            )

            await session.execute(
                delete(Users).
                where(Users.email == request_email)
            )
            await session.commit()
        if request_data['request_type'] == RequestType.CREATE_ACCOUNT:
            # update status of Approve Request table
            await session.execute(
                update(ApproveRequests).
                where(ApproveRequests.email == request_email).
                values(**{'request_data': json.dumps(request_data)})
            )
            # store data of user to posgreSQL
            (password, b_pasword) = generate_hased_password(12)
            request_data['password'] = b_pasword
            del request_data['status']
            del request_data['request_type']
            await session.execute(
                insert(Users).
                values(**request_data)
            )
            await session.commit()
            # send email notification
            message = 'This is your password {}'.format(password)
            task.send_task('worker.send_mail', ("customer_email", request_data['email'], message), queue = 'send_mail')
        return 'success'
    # deny request
    @executor(login_require=login_require, form_data=RequestEmail, allow_roles=[Role.CHECKER.value])
    async def put(self, form_data):
        request_email = form_data['email']
        result = await session.execute(select(ApproveRequests).filter_by(**{'email' : request_email}))
        result = result.fetchall()
        item = result[0]
        dict_item = item[0].as_dict
        request_data = json.loads(dict_item['request_data'])
        request_data['status'] = False
        await session.execute(
            update(ApproveRequests).
            where(ApproveRequests.email == request_email).
            values(**{'request_data': json.dumps(request_data)})
        )
        await session.commit()
        return 'success'