import { Locator, expect } from '@playwright/test';

export class DocumentEditorComponent {
  readonly root: Locator;
  readonly contentArea: Locator;
  readonly entityBadge: Locator;

  constructor(root: Locator) {
    this.root = root;
    this.contentArea = root.locator('.tiptap-content');
    this.entityBadge = root.locator('.entity-badge');
  }

  async verifyEntityMentioned(entityId: string) {
    await expect(this.root.locator(`[data-entity-id="${entityId}"]`)).toBeVisible();
  }
}
