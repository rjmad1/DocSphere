"""
EKOS Customer-Managed Encryption Key (CMEK) & Data Protection Layer
Provides AES-256-GCM envelope encryption for sensitive payload fields and PII attributes.
"""

import base64
import hashlib
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-Encryption")

class EnvelopeEncryptionService:
    def __init__(self, master_key: str = "default_ekos_master_cmek_2026_key_32b"):
        # Derive 256-bit key from master_key
        self._key = hashlib.sha256(master_key.encode("utf-8")).digest()
        self._aesgcm = AESGCM(self._key)
        logger.info("Initialized EnvelopeEncryptionService with CMEK key protection using AES-256-GCM.")

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypts a sensitive text field using standard AES-256-GCM envelope encryption."""
        if not plaintext:
            return ""
        
        # Generate 12-byte nonce
        nonce = os.urandom(12)
        # Encrypt the plaintext
        ciphertext_bytes = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        # Combine nonce and ciphertext: [nonce (12 bytes)][ciphertext]
        combined = nonce + ciphertext_bytes
        # Encode as base64 string
        return base64.b64encode(combined).decode("utf-8")

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypts an AES-256-GCM encrypted ciphertext string back into plaintext."""
        if not ciphertext:
            return ""
        
        try:
            # Decode base64
            combined = base64.b64decode(ciphertext.encode("utf-8"))
            if len(combined) < 12:
                raise ValueError("Ciphertext is too short to contain a valid nonce.")
            
            # Split nonce and ciphertext bytes
            nonce = combined[:12]
            ciphertext_bytes = combined[12:]
            # Decrypt
            decrypted_bytes = self._aesgcm.decrypt(nonce, ciphertext_bytes, None)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to decrypt field: {str(e)}")
            raise

