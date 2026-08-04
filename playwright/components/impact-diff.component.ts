import { Locator, expect } from '@playwright/test';

export class ImpactDiffComponent {
  readonly root: Locator;
  readonly beforeDiffPane: Locator;
  readonly afterDiffPane: Locator;

  constructor(root: Locator) {
    this.root = root;
    this.beforeDiffPane = root.locator('[data-testid="diff-before"]');
    this.afterDiffPane = root.locator('[data-testid="diff-after"]');
  }

  async verifyDiffHeading(headingText: string) {
    await expect(this.root.locator('.diff-heading')).toContainText(headingText);
  }
}
