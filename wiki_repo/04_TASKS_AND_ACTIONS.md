# Tasks and Actions

This document tracks task states, completed items, active implementations, technical debt, and recommended future enhancements for DocSphere.

---

## 1. Completed Tasks (v1.1 Security Hardening)
* **Zero-Trust JWT & API Key Authentication**: Refactored gateway controllers to enforce signature authentication using HMAC-SHA256 bearer tokens and API keys.
* **Input Injection Validation**: Configured strict regex validation blocking XSS tags, SQL Injection statements, and Path Traversal patterns (`../`).
* **Docker Compose Secrets Isolation**: Configured environment-derived variables (`NEO4J_PASSWORD`, `REDIS_PASSWORD`, `POSTGRES_PASSWORD`, `EKOS_MASTER_KEY`, `EKOS_JWT_SECRET`) instead of hardcoded default values.
* **Service healthcheck Orchestration**: Added check conditions to Docker container services to sequence container boots correctly.
* **Pipeline Release Scanning**: Wrote bandit SAST scanning and pip-audit check tasks inside the GitHub actions workflow.
* **Comprehensive Test Catalog Expansion**: Authoring **188 unit, integration, boundary, concurrency, and security verification tests** to ensure absolute coverage parity.
* **URL Log Leak Mitigation**: Modified `get_shared_conversation` API endpoints to support bearer tokens inside Authorization headers rather than query strings.

---

## 2. In Progress Tasks
* **Continuous Integration Actions Integration**: Deploying workflows and verifying containerization runs in remote environments.

---

## 3. Technical Debt
* **Auto-refresh keys**: Add rotation support for master CMEK keys.

---

## 4. Recommended Next Work
* **Phase 3 Implementations**:
  * **Unified Single Sign-On (SSO)**: Hook JWT decoders into OAuth2 providers (Keycloak/Okta).
  * **Grafana Dashboards**: Create dashboards mapping Prometheus metric counters.
