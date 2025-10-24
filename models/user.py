from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password_hash, is_admin=False):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)
