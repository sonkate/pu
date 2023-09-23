from pydantic import BaseModel, constr

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
class ModifyPassword(BaseModel):
    email: str
    role: str
    new_password: str
    confirm_password: str
