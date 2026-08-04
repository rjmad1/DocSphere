# 03. Codebase Structure & Module Index

## Backend Package Hierarchy (`backend/`)
- `backend/main.py`: FastAPI server entrypoint exposing `/health`, `/metrics`, `/api/v1/`.
- `backend/services/`: Service layer (using snake_case package names):
  - `knowledge_engine/`: `graph_service.py`, `retrieval_service.py`, `neo4j_adapter.py`, `qdrant_adapter.py`, `reasoning_engine.py`, `federated_graph_mesh.py`, `multi_region_cluster.py`.
  - `document_service/`: `asst_engine.py`, `generation_orchestrator.py`, `impact_analyzer.py`, `websocket_manager.py`.
  - `agent_orchestrator/`: `agent_framework.py`, `llm_gateway.py`.
  - `workflow_engine/`: `policy_engine.py`, `celery_app.py`, `notification_service.py`.
  - `ingestion/`: `document_parser.py`, `github_commit_listener.py`.
  - `connectors/`: `base_connector.py`, `jira_connector.py`, `confluence_connector.py`, `sap_alm_connector.py`, `servicenow_connector.py`.
- `backend/shared/`: Shared infrastructure primitives:
  - `models/`: `database.py`, `db_models.py`.
  - `security/`: `tenant_isolation.py`, `encryption.py`, `audit_logger.py`, `input_validator.py`, `worm_backup.py`.
  - `observability/`: `metrics.py`, `tracing.py`, `health.py`.
  - `middleware/`: `error_handlers.py`.
  - `ontology/`: `canonical-ontology.yaml`.

## Frontend Hierarchy (`frontend/`)
- `frontend/workspace/project-workspace.tsx`: Three-panel workspace container.
- `frontend/components/`: `document-editor.tsx` (TipTap), `knowledge-explorer.tsx` (Cytoscape.js), `impact-diff-viewer.tsx`.
- `frontend/hooks/`: `use-ekos-workspace.ts`, `use-websocket-graph.ts`.
- `frontend/services/api-client.ts`: REST client with tenant header injection.
