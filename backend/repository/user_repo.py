import uuid
from backend.db import DBConnector
from passlib.context import CryptContext

class UserRepo:

    def __init__(self, db: DBConnector):
        self.db = db
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

    def create_user(self, username, password, first, last, role):
        hashed = self.pwd_context.hash(password)
        user_id = str(uuid.uuid4())
        query = """
        INSERT INTO users (id, username, password, first, last, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (user_id, username, hashed, first, last, role))

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.fetchone(query, (user_id,))

    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        return self.db.fetchone(query, (username,))

    def is_username_exist(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        return bool(self.db.fetchone(query, (username,)))

    def verify_password(self, username, password):
        user = self.get_user_by_username(username)
        if not user:
            return False
        return self.pwd_context.verify(password, user["password"])

    def update_user(
            self,
            user_id,
            username=None,
            first=None,
            last=None,
            role=None
    ):
        fields = []
        values = []
    
        if username is not None:
            fields.append("username = ?")
            values.append(username)
        
        if first is not None:
            fields.append("first = ?")
            values.append(first)

        if last is not None:
            fields.append("last = ?")
            values.append(last)

        if role is not None:
            fields.append("role = ?")
            values.append(role)

        if not fields:
            return

        query = f"""
            UPDATE users
            SET {', '.join(fields)}
            WHERE id = ?
        """
        values.append(user_id)

        self.db.execute(query, values)

    def change_password(self, username, old_password, new_password):
        if not self.verify_password(username, old_password):
            return

        query = f"""
            UPDATE users
            SET password = ?
            WHERE username = ?
        """
        self.db.execute(query, (self.pwd_context.hash(new_password), username))
