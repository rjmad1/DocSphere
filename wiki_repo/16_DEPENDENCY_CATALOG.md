# Dependency Catalog

This document registers all third-party libraries, frameworks, package dependencies, and tools required to build, test, and deploy the DocSphere workspace.

---

## 1. Python Backend Dependencies (`requirements.txt`)

### Core Framework:
* **`fastapi`** (^0.110.0) — Gateway endpoint management.
* **`uvicorn`** (^0.28.0) — ASGI server process.
* **`pydantic`** (^2.6.0) — Data validation and serialization interfaces.

### Cryptography & Security:
* **`cryptography`** (^42.0.0) — AES-256-GCM CMEK authenticated encryption primitives.

### Database Drivers:
* **`neo4j`** (^5.18.0) — Official driver for Neo4j transactional graph database.
* **`qdrant-client`** (^1.8.0) — Official client SDK for vector similarity indices.

### Background Queue:
* **`celery`** (^5.3.0) — Task broker worker processor.
* **`redis`** (^5.0.0) — Celery message bus broker dependency.

### Utilities & Templates:
* **`jinja2`** (^3.1.0) — Prompt template rendering engine.

### Testing & Observability:
* **`pytest`** (^8.1.0) — Unit and integration test runner.
* **`pytest-cov`** (^4.1.0) — Statement and branch coverage analysis.
* **`pytest-asyncio`** (^0.23.0) — Async test wrapper.
* **`anyio`** (^4.3.0) — Multi-threaded asynchronous loop driver.
* **`httpx`** (^0.27.0) — HTTP client runner for FastAPI test executions.

---

## 2. React Frontend Dependencies (`package.json`)

### Core Libraries:
* **`react`** (^18.2.0) — UI component state runtime.
* **`react-dom`** (^18.2.0) — DOM rendering binding.

### Development & Build:
* **`typescript`** (^5.2.2) — Type-safe JavaScript compiler.
* **`vite`** (^5.0.0) — Asset builder and dev server.

### E2E Testing:
* **`@playwright/test`** (^1.40.0) — Browser E2E automation runner.
