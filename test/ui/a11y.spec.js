import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const VIEWS = ['view-intake', 'view-patterns', 'view-guardrails', 'view-evals', 'view-ops'];

async function scan(page) {
  return new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
}

for (const theme of ['light', 'dark']) {
  test(`axe finds no violations in ${theme} theme`, async ({ page }) => {
    await page.goto('/');
    await page.evaluate((t) => document.documentElement.setAttribute('data-theme', t), theme);
    for (const view of VIEWS) {
      await page.locator(`.md-nav-item[data-view="${view}"]`).click();
      const results = await scan(page);
      // Compare ids, not the whole violation objects: a dump is unreadable.
      const ids = results.violations.map(
        (v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(' | ')}`
      );
      expect(ids, `${view} / ${theme}`).toEqual([]);
    }
  });
}

test('axe finds no violations at compact width', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto('/');
  const results = await scan(page);
  expect(results.violations.map((v) => `${v.id} x${v.nodes.length}`)).toEqual([]);
});

test('skip link is the first tab stop and moves focus to main', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  const skip = page.locator('.md-skip-link');
  await expect(skip).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#mainContent')).toBeFocused();
});

test('editorial design tokens are defined on root', async ({ page }) => {
  await page.goto('/');
  const surfaceColor = await page.evaluate(() => {
    return getComputedStyle(document.documentElement).getPropertyValue('--adf-color-canvas').trim();
  });
  expect(surfaceColor).toBe('#fbfbfa');
});
