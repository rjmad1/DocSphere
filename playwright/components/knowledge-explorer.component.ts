import { Locator, expect } from '@playwright/test';

export class KnowledgeExplorerComponent {
  readonly root: Locator;

  constructor(root: Locator) {
    this.root = root;
  }

  async verifyGraphNodeRendered(nodeId: string) {
    await expect(this.root.locator(`[data-node-id="${nodeId}"]`)).toBeVisible();
  }
}
