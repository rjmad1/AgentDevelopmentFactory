import { test, expect } from '@playwright/test';

test('View 4 features 3 sub-tabs and switches cleanly', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-evals"]');

  // Verify sub-tab bar exists
  const tabList = page.locator('#evalSubTabs');
  await expect(tabList).toBeVisible();

  // Tab 1 (Release Gates) active by default
  await expect(page.locator('#tabBtnReleaseGates')).toHaveClass(/active/);
  await expect(page.locator('#evalTabReleaseGates')).toBeVisible();
  await expect(page.locator('#evalTabRedTeam')).toBeHidden();

  // Switch to Tab 2 (Red Team Anti-Hacking)
  await page.click('#tabBtnRedTeam');
  await expect(page.locator('#evalTabRedTeam')).toBeVisible();
  await expect(page.locator('#evalTabReleaseGates')).toBeHidden();

  // Switch to Tab 3 (Laya RLCD Judge)
  await page.click('#tabBtnLayaJudge');
  await expect(page.locator('#evalTabLayaJudge')).toBeVisible();
  await expect(page.locator('#evalTabRedTeam')).toBeHidden();
});
