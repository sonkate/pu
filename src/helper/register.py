from src.connect import session
from src.models.user import Users
from sqlalchemy import select
from src.lib.roles import Role
async def is_exists_email(email):
    result = await session.execute(select(Users).filter_by(**{'email' : email}))
    data = result.fetchall()
    return len(data)

async def is_exists_tax(tax):
    result = await session.execute(select(Users).filter_by(**{'tax' : tax}))
    data = result.fetchall()
    return len(data)

async def is_exists_user_maker():
    result = await session.execute(select(Users).filter_by(**{'role' : Role.MAKER.value}))
    data = result.fetchall()
    return len(data)