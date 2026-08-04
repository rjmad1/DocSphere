# 01. Platform Architecture

## System Overview & C4 Model

```
[ Ingestion & Connectors (Jira / Confluence / SAP ALM / ServiceNow) ]
                              │
                              ▼
[ Document Parser & ASST Engine (Markdown ↔ DocumentAST) ]
                              │
                              ▼
[ Hybrid Retrieval Engine (Neo4j Cypher + Qdrant Vector + Postgres SQL) ]
                              │
                              ▼
[ Multi-Agent Framework & Reasoning Engine (Conflict & Gap Analysis) ]
                              │
                              ▼
[ Governance Policy Engine (Progressive Autonomy + SLA Escalation) ]
                              │
                              ▼
[ Three-Panel Workspace UI (TipTap + Cytoscape + Impact Diff Viewer) ]
```

## Architectural Tenets (Document 0 / DAS)
1. **ASST Canonical Middle Layer**: All documents parse into AST nodes (`DocumentAST` → `SectionNode` → `EntityRefNode`).
2. **Hybrid Dual-Store Indexing**: Combines vector embeddings with graph relationship traversals.
3. **Progressive Autonomy**: AI agents generate proposals; humans retain ultimate approval authority.
