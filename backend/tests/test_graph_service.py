import unittest
import asyncio
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge

class TestGraphService(unittest.TestCase):
    def setUp(self):
        self.service = KnowledgeGraphService()

    def test_upsert_entity(self):
        node = EntityNode(
            id="REQ-00847",
            entity_type="BusinessRequirement",
            version="1.0.0",
            state="APPROVED",
            properties={"title": "Multi-currency EOD reconciliation"}
        )
        result = asyncio.run(self.service.upsert_entity(node))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["entity_id"], "REQ-00847")

    def test_create_relationship(self):
        edge = RelationshipEdge(
            source_id="REQ-00847",
            target_id="CAP-0012",
            relationship_type="IMPLEMENTS"
        )
        result = asyncio.run(self.service.create_relationship(edge))
        self.assertEqual(result["status"], "success")
        self.assertIn("REQ-00847 -[IMPLEMENTS]-> CAP-0012", result["relationship"])

    def test_traverse_dependencies(self):
        result = asyncio.run(self.service.traverse_dependencies("REQ-00847", max_depth=2))
        self.assertEqual(result["root_id"], "REQ-00847")
        self.assertIn("CAP-0012", result["upstream_dependencies"])
        self.assertIn("FRS-00401", result["downstream_impacts"])

if __name__ == "__main__":
    unittest.main()
