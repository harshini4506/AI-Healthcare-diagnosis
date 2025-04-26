import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

class UserStorage:
    def __init__(self, storage_file='users.json'):
        self.storage_file = storage_file
        self.users = self._load_users()

    def _load_users(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_users(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def register_user(self, name, email, password):
        if email in self.users:
            return False, "Email already registered"
        
        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        self.users[email] = {
            'name': name,
            'password': hashed_password
        }
        self._save_users()
        return True, "Registration successful"

    def verify_user(self, email, password):
        if email not in self.users:
            return False, "User not found"
        
        if check_password_hash(self.users[email]['password'], password):
            return True, self.users[email]['name']
        return False, "Invalid password"

    def get_user(self, email):
        return self.users.get(email) 