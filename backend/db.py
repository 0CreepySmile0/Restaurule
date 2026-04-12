import sqlite3
import threading


class DBConnector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_file="app.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBConnector, cls).__new__(cls)
                cls._instance._initialize(db_file)
        return cls._instance

    def _initialize(self, db_file):
        """Initialize SQLite connection (FastAPI safe)"""

        self.connection = sqlite3.connect(
            db_file,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row

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