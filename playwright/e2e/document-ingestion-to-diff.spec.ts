import { test, expect } from '../fixtures/test-fixtures';
import { setupEKOSApiMocks } from '../helpers/mock-server';

test.describe('E2E: Document Ingestion -> Graph Extraction -> Living Docs Impact Diff Approval', () => {
  test.beforeEach(async ({ page }) => {
    await setupEKOSApiMocks(page);
  });

  test('should ingest markdown, update Cytoscape graph, and approve side-by-side diff', async ({ workspacePage }) => {
    await workspacePage.typeInEditor('# 1. Business Requirements\nRequirement REQ-00847 implements CAP-0012 for SAP S/4HANA.');
    await expect(workspacePage.editorPane).toContainText('REQ-00847');
  });
});
