import { Page, Locator, expect } from '@playwright/test';

export class GovernancePage {
  readonly page: Page;
  readonly tenantId: string;
  readonly slaBadge: Locator;
  readonly policyEvaluatorForm: Locator;
  readonly approvePolicyButton: Locator;

  constructor(page: Page, tenantId: string = 'tenant_sap_001') {
    this.page = page;
    this.tenantId = tenantId;
    this.slaBadge = page.locator('[data-testid="sla-badge"]');
    this.policyEvaluatorForm = page.locator('[data-testid="policy-evaluator-form"]');
    this.approvePolicyButton = page.locator('[data-testid="approve-policy-button"]');
  }

  async goto() {
    await this.page.goto(`/governance?tenant_id=${this.tenantId}`);
  }

  async evaluatePolicy(artifactId: string, severity: 'MINOR' | 'MAJOR' | 'BREAKING') {
    await this.page.locator('[data-testid="input-artifact-id"]').fill(artifactId);
    await this.page.locator('[data-testid="select-severity"]').selectOption(severity);
    await this.page.locator('[data-testid="evaluate-btn"]').click();
  }

  async verifyEscalationAlertTriggered() {
    await expect(this.page.locator('[data-testid="escalation-alert-banner"]')).toBeVisible();
  }
}
