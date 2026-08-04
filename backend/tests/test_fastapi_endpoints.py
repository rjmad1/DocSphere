import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_deep_health_check_endpoint(self):
        response = self.client.get("/health/deep")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "UP")

    def test_metrics_endpoint(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("counters", response.json())

    def test_graph_entity_upsert_endpoint(self):
        payload = {
            "id": "REQ-00847",
            "entity_type": "BusinessRequirement",
            "version": "1.0.0",
            "state": "APPROVED",
            "properties": {"title": "Multi-currency EOD reconciliation"}
        }
        response = self.client.post("/api/v1/graph/entity", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_hybrid_search_endpoint(self):
        payload = {
            "query_text": "multi-currency reconciliation",
            "tenant_id": "tenant_sap_001",
            "top_k": 2
        }
        response = self.client.post("/api/v1/retrieval/search", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_policy_evaluate_endpoint(self):
        payload = {
            "artifact_id": "DOC-BRD-001",
            "artifact_type": "BRD",
            "change_severity": "BREAKING",
            "risk_score": 0.85,
            "impacted_entity_count": 5,
            "author_id": "USR-1092"
        }
        response = self.client.post("/api/v1/policy/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sla_hours"], 8)

if __name__ == "__main__":
    unittest.main()
