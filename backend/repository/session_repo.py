import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.db import DBConnector

SESSION_DURATION = timedelta(days=1)

class Session(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    expires_at: datetime


class SessionRepo:

    def __init__(self, db: DBConnector):
        self.db = db

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        expires = datetime.now() + SESSION_DURATION
        query = "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)"
        self.db.execute(query, (session_id, user_id, expires))
        return session_id

    def get_active_session_by_id(self, session_id):
        query = "SELECT * FROM sessions WHERE id = ? AND expires_at > CURRENT_TIMESTAMP"
        session = self.db.fetchone(query, (session_id,))
        if not session:
            return None
        return Session(**session)

    def get_all_sessions(self, is_active: bool=True):
        query = "SELECT * FROM sessions" + (" WHERE expires_at > CURRENT_TIMESTAMP" if is_active else "")
        sessions = self.db.fetchall(query)
        return [Session(**session) for session in sessions]

    def delete_session(self, session_id):
        query = "DELETE FROM sessions WHERE id = ?"
        self.db.execute(query, (session_id,))