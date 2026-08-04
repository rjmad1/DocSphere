import { useState, useEffect } from 'react';

export interface GraphSyncEvent {
  documentId: string;
  modifiedNodeId: string;
  changeType: string;
  timestamp: string;
  payload: any;
}

export const useWebSocketGraph = (documentId: string, tenantId: string = 'tenant_sap_001') => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastEvent, setLastEvent] = useState<GraphSyncEvent | null>(null);

  useEffect(() => {
    // Simulates WebSocket connection setup to EKOS backend
    const connectionId = `conn_${Math.random().toString(36).substr(2, 9)}`;
    setIsConnected(true);

    return () => {
      setIsConnected(false);
    };
  }, [documentId, tenantId]);

  const emitASSTEdit = (nodeId: string, changeType: string, payload: any) => {
    const event: GraphSyncEvent = {
      documentId,
      modifiedNodeId: nodeId,
      changeType,
      timestamp: new Date().toISOString(),
      payload
    };
    setLastEvent(event);
  };

  return {
    isConnected,
    lastEvent,
    emitASSTEdit
  };
};
