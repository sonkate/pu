import bcrypt
from src.connect import session
from sqlalchemy import select
from src.models.user import Users

import string
import secrets
# Generate a salt
salt = bcrypt.gensalt()

def generate_random_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Verify a password
async def check_password(email ,entered_password):
    result = await session.execute(select(Users).filter_by(**{'email':email}))
    list = result.fetchall()
    if len(list):
        for item in list:
            hased_password = item[0].as_dict['password']
        if bcrypt.checkpw(entered_password.encode(), hased_password):
            return True, True
        else:
            return False, True
    else:
        return False, False
def generate_hased_password(length):
    password = generate_random_password(length)
    # Generate a salt and hash the password
    return password, bcrypt.hashpw(password.encode(), salt)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), salt)

