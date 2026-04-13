from fastapi import FastAPI, Response, Request, HTTPException, Depends
from backend.db import DBConnector
from backend.repository.session_repo import SessionRepo
from backend.repository.user_repo import UserRepo, User, CHEF, MANAGER
from backend.repository.item_repo import ItemRepo, Item
from backend.repository.order_repo import OrderRepo, Order, PENDING_STATUS, SERVED_STATUS, COOKING_STATUS
from backend.services.auth_service import AuthService
from backend.services.customer_service import CustomerService
from backend.services.chef_service import ChefService
from backend.requests import RegisterRequest, LoginRequest, OrderRequest

app = FastAPI()
db = DBConnector(mock_data=True)
session_repo = SessionRepo(db)
user_repo = UserRepo(db)
item_repo = ItemRepo(db)
order_repo = OrderRepo(db)
auth_service = AuthService(user_repo, session_repo)
customer_service = CustomerService(item_repo, order_repo)
chef_service = ChefService(order_repo)

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401)

    session = auth_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(401)

    user = auth_service.get_user_by_id(session.user_id)
    return user, session_id

@app.post("/register", status_code=201, tags=["Auth"])
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
    if data.role == MANAGER:
        raise HTTPException(403, "You cannot register as a manager")
    return {"message": f"Successfully register '{data.username}'"}

@app.post("/login", status_code=201, tags=["Auth"])
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

@app.post("/logout", status_code=204, tags=["Auth"])
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
            auth_service.logout(session_id)
        except Exception as e:
            raise HTTPException(500, e)

    response.delete_cookie("session_id")

    return {"message": "Logged out"}

@app.get("/customer", response_model=list[Item], tags=["Customer"])
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

@app.post("/customer/order/{table_number}", tags=["Customer"])
def order(table_number: int, data: OrderRequest):
    try:
        customer_service.order_item(table_number, data.item_id, data.note, data.quantity)
    except Exception as e:
        raise HTTPException(500, e)
    return {"message": "Order created"}

@app.patch("/customer/cancel/{order_id}", tags=["Customer"])
def customer_cancel(order_id: int):
    try:
        success = customer_service.cancel_order(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    
    if success is None:
        raise HTTPException(404, "Order not found")
    
    if not success:
        raise HTTPException(400, f"Only able to cancel '{PENDING_STATUS}' status")
    
    return {"message": "Order cancelled"}

@app.get("/customer/checkout/{table_number}", tags=["Customer"])
def checkout_orders(table_number: int):
    try:
        total, success = customer_service.checkout(table_number)
    except Exception as e:
        raise HTTPException(500, e)
    
    return {
        "total": total,
        "checkout_success": success,
        "message": "Successfully checkout" if success else f"Can checkout only when all orders are '{SERVED_STATUS}'"
    }

@app.get("/chef", response_model=list[Order], tags=["Chef"])
def view_orders(session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role != CHEF:
        raise HTTPException(403, "For chef only")
    try:
        orders = chef_service.view_orders()
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return orders

@app.patch("/chef/cook/{order_id}", tags=["Chef"])
def cook(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role != CHEF:
        raise HTTPException(403, "For chef only")
    try:
        success = chef_service.cook_dish(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    if success is None:
        raise HTTPException(404, "Order not found")
    if not success:
        raise HTTPException(400, f"Can only cook order with '{PENDING_STATUS}' status")
    auth_service.refresh_session(session_id)
    return {"message": "You start cooking order!"}

@app.patch("/chef/cancel/{order_id}", tags=["Chef"])
def chef_cancel(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role != CHEF:
        raise HTTPException(403, "For chef only")
    try:
        success = chef_service.cancel_order(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    if success is None:
        raise HTTPException(404, "Order not found")
    if not success:
        raise HTTPException(400, f"Only able to cancel '{PENDING_STATUS}' or '{COOKING_STATUS}' status")
    auth_service.refresh_session(session_id)
    return {"message": "Order cancelled"}

@app.patch("/chef/finish/{order_id}", tags=["Chef"])
def finish_order(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role != CHEF:
        raise HTTPException(403, "For chef only")
    try:
        success = chef_service.done_dish(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    if success is None:
        raise HTTPException(404, "Order not found")
    if not success:
        raise HTTPException(400, f"Can only mark order with '{COOKING_STATUS}' status as done")
    auth_service.refresh_session(session_id)
    return {"message": "You finish an order!"}
