import { test, expect } from '@playwright/test';

const VIEWPORTS = [
  { name: 'phone-portrait', width: 360, height: 740 },
  { name: 'phone-large', width: 414, height: 896 },
  { name: 'phone-landscape', width: 740, height: 360 },
  { name: 'tablet-portrait', width: 768, height: 1024 },
  { name: 'tablet-landscape', width: 1024, height: 768 },
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'desktop-xl', width: 1920, height: 1080 },
];

const VIEWS = ['view-intake', 'view-patterns', 'view-guardrails', 'view-evals', 'view-ops', 'view-docs'];

for (const vp of VIEWPORTS) {
  test(`no horizontal overflow at ${vp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto('/');
    for (const view of VIEWS) {
      await page.locator(`.md-nav-item[data-view="${view}"]`).click();
      const over = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth
      );
      expect(over, `${view} overflows horizontally`).toBeLessThanOrEqual(1);
    }
  });
}

test('every nav destination shows its view and marks itself current', async ({ page }) => {
  await page.goto('/');
  for (const view of VIEWS) {
    const item = page.locator(`.md-nav-item[data-view="${view}"]`);
    await item.click();
    await expect(page.locator(`#${view}`)).toBeVisible();
    await expect(item).toHaveAttribute('aria-current', 'page');
  }
});

test('touch targets in the nav are at least 44px tall at compact', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto('/');
  const items = page.locator('.md-nav-item');
  const count = await items.count();
  expect(count).toBeGreaterThan(0);
  for (let i = 0; i < count; i += 1) {
    const box = await items.nth(i).boundingBox();
    expect(box.height).toBeGreaterThanOrEqual(44);
  }
});

test('dark theme keeps the layout intact', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(bg).not.toBe('rgba(0, 0, 0, 0)');
  const over = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth
  );
  expect(over).toBeLessThanOrEqual(1);
});
