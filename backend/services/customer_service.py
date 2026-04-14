from backend.repository.item_repo import ItemRepo
from backend.repository.order_repo import OrderRepo, CANCELLED_STATUS, PENDING_STATUS, SERVED_STATUS, PAID_STATUS

class CustomerService:

    def __init__(self, item_repo: ItemRepo, order_repo: OrderRepo):
        self.item_repo = item_repo
        self.order_repo = order_repo

    def order_item(self, table_number, item_id, note="", quantity=1):
        """Return None when item_id not found, True otherwise"""
        item = self.item_repo.get_item_by_id(item_id)
        if item is None:
            return None
        self.order_repo.create_order(table_number, item_id, note, quantity)
        return True

    def cancel_order(self, order_id):
        """Return None when order_id not found, False when invalid order status, True otherwise"""
        order = self.order_repo.get_order_by_id(order_id)
        if order is None:
            return None
        if order.status != PENDING_STATUS:
            return False
        self.order_repo.update_order_status(order_id, CANCELLED_STATUS)
        return True

    def view_orders(self, table_number):
        return self.order_repo.get_all_orders(True, table_number)

    def view_menu(self):
        return self.item_repo.get_all_items()

    def checkout(self, table_number):
        orders = self.order_repo.get_all_orders(True, table_number)
        total = 0
        all_id = []
        success = True
        for order in orders:
            item = self.item_repo.get_item_by_id(order.item_id)
            total += (item.price * order.quantity)
            if order.status == SERVED_STATUS:
                all_id.append(order.id)
            else:
                success = False
        
        if success:
            for order_id in all_id:
                self.order_repo.update_order_status(order_id, PAID_STATUS)
        return total, success
