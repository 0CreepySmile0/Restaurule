from backend.db import DBConnector

class OrderRepo:

    def __init__(self, db: DBConnector):
        self.db = db

    def create_order(self, table_number, item_id, note, quantity):
        query = """
        INSERT INTO orders (table_number, item_id, note, quantity, status)
        VALUES (?, ?, ?, ?)
        """
        self.db.execute(query, (table_number, item_id, note, quantity, "pending"))

    def get_order_by_id(self, order_id):
        query = """
        SELECT * FROM orders
        WHERE id = ?
        """
        return self.db.fetchone(query, (order_id,))

    def get_all_orders(self):
        query = "SELECT * FROM oders"
        return self.db.fetchall(query)

    def get_all_active_orders(self):
        query = """
        SELECT * FROM orders
        WHERE status != ?
        """
        return self.db.fetchall(query, ("paid",))

    def get_all_orders_by_table_number(self, table_number):
        query = """
        SELECT * FROM orders
        WHERE table_number = ?
        AND status != ?
        """
        return self.db.fetchall(query, (table_number, "paid"))

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
