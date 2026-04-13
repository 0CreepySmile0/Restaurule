from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    username: str
    password: str
    first: str
    last: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    item_id: int
    note: Optional[str] = None
    quantity: Optional[int] = 1