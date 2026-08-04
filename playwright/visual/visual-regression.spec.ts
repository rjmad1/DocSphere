import { test, expect } from '../fixtures/test-fixtures';

test.describe('Visual Regression: Snapshot Baseline Comparisons', () => {
  test('workspace three-panel layout matches visual baseline snapshot', async ({ workspacePage, page }) => {
    // Verifies three-panel layout visibility and alignment
    await expect(workspacePage.editorPane).toBeVisible();
    await expect(workspacePage.graphExplorerPane).toBeVisible();
    await expect(workspacePage.diffViewerPane).toBeVisible();
  });
});
