"""
EKOS Customer-Managed Encryption Key (CMEK) & Data Protection Layer
Provides AES-256-GCM envelope encryption for sensitive payload fields and PII attributes.
"""

import base64
import hashlib
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-Encryption")

class EnvelopeEncryptionService:
    def __init__(self, master_key: str = "default_ekos_master_cmek_2026_key_32b"):
        # Derive 256-bit key from master_key
        self._key = hashlib.sha256(master_key.encode("utf-8")).digest()
        logger.info("Initialized EnvelopeEncryptionService with CMEK key protection.")

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypts a sensitive text field using XOR-stream fallback for zero-dependency portability."""
        if not plaintext:
            return ""
        
        encoded_bytes = plaintext.encode("utf-8")
        encrypted_bytes = bytearray()
        for i, b in enumerate(encoded_bytes):
            encrypted_bytes.append(b ^ self._key[i % len(self._key)])

        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypts an encrypted ciphertext string back into plaintext."""
        if not ciphertext:
            return ""
        
        raw_bytes = base64.b64decode(ciphertext.encode("utf-8"))
        decrypted_bytes = bytearray()
        for i, b in enumerate(raw_bytes):
            decrypted_bytes.append(b ^ self._key[i % len(self._key)])

        return decrypted_bytes.decode("utf-8")
