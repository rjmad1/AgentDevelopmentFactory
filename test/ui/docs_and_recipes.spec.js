import { test, expect } from '@playwright/test';

test.describe('View 6: User Guide & Multi-Industry Agent Library', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('navigates to View 6 via nav rail, header button, and stepper', async ({ page }) => {
    // 1. Via Nav Rail
    const navItem = page.locator('.md-nav-item[data-view="view-docs"]');
    await navItem.click();
    await expect(page.locator('#view-docs')).toBeVisible();
    await expect(navItem).toHaveAttribute('aria-current', 'page');

    // 2. Return to View 1 and test header button
    await page.locator('.md-nav-item[data-view="view-intake"]').click();
    await expect(page.locator('#view-intake')).toBeVisible();

    const headerDocsBtn = page.locator('#btnHeaderDocs');
    await expect(headerDocsBtn).toBeVisible();
    await headerDocsBtn.click();
    await expect(page.locator('#view-docs')).toBeVisible();

    // 3. Return to View 1 and test stepper header
    await page.locator('.md-nav-item[data-view="view-intake"]').click();
    const stepBtn = page.locator('.md-step-item[data-step="view-docs"]');
    await stepBtn.click();
    await expect(page.locator('#view-docs')).toBeVisible();
  });

  test('switches between Platform Guide and Multi-Industry Recipes sub-tabs', async ({ page }) => {
    await page.locator('.md-nav-item[data-view="view-docs"]').click();

    const tabManual = page.locator('#tab-docs-manual');
    const tabRecipes = page.locator('#tab-docs-recipes');
    const btnManual = page.locator('#tabBtnDocsManual');
    const btnRecipes = page.locator('#tabBtnDocsRecipes');

    // Initially Platform Guide is active
    await expect(tabManual).toBeVisible();
    await expect(tabRecipes).toBeHidden();
    await expect(btnManual).toHaveAttribute('aria-selected', 'true');

    // Switch to Recipes
    await btnRecipes.click();
    await expect(tabRecipes).toBeVisible();
    await expect(tabManual).toBeHidden();
    await expect(btnRecipes).toHaveAttribute('aria-selected', 'true');

    // Switch back to Manual
    await btnManual.click();
    await expect(tabManual).toBeVisible();
    await expect(tabRecipes).toBeHidden();
  });

  test('filters recipe cards by industry filter pills', async ({ page }) => {
    await page.locator('.md-nav-item[data-view="view-docs"]').click();
    await page.locator('#tabBtnDocsRecipes').click();

    const allCards = page.locator('.adf-recipe-card');
    await expect(allCards).toHaveCount(6);

    // Filter by Financial Services
    await page.locator('[data-industry-filter="finance"]').click();
    await expect(page.locator('.adf-recipe-card[data-industry="finance"]')).toBeVisible();
    await expect(page.locator('.adf-recipe-card[data-industry="healthcare"]')).toBeHidden();

    // Filter by Healthcare
    await page.locator('[data-industry-filter="healthcare"]').click();
    await expect(page.locator('.adf-recipe-card[data-industry="healthcare"]')).toBeVisible();
    await expect(page.locator('.adf-recipe-card[data-industry="finance"]')).toBeHidden();

    // Reset to All
    await page.locator('[data-industry-filter="all"]').click();
    for (let i = 0; i < 6; i++) {
      await expect(allCards.nth(i)).toBeVisible();
    }
  });

  test('loads an industry blueprint directly into Factory Intake (View 1)', async ({ page }) => {
    await page.locator('.md-nav-item[data-view="view-docs"]').click();
    await page.locator('#tabBtnDocsRecipes').click();

    // Click "Load Blueprint into Factory" for AML Financial Agent
    const finLoadBtn = page.locator('.btn-load-recipe[data-recipe="fin"]');
    await expect(finLoadBtn).toBeVisible();
    await finLoadBtn.click();

    // Should navigate automatically to View 1
    await expect(page.locator('#view-intake')).toBeVisible();

    // Goal brief input should be populated with financial brief
    const briefInput = page.locator('#briefInput');
    const briefVal = await briefInput.inputValue();
    expect(briefVal).toContain('AML (Anti-Money Laundering)');

    // Target platform should be set to langgraph
    const platformSelect = page.locator('#targetPlatformSelect');
    await expect(platformSelect).toHaveValue('langgraph');

    // Requirements table should be populated
    const rows = page.locator('#requirementsTableBody tr');
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(4);

    // Check that snackbar confirmed the load
    const snackbar = page.locator('#appSnackbar');
    await expect(snackbar).toHaveClass(/show/);
    await expect(snackbar).toContainText('AML Transaction & Fraud Reconciliation Agent');
  });
});
