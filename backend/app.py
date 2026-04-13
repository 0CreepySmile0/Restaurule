from fastapi import FastAPI, Response, Request, HTTPException, Depends
from backend.db import DBConnector
from backend.repository.session_repo import SessionRepo
from backend.repository.user_repo import UserRepo
from backend.repository.item_repo import ItemRepo, Item
from backend.repository.order_repo import OrderRepo, Order
from backend.services.auth_service import AuthService
from backend.services.customer_service import CustomerService
from backend.requests import RegisterRequest, LoginRequest, OrderRequest

app = FastAPI()
db = DBConnector(mock_data=True)
session_repo = SessionRepo(db)
user_repo = UserRepo(db)
item_repo = ItemRepo(db)
order_repo = OrderRepo(db)
auth_service = AuthService(user_repo, session_repo)
customer_service = CustomerService(item_repo, order_repo)

@app.post("/register", tags=["Auth"], status_code=201)
def register(data: RegisterRequest):
    try:
        success = auth_service.register(
            data.username,
            data.password,
            data.first,
            data.last,
            data.role
        )
    except Exception as e:
        raise HTTPException(500, e)
    if not success:
        raise HTTPException(400, "Username existed or role not allowed")
    return {"message": f"Successfully register '{data.username}'"}

@app.post("/login", tags=["Auth"], status_code=201)
def login(response: Response, data: LoginRequest):
    try:
        session_id = auth_service.login(data.username, data.password)
    except Exception as e:
        raise HTTPException(500, e)

    if session_id is None:
        raise HTTPException(401, "Invalid login")

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=60 * 60 * 24,
        secure=False,  # True in production (HTTPS)
        samesite="lax"
    )

    return {"message": "Logged in"}

@app.post("/logout", tags=["Auth"], status_code=204)
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
            auth_service.logout()
        except Exception as e:
            raise HTTPException(500, e)

    response.delete_cookie("session_id")

    return {"message": "Logged out"}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401)

    session = auth_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(401)

    user = auth_service.get_user_by_id(session.user_id)
    return user

@app.get("/customer", tags=["Customer"], response_model=list[Item])
def view_menu():
    try:
        items = customer_service.view_menu()
    except Exception as e:
        raise HTTPException(500, e)
    return items

@app.get("/customer/orders/{table_number}", tags=["Customer"], response_model=list[Order])
def view_orders(table_number: int):
    try:
        orders = customer_service.view_orders(table_number)
    except Exception as e:
        raise HTTPException(500, e)
    return orders

@app.post("/customer/order-food/{table_number}", tags=["Customer"])
def order(table_number: int, data: OrderRequest):
    try:
        customer_service.order_item(table_number, data.item_id, data.note, data.quantity)
    except Exception as e:
        raise HTTPException(500, e)
    return {"message": "Order created"}

@app.patch("/customer/cancel-order/{order_id}", tags=["Customer"])
def customer_cancel(order_id: int):
    try:
        success = customer_service.cancel_order(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    
    if success is None:
        raise HTTPException(404, "Order not found")
    
    if not success:
        raise HTTPException(400, "Only able to cancel 'pending' status")
    
    return {"message": "Order cancelled"}

@app.get("/customer/checkout/{table_number}", tags=["Customer"])
def checkout_orders(table_number: int):
    try:
        total = customer_service.checkout(table_number)
    except Exception as e:
        raise HTTPException(500, e)
    
    return {"total": total}
    