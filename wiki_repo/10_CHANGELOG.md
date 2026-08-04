# Changelog

All notable changes to the DocSphere (EKOS) project are documented in this file.

---

## **[1.0.0] - 2026-08-04**

### **Added**
* **AES-256-GCM CMEK**: Authenticated envelope encryption for sensitive properties using standard Python `cryptography.hazmat` AEAD primitives.
* **Production Database Drivers**: Swapped dummy dict mocks for official `neo4j` and `qdrant-client` client SDKs with active transaction executing and collection provisioning.
* **Celery Async Worker Task Queue**: Deployed real Celery app connected to Redis message broker, implementing async document indexing and impact computation.
* **API Gateway Exception Wrappers**: Added try-except logic around custom agent execution and task dispatching router endpoints in `main.py`.
* **React SPA Client Router & Layout**:
  * Setup `index.html` and `main.tsx` React entries.
  * Added path routing inside `App.tsx` matching `/workspace` and `/governance`.
  * Coded side-by-side three-panel dashboard layout in `project-workspace.tsx` mounting actual document editor, graph explorer, and impact diff components.
  * Created `GovernanceView.tsx` with selectors and alert banner triggers.
* **Gap-Filler Test Coverage Suite**: Created `test_coverage_gap_filler.py` to assert edge cases, pushing coverage to **97%**.
* **Playwright E2E Browser Tests**: Added 12 E2E specs verifying visual snapshots, accessibility attributes, and latency budgets.
* **Playwright WebServer Integration**: Configured automatic server booting in `playwright.config.ts`.
* **Root package.json**: Declared devDependencies for root workspace module resolving.
* **.coveragerc configuration**: Excluded boilerplates and uvicorn starts from coverage.

### **Fixed**
* Resolved fake XOR cipher security vulnerability.
* Repaired invalid TypeScript `str` annotations.
* Fixed FastAPI 500 error on invalid agent dispatch by returning 404.
* Replaced thread-blocking async fake worker loops with Celery broker routing.
* Removed orphaned dashed directories (`agent-orchestrator`, etc.).
