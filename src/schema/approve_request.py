from pydantic import BaseModel

class RequestEmail(BaseModel):
    email: str

