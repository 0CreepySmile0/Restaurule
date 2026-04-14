from backend.repository.order_repo import OrderRepo, SERVED_STATUS, SERVING_STATUS, COOKING_STATUS

class WaiterService:

    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    def read_orders(self):
        return self.order_repo.get_orders_by_status([COOKING_STATUS, SERVING_STATUS])

    def serve_dish(self, order_id):
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status != SERVING_STATUS:
            return False
        self.order_repo.update_order_status(order_id, SERVED_STATUS)
        return True
