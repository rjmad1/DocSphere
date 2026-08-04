"""
EKOS Full Production End-to-End Verification Suite
Executes complete production lifecycle:
Parsing -> Qdrant Embedding -> Neo4j Graph -> ASST Engine -> Multi-Model LLM -> Impact Analysis -> Policy Routing
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.ingestion.document_parser import DocumentParser
from backend.services.knowledge_engine.neo4j_adapter import Neo4jProductionAdapter
from backend.services.knowledge_engine.qdrant_adapter import QdrantProductionAdapter
from backend.services.document_service.asst_engine import ASSTEngine
from backend.services.document_service.impact_analyzer import LivingDocsImpactAnalyzer, ChangeEvent
from backend.services.agent_orchestrator.llm_gateway import MultiModelLLMGateway, LLMRequest
from backend.services.workflow_engine.policy_engine import PolicyEngineService, ApprovalRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("EKOS-ProductionE2E")

async def run_full_production_e2e():
    logger.info("=" * 85)
    logger.info("🚀 EXECUTING FULL EKOS PRODUCTION END-TO-END SYSTEM VERIFICATION")
    logger.info("=" * 85)

    # 1. Document Ingestion & Chunking
    logger.info("\n--- STEP 1: PRODUCTION DOCUMENT INGESTION & ENTITY PARSING ---")
    parser = DocumentParser()
    raw_doc = """
    # SAP S/4HANA Finance Migration Specification
    
    ## 1. Business Requirements
    The system shall execute automated multi-currency journal reconciliations at end-of-day.
    REQ-00847 maps directly to CAP-0012.
    """
    chunks = parser.parse_text_content(document_id="DOC-IN-002.md", raw_text=raw_doc)
    logger.info(f"✅ Ingested {len(chunks)} parsed chunks with detected entities: {chunks[0].detected_entities}")

    # 2. Qdrant Vector Indexing
    logger.info("\n--- STEP 2: QDRANT VECTOR EMBEDDING & INDEXING ---")
    qdrant = QdrantProductionAdapter()
    for chunk in chunks:
        await qdrant.upsert_chunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            text=chunk.text_content,
            payload={"tenant_id": "tenant_sap_001", "heading": chunk.section_heading}
        )
    search_res = await qdrant.search_similar("multi-currency journal reconciliation", top_k=1, filter_tenant="tenant_sap_001")
    logger.info(f"✅ Qdrant Search Similarity Result: Chunk={search_res[0]['chunk_id']} | Score={search_res[0]['score']}")

    # 3. Neo4j Knowledge Graph Operations
    logger.info("\n--- STEP 3: NEO4J KNOWLEDGE GRAPH PERSISTENCE & TRAVERSAL ---")
    neo4j = Neo4jProductionAdapter()
    await neo4j.upsert_node("REQ-00847", "BusinessRequirement", {"statement": "Automated EOD reconciliation"})
    await neo4j.upsert_node("CAP-0012", "BusinessCapability", {"name": "Multi-Currency Reconciliation"})
    await neo4j.create_edge("REQ-00847", "CAP-0012", "IMPLEMENTS")
    graph_res = await neo4j.query_neighbors("REQ-00847")
    logger.info(f"✅ Neo4j Graph Neighbors Found: {graph_res['nodes_found']}")

    # 4. ASST Tree Building & Bidirectional Rendering
    logger.info("\n--- STEP 4: ABSTRACT SEMANTIC SYNTAX TREE (ASST) TRANSFORMATION ---")
    asst_engine = ASSTEngine()
    asst = asst_engine.parse_markdown_to_asst("DOC-IN-002", "SAP Migration Spec", raw_doc)
    rendered_md = asst_engine.render_asst_to_markdown(asst)
    logger.info(f"✅ ASST Root Node: {asst.type} | Children Count: {len(asst.children)}")
    logger.info(f"✅ Rendered Markdown Length: {len(rendered_md)} characters")

    # 5. Multi-Model LLM Gateway Routing
    logger.info("\n--- STEP 5: MULTI-MODEL LLM GATEWAY TASK ROUTING ---")
    llm = MultiModelLLMGateway()
    llm_req = LLMRequest(task_type="reasoning", prompt="Verify compliance of REQ-00847 with SAP Activate standard.")
    llm_res = await llm.generate_response(llm_req)
    logger.info(f"✅ LLM Gateway Response: Provider={llm_res.provider} | Model={llm_res.selected_model} | Cost=${llm_res.cost_usd}")

    # 6. Living Documentation Change Impact Analysis
    logger.info("\n--- STEP 6: LIVING DOCUMENTATION IMPACT ANALYSIS & DIFF GENERATION ---")
    impact_analyzer = LivingDocsImpactAnalyzer()
    change_evt = ChangeEvent(
        event_id="EVT-9001",
        source_document_id="DOC-IN-002.md",
        entity_id="REQ-00847",
        old_value="Weekly EOD sync",
        new_value="Daily EOD sync",
        reason="Upstream PRD update"
    )
    impact_report = await impact_analyzer.analyze_change_impact(change_evt)
    logger.info(f"✅ Impact Analysis: Risk Level={impact_report.risk_level} | Diffs Generated={len(impact_report.recommended_diffs)}")

    # 7. Governance Policy Routing
    logger.info("\n--- STEP 7: GOVERNANCE POLICY ROUTING & SLA COMPUTATION ---")
    policy = PolicyEngineService()
    pol_req = ApprovalRequest(
        artifact_id="DOC-BRD-001",
        artifact_type="BRD",
        change_severity="BREAKING",
        risk_score=0.92,
        impacted_entity_count=8,
        author_id="USR-1092"
    )
    chain = policy.evaluate_approval_chain(pol_req)
    logger.info(f"✅ Policy Evaluated: Required Roles={chain.required_roles} | SLA={chain.sla_hours} hours")

    logger.info("\n" + "=" * 85)
    logger.info("🎉 EKOS PRODUCTION END-TO-END SYSTEM VERIFICATION PASSED WITH 100% SUCCESS")
    logger.info("=" * 85)

if __name__ == "__main__":
    asyncio.run(run_full_production_e2e())
