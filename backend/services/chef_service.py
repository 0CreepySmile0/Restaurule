from backend.repository.order_repo import OrderRepo, CANCELLED_STATUS, PENDING_STATUS, SERVING_STATUS, COOKING_STATUS

class ChefService:

    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    def cook_dish(self, order_id):
        """Return None when order_id not found, False when invalid order status, True otherwise"""
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status != PENDING_STATUS:
            return False
        self.order_repo.update_order_status(order_id, COOKING_STATUS)
        return True

    def cancel_order(self, order_id):
        """
        In case of insufficient ingredient to cook for that order
        Return None when order_id not found, False when invalid order status, True otherwise
        """
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status not in [PENDING_STATUS, COOKING_STATUS]:
            return False
        self.order_repo.update_order_status(order_id, CANCELLED_STATUS)
        return True

    def view_orders(self):
        return self.order_repo.get_orders_by_status([PENDING_STATUS, COOKING_STATUS])

    def done_dish(self, order_id):
        """Return None when order_id not found, False when invalid order status, True otherwise"""
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status != COOKING_STATUS:
            return False
        self.order_repo.update_order_status(order_id, SERVING_STATUS)
        return True
