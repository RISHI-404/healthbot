"""AES-256-GCM encryption service for sensitive data."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings


class EncryptionService:
    """Encrypt and decrypt sensitive data using AES-256-GCM."""

    def __init__(self):
        key_hex = settings.AES_ENCRYPTION_KEY
        # Ensure 32 bytes (256 bits)
        self.key = bytes.fromhex(key_hex.ljust(64, '0')[:64])

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        # Prepend nonce to ciphertext
        encrypted = nonce + ciphertext
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64-encoded ciphertext string."""
        raw = base64.b64decode(encrypted_data)
        nonce = raw[:12]
        ciphertext = raw[12:]
        aesgcm = AESGCM(self.key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')


encryption_service = EncryptionService()
