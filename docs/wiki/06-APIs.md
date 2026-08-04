# 06. API Specifications & Endpoints

## Core REST Endpoints (`backend/main.py`)

### 1. Health Diagnostics
- `GET /health`: Liveness probe returning `{"status": "healthy"}`.
- `GET /health/deep`: Readiness probe verifying PostgreSQL, Neo4j, Qdrant, and Redis.

### 2. Metrics & Telemetry
- `GET /metrics`: Serves Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`).

### 3. Knowledge Graph Management
- `POST /api/v1/graph/entity`: Upserts an entity node.
  - Body: `{"id": "REQ-00847", "entity_type": "BusinessRequirement", "version": "1.0.0", "state": "APPROVED", "properties": {"title": "Multi-currency EOD reconciliation"}}`

### 4. Hybrid Retrieval
- `POST /api/v1/retrieval/search`: Hybrid vector/graph search.
  - Body: `{"query_text": "multi-currency reconciliation", "tenant_id": "tenant_sap_001", "top_k": 5}`

### 5. Policy Governance
- `POST /api/v1/policy/evaluate`: Evaluates change approval policies and computes SLA windows.
  - Body: `{"artifact_id": "DOC-BRD-001", "artifact_type": "BRD", "change_severity": "BREAKING", "risk_score": 0.85, "impacted_entity_count": 5, "author_id": "USR-1092"}`
