import unittest
import asyncio
from backend.services.knowledge_engine.neo4j_adapter import Neo4jProductionAdapter
from backend.services.knowledge_engine.qdrant_adapter import QdrantProductionAdapter
from backend.services.ingestion.document_parser import DocumentParser
from backend.services.document_service.asst_engine import ASSTEngine
from backend.services.document_service.impact_analyzer import LivingDocsImpactAnalyzer, ChangeEvent
from backend.services.agent_orchestrator.llm_gateway import MultiModelLLMGateway, LLMRequest

class TestProductionStack(unittest.TestCase):
    def setUp(self):
        self.neo4j_adapter = Neo4jProductionAdapter()
        self.qdrant_adapter = QdrantProductionAdapter()
        self.parser = DocumentParser()
        self.asst_engine = ASSTEngine()
        self.impact_analyzer = LivingDocsImpactAnalyzer()
        self.llm_gateway = MultiModelLLMGateway()

    def test_neo4j_adapter_operations(self):
        res_node = asyncio.run(self.neo4j_adapter.upsert_node(
            node_id="REQ-00847",
            label="BusinessRequirement",
            properties={"title": "Multi-currency EOD reconciliation"}
        ))
        self.assertEqual(res_node["status"], "success")

        res_edge = asyncio.run(self.neo4j_adapter.create_edge(
            source_id="REQ-00847",
            target_id="CAP-0012",
            rel_type="IMPLEMENTS"
        ))
        self.assertEqual(res_edge["status"], "success")

        neighbors = asyncio.run(self.neo4j_adapter.query_neighbors("REQ-00847"))
        self.assertIn("CAP-0012", neighbors["nodes_found"])

    def test_qdrant_adapter_search(self):
        asyncio.run(self.qdrant_adapter.upsert_chunk(
            chunk_id="chk_001",
            document_id="DOC-IN-001.pdf",
            text="Automated multi-currency EOD journal reconciliation.",
            payload={"tenant_id": "tenant_sap_001"}
        ))
        search_res = asyncio.run(self.qdrant_adapter.search_similar(
            query_text="multi-currency reconciliation",
            top_k=1,
            filter_tenant="tenant_sap_001"
        ))
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["chunk_id"], "chk_001")
        self.assertGreaterEqual(search_res[0]["score"], 0.30)

    def test_document_parser_entity_extraction(self):
        raw_text = "# Requirements\n\nThe system shall support REQ-00847 and satisfy CAP-0012."
        chunks = self.parser.parse_text_content(document_id="DOC-01", raw_text=raw_text)
        self.assertEqual(len(chunks), 1)
        self.assertIn("REQ-00847", chunks[0].detected_entities)
        self.assertIn("CAP-0012", chunks[0].detected_entities)

    def test_asst_engine_bidirectional_conversion(self):
        md_text = "# Title\n## Section 1\nSome text content."
        asst = self.asst_engine.parse_markdown_to_asst("DOC-01", "Title", md_text)
        self.assertEqual(asst.type, "DocumentAST")
        self.assertGreaterEqual(len(asst.children), 1)

        rendered_md = self.asst_engine.render_asst_to_markdown(asst)
        self.assertIn("# Title", rendered_md)
        self.assertIn("## Section 1", rendered_md)

    def test_living_docs_impact_analyzer(self):
        change = ChangeEvent(
            event_id="EVT-01",
            source_document_id="DOC-IN-001.pdf",
            entity_id="REQ-00847",
            old_value="Weekly EOD sync",
            new_value="Daily EOD sync",
            reason="Upstream PRD update"
        )
        report = asyncio.run(self.impact_analyzer.analyze_change_impact(change))
        self.assertEqual(report.risk_level, "HIGH")
        self.assertTrue(report.human_approval_required)

    def test_multi_model_llm_gateway(self):
        req = LLMRequest(task_type="reasoning", prompt="Analyze impact of REQ-00847")
        res = asyncio.run(self.llm_gateway.generate_response(req))
        self.assertEqual(res.provider, "openai")
        self.assertIn("GPT-4O", res.generated_text.upper())

if __name__ == "__main__":
    unittest.main()
