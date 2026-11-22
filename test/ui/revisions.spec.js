import { test, expect } from '@playwright/test';

test('View 5 features Historical Revisions Browser', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  // Verify Revisions Card exists
  const card = page.locator('#revisionsHistoryCard');
  await expect(card).toBeVisible();

  // Verify List exists
  const list = page.locator('#revisionsList');
  await expect(list).toBeVisible();

  // Click refresh button
  const btn = page.locator('#btnRefreshRevisions');
  await expect(btn).toBeVisible();
  await btn.click();

  // Assert revisions list has rendered content
  await expect(list).not.toBeEmpty();
});
