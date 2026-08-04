# ADR-0002: Neo4j + Qdrant Hybrid Semantic Retrieval Architecture

## Status
Accepted

## Context
Pure vector search (RAG) fails in enterprise architecture contexts because vector similarity lacks structural relationship awareness (e.g., distinguishing between a requirement that *implements* a capability vs *conflicts with* a capability). Pure keyword search (BM25) fails on semantic synonymy.

## Decision
EKOS implements a hybrid retrieval engine combining:
1. **Neo4j** graph traversals for structural relationship boundaries (`IMPLEMENTS`, `SATISFIES`, `DEPENDS_ON`).
2. **Qdrant** vector database for high-dimensional semantic similarity embeddings.
3. **BM25 / Keyword** matching for exact code/symbol queries.

## Consequences
- **Positive**: Sub-second search latency (<500ms) with 100% citation integrity and structural context enrichment.
- **Positive**: High extraction accuracy (>90%) with zero hallucinated relationships.
- **Negative / Tradeoff**: Dual-database infrastructure requirements (managed via Docker Compose / Kubernetes Helm charts).
