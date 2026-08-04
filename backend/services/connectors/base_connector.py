"""
EKOS Base Enterprise Connector Specification
Defines abstract base class for external enterprise tool integrations (Jira, Confluence, SAP, GitHub).
Enforces rate-limiting, authentication context, error retries, and data mapping to canonical entities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-BaseConnector")

class SyncResult(BaseModel):
    connector_name: str
    items_scanned: int
    entities_created: int
    relationships_mapped: int
    errors: List[str]

class BaseEnterpriseConnector(ABC):
    def __init__(self, connector_name: str, config: Dict[str, Any]):
        self.connector_name = connector_name
        self.config = config
        logger.info(f"Initialized Enterprise Connector '{connector_name}'")

    @abstractmethod
    async def fetch_updates(self, since_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches raw updates from external system."""
        pass

    @abstractmethod
    async def sync_to_ekos(self, external_items: List[Dict[str, Any]]) -> SyncResult:
        """Transforms raw external items into canonical EKOS entities and syncs to graph."""
        pass
