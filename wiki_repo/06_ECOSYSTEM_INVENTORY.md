# Ecosystem Inventory

This document maps the complete ecosystem inventory of DocSphere EKOS directories, dependencies, databases, tools, and configurations.

---

## 1. Directory Inventory
* **`/backend`**: Python FastAPI gateway and service modules.
  * **`/backend/services`**: Subsystems layer.
    * **`/backend/services/agent_orchestrator`**: Multi-agent framework, prompt templating, and model gateways.
    * **`/backend/services/analytics`**: Feedback recording and usage logging.
    * **`/backend/services/channels`**: Adapters for Slack, Discord, and Telegram integrations.
    * **`/backend/services/chat_service`**: Chat Engine, conversation storage, and HTML/MD exports.
    * **`/backend/services/connectors`**: Integration connectors (SAP ALM, Confluence, Jira, Reddit, ServiceNow).
    * **`/backend/services/document_service`**: Canonical ASST schema parser, live diff builder.
    * **`/backend/services/ingestion`**: Web crawlers (recursive, sitemap), audio processors.
    * **`/backend/services/knowledge_engine`**: Graph engines, Neo4j production adapters, Qdrant vector adapters.
    * **`/backend/services/widget`**: Chat widget embed scripts generator.
    * **`/backend/services/workflow_engine`**: Celery queues, notification managers, policy engines.
  * **`/backend/shared`**: Cross-cutting concerns.
    * **`/backend/shared/security`**: Tenant isolation, CMEK encryption, API keys, WORM backup scripts.
    * **`/backend/shared/observability`**: Health status, metrics registry, tracing middlewares.
  * **`/backend/tests`**: Pytest suite containing 14 test execution modules.
* **`/frontend`**: React Next/Vite codebase.
  * **`/frontend/components`**: Rich interface elements (`document-editor`, `knowledge-explorer`, `impact-diff-viewer`, `search-bar`, `chat-widget`).
  * **`/frontend/src`**: React mount entries, App routers, governance pages.
  * **`/frontend/workspace`**: Side-by-side workspace dashboard.
* **`/playwright`**: Browser test suites.
  * Accessibility check, AI copilot, document-to-diff flow, latency budgets, security token tests, visual baseline comparison.
* **`/deployment`**: Platform configuration.
  * Kubernetes manifests, Helm values configuration, Terraform modules.
* **`/docs`**: ADR records (ADR-0001 through ADR-0010) and specifications.

---

## 2. Infrastructure & Databases
* **Neo4j Graph Database**: Runs on bolt port `7687` for requirements entity relationship tracking.
* **Qdrant Vector Database**: Runs on HTTP port `6333` for vector index storage and hybrid semantic RAG searches.
* **Redis Message Broker**: Message bus running on port `6379` for Celery background tasks.
* **Uvicorn Gateway**: Serves FastAPI on port `8000`.
* **Vite Dev Server**: Serves React on port `3000`.

---

## 3. Tooling & Automation
* **`pytest`**: Pytest testing runtime with `pytest-cov` and `pytest-asyncio`.
* **`playwright`**: E2E browser automation runtime.
* **`docker-compose`**: Automatically boots backend, frontend, Neo4j, Qdrant, Redis, and Celery worker.
