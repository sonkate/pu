from pydantic import BaseModel
import typing
class ModifyAccount(BaseModel):
    user_email: str
    role: str
    tax: typing.Optional[int] = None
    merchant_name: str
    address: str
    legal_representative: str
    email: str
    is_active: bool
class EmailRoleModifyAccount:
    email: str
    role: str

