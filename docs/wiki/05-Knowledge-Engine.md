# 05. Knowledge Engine & Canonical Ontology

## Canonical Ontology (`backend/shared/ontology/canonical-ontology.yaml`)
Defines 40+ canonical entity types and semantic relationship edges:
- Entity Types: `BusinessCapability` (`CAP-`), `BusinessRequirement` (`REQ-`), `ArchitecturalDecision` (`ADR-`), `FunctionalSpecification` (`FRS-`), `TestCase` (`TC-`), `OperationalControl` (`CHG-`, `INC-`).
- Semantic Relationships: `IMPLEMENTS`, `SATISFIES`, `VALIDATED_BY`, `DEPENDS_ON`, `CONFLICTS_WITH`.

## Neo4j Graph Adapter (`backend/services/knowledge_engine/neo4j_adapter.py`)
- Identity-preserving graph node upserts (`MERGE (e:Entity {id: $id})`).
- Multi-depth Cypher dependency traversals (`query_neighbors`).

## Qdrant Vector Adapter (`backend/services/knowledge_engine/qdrant_adapter.py`)
- Dense vector indexing and cosine similarity search (`search_similar_chunks`).

## Graph Reasoning Engine (`backend/services/knowledge_engine/reasoning_engine.py`)
- Automated semantic conflict detection (`CONFLICTS_WITH`).
- Traceability gap finder identifying requirements missing test cases or capabilities.
