import sqlite3
import threading


CREATE_TABLES = [
	"""
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT NOT NULL UNIQUE,
		password TEXT NOT NULL,
		first TEXT,
		last TEXT,
		role TEXT
	)
	""",

	"""
	CREATE TABLE IF NOT EXISTS items (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		item_name TEXT NOT NULL,
		description TEXT,
		price REAL NOT NULL
	)
	""",

	"""
	CREATE TABLE IF NOT EXISTS orders (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		table_number INTEGER NOT NULL,
		item_id INTEGER NOT NULL,
		note TEXT,
		quantity INTEGER DEFAULT 1,
		status TEXT,
		FOREIGN KEY(item_id) REFERENCES items(id)
	)
	""",

	"""
	CREATE TABLE IF NOT EXISTS sessions (
		id TEXT PRIMARY KEY,
		user_id TEXT NOT NULL,
		expires_at TIMESTAMP NOT NULL,
		FOREIGN KEY(user_id) REFERENCES users(id)
	)
	""",
]


MOCK_DATA = [
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u1', 'manager', 'managerpass', 'Alice', 'M', 'manager')",
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u2', 'chef', 'chefpass', 'Bob', 'C', 'chef')",
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u3', 'waiter', 'waiterpass', 'Carol', 'W', 'waiter')",
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u4', 'customer', 'custpass', 'Dave', 'Q', 'customer')",

    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (1, 'Margherita Pizza', 'Classic pizza with tomato and mozzarella', 8.99)",
    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (2, 'Caesar Salad', 'Romaine lettuce, parmesan, croutons', 5.99)",
    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (3, 'Espresso', 'Strong coffee shot', 2.50)",

    "INSERT OR IGNORE INTO orders (id, table_number, item_id, note, quantity, status) VALUES (1, 12, 1, 'No olives', 1, 'pending')",
    "INSERT OR IGNORE INTO orders (id, table_number, item_id, note, quantity, status) VALUES (2, 5, 3, '', 2, 'served')",

    "INSERT OR IGNORE INTO sessions (id, user_id, expires_at) VALUES ('s1', 'u4', datetime('now', '+1 day'))",
]



class DBConnector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_file="app.db", mock_data=False):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBConnector, cls).__new__(cls)
                cls._instance._initialize(db_file, mock_data)
        return cls._instance

    def _initialize(self, db_file, mock_data):
        """Initialize SQLite connection (FastAPI safe)"""

        self.connection = sqlite3.connect(
            db_file,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self._create_table(mock_data=mock_data)

    def _create_table(self, statements=CREATE_TABLES, mock_data=False):
        for statement in statements:
            self.execute(statement)

        if mock_data:
            for statement in MOCK_DATA:
                try:
                    self.execute(statement)
                except Exception:
                    pass

    def execute(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE"""
        cursor = self.connection.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            return cursor

        except Exception as e:
            self.connection.rollback()
            raise e

    def fetchone(self, query, params=None):
        """Fetch single record"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row

    def fetchall(self, query, params=None):
        """Fetch multiple records"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            DBConnector._instance = None