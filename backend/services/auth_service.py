from backend.repository.user_repo import UserRepo, AVAILABLE_ROLE
from backend.repository.session_repo import SessionRepo


class AuthService:

    def __init__(self, user_repo: UserRepo, session_repo: SessionRepo):
        self.user_repo = user_repo
        self.session_repo = session_repo

    def register(self, username, password, first, last, role) -> bool:
        """Return None when username exist, False when role not allowed, True otherwise"""
        if role not in AVAILABLE_ROLE:
            return False
        if self.user_repo.is_username_exist(username):
            return None
        self.user_repo.create_user(username, password, first, last, role)
        return True

    def login(self, username, password):
        user = self.user_repo.verify_password(username, password)
        if user is None:
            return None, None
        return self.session_repo.create_session(user.id), user.role

    def get_session_by_id(self, session_id, is_active=True):
        return self.session_repo.get_session_by_id(session_id, is_active)

    def refresh_session(self, session_id):
        """Return None when session_id not found otherwise True"""
        session = self.get_session_by_id(session_id)
        if session is None:
            return None
        self.session_repo.refresh_session(session_id)
        return True

    def logout(self, session_id):
        """Return None when session_id not found otherwise True"""
        session = self.get_session_by_id(session_id, False)
        if session is None:
            return None
        self.session_repo.delete_session(session_id)
        return True

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        return self.user_repo.get_user_by_username(username)

    def change_password(self, username, old_password, new_password) -> bool:
        return self.user_repo.change_password(username, old_password, new_password)

    def update_profile(self, user_id, username, first, last):
        """Return None when user_id not found, False when username exist, True otherwise"""
        user = self.get_user_by_id(user_id)
        if user is None:
            return None
        if self.user_repo.is_username_exist(username):
            return False
        self.user_repo.update_user(user_id, username, first, last)
        return True