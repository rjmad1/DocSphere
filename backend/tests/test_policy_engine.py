import unittest
from backend.services.workflow_engine.policy_engine import PolicyEngineService, ApprovalRequest

class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngineService()

    def test_minor_approval_chain(self):
        request = ApprovalRequest(
            artifact_id="DOC-BRD-001",
            artifact_type="BRD",
            change_severity="MINOR",
            risk_score=0.2,
            impacted_entity_count=1,
            author_id="USR-1092"
        )
        chain = self.engine.evaluate_approval_chain(request)
        self.assertEqual(chain.sla_hours, 24)
        self.assertIn("Steward", chain.required_roles)

    def test_breaking_approval_chain(self):
        request = ApprovalRequest(
            artifact_id="DOC-BRD-001",
            artifact_type="BRD",
            change_severity="BREAKING",
            risk_score=0.85,
            impacted_entity_count=15,
            author_id="USR-1092"
        )
        chain = self.engine.evaluate_approval_chain(request)
        self.assertEqual(chain.sla_hours, 8)
        self.assertIn("Lead Enterprise Architect", chain.required_roles)
        self.assertIn("Security Officer", chain.required_roles)

if __name__ == "__main__":
    unittest.main()
