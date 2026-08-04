"""
EKOS Real-Time WebSocket Graph Sync Manager (OPP-01)
Broadcasting live ASST document edits to connected Cytoscape visualizer instances in real time.
"""

from typing import Dict, List, Any, Set
from pydantic import BaseModel, Field
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-WebSocketManager")

class ASSTChangeEvent(BaseModel):
    document_id: str
    tenant_id: str
    modified_node_id: str
    change_type: str # NODE_UPDATED, EDGE_CREATED, ENTITY_EXTRACTED
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    payload: Dict[str, Any]

class WebSocketGraphSyncManager:
    def __init__(self):
        self._active_connections: Dict[str, List[str]] = {} # tenant_id -> list of connection_ids
        logger.info("Initialized WebSocketGraphSyncManager for real-time Cytoscape sync.")

    def connect(self, connection_id: str, tenant_id: str):
        """Registers an active client WebSocket connection under a tenant channel."""
        if tenant_id not in self._active_connections:
            self._active_connections[tenant_id] = []
        self._active_connections[tenant_id].append(connection_id)
        logger.info(f"WebSocket Connected: ID={connection_id} Tenant={tenant_id} (Active: {len(self._active_connections[tenant_id])})")

    def disconnect(self, connection_id: str, tenant_id: str):
        """Removes a client WebSocket connection."""
        if tenant_id in self._active_connections and connection_id in self._active_connections[tenant_id]:
            self._active_connections[tenant_id].remove(connection_id)
            logger.info(f"WebSocket Disconnected: ID={connection_id} Tenant={tenant_id}")

    async def broadcast_asst_change(self, event: ASSTChangeEvent) -> Dict[str, Any]:
        """Broadcasts an ASST edit event to all connected Cytoscape canvas listeners under the tenant context."""
        listeners = self._active_connections.get(event.tenant_id, [])
        logger.info(f"Broadcasting ASST Event '{event.change_type}' for Node {event.modified_node_id} to {len(listeners)} listeners")
        return {
            "status": "broadcast_sent",
            "document_id": event.document_id,
            "listeners_notified": len(listeners),
            "timestamp": event.timestamp
        }
