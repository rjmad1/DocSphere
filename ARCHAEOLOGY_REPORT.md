# DocSphere — Software Archaeology Report
**Job ID:** `SDF-DOCSPHERE-001`  
**Date:** 2026-08-15  
**Confidence Threshold:** All findings are HIGH unless otherwise marked.

---

## System Purpose
DocSphere is an AI-native Enterprise Knowledge Operating System (EKOS) that transforms enterprise documentation into a living knowledge ecosystem using:
- AI agents (requirement analyzers, impact estimators, test planners)
- Knowledge graphs (Neo4j)
- Hybrid RAG (Qdrant + Neo4j)
- Workflow automation (Celery + Redis)
- Standards-based governance (IEEE 29148, ISO 25010, etc.)

---

## Major Components

| Component | Location | Description | Confidence |
|---|---|---|---|
| **FastAPI Backend** | `backend/main.py` | REST API with 150+ endpoints across KG, retrieval, agents, documents, policies, health, metrics. | HIGH |
| **AI Agents** | `ai/agents/` | `requirement_analyzer.py`, `impact_analyzer.py`, `test_planner.py`, `spec_writer.py` | HIGH |
| **LLM Gateway** | `backend/services/agent_orchestrator/llm_gateway.py` | Task-based multi-model router (OpenAI, Anthropic, Google). | HIGH |
| **Knowledge Graph** | `backend/services/knowledge_engine/graph_service.py` | Neo4j adapter with entity/relationship CRUD. | HIGH |
| **Vector Store** | `backend/services/knowledge_engine/qdrant_adapter.py` | Qdrant client for hybrid retrieval. | HIGH |
| **Orchestration** | `backend/services/agent_orchestrator/agent_framework.py` | Task scheduling, retry, dependency resolution. | HIGH |
| **Document Generation** | `backend/services/document_service/` | AST engine, impact analyzer, export service. | HIGH |
| **Frontend** | `frontend/` | React/TypeScript SPA with Playwright E2E tests. | HIGH |
| **Deployment** | `deployment/` | Docker Compose, Kubernetes, Terraform. | HIGH |

---

## Technology Stack

| Layer | Technology | Version | Confidence |
|---|---|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn | 0.100+, 0.22+ | HIGH |
| **Database** | PostgreSQL 15, Neo4j 5.12, Qdrant v1.6, Redis 7 | Alpine-based | HIGH |
| **AI Models** | OpenAI GPT-4o, Claude 3.5 Sonnet, Google Gemini | Configurable | HIGH |
| **Task Queue** | Celery 5.3 | + Redis 5 | HIGH |
| **Frontend** | React 18, TypeScript 5, Vite | — | MEDIUM |
| **Testing** | pytest 7.3, Playwright 1.40 | — | HIGH |
| **Observability** | Prometheus, OpenTelemetry | — | HIGH |

---

## Runtime Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                              FastAPI Server                         │
│  /kg/*  /retrieval/*  /agents/*  /documents/*  /policies/* /health/*│
└──────────────────────┬──────────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Neo4j   │  │  Qdrant  │  │  Redis   │
  │ (Graph)  │  │  (Vector)│  │ (Queue)  │
  └──────────┘  └──────────┘  └──────────┘
         │             │             │
         └─────────────┴─────────────┘
                       │
              ┌────────▼────────┐
              │  Postgres 15    │
              │ (Relational)    │
              └─────────────────┘
```

---

## Dependency Graph

```
FastAPI Backend
├── knowledge_engine
│   ├── graph_service.py (Neo4j)
│   ├── qdrant_adapter.py (Qdrant)
│   ├── retrieval_service.py (Hybrid RAG)
│   └── multi_region_cluster.py
├── agent_orchestrator
│   ├── llm_gateway.py (Multi-model)
│   ├── agent_framework.py (Celery)
│   └── agent_builder.py
├── document_service
│   ├── asst_engine.py
│   ├── generation_orchestrator.py
│   ├── impact_analyzer.py
│   └── websocket_manager.py
├── workflow_engine
│   ├── policy_engine.py
│   └── audit_service.py
├── analytics
│   └── analytics_service.py
├── channels
│   └── channel_integrations.py (Discord, Slack)
├── chat_service
│   ├── chat_service.py
│   └── prompt_manager.py
├── connectors
│   ├── confluence_connector.py
│   ├── jira_connector.py
│   ├── reddit_connector.py
│   ├── sap_alm_connector.py
│   └── servicenow_connector.py
├── ingestion
│   ├── document_parser.py
│   ├── audio_processor.py
│   ├── web_crawler.py
│   └── github_commit_listener.py
└── shared
    ├── models (SQLAlchemy)
    ├── middleware
    ├── observability (Health, Metrics, Tracing)
    └── security (Tenant isolation, API keys)
```

---

## Agent Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      AgentOrchestrator (Celery)                │
│  - Task queue management                                       │
│  - Retry policies, exponential backoff                         │
│  - Dependency resolution graph                                 │
└────────────────────────────┬───────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Requirement     │  │ Impact          │  │ Test Planner    │
│ Analyzer Agent  │  │ Analyzer Agent  │  │ Agent           │
│ (IEEE 29148)    │  │ (上下游影響評估) │  │ (Test cases)    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                  ┌───────────▼───────────┐
                  │  Spec Writer Agent    │
                  │ (Generates FRD/SDD)   │
                  └───────────────────────┘
```

**Note:** Agent implementations exist as Python files, but integration with LLM gateway appears partial (hardcoded return values observed in `requirement_analyzer.py`).

---

## Data Flows

1. **Requirement Capture Flow:**
   ```
   User Input (text) → RequirementAnalyzerAgent → ExtractedRequirement (Pydantic)
   → Knowledge Graph (Neo4j) → Retrieval Service (Qdrant) → Cache (Redis)
   ```

2. **Impact Analysis Flow:**
   ```
   Change Request → ImpactAnalyzerAgent → Graph Traversal (Neo4j)
   → Affected Requirements Identified → Report Generation
   ```

3. **Document Generation Flow:**
   ```
   GenerationRequest → DocumentGenerationOrchestrator → AST Engine
   → Canonical Ontology Compliance Check → Export (Markdown/Word/Excel)
   ```

4. **Policy Enforcement Flow:**
   ```
   Request → TenantSecurityContext → PolicyEngine → Approval Chain
   → Execution (or rejected with reason)
   ```

---

## API Surface

**Total endpoints:** ~150+

**Key endpoint categories:**

| Category | Count | Examples |
|---|---|---|
| **Knowledge Graph** | 35+ | `POST /kg/entity`, `GET /kg/entity/{id}`, `POST /kg/relationship` |
| **Retrieval** | 15+ | `POST /retrieval/hybrid`, `POST /retrieval/semantic`, `GET /retrieval/related` |
| **Agents** | 20+ | `POST /agents/task`, `GET /agents/task/{id}`, `GET /agents/status` |
| **Documents** | 20+ | `POST /documents/generate`, `GET /documents/{id}`, `POST /documents/export` |
| **Policies** | 10+ | `POST /policies/evaluate`, `POST /policies/approval/request` |
| **Health/Metrics** | 10+ | `GET /health`, `GET /health/deep`, `GET /metrics`, `GET /traces` |
| **Connectors** | 10+ | `POST /connectors/confluence/import`, `POST /connectors/jira/import` |
| **Ingestion** | 10+ | `POST /ingestion/parse`, `POST /ingestion/audio`, `POST /ingestion/web` |
| **Analytics** | 5+ | `GET /analytics/requirements`, `GET /analytics/traceability` |

---

## External Integrations

| Integration | Status | Evidence |
|---|---|---|
| **Confluence** | Implemented | `backend/services/connectors/confluence_connector.py` |
| **Jira** | Implemented | `backend/services/connectors/jira_connector.py` |
| **Reddit** | Implemented | `backend/services/connectors/reddit_connector.py` |
| **SAP ALM** | Implemented | `backend/services/connectors/sap_alm_connector.py` |
| **ServiceNow** | Implemented | `backend/services/connectors/servicenow_connector.py` |
| **Discord** | Implemented | `backend/services/channels/channel_integrations.py` (webhook handler) |
| **GitHub** | Implemented | `backend/services/ingestion/github_commit_listener.py` |

---

## Persistence

| Database | Purpose | Size | Notes |
|---|---|---|---|
| **PostgreSQL** | Relational data (users, tenants, audit logs) | Unknown | SQLAlchemy ORM, `backend/shared/models/db_models.py` |
| **Neo4j** | Knowledge Graph (40+ entity types) | Unknown | Bolt protocol, Cypher queries |
| **Qdrant** | Vector embeddings (RAG) | Unknown | Collection: `ekos_knowledge` |
| **Redis** | Caching, session, Celery broker | Unknown | Password protected |
| **Filesystem** | Audit snapshots (WORM), artifacts | Unknown | S3 bucket reference in `.env.example` |

---

## Configuration

| Config | Location | Notes |
|---|---|---|
| **Environment** | `.env` | Required: `EKOS_MASTER_KEY`, `EKOS_JWT_SECRET`, `POSTGRES_*`, `NEO4J_*`, `REDIS_PASSWORD` |
| **Docker Compose** | `docker-compose.yml` | 5 services: neo4j, qdrant, redis, postgres, api |
| **Kubernetes** | `deployment/k8s/` | StatefulSets, Ingress, ConfigMaps |
| **Terraform** | `deployment/terraform/` | Cloud infrastructure provisioning |

---

## CI/CD

| Tool | Status | Evidence |
|---|---|---|
| **GitHub Actions** | Implemented | `.github/workflows/ci.yml` |
| **pytest** | Implemented | `backend/tests/` (30+ test files) |
| **Playwright** | Implemented | `playwright/` (10+ E2E tests) |
| **bandit** | Implemented | Security scanning (`.coveragerc`) |
| **ruff** | Implemented | Linting (`requirements.txt`) |

**Found gap:** No integration test coverage for LLM gateway (`llm_gateway.py` lacks tests).

---

## Testing

| Test Type | Count | Coverage |
|---|---|---|
| **Unit Tests** | ~30 | Python modules |
| **Integration Tests** | ~10 | End-to-end workflows |
| **Playwright E2E** | ~10 | Frontend + API flows |
| **LLM Gateway Tests** | 0 | **MISSING** — high risk |

---

## Observability

| Layer | Tool | Status |
|---|---|---|
| **Health** | DeepHealthCheckService | ✅ Implemented |
| **Metrics** | Prometheus metrics | ✅ Implemented (`/metrics`) |
| **Tracing** | OpenTelemetry | ✅ Implemented (`/traces`) |
| **Logging** | Python logging | ✅ Implemented |
| **Alerting** | — | ❌ Not observed |

---

## Security

| Layer | Mechanism | Status |
|---|---|---|
| **Authentication** | JWT + API Key | ✅ Implemented |
| **Authorization** | Tenant isolation | ✅ Implemented |
| **Encryption** | AES-256 envelope | ✅ Implemented (via `EKOS_MASTER_KEY`) |
| **Secrets** | Environment variables | ⚠️ `.env.example` provided, but no vault integration |
| **Security Scanning** | bandit (CI) | ✅ Implemented |

---

## Known Risks

| Risk | Severity | Evidence |
|---|---|---|
| **LLM Gateway untested** | HIGH | No tests for multi-model routing, fallback logic |
| **Connection pool missing** | MEDIUM | Neo4j connection reused without pooling |
| **Hardcoded agent output** | MEDIUM | `requirement_analyzer.py` returns fixed example |
| **No versioning strategy** | MEDIUM | No semver for entity types or API |
| **No migration tooling** | MEDIUM | Schema changes not tracked |
| **No alerting** | LOW | Metrics exist but no alert thresholds |

---

## Unknowns

| Unknown | Investigation Method | Notes |
|---|---|---|---|
| **Actual test coverage %** | Run `pytest --cov` | Not yet executed |
| **LLM token usage patterns** | Trace logs | Not yet analyzed |
| **Frontend runtime errors** | Browser console | Not yet captured |
| **Performance benchmarks** | Load tests | Not yet executed |

---

## Architecture Contradictions

| Document Claim | Implementation Evidence | Discrepancy |
|---|---|---|
| **"Complete IEEE 29148 compliance"** | `requirement_analyzer.py` exists but returns hardcoded examples | ⚠️ Partial implementation |
| **"Production-ready LLM gateway"** | No tests for model routing, fallback, or cost accounting | ⚠️ Functional but unverified |
| **"Multi-region knowledge graph"** | `multi_region_cluster.py` exists but no deployment config | ⚠️ Code present, untested |

---

## Documentation Contradictions

| Document | Claim | Evidence |
|---|---|---|
| `README.md` | "AI-native Enterprise Knowledge Operating System" | ✅ Matches implementation |
| `DocSphere_ImplementationGuide_Architecture.md` | "40+ entity types" | ✅ Confirmed in `canonical-ontology.yaml` |
| `DocSphere_ImplementationGuide_Architecture.md` | "End-to-end transformation lifecycle" | ⚠️ Partial (upstream/downstream flow exists, but not fully connected) |

---

## Technical Debt

| Debt Item | Priority | Effort | Impact |
|---|---|---|---|
| **LLM Gateway tests** | HIGH | 4h | High reliability risk |
| **Connection pooling** | MEDIUM | 2h | Medium scalability risk |
| **Agent LLM integration** | HIGH | 8h | Core functionality |
| **Alerting rules** | LOW | 2h | Operational risk |

---

**End of Archaeology Report**
