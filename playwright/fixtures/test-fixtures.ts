import { test as base, expect, Page } from '@playwright/test';
import { WorkspacePage } from '../page-objects/workspace.page';
import { GovernancePage } from '../page-objects/governance.page';

type EKOSFixtures = {
  workspacePage: WorkspacePage;
  governancePage: GovernancePage;
  tenantId: string;
};

export const test = base.extend<EKOSFixtures>({
  tenantId: async ({}, use) => {
    await use('tenant_sap_001');
  },
  workspacePage: async ({ page, tenantId }, use) => {
    const workspace = new WorkspacePage(page, tenantId);
    await workspace.goto();
    await use(workspace);
  },
  governancePage: async ({ page, tenantId }, use) => {
    const governance = new GovernancePage(page, tenantId);
    await use(governance);
  }
});

export { expect };
