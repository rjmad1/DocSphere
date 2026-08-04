# ADR-0001: Abstract Semantic Syntax Tree (ASST) as Canonical Representation

## Status
Accepted

## Context
Enterprise documentation in legacy transformation projects suffers from semantic drift across documents, schemas, and live UI views. Traditional systems treat documents as static Markdown/PDF blobs or isolated database rows, making it impossible to perform automated bidirectional synchronization or Living Documentation impact analysis.

## Decision
EKOS adopts the **Abstract Semantic Syntax Tree (ASST)** as the single canonical representation layer. All document projections (Markdown, TipTap Rich Text JSON, HTML, PDF) and Knowledge Graph representations (Neo4j nodes and edges) are dynamic projections of an underlying ASST structure.

## Consequences
- **Positive**: Eliminates semantic drift; enables point-in-time versioning; guarantees bidirectional sync between UI editors and Knowledge Graph.
- **Positive**: Allows inline binding of canonical entity IDs (`REQ-00847`) with character-offset citations to source evidence.
- **Negative / Tradeoff**: Requires parsing and serializing ASST trees on document read/write operations, introducing minor CPU overhead (mitigated via caching).
