from pydantic import BaseModel
from datetime import datetime
import typing
class Register(BaseModel):
    merchant_name: str
    email: str
    tax: typing.Optional[int] = None
    address: str
    role: str
    legal_representative: str

