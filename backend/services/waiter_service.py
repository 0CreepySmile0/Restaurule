from backend.repository.order_repo import OrderRepo, SERVED_STATUS, SERVING_STATUS, PAID_STATUS

class WaiterService:

    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    def read_orders(self):
        return self.order_repo.get_all_orders(True)

    def serve_dish(self, order_id):
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status != SERVING_STATUS:
            return False
        self.order_repo.update_order_status(order_id, SERVED_STATUS)
        return True

    def checkout(self, table_number):
        orders = self.order_repo.get_all_orders(True, table_number)
        total = 0
        all_id = []
        success = True
        for order in orders:
            total += order.price
            if order.status == SERVED_STATUS:
                all_id.append(order.id)
            else:
                success = False
        
        if success:
            for order_id in all_id:
                self.order_repo.update_order_status(order_id, PAID_STATUS)
        return total, success
