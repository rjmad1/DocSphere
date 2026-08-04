import unittest
import asyncio
from backend.services.connectors.jira_connector import JiraConnector
from backend.services.connectors.confluence_connector import ConfluenceConnector
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService
from backend.services.document_service.asst_engine import ASSTEngine

class TestEnterpriseConnectors(unittest.TestCase):
    def setUp(self):
        self.graph_service = KnowledgeGraphService()
        self.asst_engine = ASSTEngine()
        self.jira = JiraConnector(config={"url": "https://jira.enterprise.com"}, graph_service=self.graph_service)
        self.confluence = ConfluenceConnector(config={"url": "https://confluence.enterprise.com"}, asst_engine=self.asst_engine)

    def test_jira_sync(self):
        updates = asyncio.run(self.jira.fetch_updates())
        self.assertEqual(len(updates), 2)

        sync_res = asyncio.run(self.jira.sync_to_ekos(updates))
        self.assertEqual(sync_res.entities_created, 2)
        self.assertEqual(sync_res.relationships_mapped, 1)

    def test_confluence_sync(self):
        pages = asyncio.run(self.confluence.fetch_updates())
        self.assertEqual(len(pages), 1)

        sync_res = asyncio.run(self.confluence.sync_to_ekos(pages))
        self.assertEqual(sync_res.entities_created, 1)
        self.assertEqual(len(sync_res.errors), 0)

if __name__ == "__main__":
    unittest.main()
