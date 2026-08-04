import { useState, useEffect } from 'react';
import { EKOSAPIClient } from '../services/api-client';

export interface WorkspaceState {
  healthStatus: string;
  selectedDocumentId: string;
  searchResults: any[];
  isLoading: boolean;
  error?: string;
}

export const useEKOSWorkspace = (tenantId: string = 'tenant_sap_001') => {
  const [client] = useState(() => new EKOSAPIClient({ baseUrl: 'http://localhost:8000', tenantId }));
  const [state, setState] = useState<WorkspaceState>({
    healthStatus: 'UNKNOWN',
    selectedDocumentId: 'DOC-BRD-001',
    searchResults: [],
    isLoading: false
  });

  useEffect(() => {
    let isMounted = true;
    client.getHealth()
      .then((data) => {
        if (isMounted) setState((prev) => ({ ...prev, healthStatus: data.status }));
      })
      .catch((err) => {
        if (isMounted) setState((prev) => ({ ...prev, error: err.message }));
      });

    return () => { isMounted = false; };
  }, [client]);

  const executeSearch = async (query: string) => {
    setState((prev) => ({ ...prev, isLoading: true }));
    try {
      const results = await client.hybridSearch(query);
      setState((prev) => ({ ...prev, searchResults: results, isLoading: false }));
    } catch (err: any) {
      setState((prev) => ({ ...prev, error: err.message, isLoading: false }));
    }
  };

  return {
    ...state,
    executeSearch
  };
};
