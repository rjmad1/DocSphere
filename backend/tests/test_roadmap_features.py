import unittest
import asyncio
from backend.shared.security.worm_backup import WORMBackupService
from backend.services.workflow_engine.notification_service import PolicyEscalationNotificationService
from backend.services.connectors.sap_alm_connector import SAPCloudALMConnector
from backend.services.connectors.servicenow_connector import ServiceNowConnector
from backend.services.knowledge_engine.multi_region_cluster import MultiRegionClusterManager
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService

class TestRoadmapFeatures(unittest.TestCase):
    def setUp(self):
        self.worm = WORMBackupService()
        self.notifications = PolicyEscalationNotificationService()
        self.graph_service = KnowledgeGraphService()
        self.sap_alm = SAPCloudALMConnector(config={}, graph_service=self.graph_service)
        self.servicenow = ServiceNowConnector(config={}, graph_service=self.graph_service)
        self.cluster = MultiRegionClusterManager()

    def test_worm_backup_snapshot_creation(self):
        entries = [
            {"checksum_hash": "a1b2c3d4e5f60000000000000000000000000000000000000000000000000001"},
            {"checksum_hash": "a1b2c3d4e5f60000000000000000000000000000000000000000000000000002"}
        ]
        manifest = self.worm.create_snapshot("tenant_sap_001", entries)
        self.assertEqual(manifest.record_count, 2)
        self.assertIsNotNone(manifest.manifest_checksum)

    def test_notification_escalation_triggers(self):
        pd_res = asyncio.run(self.notifications.trigger_pagerduty_incident("DOC-BRD-001", "BREAKING", 8, 4))
        self.assertEqual(pd_res.channel, "PagerDuty")
        self.assertEqual(pd_res.status, "TRIGGERED")

        slack_res = asyncio.run(self.notifications.send_slack_escalation("DOC-BRD-001", "BREAKING", ["Steward", "Approver"]))
        self.assertEqual(slack_res.channel, "Slack")
        self.assertEqual(slack_res.status, "DELIVERED")

    def test_sap_alm_connector_sync(self):
        items = asyncio.run(self.sap_alm.fetch_updates())
        self.assertEqual(len(items), 2)
        res = asyncio.run(self.sap_alm.sync_to_ekos(items))
        self.assertEqual(res.entities_created, 2)

    def test_servicenow_connector_sync(self):
        items = asyncio.run(self.servicenow.fetch_updates())
        self.assertEqual(len(items), 2)
        res = asyncio.run(self.servicenow.sync_to_ekos(items))
        self.assertEqual(res.entities_created, 2)

    def test_multi_region_cluster_routing(self):
        endpoint = asyncio.run(self.cluster.get_read_endpoint("eu-central-1"))
        self.assertIn("eu-central-1", endpoint)

        health = asyncio.run(self.cluster.check_cluster_health())
        self.assertTrue(health.failover_ready)
        self.assertEqual(len(health.healthy_read_replicas), 2)

if __name__ == "__main__":
    unittest.main()
