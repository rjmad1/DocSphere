# Risk Register

This document tracks identified technical, security, and operational risks, their potential impacts, and implementation mitigation strategies.

---

## **Current Risk Registry**

### **Risk 1: Cross-Tenant Data Leakage**
* **Category**: Security
* **Likelihood**: High (without enforcement)
* **Impact**: Critical (unauthorized data exposure)
* **Mitigation**: Implemented `TenantIsolationMiddleware` in [`tenant_isolation.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/tenant_isolation.py). It extracts and validates the tenant context from the `X-EKOS-Tenant-ID` header on every request, raising HTTP 403 Forbidden for mismatched tenant resources.

### **Risk 2: Weak Field-Level Encryption**
* **Category**: Security / Compliance
* **Likelihood**: Medium
* **Impact**: Critical (PII disclosure)
* **Mitigation**: Removed the legacy XOR fake encryption and replaced it with authenticated **AES-256-GCM CMEK envelope encryption** in [`encryption.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/encryption.py) with base64 serialization.

### **Risk 3: Gateway CPU Starvation under Ingestion Load**
* **Category**: Reliability / Performance
* **Likelihood**: Medium
* **Impact**: High (API gateway timeout/downtime)
* **Mitigation**: Offloaded high-computation PDF chunk parsing and change impact simulations to a Redis-backed **Celery async task queue** in [`celery_app.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/services/workflow_engine/celery_app.py).

### **Risk 4: Rate-Limiting Bypass under High Traffic**
* **Category**: Reliability / DDoS
* **Likelihood**: Low
* **Impact**: Medium (API degradation)
* **Mitigation**: Configured in-memory rate-limit validation checking scopes and prefix usage in [`api_key_manager.py`](file:///c:/Users/rajaj/Projects/DocSphere/backend/shared/security/api_key_manager.py). Externalizing rate limits using Redis sliding window is recommended.
