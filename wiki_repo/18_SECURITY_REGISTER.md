# Security Register

This document registers the active security architecture, cryptographic mechanisms, tenant boundaries, and access controls implemented in DocSphere.

---

## 1. Cryptographic Controls (AES-256-GCM CMEK)
* **Design**: DocSphere enforces field-level authenticated envelope encryption for sensitive properties (such as requirement text content or credentials).
* **Implementation** ([`encryption.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/encryption.py)):
  * Utilizes `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
  * For each field, a unique random 12-byte initialization vector (IV) is generated.
  * The ciphertext is serialized as `Base64(IV + Ciphertext)`.
  * Decrypting checks the minimum byte length (> 12 bytes) and raises a `ValueError` on validation failure.

---

## 2. Logical Tenant Isolation Boundaries
* **Design**: Prevent cross-tenant data leaks in multi-tenant environments.
* **Implementation** ([`tenant_isolation.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/tenant_isolation.py)):
  * `TenantIsolationMiddleware` intercepts every incoming HTTP request.
  * Resolves the `X-EKOS-Tenant-ID` header.
  * Injects the tenant context into FastAPI endpoint handlers.
  * Filters all Neo4j query parameters and Qdrant similarity searches with `filter_tenant` clauses.

---

## 3. API Key Authorization Scopes
* **Design**: Grant narrow authorization access tokens.
* **Implementation** ([`api_key_manager.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/api_key_manager.py)):
  * Keys are generated as UUID4 strings, and stored as SHA256 hashes inside database adapters.
  * Scopes (`CHAT`, `SEARCH`, `AGENTS`, `ADMIN`, `WIDGET`) are validated at the gateway controller.
  * Rate-limiting checks restrict usage to 60 queries/minute per key by default.

---

## 4. Immutable Compliance Logs (WORM Backups)
* **Design**: Protect change histories from alterations.
* **Implementation** ([`worm_backup.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/worm_backup.py)):
  * `WebWormBackupService` saves snapshots of change diffs to directory files flagged with read-only/immutable file systems.
  * Every write transaction triggers an asynchronous write-once-read-many copy to secure file vaults.
