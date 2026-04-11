import sqlite3
from sqlite3 import Error


class DBConnector:
    _instance = None

    def __new__(cls, db_file="database.db"):
        """Use singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DBConnector, cls).__new__(cls)
            cls._instance._initialize(db_file)
        return cls._instance

    def _initialize(self, db_file):
        """Initialize database connection"""
        try:
            self.connection = sqlite3.connect(db_file)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print("SQLite connection established")
        except Error as e:
            print(f"Database connection error: {e}")

    def execute(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.connection.commit()
            return self.cursor

        except Error as e:
            print(f"Execution error: {e}")
            self.connection.rollback()

    def fetchone(self, query, params=None):
        """Fetch single record"""
        cursor = self.execute(query, params)
        return cursor.fetchone() if cursor else None

    def fetchall(self, query, params=None):
        """Fetch multiple records"""
        cursor = self.execute(query, params)
        return cursor.fetchall() if cursor else []

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            DBConnector._instance = None
            print("SQLite connection closed")
