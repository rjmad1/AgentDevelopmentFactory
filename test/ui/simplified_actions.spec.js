import { test, expect } from '@playwright/test';

test.describe('1-Primary-Action Workflow Simplification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Step 1: Single primary action analyzes goal, confirms budget, and scaffolds rules in one shot', async ({ page }) => {
    const briefInput = page.locator('#briefInput');
    await briefInput.fill('Build an automated anomaly detection agent for customer CSV datasets with zero API costs');

    const primaryActionBtn = page.locator('#btnRunTriage');
    await expect(primaryActionBtn).toBeVisible();
    await expect(primaryActionBtn).toHaveText(/Analyze & Prepare Assistant/i);

    // Click primary action
    await primaryActionBtn.click();

    // Verify complexity card and budget are revealed
    const triageContainer = page.locator('#triageOutputContainer');
    await expect(triageContainer).toBeVisible();

    const budgetChip = page.locator('#tokenBudgetChip');
    await expect(budgetChip).toContainText('Within Free Budget');

    // Verify requirements table is populated with contracts
    const rows = page.locator('#requirementsTableBody tr');
    await expect.poll(async () => await rows.count()).toBeGreaterThan(0);
  });

  test('Step 4: Unified pre-flight verification runs gates, red team, and judge in one click', async ({ page }) => {
    await page.locator('.md-nav-item[data-view="view-evals"]').click();

    const verifyBtn = page.locator('#btnRunFullVerification');
    await expect(verifyBtn).toBeVisible();
    await expect(verifyBtn).toHaveText(/Run Complete Pre-Flight Verification/i);

    // Click unified verification
    await verifyBtn.click();

    // Verify button transforms to signoff action once complete
    await expect(verifyBtn).toHaveText(/Personal Approval Signoff/i);

    // Clicking it opens the human approval modal
    await verifyBtn.click();
    await expect(page.locator('#hitlModal')).toHaveClass(/open/);
  });

  test('Step 5: Unified diagnostics refresh updates live telemetry in one click', async ({ page }) => {
    await page.locator('.md-nav-item[data-view="view-ops"]').click();

    const refreshAllBtn = page.locator('#btnRefreshAllDiagnostics');
    await expect(refreshAllBtn).toBeVisible();

    await refreshAllBtn.click();

    // Verify snackbar confirmed refresh
    const snackbar = page.locator('#appSnackbar');
    await expect(snackbar).toHaveClass(/show/);
    await expect(snackbar).toContainText('All live diagnostics and telemetry refreshed');
  });
});
