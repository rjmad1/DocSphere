import unittest
import asyncio
from backend.services.knowledge_engine.retrieval_service import HybridRetrievalService, SearchQuery

class TestRetrievalService(unittest.TestCase):
    def setUp(self):
        self.service = HybridRetrievalService()

    def test_hybrid_search(self):
        query = SearchQuery(
            query_text="multi-currency reconciliation",
            tenant_id="tenant_sap_001",
            top_k=2
        )
        results = asyncio.run(self.service.search(query))
        self.assertEqual(len(results), 2)
        self.assertGreaterEqual(results[0].score, 0.90)
        self.assertIn("DOC-IN-001.pdf", results[0].citation["source_doc"])

if __name__ == "__main__":
    unittest.main()
