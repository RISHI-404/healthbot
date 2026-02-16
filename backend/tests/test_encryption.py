"""
Tests for encryption service.
"""
import pytest
from app.services.encryption import EncryptionService


class TestEncryption:
    def setup_method(self):
        self.enc = EncryptionService()

    def test_encrypt_decrypt(self):
        plaintext = "Patient has diabetes type 2"
        encrypted = self.enc.encrypt(plaintext)
        assert encrypted != plaintext
        decrypted = self.enc.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_produces_different_ciphertext(self):
        """Each encryption should produce unique output (random nonce)."""
        plaintext = "Same data"
        c1 = self.enc.encrypt(plaintext)
        c2 = self.enc.encrypt(plaintext)
        assert c1 != c2

    def test_empty_string(self):
        encrypted = self.enc.encrypt("")
        decrypted = self.enc.decrypt(encrypted)
        assert decrypted == ""

    def test_unicode(self):
        plaintext = "Patient complained of nausée and douleur"
        encrypted = self.enc.encrypt(plaintext)
        decrypted = self.enc.decrypt(encrypted)
        assert decrypted == plaintext

    def test_long_text(self):
        plaintext = "Medical record: " * 500
        encrypted = self.enc.encrypt(plaintext)
        decrypted = self.enc.decrypt(encrypted)
        assert decrypted == plaintext
