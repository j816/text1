# project_root/secure_storage.py
import os
from cryptography.fernet import Fernet

# In a real application, you would store the key in a secure location (e.g., OS keychain)
# For demonstration, we generate or reuse a key stored locally.

KEY_FILE = os.path.join(os.path.expanduser("~"), ".my_app_key")

def _get_or_create_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

class SecureStorage:
    def __init__(self):
        self.key = _get_or_create_key()
        self.fernet = Fernet(self.key)
        self.api_key_file = os.path.join(os.path.expanduser("~"), ".my_app_api_key.enc")

    def store_api_key(self, api_key: str):
        encrypted = self.fernet.encrypt(api_key.encode("utf-8"))
        with open(self.api_key_file, "wb") as f:
            f.write(encrypted)

    def retrieve_api_key(self):
        if not os.path.exists(self.api_key_file):
            return ""
        with open(self.api_key_file, "rb") as f:
            encrypted = f.read()
        try:
            return self.fernet.decrypt(encrypted).decode("utf-8")
        except:
            return ""
