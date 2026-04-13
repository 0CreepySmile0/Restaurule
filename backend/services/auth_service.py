from backend.repository.user_repo import UserRepo, AVAILABLE_ROLE
from backend.repository.session_repo import SessionRepo


class AuthService:

    def __init__(self, user_repo: UserRepo, session_repo: SessionRepo):
        self.user_repo = user_repo
        self.session_repo = session_repo

    def register(self, username, password, first, last, role) -> bool:
        if role not in AVAILABLE_ROLE:
            return False
        if self.user_repo.is_username_exist(username):
            return False
        self.user_repo.create_user(username, password, first, last, role)
        return True

    def login(self, username, password):
        user = self.user_repo.verify_password(username, password)
        if user is None:
            return None
        return self.session_repo.create_session(user["id"])

    def get_session_by_id(self, session_id):
        return self.session_repo.get_active_session_by_id(session_id)

    def refresh_session(self, session_id):
        self.session_repo.refresh_session(session_id)

    def logout(self, session_id):
        self.session_repo.delete_session(session_id)

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        return self.user_repo.get_user_by_username(username)

    def change_password(self, username, old_password, new_password) -> bool:
        return self.user_repo.change_password(username, old_password, new_password)

    def update_profile(self, user_id, username, first, last) -> bool:
        if self.user_repo.is_username_exist(username):
            return False
        self.user_repo.update_user(user_id, username, first, last)
        return True