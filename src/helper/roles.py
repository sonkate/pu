from src.lib.roles import Role
from src.connect import session
from sqlalchemy import select
from src.models.user import Users

def check_role_constraint(creater_role, user_role):
    if creater_role == Role.MAKER.value or creater_role == Role.CHECKER.value:
        if user_role == Role.MERCHANT.value or user_role == Role.SUB_MERCHANT.value:
            return True
    if creater_role == Role.MERCHANT.value and user_role == Role.SUB_MERCHANT.value:
        return True
    return False
async def get_role_by_email(email):
    result = await session.execute(select(Users).filter_by(**{'email':email}))
    list = result.fetchall()
    if len(list):
        item = list[0]
        user_role = item[0].as_dict['role']
        return user_role
    else:
        return None