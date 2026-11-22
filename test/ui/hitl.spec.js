import { test, expect } from '@playwright/test';

test('View 4 features Contextual HITL Signoff Modal', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-evals"]');

  const modal = page.locator('#hitlModal');
  await expect(modal).toBeHidden();

  // Click on Gate 8 Box
  const gate8 = page.locator('#gateBox8');
  await expect(gate8).toBeVisible();
  await gate8.click();

  // Verify modal is open and contextual summary is visible
  await expect(modal).toBeVisible();
  const summary = page.locator('#hitlAgentSummary');
  await expect(summary).toBeVisible();
  const text = await summary.innerText();
  expect(text).toMatch(/Agent|Tier/i);

  // Cancel and verify modal closes
  await page.click('#btnCancelHitl');
  await expect(modal).toBeHidden();
});
