from pydantic import BaseModel

class ResetPassword(BaseModel):
    email: str
class VerifyResetPassword(BaseModel):
    token: str
class ChangeResetPassword(BaseModel):
    new_password: str
    confirm_password: str

