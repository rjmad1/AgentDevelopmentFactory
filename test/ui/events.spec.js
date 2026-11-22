import { test, expect } from '@playwright/test';

test('View 5 features Live Event Stream Terminal', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  // Verify Event Stream Card exists
  const card = page.locator('#eventStreamCard');
  await expect(card).toBeVisible();

  // Verify Feed exists
  const feed = page.locator('#eventStreamFeed');
  await expect(feed).toBeVisible();

  // Click refresh button
  const btn = page.locator('#btnRefreshEvents');
  await expect(btn).toBeVisible();
  await btn.click();

  // Assert feed has rendered content
  await expect(feed).not.toBeEmpty();
});
