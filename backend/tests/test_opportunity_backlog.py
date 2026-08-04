import unittest
import asyncio
from backend.services.document_service.websocket_manager import WebSocketGraphSyncManager, ASSTChangeEvent
from backend.services.ingestion.github_commit_listener import GitHubCommitListener, GitHubCommitWebhookPayload
from backend.services.knowledge_engine.federated_graph_mesh import FederatedGraphMeshService, FederatedQueryRequest
from backend.services.document_service.impact_analyzer import LivingDocsImpactAnalyzer
from backend.services.document_service.asst_engine import ASSTEngine

class TestOpportunityBacklog(unittest.TestCase):
    def setUp(self):
        self.ws_manager = WebSocketGraphSyncManager()
        self.impact_analyzer = LivingDocsImpactAnalyzer()
        self.asst_engine = ASSTEngine()
        self.github_listener = GitHubCommitListener(self.impact_analyzer, self.asst_engine)
        self.federated_mesh = FederatedGraphMeshService()

    def test_websocket_connection_and_broadcast(self):
        self.ws_manager.connect("conn_101", "tenant_sap_001")
        self.ws_manager.connect("conn_102", "tenant_sap_001")
        
        event = ASSTChangeEvent(
            document_id="DOC-BRD-001",
            tenant_id="tenant_sap_001",
            modified_node_id="REQ-00847",
            change_type="NODE_UPDATED",
            payload={"title": "Updated Multi-Currency Rule"}
        )

        res = asyncio.run(self.ws_manager.broadcast_asst_change(event))
        self.assertEqual(res["listeners_notified"], 2)
        
        self.ws_manager.disconnect("conn_101", "tenant_sap_001")

    def test_github_commit_listener(self):
        payload = GitHubCommitWebhookPayload(
            commit_sha="a8f9102c4b57890123456789abcdef0123456789",
            repository_name="enterprise-sap-finance",
            author="lead.architect@enterprise.com",
            commit_message="Update REQ-00847 and CAP-0012 specifications",
            modified_files=["docs/finance_spec.md"],
            added_files=[],
            diff_text="+ Update specification for REQ-00847 and CAP-0012."
        )

        res = asyncio.run(self.github_listener.process_push_event(payload))
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["entities_extracted"]), 2)
        self.assertEqual(res["impact_analyses_triggered"], 2)

    def test_federated_graph_mesh_query(self):
        request = FederatedQueryRequest(
            source_tenant_id="tenant_org_alpha",
            target_tenant_id="tenant_org_beta",
            target_entity_id="REQ-SAP-901",
            federation_token="fed_tok_9912"
        )

        res = asyncio.run(self.federated_mesh.execute_federated_query(request))
        self.assertEqual(res.source_tenant_id, "tenant_org_alpha")
        self.assertEqual(res.target_tenant_id, "tenant_org_beta")
        self.assertIsNotNone(res.cryptographic_signature)
        self.assertEqual(len(res.cryptographic_signature), 64)

if __name__ == "__main__":
    unittest.main()
