import { Page, Locator, expect } from '@playwright/test';

export class WorkspacePage {
  readonly page: Page;
  readonly tenantId: string;
  readonly editorPane: Locator;
  readonly graphExplorerPane: Locator;
  readonly diffViewerPane: Locator;
  readonly publishButton: Locator;
  readonly entityNodeTag: Locator;

  constructor(page: Page, tenantId: string = 'tenant_sap_001') {
    this.page = page;
    this.tenantId = tenantId;
    this.editorPane = page.locator('[data-testid="tiptap-editor-pane"]');
    this.graphExplorerPane = page.locator('[data-testid="cytoscape-graph-explorer"]');
    this.diffViewerPane = page.locator('[data-testid="impact-diff-viewer"]');
    this.publishButton = page.locator('[data-testid="publish-diff-button"]');
    this.entityNodeTag = page.locator('[data-testid="entity-node-tag"]');
  }

  async goto() {
    await this.page.goto(`/workspace?tenant_id=${this.tenantId}`);
  }

  async typeInEditor(text: string) {
    await this.editorPane.fill(text);
  }

  async selectGraphNode(nodeId: string) {
    await this.graphExplorerPane.locator(`[data-node-id="${nodeId}"]`).click();
  }

  async approveImpactDiff() {
    await this.publishButton.click();
    await expect(this.page.locator('[data-testid="diff-status-badge"]')).toHaveText('APPROVED');
  }
}
