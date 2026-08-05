# Security Register

This document registers the active security architecture, cryptographic mechanisms, tenant boundaries, and access controls implemented in DocSphere.

---

## 1. Cryptographic Controls (AES-256-GCM CMEK)
* **Design**: DocSphere enforces field-level authenticated envelope encryption for sensitive properties (such as requirement text content or credentials).
* **Implementation** ([`encryption.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/encryption.py)):
  * Utilizes `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
  * Derives key from `EKOS_MASTER_KEY` environment variable. Refuses to boot if default or empty master key is detected in production.
  * For each field, a unique random 12-byte initialization vector (IV) is generated.
  * The ciphertext is serialized as `Base64(IV + Ciphertext)`.
  * Decrypting checks the minimum byte length (> 12 bytes) and raises a `ValueError` on validation failure.

---

## 2. Logical Tenant Isolation Boundaries
* **Design**: Prevent cross-tenant data leaks in multi-tenant environments.
* **Implementation** ([`tenant_isolation.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/tenant_isolation.py)):
  * `TenantIsolationMiddleware` intercepts every incoming HTTP request.
  * Injects the tenant context (resolved via authenticated API keys or JWT bearer tokens) into FastAPI endpoint handlers.
  * Filters all database queries with tenant parameters.

---

## 3. Zero-Trust Authentication & RBAC Checks
* **JWT Bearer Verification**: Enforces signature checks using HMAC-SHA256 of `EKOS_JWT_SECRET` (or `EKOS_MASTER_KEY`). Rejects expired tokens automatically.
* **API Key validation**: Verifies prefix keys against SHA256 hashes inside database adapters and checks rate limits (max 60 requests/minute per key).
* **Role-Based Authorization (RBAC)**: Validates required permissions on sensitive endpoints:
  * `Admin`: Create/list keys, export analytics, revoke share links.
  * `Steward`: Register tools, read analytics summaries.
  * `Author`: Execute queries, submit feedback, export threads.

---

## 4. Input Sanitization & Threat Injection Filters
* **Regex Injections Checker** ([`input_validator.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/input_validator.py)):
  * **XSS attacks**: Rejects content containing scripting patterns (`<script>`, `javascript:`).
  * **SQL Injections**: Detects and blocks query injection commands (`UNION SELECT`, `INSERT INTO`, `DROP TABLE`).
  * **Path Traversals**: Rejects string paths containing navigation markers (`../` or `..\`).

---

## 5. Deployment Secrets Isolation
* **Docker Compose Configurations** ([`docker-compose.yml`](file:///c:/Users/rajaj/Projects/DocSphere/docker-compose.yml)):
  * Real secrets (`NEO4J_PASSWORD`, `REDIS_PASSWORD`, `POSTGRES_PASSWORD`, `EKOS_MASTER_KEY`, `EKOS_JWT_SECRET`) are completely isolated and loaded from `.env` environment variables.
  * Local databases are added to `.gitignore` to prevent accidental checkin of credentials.
  * Proxy logs leakage is mitigated by passing shared link access tokens in Bearer headers rather than URL query parameters.
