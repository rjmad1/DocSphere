"""
EKOS Input Sanitizer & Security Validation Middleware
Guards API inputs against Cypher/NoSQL injection, prompt injection, XSS vectors,
path traversal attacks, and SQL injection.
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
    PATH_TRAVERSAL = re.compile(r'(\.\./|\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|%2e%2e%5c)', re.IGNORECASE)
    SQL_INJECTION = re.compile(
        r"(?i)\b(UNION\s+SELECT|INSERT\s+INTO|UPDATE\s+SET|DELETE\s+FROM|DROP\s+TABLE|"
        r"ALTER\s+TABLE|EXEC\s*\(|EXECUTE\s*\(|xp_cmdshell|INFORMATION_SCHEMA)\b"
    )

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

        if cls.PATH_TRAVERSAL.search(input_text):
            logger.error(f"SECURITY ALERT: Path traversal attempt detected: {input_text[:50]}")
            raise InputSecurityValidationError("Path traversal payload detected.")

        if cls.SQL_INJECTION.search(input_text):
            logger.error(f"SECURITY ALERT: SQL injection pattern detected: {input_text[:50]}")
            raise InputSecurityValidationError("SQL injection payload detected.")

        return input_text.strip()
