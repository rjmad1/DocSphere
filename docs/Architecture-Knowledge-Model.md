# 🏛️ Canonical Architecture Knowledge Model: EKOS / DocSphere Platform
**Document Name**: `Architecture-Knowledge-Model.md`  
**Version**: 1.0.0  
**Specification Standard**: Single-Source-of-Truth Architecture Knowledge Model (AKM) v1.0  
**Target Repository**: `https://github.com/rjmad1/DocSphere`  
**Determinism Standard**: 100% Machine-Readable & Diagram Extractable  

---

## 1. Project Metadata

| Field | Value |
| :--- | :--- |
| **System Name** | DocSphere / EKOS (Enterprise Knowledge Operating System) |
| **System ID** | `SYS-EKOS-001` |
| **Version** | `1.0.0-GA` |
| **Repository** | `https://github.com/rjmad1/DocSphere` |
| **Languages** | Python 3.11+, TypeScript, SQL, Cypher, HCL (Terraform), YAML, Markdown |
| **Frameworks** | FastAPI, Pydantic v2, SQLAlchemy, Celery, React/Next.js, TipTap, Cytoscape.js |
| **Runtime Environments** | CPython 3.11+, Node.js v20+, Docker Engine, Kubernetes v1.28+ |
| **Build System** | `pip`, `npm`, `docker-compose`, GitHub Actions (`.github/workflows/ci.yml`) |
| **Primary Owners** | Enterprise Architecture Review Board & DevSecOps Platform Engineering |
| **Primary Business Domain** | Living Software Documentation, Architectural Knowledge Graphs, Impact Analysis |
| **Deployment Targets** | AWS EKS (Kubernetes via Helm), Docker Compose (Local Dev/Staging) |

---

## 2. Executive Summary

### 2.1 System Purpose
DocSphere / EKOS is an **Enterprise Knowledge Operating System**. It eliminates technical debt and documentation drift by replacing static, decaying Markdown wikis with a self-governing **Abstract Semantic Syntax Tree (ASST)** middle-layer and hybrid knowledge graph.

### 2.2 Core Capabilities
1. **ASST Line-Indexed AST Parsing**: Bi-directional Markdown ↔ AST serialization preserving line numbers.
2. **Hybrid Graph + Vector RAG**: Neo4j Cypher dependency traversals combined with Qdrant vector similarity.
3. **Deterministic Impact Analysis**: Blast radius calculations across requirements (`REQ-`), capabilities (`CAP-`), specs (`FRS-`), and operational controls (`CHG-`, `INC-`).
4. **Progressive Autonomy Governance**: AI agents generate change diff proposals, requiring human Steward/Approver signoff with SLA tracking and webhooks.
5. **Zero-Trust Security & Compliance**: Multi-tenant RBAC isolation, AES-256 CMEK envelope encryption, and SHA-256 WORM cryptographic audit logs.

### 2.3 Architectural Style
Modular Layered Architecture with Event-Driven Background Indexing (Celery + Redis) and Multi-Model LLM Gateway Routing.

---

## 3. Architecture Style

| Attribute | Specification |
| :--- | :--- |
| **Primary Architectural Pattern** | Modular Monolith / Microservices-Ready Clean Architecture |
| **Data Processing Pattern** | Hybrid Vector RAG + Graph Reasoning Engine |
| **Execution Pattern** | Asynchronous Event-Driven (Celery Task Queues + Redis) |
| **Rationale** | Decouples document ingestion and graph sync from synchronous REST API endpoints, guaranteeing sub-100ms UI interaction latency. |

---

## 4. External Actors

| Actor ID | Name | Description | Responsibilities | Entry Points | Auth Protocol | RBAC Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ACT-01` | Enterprise Architect | System Administrator & Spec Owner | Governs canonical ontology, approves breaking ADR changes | Three-Panel Web Workspace | OAuth2 / OIDC JWT | `Admin`, `Lead Architect` |
| `ACT-02` | Software Engineer | Contributor / Developer | Edits Markdown specs, visualizes impact diffs | Workspace UI / Git Webhook | Bearer Token / Git SSH | `Author` |
| `ACT-03` | Compliance Auditor | Third-Party Inspector | Verifies SHA-256 audit logs & CMEK keys | Audit Log Endpoint | TLS Client Cert | `Auditor` |
| `ACT-04` | External System (CI/CD) | Automated Bot | Triggers git diff ingestion webhooks | Webhook Ingestion API | HMAC SHA-256 Header | `System` |

---

## 5. External Systems

| System ID | Name | Protocol | Auth Type | Data Exchanged | Frequency | Failure Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EXT-01` | Jira Cloud | REST / Webhook | OAuth2 / API Token | User Stories (`REQ-`), Tests (`TC-`) | Polling / Webhook | Exponential Backoff Retry |
| `EXT-02` | Confluence | REST / Webhook | OAuth2 / API Token | Wiki Pages, Specification ASTs | Batch Sync | Retry Queue |
| `EXT-03` | SAP Cloud ALM | OData / REST | OAuth2 Client Credentials | Process Models (`PROC-`), Specs | Periodic Cron | Alert Notification |
| `EXT-04` | ServiceNow ITSM | REST API | Basic Auth / OAuth2 | Change Requests (`CHG-`), Incidents | Webhook Sync | Dead Letter Queue |
| `EXT-05` | OpenAI API | HTTPS REST | Bearer Key | Reasoning Prompts & Embeddings | On-Demand | Provider Fallback Gateway |
| `EXT-06` | PagerDuty | HTTPS Webhook | API Key | Critical Governance SLA Breaches | Event Triggered | Fallback to Slack |

---

## 6. System Context

```
[ External Systems: Jira, Confluence, SAP ALM, ServiceNow, PagerDuty ]
                                ▲
                                │ REST / Webhooks
                                ▼
         ┌──────────────────────────────────────────────┐
         │          SYSTEM BOUNDARY: SYS-EKOS-001       │
         │  DocSphere / Enterprise Knowledge OS (EKOS)  │
         └──────────────────────────────────────────────┘
                                ▲
                                │ HTTPS / WebSockets
                                ▼
               [ Human Actors: Developer, Architect, Auditor ]
```

---

## 7. Containers

| Container ID | Name | Technology | Purpose & Responsibilities | Owned Data | Scaling |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CNT-API` | FastAPI Gateway | Python 3.11, Uvicorn | REST routing, Pydantic validation, Auth Middleware | Transient API State | HPA 3–10 Replicas |
| `CNT-DOC` | Document & ASST Service | Python 3.11, ASST Engine | Line-indexed text parsing, AST serialization, diff analyzer | ASST JSON Trees | HPA 2–8 Replicas |
| `CNT-GRAPH`| Knowledge Graph Service | Python 3.11, Neo4j Driver | Cypher node/edge upserts, blast radius traversals | Neo4j Graph Topology | Multi-Region Read-Replicas |
| `CNT-AI` | LLM Gateway Service | Python 3.11, Async HTTP | Multi-model routing (OpenAI, Anthropic, Gemini) | Prompt Cost Metrics | HPA 2–6 Replicas |
| `CNT-WORK` | Celery Background Worker| Python 3.11, Celery | Async background ingestion, vector indexing | Task Queue State | Auto-scaling Workers |
| `CNT-UI` | React Workspace UI | React, Next.js, Cytoscape | Three-panel workspace rendering, live graph sync | Local Component State | Static CDN / Edge |

---

## 8. Components

| Component ID | Container | Component Name | Responsibilities | Interfaces | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CMP-01` | `CNT-DOC` | `ASSTEngine` | Markdown ↔ DocumentAST transformation | Python API | `Pydantic` |
| `CMP-02` | `CNT-GRAPH` | `Neo4jProductionAdapter` | Cypher query execution & node indexing | Cypher / Bolt | `neo4j` Python driver |
| `CMP-03` | `CNT-GRAPH` | `QdrantProductionAdapter` | Vector embedding insertion & cosine search | gRPC / HTTP | `qdrant-client` |
| `CMP-04` | `CNT-GRAPH` | `HybridRetrievalService` | Unified vector + graph search execution | Python API | `CMP-02`, `CMP-03` |
| `CMP-05` | `CNT-GRAPH` | `KnowledgeGraphReasoningEngine` | Conflict detection (`CONFLICTS_WITH`) & gap finder | Python API | `CMP-02` |
| `CMP-06` | `CNT-AI` | `MultiModelLLMGateway` | Task-based provider routing | Python API | OpenAI, Anthropic, Gemini |
| `CMP-07` | `CNT-API` | `TenantSecurityContext` | Multi-tenant RBAC context validation | FastAPI Middleware | JWT Tokens |
| `CMP-08` | `CNT-API` | `EnvelopeEncryptionService` | Field-level AES-256 CMEK encryption | Python API | Cryptography Primitive |
| `CMP-09` | `CNT-API` | `CryptographicAuditLogger` | Append-only SHA-256 hash chaining | Python API | `PostgreSQL`, `WORMBackup` |
| `CMP-10` | `CNT-DOC` | `WebSocketGraphSyncManager` | Real-time WebSocket Cytoscape canvas sync | Async WebSocket | `Redis Pub/Sub` |

---

## 9. APIs

| Endpoint ID | Method | URI Path | Description | Input Schema | Output Schema | Auth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `API-01` | `GET` | `/health` | Liveness health probe | None | `{"status": "healthy"}` | Public |
| `API-02` | `GET` | `/health/deep` | Deep database diagnostics probe | None | Diagnostic JSON | Bearer |
| `API-03` | `GET` | `/metrics` | Prometheus telemetry metrics | None | OpenMetrics Plaintext | Public |
| `API-04` | `POST` | `/api/v1/graph/entity` | Upserts entity into Neo4j graph | `EntityPayload` | `{"status": "upserted"}` | Bearer (RBAC) |
| `API-05` | `POST` | `/api/v1/retrieval/search`| Hybrid vector/graph retrieval search | `SearchQuery` | `SearchResultList` | Bearer (Tenant) |
| `API-06` | `POST` | `/api/v1/policy/evaluate` | Evaluates change governance SLA | `PolicyEvaluationRequest` | `PolicyEvaluationResponse` | Bearer (Steward) |

---

## 10. Events

| Event ID | Event Name | Producer | Consumers | Payload Schema | DLQ Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `EVT-01` | `DocumentIngested` | `CNT-DOC` | `CNT-GRAPH`, `CNT-WORK` | `document_id`, `tenant_id`, `asst_json` | `dlq_doc_ingest` |
| `EVT-02` | `EntityGraphUpserted` | `CNT-GRAPH` | `CNT-UI` (WebSocket) | `entity_id`, `label`, `tenant_id` | `dlq_graph_sync` |
| `EVT-03` | `SLAWindowBreached` | `CNT-API` | `NotificationService` | `artifact_id`, `sla_hours`, `severity` | `dlq_sla_alert` |

---

## 11. Datastores

| Datastore ID | Name | Technology | Primary Entities | Backup Policy | Encryption |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DB-01` | Relational DB | PostgreSQL 15 | `DocumentModel`, `AuditLogModel`, `EntityMetadataModel` | Nightly Snapshot + WAL | AES-256 at Rest |
| `DB-02` | Knowledge Graph | Neo4j Enterprise | Nodes (`REQ-`, `CAP-`), Relationships (`IMPLEMENTS`) | Multi-Region Replicas | TLS 1.3 + Disk CMEK |
| `DB-03` | Vector Store | Qdrant Vector Engine | Document Chunk Embeddings (1536-dim) | Snapshot Backup | TLS 1.3 |
| `DB-04` | Cache & Queue | Redis 7 | Session Keys, Celery Task Queues, WebSocket Pub/Sub | In-Memory / AOF | TLS 1.3 |

---

## 12. Domain Model

```
[ BusinessCapability (CAP-) ] ◄───[ IMPLEMENTS ]─── [ BusinessRequirement (REQ-) ]
                                                            │
                                                     [ VALIDATED_BY ]
                                                            ▼
[ FunctionalSpecification (FRS-) ] ◄───[ SATISFIES ]─── [ TestCase (TC-) ]
```

---

## 13. State Machines

### Document / Entity State Machine (`SM-DOC-01`)
- **States**: `DRAFT` → `IN_REVIEW` → `APPROVED` → `PUBLISHED` (or `REJECTED`).
- **Transitions**:
  - `DRAFT` to `IN_REVIEW`: Triggered by Author edit submission.
  - `IN_REVIEW` to `APPROVED`: Triggered by Steward/Approver signoff.
  - `IN_REVIEW` to `REJECTED`: Triggered by Approver rejection.

---

## 14. Data Flow

```
[ Author Edit ] ──(HTTPS)──► [ FastAPI Gateway ] ──► [ ASST Engine ]
                                                          │
                                     ┌────────────────────┴────────────────────┐
                                     ▼                                         ▼
                           [ Neo4j Cypher Graph ]                    [ Qdrant Vector Engine ]
                                     │                                         │
                                     └────────────────────┬────────────────────┘
                                                          ▼
                                            [ SHA-256 Audit Log & S3 WORM ]
```

---

## 15. Sequence Flows

### End-to-End Living Docs Impact Diff Approval Sequence (`SEQ-01`)
1. `Author` edits specification in `TipTap Workspace UI`.
2. `Workspace UI` sends edit payload to `FastAPI Gateway`.
3. `FastAPI Gateway` invokes `ASSTEngine` to convert Markdown to `DocumentAST`.
4. `ASSTEngine` notifies `LivingDocsImpactAnalyzer` to calculate blast radius.
5. `LivingDocsImpactAnalyzer` queries `Neo4jProductionAdapter` for downstream entities.
6. `LivingDocsImpactAnalyzer` returns side-by-side diff recommendations to `Workspace UI`.
7. `Steward` approves change; `CryptographicAuditLogger` writes SHA-256 hash log to `PostgreSQL` and exports manifest to `S3 WORM Vault`.

---

## 16. Security Model

- **Authentication**: OAuth2 / OIDC JWT tokens validated at `TenantSecurityContext` middleware.
- **Authorization**: Zero-Trust RBAC hierarchy (`Author` < `Steward` < `Approver` < `Admin`).
- **Field-Level Encryption**: AES-256 CMEK envelope encryption (`EnvelopeEncryptionService`).
- **Injection Sanitization**: `InputSanitizer` blocking Cypher injection, prompt injection, XSS, and path traversal.

---

## 17. Deployment Architecture

- **Primary Cloud Provider**: AWS EKS (Elastic Kubernetes Service).
- **Orchestration**: Kubernetes Helm Charts (`deployment/helm/`).
- **Infrastructure as Code**: Terraform AWS EKS IaC (`deployment/terraform/infrastructure.tf`).
- **Autoscaling**: HPA configured for 3 to 10 replicas at 75% CPU load.

---

## 18. Observability

- **Metrics**: Prometheus client exposing `/metrics` (request rates, latency histograms).
- **Tracing**: OpenTelemetry distributed tracing propagating `trace_id` headers.
- **Health**: Liveness probe `/health` & Readiness deep diagnostic probe `/health/deep`.

---

## 19. Runtime Dependencies

- `fastapi`, `uvicorn`, `pydantic` (v2), `sqlalchemy`, `neo4j`, `qdrant-client`, `celery`, `redis`, `httpx`, `prometheus-client`.

---

## 20. Infrastructure Dependencies

- AWS EKS, AWS S3 (WORM Vault), Managed PostgreSQL, Neo4j Enterprise Cluster, Qdrant Vector Cluster, Redis Enterprise.

---

## 21. Configuration Matrix

| Variable Name | Environment | Default Value | Secret | Owner |
| :--- | :--- | :--- | :---: | :--- |
| `POSTGRES_URI` | Production / Staging | `postgresql://...` | Yes | Platform Team |
| `NEO4J_URI` | Production / Staging | `bolt://localhost:7687` | Yes | Database Team |
| `QDRANT_HOST` | Production / Staging | `localhost` | No | Knowledge Team |
| `OPENAI_API_KEY` | Production / Staging | `sk-live-...` | Yes | AI Platform |

---

## 22. Dependency Matrix

| Component | Depends On | Used By | Owned Data |
| :--- | :--- | :--- | :--- |
| `HybridRetrievalService` | `Neo4jProductionAdapter`, `QdrantProductionAdapter` | `FastAPI Gateway` | Unified Search Cache |
| `LivingDocsImpactAnalyzer` | `Neo4jProductionAdapter`, `ASSTEngine` | `Workspace UI` | Change Impact Diffs |

---

## 23. Relationship Matrix

- `CNT-API` → `DB-01` (SQL Read/Write)
- `CNT-GRAPH` → `DB-02` (Cypher Graph Read/Write)
- `CNT-GRAPH` → `DB-03` (gRPC Vector Search)
- `CNT-WORK` → `DB-04` (Redis Queue Worker)

---

## 24. Ownership Matrix

| Service / Component | Business Owner | Technical Owner | Runtime Owner |
| :--- | :--- | :--- | :--- |
| `Knowledge Engine` | Head of Architecture | Staff Graph Engineer | SRE Lead |
| `Security & Audit` | CISO / Compliance Lead | DevSecOps Lead | Platform Lead |

---

## 25. Failure Analysis

| Failure Scenario | Mitigation | Fallback Mechanism | Recovery SLA |
| :--- | :--- | :--- | :---: |
| Primary Neo4j Region Outage | `MultiRegionClusterManager` | Auto-failover to Read-Replica | <30s |
| OpenAI API Rate Limit Exceeded | `MultiModelLLMGateway` | Fallback to Anthropic Claude 3.5 | <1s |

---

## 26. Architectural Decisions (ADR Index)

- `ADR-0001`: Abstract Semantic Syntax Tree (ASST) Canonical Representation
- `ADR-0002`: Neo4j Cypher + Qdrant Vector Hybrid Retrieval Engine
- `ADR-0003`: Progressive Autonomy AI Governance Policy Engine
- `ADR-0004`: Task-Based Multi-Model LLM Gateway Routing
- `ADR-0005`: Multi-Tenant Data Isolation & CMEK AES-256 Encryption
- `ADR-0006`: Event-Driven Celery ASST Graph Indexing
- `ADR-0007`: Zero-Trust Multi-Tenant RBAC Permissions
- `ADR-0008`: CI/CD Security Scanning & Kubernetes Helm Release Packaging
- `ADR-0009`: Immutable SHA-256 Audit Logging & S3 WORM Vault Backup
- `ADR-0010`: Disaster Recovery & Multi-Region Database Replication Strategy

---

## 27. Assumptions & Unknowns

- **Explicit Assumption 1**: Production Kubernetes cluster has AWS S3 bucket IAM policies configured for WORM snapshot manifests.
- **Explicit Assumption 2**: Neo4j Enterprise licenses are active for multi-region read-replica clustering.

---

## 28. Diagram Extraction Metadata

### A. System Context Diagram (C4 Level 1)
- **System**: `SYS-EKOS-001` (DocSphere / EKOS Platform)
- **Actors**: `ACT-01` (Enterprise Architect), `ACT-02` (Developer), `ACT-03` (Compliance Auditor)
- **External Systems**: `EXT-01` (Jira), `EXT-02` (Confluence), `EXT-03` (SAP ALM), `EXT-04` (ServiceNow), `EXT-06` (PagerDuty)
- **Trust Boundaries**: Perimeter TLS 1.3 Ingress Boundary (`TB-01`).

### B. Container Diagram (C4 Level 2)
- **Containers**: `CNT-API`, `CNT-DOC`, `CNT-GRAPH`, `CNT-AI`, `CNT-WORK`, `CNT-UI`
- **Datastores**: `DB-01` (PostgreSQL), `DB-02` (Neo4j), `DB-03` (Qdrant), `DB-04` (Redis)
- **Protocols**: HTTPS, Cypher/Bolt, gRPC, Redis Protocol.

### C. End-to-End Sequence Diagram
- **Step 1**: `ACT-02` → `CNT-UI` (Edit Spec)
- **Step 2**: `CNT-UI` → `CNT-API` (POST /api/v1/graph/entity)
- **Step 3**: `CNT-API` → `CMP-01` (Parse ASST)
- **Step 4**: `CMP-01` → `CMP-02` (Upsert Neo4j Node)
- **Step 5**: `CMP-02` → `CMP-09` (Record SHA-256 Audit Hash)

### D. Domain Model Diagram
- **Entities**: `BusinessCapability` (`CAP-`), `BusinessRequirement` (`REQ-`), `ArchitecturalDecision` (`ADR-`), `FunctionalSpecification` (`FRS-`), `TestCase` (`TC-`).

### E. State Machine Diagram
- **Entity**: `SM-DOC-01` (`DRAFT` → `IN_REVIEW` → `APPROVED` → `PUBLISHED`).

### F. Data Flow Diagram
- **Flow**: `Author Edit` → `FastAPI Ingress` → `ASST Engine` → `Neo4j + Qdrant Dual Store` → `SHA-256 Audit Log`.

### G. Deployment Diagram
- **Provider**: AWS EKS (us-east-1 / eu-central-1), Kubernetes HPA 3–10 Pod Replicas.

### H. Observability Diagram
- **Telemetry**: Prometheus Metrics (`/metrics`), OpenTelemetry Spans, Deep Diagnostic Probe (`/health/deep`).
