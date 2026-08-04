# 20. Searchable Repository Index

## Index of Key System Components

### Service Modules (`backend/services/`)
- `KnowledgeGraphService`: `backend/services/knowledge_engine/graph_service.py`
- `HybridRetrievalService`: `backend/services/knowledge_engine/retrieval_service.py`
- `Neo4jProductionAdapter`: `backend/services/knowledge_engine/neo4j_adapter.py`
- `QdrantProductionAdapter`: `backend/services/knowledge_engine/qdrant_adapter.py`
- `KnowledgeGraphReasoningEngine`: `backend/services/knowledge_engine/reasoning_engine.py`
- `FederatedGraphMeshService`: `backend/services/knowledge_engine/federated_graph_mesh.py`
- `MultiRegionClusterManager`: `backend/services/knowledge_engine/multi_region_cluster.py`
- `ASSTEngine`: `backend/services/document_service/asst_engine.py`
- `LivingDocsImpactAnalyzer`: `backend/services/document_service/impact_analyzer.py`
- `WebSocketGraphSyncManager`: `backend/services/document_service/websocket_manager.py`
- `MultiModelLLMGateway`: `backend/services/agent_orchestrator/llm_gateway.py`
- `PolicyEngineService`: `backend/services/workflow_engine/policy_engine.py`
- `PolicyEscalationNotificationService`: `backend/services/workflow_engine/notification_service.py`
- `GitHubCommitListener`: `backend/services/ingestion/github_commit_listener.py`
- `JiraConnector`: `backend/services/connectors/jira_connector.py`
- `ConfluenceConnector`: `backend/services/connectors/confluence_connector.py`
- `SAPCloudALMConnector`: `backend/services/connectors/sap_alm_connector.py`
- `ServiceNowConnector`: `backend/services/connectors/servicenow_connector.py`

### Security Primitives (`backend/shared/security/`)
- `TenantSecurityContext`: `backend/shared/security/tenant_isolation.py`
- `EnvelopeEncryptionService`: `backend/shared/security/encryption.py`
- `CryptographicAuditLogger`: `backend/shared/security/audit_logger.py`
- `InputSanitizer`: `backend/shared/security/input_validator.py`
- `WORMBackupService`: `backend/shared/security/worm_backup.py`

### Test Suites (`backend/tests/`)
- 47 Backend Unit & Contract Test Cases across 13 modules.
