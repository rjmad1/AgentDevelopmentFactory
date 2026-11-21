import { test, expect } from '@playwright/test';

test('nothing is reported as measured before anything runs', async ({ page }) => {
  await page.goto('/');
  // Release gates must not claim PASS until the backend has answered.
  const labels = await page.locator('#releaseGatesGrid .md-gate-box .md-chip').allTextContents();
  expect(labels.length).toBeGreaterThan(0);
  for (const label of labels) {
    expect(label).not.toMatch(/PASS|FAIL/i);
  }
  for (const id of ['rtTotalProbes', 'rtBlockRate', 'scaleWorkers', 'scaleQueue', 'scaleUtilization']) {
    await expect(page.locator(`#${id}`)).toHaveText('—');
  }
  await expect(page.locator('#rtVerdict')).toHaveText('Not run');
});

test('with the backend down the UI says so instead of inventing health', async ({ page }) => {
  await page.route('**/api/**', (route) => route.abort('failed'));
  await page.goto('/');
  await expect(page.locator('#clientModeText')).toContainText(/unreachable|offline|error/i);
  await expect(page.locator('#doctorHealthText')).toHaveText('Health: not checked');
});

test('a failing endpoint renders an error state with a retry', async ({ page }) => {
  await page.route('**/api/traces', (route) => route.abort('failed'));
  await page.goto('/');
  await page.locator('.md-nav-item[data-view="view-ops"]').click();
  const block = page.locator('#traceSpanHierarchyContainer .md-state-error');
  await expect(block).toBeVisible();
  await expect(block.getByRole('button')).toBeVisible();
});
