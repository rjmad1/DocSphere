# 16. Architectural Decision Records (ADR Index)

| ADR | Title | Decision Summary | Status |
| :--- | :--- | :--- | :---: |
| **ADR-0001** | [ASST Canonical Representation](../adrs/ADR-0001-asst-canonical-representation.md) | Standardized Abstract Semantic Syntax Tree middle-layer | Accepted |
| **ADR-0002** | [Hybrid Graph/Vector Retrieval](../adrs/ADR-0002-neo4j-qdrant-hybrid-retrieval.md) | Dual-store Neo4j Cypher + Qdrant Vector search | Accepted |
| **ADR-0003** | [Progressive Autonomy Governance](../adrs/ADR-0003-progressive-autonomy-governance.md) | AI proposals require human Steward/Approver signoff | Accepted |
| **ADR-0004** | [Multi-Model LLM Routing](../adrs/ADR-0004-multi-model-llm-routing.md) | Task-based provider routing (OpenAI, Anthropic, Google) | Accepted |
| **ADR-0005** | [Multi-Tenant Data Residency & CMEK](../adrs/ADR-0005-multi-tenant-data-residency-and-cmek.md) | Zero-trust isolation & AES-256 CMEK envelope encryption | Accepted |
| **ADR-0006** | [Event-Driven ASST Graph Sync](../adrs/ADR-0006-event-driven-asst-sync.md) | Celery background worker queue for graph indexing | Accepted |
| **ADR-0007** | [Multi-Tenant RBAC Permissions](../adrs/ADR-0007-multi-tenant-rbac-and-security.md) | Context-aware role hierarchy (Author -> Admin) | Accepted |
| **ADR-0008** | [CI/CD & Helm Release Packaging](../adrs/ADR-0008-ci-cd-security-scanning-and-release-automation.md) | GitHub Actions CI & Kubernetes Helm charts | Accepted |
| **ADR-0009** | [Cryptographic Audit Logging](../adrs/ADR-0009-audit-logging-and-compliance.md) | Immutable SHA-256 hash chaining & S3 WORM snapshots | Accepted |
| **ADR-0010** | [Disaster Recovery & Replication](../adrs/ADR-0010-disaster-recovery-and-backup-strategy.md) | Multi-region read-replica failover management | Accepted |
