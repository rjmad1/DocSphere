# 08. Platform Workflows

## 1. Document Ingestion Pipeline
1. Input file ingested via `DocumentParser` (`backend/services/ingestion/document_parser.py`).
2. Parsed text converted into ASST tree by `ASSTEngine` (`backend/services/document_service/asst_engine.py`).
3. Chunks indexed in Qdrant; entity nodes/edges merged into Neo4j graph.

## 2. Living Documentation Impact Diff Workflow
1. Editor change triggers `LivingDocsImpactAnalyzer` (`backend/services/document_service/impact_analyzer.py`).
2. Downstream impacted entities identified via Neo4j Cypher traversals.
3. Side-by-side diff recommendations generated for human Steward review.
4. Celery background task (`celery_app.py`) updates search indexes upon approval.
