import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from pathlib import Path

class EncryptionService:
    def __init__(self, master_key=None):
        if master_key is None:
            master_key = os.getenv('ENCRYPTION_KEY')
            if not master_key:
                raise ValueError("ENCRYPTION_KEY not found in environment variables")

        self.master_key = master_key.encode() if isinstance(master_key, str) else master_key
        self.cipher = self._create_cipher()

    def _create_cipher(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mindfulscreen_salt_v1',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)

    def encrypt_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            data = f.read()

        encrypted_data = self.cipher.encrypt(data)

        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)

        os.remove(file_path)

        return str(encrypted_path)

    def decrypt_file(self, encrypted_path):
        encrypted_path = Path(encrypted_path)
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")

        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)

        return decrypted_data

    def encrypt_data(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()

    def decrypt_data(self, encrypted_data):
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()

    def secure_delete_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.exists():
            return

        file_size = file_path.stat().st_size
        with open(file_path, 'wb') as f:
            f.write(os.urandom(file_size))

        os.remove(file_path)
