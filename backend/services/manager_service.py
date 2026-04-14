from backend.repository.item_repo import ItemRepo
from backend.repository.user_repo import UserRepo
from backend.services.auth_service import AVAILABLE_ROLE

class ManagerService:

    def __init__(self, item_repo: ItemRepo, user_repo: UserRepo):
        self.item_repo = item_repo
        self.user_repo = user_repo

    def create_staff_account(self, username, password, first, last, role):
        """Same as register in auth_service"""
        if role not in AVAILABLE_ROLE:
            return False
        if self.user_repo.is_username_exist(username):
            return None
        self.user_repo.create_user(username, password, first, last, role)
        return True

    def get_staff_accounts(self):
        return self.user_repo.get_users()

    def update_staff_role(self, user_id, role):
        """Return None when user_id not found, False when role not allowed, True otherwise"""
        if role not in AVAILABLE_ROLE:
            return False
        user = self.user_repo.get_user_by_id(user_id)
        if user is None:
            return None
        self.user_repo.update_user(user_id, role=role)
        return True

    def delete_staff_account(self, user_id):
        """Return None when user_id not found, True otherwise"""
        user = self.user_repo.get_user_by_id(user_id)
        if user is None:
            return None
        self.user_repo.delete_user(user_id)
        return True

    def create_dish(self, item_name, description, price):
        """Adding dish to menu"""
        self.item_repo.create_item(item_name, description, price)

    def get_all_dishes(self):
        return self.item_repo.get_all_items()

    def update_dish_info(self, item_id, item_name=None, description=None, price=None):
        """
        Change dish information
        Return None when item_id not found, True otherwise
        """
        item = self.item_repo.get_item_by_id(item_id)
        if item is None:
            return None
        self.item_repo.update_item(item_id, item_name, description, price)
        return True

    def delete_dish(self, item_id):
        """Return None when item_id not found, True otherwise"""
        item = self.item_repo.get_item_by_id(item_id)
        if item is None:
            return None
        self.item_repo.delete_item(item_id)
        return True
