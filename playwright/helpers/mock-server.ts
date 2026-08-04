import { Page } from '@playwright/test';

export async function setupEKOSApiMocks(page: Page) {
  await page.route('/api/v1/retrieval/search', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [
          {
            chunk_id: 'chk_001',
            document_id: 'DOC-BRD-001',
            score: 0.94,
            content: 'Multi-currency EOD reconciliation rules for SAP S/4HANA.',
            metadata: { entity_id: 'REQ-00847', entity_type: 'BusinessRequirement' }
          }
        ]
      })
    });
  });

  await page.route('/api/v1/graph/entity', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'upserted', id: 'REQ-00847', version: '1.0.0' })
    });
  });

  await page.route('/api/v1/policy/evaluate', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        policy_id: 'pol_governance_001',
        requires_approval: true,
        sla_hours: 8.0,
        required_approver_roles: ['Steward', 'Approver'],
        escalation_channels: ['PAGERDUTY', 'SLACK']
      })
    });
  });
}
