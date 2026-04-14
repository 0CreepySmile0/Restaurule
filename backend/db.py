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
        item_name TEXT NOT NULL,
		note TEXT,
		quantity INTEGER DEFAULT 1,
		status TEXT,
        price REAL NOT NULL,
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


"""
Mock passwords are:
manager: managerpass
chef: chefpass
waiter: waiterpass
"""
MOCK_DATA = [
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u1', 'manager', '$argon2id$v=19$m=65536,t=3,p=4$VYoxRmhNiXGutda6txZCqA$cRc6ieqkQ+w7RvFbk8h7hNVEwAUBl8aLr7OfjfOIm68', 'Alice', 'M', 'manager')",
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u2', 'chef', '$argon2id$v=19$m=65536,t=3,p=4$836vtbbWei+ltDYGYGxN6Q$p+a9FdGK5Azij6LYpdvUgTpy4FL6jORpapR5pphOj2Y', 'Bob', 'C', 'chef')",
    "INSERT OR IGNORE INTO users (id, username, password, first, last, role) VALUES ('u3', 'waiter', '$argon2id$v=19$m=65536,t=3,p=4$bO3dW0upVQrBGCPEGANACA$6NzWw0trXc5JCXkYfmmD2IdJFmg6we1JKH++kNEt2wI', 'Carol', 'W', 'waiter')",

    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (1, 'กะเพราหมูสับ', 'เมนูบ้านๆที่คนไทยรัก', 40)",
    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (2, 'กะเพราไก่สับ', 'อีกหนึ่งเมนูบ้านๆ แต่เป็นเนื้อไก่แทน', 40)",
    "INSERT OR IGNORE INTO items (id, item_name, price) VALUES (3, 'ข้าวเปล่า', 10)",
    "INSERT OR IGNORE INTO items (id, item_name, description, price) VALUES (4, 'ข้าวไข่เจียว', 'มีไข่ 3 ฟอง', 25)"
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