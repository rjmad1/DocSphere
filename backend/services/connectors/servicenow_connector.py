"""
EKOS ServiceNow ITSM Enterprise Connector
Bi-directionally synchronizes ServiceNow Change Requests (CHG-) and Incidents (INC-) to canonical EKOS OperationalControl entities.
"""

from typing import Dict, Any, List, Optional
from backend.services.connectors.base_connector import BaseEnterpriseConnector, SyncResult
from backend.services.knowledge_engine.graph_service import KnowledgeGraphService, EntityNode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-ServiceNowConnector")

class ServiceNowConnector(BaseEnterpriseConnector):
    def __init__(self, config: Dict[str, Any], graph_service: KnowledgeGraphService):
        super().__init__("ServiceNowConnector", config)
        self.graph_service = graph_service

    async def fetch_updates(self, since_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
        """Simulates fetching ServiceNow Change Requests and Incidents via REST Table API."""
        logger.info("Fetching ServiceNow ITSM tickets...")
        return [
            {
                "sys_id": "CHG009812",
                "short_description": "Upgrade EOD reconciliation microservice to v1.2.0",
                "type": "ChangeRequest",
                "state": "Implement",
                "ekos_entity_id": "CHG-009812"
            },
            {
                "sys_id": "INC004519",
                "short_description": "Intermittent API timeout during high batch load",
                "type": "Incident",
                "state": "In Progress",
                "ekos_entity_id": "INC-004519"
            }
        ]

    async def sync_to_ekos(self, external_items: List[Dict[str, Any]]) -> SyncResult:
        """Transforms ServiceNow items into canonical EKOS OperationalControl entities."""
        entities_created = 0
        relationships_mapped = 0
        errors = []

        for item in external_items:
            try:
                entity_id = item["ekos_entity_id"]
                node = EntityNode(
                    id=entity_id,
                    entity_type="OperationalControl",
                    version="1.0.0",
                    state="APPROVED" if item["state"] == "Closed" else "IN_REVIEW",
                    properties={
                        "title": item["short_description"],
                        "servicenow_sys_id": item["sys_id"],
                        "itsm_type": item["type"],
                        "itsm_state": item["state"]
                    }
                )
                await self.graph_service.upsert_entity(node)
                entities_created += 1
            except Exception as e:
                errors.append(f"Error syncing ServiceNow item {item.get('sys_id')}: {str(e)}")

        return SyncResult(
            connector_name=self.connector_name,
            items_scanned=len(external_items),
            entities_created=entities_created,
            relationships_mapped=relationships_mapped,
            errors=errors
        )
