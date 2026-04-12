from backend.db import DBConnector

class ItemRepo:

    def __init__(self, db: DBConnector):
        self.db = db

    def create_item(self, item_name, description, price):
        query = """
        INSERT INTO items (item_name, description, price)
        VALUES (?, ?, ?)
        """
        self.db.execute(query, (item_name, description, price))

    def get_item_by_id(self, item_id):
        query = """
        SELECT * FROM items
        WHERE id = ?
        """
        return self.db.fetchone(query, (item_id,))

    def get_all_items(self):
        query = "SELECT * FROM items"
        return self.db.fetchall(query)

    def update_item(self, item_id, item_name=None, description=None, price=None):
        fields = []
        values = []

        if item_name is not None:
            fields.append("item_name = ?")
            values.append(item_name)

        if description is not None:
            fields.append("description = ?")
            values.append(description)

        if price is not None:
            fields.append("price = ?")
            values.append(price)

        if not fields:
            return

        query = f"""
            UPDATE items
            SET {', '.join(fields)}
            WHERE id = ?
        """
        values.append(item_id)

        self.db.execute(query, values)

        