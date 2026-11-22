import { test, expect } from '@playwright/test';

test('View 5 features State Drift Reconciler and triggers reconcile', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  // Verify Reconciler Card exists
  const card = page.locator('#syncDriftCard');
  await expect(card).toBeVisible();

  // Verify Button exists
  const btn = page.locator('#btnReconcileState');
  await expect(btn).toBeVisible();

  // Click reconcile button
  await btn.click();

  // Verify status badge confirms synchronization / 0 drift
  const badge = page.locator('#syncStatusBadge');
  await expect(badge).toBeVisible();
  const text = await badge.innerText();
  expect(text).toMatch(/Sync|0 Drift/i);
});
