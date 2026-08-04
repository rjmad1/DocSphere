# 07. Data Architecture & Schemas

## PostgreSQL Relational Schema (`backend/shared/models/db_models.py`)
- `DocumentModel`: Stores document metadata, title, template type, tenant ID, and ASST JSON snapshot.
- `AuditLogModel`: Stores audit events, actor ID, action type, timestamp, delta JSON, and SHA-256 cryptographic checksum hash.
- `EntityMetadataModel`: Stores canonical entity property mappings.

## Neo4j Graph Model (`backend/services/knowledge_engine/neo4j_adapter.py`)
- Nodes: Indexed by immutable entity ID (`REQ-`, `CAP-`, `ADR-`) and labeled by canonical entity type.
- Edges: Typed directional relationships (`IMPLEMENTS`, `SATISFIES`, `VALIDATED_BY`).

## Redis Cache & Task Lock
- Manages session keys, cached search queries, and Celery task locks.
