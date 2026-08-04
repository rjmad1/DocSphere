# 12. Security & Compliance Architecture

## Zero-Trust RBAC Multi-Tenant Isolation (`backend/shared/security/tenant_isolation.py`)
- Automatically validates `tenant_id` context on all queries and endpoints.
- Enforces role permission hierarchy (`Author` → `Steward` → `Approver` → `Admin`).

## CMEK Envelope Encryption (`backend/shared/security/encryption.py`)
- Field-level AES-256 encryption protecting sensitive properties using Customer-Managed Encryption Keys.

## Cryptographic Audit Logging (`backend/shared/security/audit_logger.py` & `worm_backup.py`)
- Append-only SHA-256 hash chaining creating tamper-evident audit logs.
- WORM snapshot manifests exported to S3 vaults.

## Injection Defense (`backend/shared/security/input_validator.py`)
- Regex sanitizer blocking Cypher query injection, NoSQL injection, prompt injection, XSS attacks, and path traversal.
