# Tasks and Actions

This document tracks task states, completed items, active implementations, technical debt, and recommended future enhancements for DocSphere.

---

## 1. Completed Tasks (MVP v1.0)
* **AES-256-GCM Envelope Encryption CMEK**: Rewrote fake encryption to use standard authenticated `AESGCM` primitives.
* **Database Adapters Refactoring**: Replaced dummy dict DB stubs with the official `neo4j` and `qdrant-client` SDK drivers.
* **Redis Celery Work Queue Integration**: Configured Celery worker client and production background tasks.
* **React SPA Client Refactoring**: Created standard index entrypoints, path routers, interactive compliance views, and three-panel side-by-side workspace components.
* **FastAPI Endpoint Fixes**: Wrapped task dispatching endpoint in a `try...except ValueError` block to return HTTP 404 cleanly.
* **Automated Python Tests Expansion**: Created 101 tests achieving 97% overall backend coverage.
* **E2E Playwright Tests Verification**: Wrote and executed browser-level verifications covering WCAG accessibility, latency budgets, tenant isolation, and visual regression (100% pass on Chromium/Mobile Chrome).

---

## 2. In Progress Tasks
* **Documentation Synchronization**: Curating and updating the GitHub Wiki files with current repository details.

---

## 3. Technical Debt
* **Externalize Connection Parameters**: Configuration values for Redis, Neo4j, and Qdrant are currently configured as fallback defaults. They should be completely externalized to AWS Secrets Manager/Kubernetes Secrets in production.
* **Redis Connection Lifecycle**: The Celery client currently falls back to inline async tasks when connection fails. Add a retry strategy for Redis connection recovery.

---

## 4. Recommended Next Work
* **Phase 3 Implementations**:
  * **User Authentication & SSO**: Integrate OAuth2 / OpenID Connect (OIDC) and Okta/Active Directory.
  * **Multi-Region DB Scaling**: Configure active-active replication for Neo4j clusters.
  * **CI/CD Build Action**: Write a GitHub Actions YAML workflow to automatically execute pytest and playwright E2E suites on every pull request.
