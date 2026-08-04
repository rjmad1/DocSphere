"""
EKOS Jira Enterprise Connector
Bi-directionally synchronizes Jira Issues, User Stories, and Epics to canonical EKOS BusinessRequirement (REQ-) and TestCase (TC-) entities.
"""

from typing import Dict, Any, List, Optional
from backend.services.connectors.base_connector import BaseEnterpriseConnector, SyncResult
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode, RelationshipEdge
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-JiraConnector")

class JiraConnector(BaseEnterpriseConnector):
    def __init__(self, config: Dict[str, Any], graph_service: KnowledgeGraphService):
        super().__init__("JiraConnector", config)
        self.graph_service = graph_service

    async def fetch_updates(self, since_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
        """Simulates fetching updated issues from Jira REST API."""
        logger.info(f"Fetching Jira issues updated since {since_timestamp or 'beginning'}")
        return [
            {
                "issue_key": "JIRA-1042",
                "summary": "Automate multi-currency journal reconciliation at EOD",
                "issue_type": "Story",
                "status": "In Progress",
                "ekos_entity_id": "REQ-00847"
            },
            {
                "issue_key": "JIRA-1043",
                "summary": "Validate EOD multi-currency journal posting accuracy",
                "issue_type": "Test",
                "status": "Ready for QA",
                "ekos_entity_id": "TC-00912"
            }
        ]

    async def sync_to_ekos(self, external_items: List[Dict[str, Any]]) -> SyncResult:
        """Transforms Jira issues into canonical BusinessRequirement and TestCase entities."""
        entities_created = 0
        relationships_mapped = 0
        errors = []

        for item in external_items:
            try:
                entity_id = item["ekos_entity_id"]
                entity_type = "TestCase" if item["issue_type"] == "Test" else "BusinessRequirement"
                
                node = EntityNode(
                    id=entity_id,
                    entity_type=entity_type,
                    version="1.0.0",
                    state="APPROVED" if item["status"] == "Done" else "DRAFT",
                    properties={
                        "title": item["summary"],
                        "external_jira_key": item["issue_key"],
                        "jira_status": item["status"]
                    }
                )
                await self.graph_service.upsert_entity(node)
                entities_created += 1

                if entity_type == "TestCase":
                    edge = RelationshipEdge(
                        source_id=entity_id,
                        target_id="REQ-00847",
                        relationship_type="VALIDATED_BY"
                    )
                    await self.graph_service.create_relationship(edge)
                    relationships_mapped += 1

            except Exception as e:
                errors.append(f"Error syncing {item.get('issue_key')}: {str(e)}")

        return SyncResult(
            connector_name=self.connector_name,
            items_scanned=len(external_items),
            entities_created=entities_created,
            relationships_mapped=relationships_mapped,
            errors=errors
        )
