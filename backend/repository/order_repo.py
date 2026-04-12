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

    def get_all_orders(self, is_active: bool=True, table_number=None):
        fields = []
        values = []
        if is_active:
            fields.append("status != ? AND status != ?")
            values.append("paid")
            values.append("cancelled")
        if table_number is not None:
            fields.append("table_number = ?")
            values.append(table_number)

        query = "SELECT * FROM oders" + (f" WHERE {" AND ".join(fields)}" if fields else "")
        return self.db.fetchall(query, values)

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
