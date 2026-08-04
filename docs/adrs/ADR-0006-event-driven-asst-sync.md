# ADR-0006: Event-Driven Abstract Semantic Syntax Tree (ASST) & Graph Synchronization

## Status
Accepted

## Context
When users edit documents in the rich-text TipTap editor or ingest external Confluence/Jira items, updating the Knowledge Graph synchronously on every keystroke causes latency degradation and potential database transaction locks.

## Decision
EKOS implements an **Event-Driven Asynchronous Synchronization Engine**:
1. Editor edits publish `ASSTUpdated` events to Redis / Celery queues.
2. Background workers process ASST tree diffs, extract canonical entities (`REQ`, `CAP`, `ADR`), and update Neo4j & Qdrant idempotently in batches.

## Consequences
- **Positive**: Sub-100ms response time in the TipTap editor UI; resilient transaction processing with automatic retries.
- **Negative / Tradeoff**: Eventual consistency between active document editor buffer and Neo4j graph (typically <500ms lag).
