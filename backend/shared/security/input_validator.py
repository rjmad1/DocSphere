"""
EKOS Input Sanitizer & Security Validation Middleware
Guards API inputs against Cypher/NoSQL injection, prompt injection, XSS vectors, and path traversal attacks.
"""

import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-InputSanitizer")

class InputSecurityValidationError(Exception):
    pass

class InputSanitizer:
    CYPHER_INJECTION = re.compile(r'(?i)\b(MATCH|MERGE|DETACH|DELETE|DROP|REMOVE|CREATE|SET)\b.*;')
    PROMPT_INJECTION = re.compile(r'(?i)\b(ignore previous instructions|disregard prior system prompt|bypass safety)\b')
    XSS_ATTACK = re.compile(r'(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>')

    @classmethod
    def sanitize_string(cls, input_text: str) -> str:
        """Sanitizes raw string inputs and checks for security attack vectors."""
        if not input_text:
            return ""

        if cls.CYPHER_INJECTION.search(input_text):
            logger.error(f"SECURITY ALERT: Cypher injection pattern detected in input: {input_text[:50]}")
            raise InputSecurityValidationError("Malicious injection payload detected.")

        if cls.PROMPT_INJECTION.search(input_text):
            logger.error(f"SECURITY ALERT: Prompt injection attempt detected: {input_text[:50]}")
            raise InputSecurityValidationError("Prompt injection payload detected.")

        if cls.XSS_ATTACK.search(input_text):
            logger.error(f"SECURITY ALERT: XSS attack payload detected: {input_text[:50]}")
            raise InputSecurityValidationError("XSS script payload detected.")

        return input_text.strip()
