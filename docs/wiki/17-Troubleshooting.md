# 17. Operational Troubleshooting & FAQs

## Common Diagnostic Procedures

### 1. Database Connectivity Failure
- **Symptom**: `GET /health/deep` returns status `DOWN`.
- **Root Cause**: Local Neo4j, Qdrant, or PostgreSQL container is disconnected.
- **Resolution**: Run `docker-compose up -d` to restart local database containers.

### 2. Hyphen Import Syntax Error
- **Symptom**: `SyntaxError` when importing from `backend.services`.
- **Root Cause**: Directory path contains hyphens.
- **Resolution**: Use snake_case package paths (`backend/services/knowledge_engine/`, `document_service/`, `agent_orchestrator/`, `workflow_engine/`, `ingestion/`, `connectors/`).
