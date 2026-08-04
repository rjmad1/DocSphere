"""
EKOS Sprint 1 End-to-End Ingestion & Autonomous Execution Runner
Demonstrates full Project Initiation workflow execution:
Ingestion -> Requirement Extraction -> Graph Population -> Hybrid Search -> Policy Routing -> Impact Diffs
"""

import asyncio
import json
import logging
import sys
import os

# Adjust sys.path to include project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge
from backend.services.knowledge_engine.retrieval_service import HybridRetrievalService, SearchQuery
from backend.services.agent_orchestrator.agent_framework import AgentOrchestrator, TaskRequest
from backend.services.workflow_engine.policy_engine import PolicyEngineService, ApprovalRequest
from backend.services.document_service.generation_orchestrator import DocumentGenerationOrchestrator, GenerationRequest
from ai.agents.requirement_analyzer import RequirementAnalyzerAgent, RawRequirementInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("EKOS-Sprint1-Runner")

async def run_sprint1_execution():
    logger.info("=" * 80)
    logger.info("🚀 STARTING SPRINT 1 AUTONOMOUS EXECUTION DEMONSTRATION")
    logger.info("=" * 80)

    # 1. Ingestion & Requirement Extraction
    logger.info("\n--- STEP 1: REQUIREMENT EXTRACTION & SMART ANALYSIS ---")
    analyzer = RequirementAnalyzerAgent()
    raw_input = RawRequirementInput(
        source_text="The enterprise platform must execute daily automated multi-currency journal reconciliations at end-of-day.",
        source_document_id="DOC-IN-001.pdf",
        page_number=14
    )
    extracted_reqs = await analyzer.analyze_text(raw_input)
    req = extracted_reqs[0]
    logger.info(f"✅ Extracted Entity: ID={req.requirement_id} | Category={req.category} | Priority={req.priority}")
    logger.info(f"   Citation Verified: Source={req.evidence_citation['source_id']} (Page {req.evidence_citation['page']})")

    # 2. Knowledge Graph Population
    logger.info("\n--- STEP 2: KNOWLEDGE GRAPH ENTITY & RELATIONSHIP POPULATION ---")
    graph_svc = KnowledgeGraphService()
    node_req = EntityNode(
        id=req.requirement_id,
        entity_type="BusinessRequirement",
        version="1.0.0",
        state="DRAFT",
        properties={"statement": req.statement}
    )
    node_cap = EntityNode(
        id="CAP-0012",
        entity_type="BusinessCapability",
        version="1.0.0",
        state="APPROVED",
        properties={"name": "Multi-Currency Reconciliation Management"}
    )
    
    await graph_svc.upsert_entity(node_req)
    await graph_svc.upsert_entity(node_cap)

    edge = RelationshipEdge(
        source_id=req.requirement_id,
        target_id="CAP-0012",
        relationship_type="IMPLEMENTS"
    )
    rel_res = await graph_svc.create_relationship(edge)
    logger.info(f"✅ Knowledge Graph Relationship Populated: {rel_res['relationship']}")

    # 3. Hybrid Search & Citation Tracking
    logger.info("\n--- STEP 3: HYBRID SEARCH & EVIDENCE RETRIEVAL ---")
    retrieval_svc = HybridRetrievalService()
    search_q = SearchQuery(query_text="multi-currency journal reconciliation", tenant_id="tenant_sap_001")
    search_results = await retrieval_svc.search(search_q)
    for res in search_results:
        logger.info(f"✅ Retrieved Chunk ID: {res.chunk_id} | Score: {res.score} | Citation: {res.citation['source_doc']} (Page {res.citation['page_number']})")

    # 4. Multi-Agent Task Dispatching
    logger.info("\n--- STEP 4: MULTI-AGENT TASK DISPATCH (Chief of Staff -> Architecture Agent) ---")
    orchestrator = AgentOrchestrator()
    task = TaskRequest(
        task_id="TSK-SP1-001",
        target_agent_id="AGT-ARCH",
        prompt_context={"document_id": "DOC-BRD-001", "entity_id": req.requirement_id},
        required_outputs=["adr_verification"]
    )
    agent_res = await orchestrator.dispatch_task(task)
    logger.info(f"✅ Agent Response [{agent_res.agent_id}]: Status={agent_res.status} | ExecutionTime={agent_res.execution_time_ms}ms")

    # 5. Dynamic Governance & Approval Routing
    logger.info("\n--- STEP 5: DYNAMIC GOVERNANCE POLICY EVALUATION ---")
    policy_svc = PolicyEngineService()
    approval_req = ApprovalRequest(
        artifact_id="DOC-BRD-001",
        artifact_type="BRD",
        change_severity="MAJOR",
        risk_score=0.65,
        impacted_entity_count=4,
        author_id="USR-1092"
    )
    chain = policy_svc.evaluate_approval_chain(approval_req)
    logger.info(f"✅ Policy Evaluated: SLA={chain.sla_hours}h | Required Roles={chain.required_roles}")

    # 6. Document Generation Orchestration
    logger.info("\n--- STEP 6: DOCUMENT GENERATION ORCHESTRATION ---")
    doc_orchestrator = DocumentGenerationOrchestrator()
    gen_req = GenerationRequest(
        document_title="SAP S/4HANA Finance Migration BRD",
        template_type="BRD",
        project_id="PRJ-SAP-01",
        input_source_ids=["DOC-IN-001.pdf"],
        tenant_id="tenant_sap_001"
    )
    gen_status = await doc_orchestrator.start_generation(gen_req)
    logger.info(f"✅ Document Generated: ID={gen_status.document_id} | Status={gen_status.status} | Progress={gen_status.progress_percentage}%")

    logger.info("\n" + "=" * 80)
    logger.info("🎉 SPRINT 1 AUTONOMOUS EXECUTION DEMONSTRATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_sprint1_execution())
