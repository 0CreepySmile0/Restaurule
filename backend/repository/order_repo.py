from backend.db import DBConnector

PENDING_STATUS = "pending"
PAID_STATUS = "paid"
CANCELLED_STATUS = "cancelled"
COOKING_STATUS = "cooking"
SERVING_STATUS = "serving"
SERVED_STATUS = "served"


class OrderRepo:

    def __init__(self, db: DBConnector):
        self.db = db

    def create_order(self, table_number, item_id, note, quantity):
        query = """
        INSERT INTO orders (table_number, item_id, note, quantity, status)
        VALUES (?, ?, ?, ?)
        """
        self.db.execute(query, (table_number, item_id, note, quantity, PENDING_STATUS))

    def get_order_by_id(self, order_id):
        query = """
        SELECT * FROM orders
        WHERE id = ?
        """
        return self.db.fetchone(query, (order_id,))

    def get_all_orders(self, is_active: bool=True, table_number=None):
        fields = []
        values = []
        if is_active:
            fields.append("status != ? AND status != ?")
            values.append(PAID_STATUS)
            values.append(CANCELLED_STATUS)
        if table_number is not None:
            fields.append("table_number = ?")
            values.append(table_number)

        query = "SELECT * FROM oders" + (f" WHERE {" AND ".join(fields)}" if fields else "")
        return self.db.fetchall(query, values)

    def get_orders_by_status(self, status: list[str]):
        query = "SELECT * FROM orders" + (f" WHERE {" OR ".join(["status = ?" for _ in status])}" if status else "")
        return self.db.fetchall(query, status)

    def update_order_status(self, order_id, status):
        query = """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """
        self.db.execute(query, (status, order_id))

    def delete_order(self, order_id):
        query ="DELETE FROM orders WHERE id = ?"
        self.db.execute(query, (order_id,))
