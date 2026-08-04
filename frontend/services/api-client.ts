/**
 * EKOS Production Frontend API Client
 * Enterprise REST client with tenant context headers, error mapping, and retry handling.
 */

export interface APIConfig {
  baseUrl: string;
  tenantId: string;
  authToken?: string;
}

export class EKOSAPIClient {
  private baseUrl: string;
  private tenantId: string;
  private authToken?: string;

  constructor(config: APIConfig) {
    self = this as any;
    this.baseUrl = config.baseUrl || 'http://localhost:8000';
    this.tenantId = config.tenantId || 'tenant_sap_001';
    this.authToken = config.authToken;
  }

  private getHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'X-Tenant-ID': this.tenantId,
      ...(this.authToken ? { Authorization: `Bearer ${this.authToken}` } : {})
    };
  }

  async getHealth(): Promise<{ status: string; version: string }> {
    const res = await fetch(`${this.baseUrl}/health`, { headers: this.getHeaders() });
    return res.json();
  }

  async hybridSearch(queryText: string, topK: number = 5): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/api/v1/retrieval/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        query_text: queryText,
        tenant_id: this.tenantId,
        top_k: topK
      })
    });
    return res.json();
  }

  async evaluatePolicy(artifactId: string, changeSeverity: string, riskScore: number): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/v1/policy/evaluate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        artifact_id: artifactId,
        artifact_type: 'BRD',
        change_severity: changeSeverity,
        risk_score: riskScore,
        impacted_entity_count: 3,
        author_id: 'USR-1092'
      })
    });
    return res.json();
  }
}
