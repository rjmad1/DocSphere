import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './playwright',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright/reports/html' }],
    ['json', { outputFile: 'playwright/reports/test-results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    extraHTTPHeaders: {
      'X-EKOS-Tenant-ID': 'tenant_sap_001',
      'X-EKOS-Role': 'Steward'
    }
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    }
  ],
  webServer: [
    {
      command: 'npm run dev -- --port 3000',
      cwd: './frontend',
      port: 3000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'python -m uvicorn backend.main:app --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
    }
  ]
});
