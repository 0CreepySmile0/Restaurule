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

class CreateMenuRequest(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: float

class UpdateMenuRequest(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None