import os
from fastapi import FastAPI, Response, Request, HTTPException, Depends
from dotenv import load_dotenv
from backend.db import DBConnector
from backend.repository.session_repo import SessionRepo
from backend.repository.user_repo import UserRepo, User, CHEF, MANAGER, WAITER, WAITRESS
from backend.repository.item_repo import ItemRepo, Item
from backend.repository.order_repo import OrderRepo, Order, PENDING_STATUS, SERVED_STATUS, COOKING_STATUS, SERVING_STATUS
from backend.services.auth_service import AuthService
from backend.services.customer_service import CustomerService
from backend.services.chef_service import ChefService
from backend.services.waiter_service import WaiterService
from backend.services.manager_service import ManagerService
from backend.requests import RegisterRequest, LoginRequest, OrderRequest, CreateMenuRequest, UpdateMenuRequest

AUTH = "auth"
CUSTOMER = "customer"

load_dotenv()
app = FastAPI(
    title="Restaurule API",
    summary="API endpoints provided for Restaurule app"
)
db = DBConnector(os.environ.get("DB_FILE", "app.db"), os.environ.get("MOCK_DATA", False))
session_repo = SessionRepo(db)
user_repo = UserRepo(db)
item_repo = ItemRepo(db)
order_repo = OrderRepo(db)
auth_service = AuthService(user_repo, session_repo)
customer_service = CustomerService(item_repo, order_repo)
chef_service = ChefService(order_repo)
waiter_service = WaiterService(order_repo)
manager_service = ManagerService(item_repo, user_repo)

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401)

    session = auth_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(401)

    user = auth_service.get_user_by_id(session.user_id)
    return user, session_id

@app.get("/", include_in_schema=False)
def hello():
    return {
        "message": "Welcome to Restaurule API!",
        "help": "To see more information, navigate to /docs"
    }

@app.post("/register", status_code=201, tags=[AUTH.capitalize()])
def register(data: RegisterRequest):
    try:
        success = auth_service.register(
            data.username,
            data.password,
            data.first,
            data.last,
            data.role.lower()
        )
    except Exception as e:
        raise HTTPException(500, e)
    if not success:
        raise HTTPException(400, "Username existed or role not allowed")
    if data.role.lower() == MANAGER:
        raise HTTPException(403, "You cannot register as a manager")
    return {"message": f"Successfully register '{data.username}'"}

@app.post("/login", status_code=201, tags=[AUTH.capitalize()])
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
        max_age=os.environ.get("MAX_AGE", 60 * 60 * 24), # 1 day by default
        secure=os.environ.get("HTTPS", False),  # True in production (HTTPS)
        samesite="lax"
    )

    return {"message": "Logged in"}

@app.post("/logout", tags=[AUTH.capitalize()])
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
            auth_service.logout(session_id)
        except Exception as e:
            raise HTTPException(500, e)

    response.delete_cookie("session_id")

    return {"message": "Logged out"}

@app.get("/customer", response_model=list[Item], tags=[CUSTOMER.capitalize()])
def view_menu():
    try:
        items = customer_service.view_menu()
    except Exception as e:
        raise HTTPException(500, e)
    return items

@app.get("/customer/orders/{table_number}", response_model=list[Order], tags=[CUSTOMER.capitalize()])
def customer_view_orders(table_number: int):
    try:
        orders = customer_service.view_orders(table_number)
    except Exception as e:
        raise HTTPException(500, e)
    return orders

@app.post("/customer/order/{table_number}", tags=[CUSTOMER.capitalize()])
def order(table_number: int, data: OrderRequest):
    try:
        customer_service.order_item(table_number, data.item_id, data.note, data.quantity)
    except Exception as e:
        raise HTTPException(500, e)
    return {"message": "Order created"}

@app.patch("/customer/cancel/{order_id}", tags=[CUSTOMER.capitalize()])
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

@app.get("/customer/checkout/{table_number}", tags=[CUSTOMER.capitalize()])
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

@app.get("/chef", response_model=list[Order], tags=[CHEF.capitalize()])
def chef_view_orders(session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role.lower() != CHEF:
        raise HTTPException(403, "For chef only")
    try:
        orders = chef_service.view_orders()
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return orders

@app.patch("/chef/cook/{order_id}", tags=[CHEF.capitalize()])
def cook(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role.lower() != CHEF:
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

@app.patch("/chef/cancel/{order_id}", tags=[CHEF.capitalize()])
def chef_cancel(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role.lower() != CHEF:
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

@app.patch("/chef/finish/{order_id}", tags=[CHEF.capitalize()])
def finish_order(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For chef only")
    if user.role.lower() != CHEF:
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

@app.get("/waiter", response_model=list[Order], tags=[WAITER.capitalize()])
def waiter_view_orders(session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For waiter only")
    if user.role.lower() not in [WAITRESS, WAITER]:
        raise HTTPException(403, "For waiter only")
    try:
        orders = waiter_service.read_orders()
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return orders

@app.patch("/waiter/serve/{order_id}", tags=[WAITER.capitalize()])
def serve_order(order_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For waiter only")
    if user.role.lower() not in [WAITRESS, WAITER]:
        raise HTTPException(403, "For waiter only")
    try:
        success = waiter_service.serve_dish(order_id)
    except Exception as e:
        raise HTTPException(500, e)
    if success is None:
        raise HTTPException(404, "Order not found")
    if not success:
        raise HTTPException(400, f"Can only serve order with '{SERVING_STATUS}' status")
    auth_service.refresh_session(session_id)
    return {"message": "You served the order!"}

@app.post("/manager/staff", status_code=201, tags=[MANAGER.capitalize()])
def create_staff_account(data: RegisterRequest, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        success = manager_service.create_staff_account(
            data.username,
            data.password,
            data.first,
            data.last,
            data.role.lower()
        )
    except Exception as e:
        raise HTTPException(500, e)
    if not success:
        raise HTTPException(400, "Username existed or role not allowed")
    auth_service.refresh_session(session_id)
    return {"message": f"Successfully register '{data.username}'"}

@app.get("/manager/staff", response_model=list[User], tags=[MANAGER.capitalize()])
def view_staffs(session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        staffs = manager_service.get_staff_accounts()
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return staffs

@app.patch("/manager/staff/{staff_id}/{role}", tags=[MANAGER.capitalize()])
def update_staff_role(staff_id: str, role: str, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    if user.id == staff_id:
        raise HTTPException(400, "Cannot change your role")
    try:
        success = manager_service.update_staff_role(staff_id, role.lower())
    except Exception as e:
        raise HTTPException(500, e)
    if not success:
        raise HTTPException(400, "Role not allowed")
    auth_service.refresh_session(session_id)
    return {"message": "Successfully update role"}

@app.delete("/manager/staff/{staff_id}", tags=[MANAGER.capitalize()])
def delete_staff_account(staff_id: str, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    if user.id == staff_id:
        raise HTTPException(400, "Cannot delete yourself")
    try:
        manager_service.delete_staff_account(staff_id)
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return {"message": "Staff account deleted"}

@app.post("/manager/menu", status_code=201, tags=[MANAGER.capitalize()])
def create_menu(data: CreateMenuRequest, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        manager_service.create_dish(data.item_name, data.description, data.price)
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return {"message": "Menu created"}

@app.get("/manager/menu", response_model=list[Item], tags=[MANAGER.capitalize()])
def view_all_menu(session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        menu = manager_service.get_all_dishes()
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return menu

@app.patch("/manager/menu/{item_id}", tags=[MANAGER.capitalize()])
def update_menu(item_id: int, data: UpdateMenuRequest, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        manager_service.update_dish_info(item_id, data.item_name, data.description, data.price)
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return {"message": "Successfully update menu"}

@app.delete("/manager/menu/{item_id}", tags=[MANAGER.capitalize()])
def delete_menu(item_id: int, session_data: tuple[User | None, str] = Depends(get_current_user)):
    user, session_id = session_data
    if user is None:
        raise HTTPException(403, "For manager only")
    if user.role.lower() != MANAGER:
        raise HTTPException(403, "For manager only")
    try:
        manager_service.delete_dish(item_id)
    except Exception as e:
        raise HTTPException(500, e)
    auth_service.refresh_session(session_id)
    return {"message": "Menu deleted"}
