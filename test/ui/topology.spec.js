import { test, expect } from '@playwright/test';

test('View 2 features interactive Topology Node Inspector', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-patterns"]');

  // Verify Drawer is initially hidden
  const drawer = page.locator('#topologyInspectorDrawer');
  await expect(drawer).toBeHidden();

  // Click on Coordinator Node
  const node = page.locator('#svgNodeCoordinator');
  await expect(node).toBeVisible();
  await node.click();

  // Verify Drawer opens
  await expect(drawer).toBeVisible();
  const title = page.locator('#inspectorNodeTitle');
  await expect(title).toBeVisible();
  const titleText = await title.innerText();
  expect(titleText).toMatch(/Team Lead|Coordinator/i);

  // Close Drawer
  const closeBtn = page.locator('#btnCloseInspector');
  await closeBtn.click();
  await expect(drawer).toBeHidden();
});
