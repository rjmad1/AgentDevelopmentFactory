import { test, expect } from '@playwright/test';

test.describe('Goal Definition, Document Upload & Deduplicated Rules Engine', () => {
  test('intake view has removed the redundant Step 1 banner', async ({ page }) => {
    await page.goto('/');
    // Verify redundant callout banner is absent in #view-intake
    const redundantCallout = page.locator('#view-intake .md-friendly-callout');
    await expect(redundantCallout).toHaveCount(0);
    // Primary card title remains clear
    const primaryTitle = page.locator('#view-intake .md-card-title');
    await expect(primaryTitle.first()).toContainText('Define Your AI Assistant Goal');
  });

  test('target agent development platform selector functions cleanly', async ({ page }) => {
    await page.goto('/');
    const platformSelect = page.locator('#targetPlatformSelect');
    await expect(platformSelect).toBeVisible();
    await expect(platformSelect).toHaveValue('antigravity');

    const descEl = page.locator('#platformDescriptionText');
    await expect(descEl).toContainText('MCP');

    // Switch to LangGraph
    await platformSelect.selectOption('langgraph');
    await expect(descEl).toContainText('StateGraph');

    // Switch to CrewAI
    await platformSelect.selectOption('crewai');
    await expect(descEl).toContainText('CrewAI');
  });

  test('document upload dropzone attaches files and updates badge and list', async ({ page }) => {
    await page.goto('/');
    const dropzone = page.locator('#docDropzone');
    await expect(dropzone).toBeVisible();

    const fileInput = page.locator('#docFileInput');
    await expect(fileInput).toBeAttached();

    // Upload test document via file input
    await fileInput.setInputFiles({
      name: 'compliance_policies.md',
      mimeType: 'text/markdown',
      buffer: Buffer.from('# Security & Compliance Policies\n1. Zero data exfiltration allowed.\n'),
    });

    // Badge should show 1 document attached
    const docBadge = page.locator('#docCountBadge');
    await expect(docBadge).toContainText('1 Document Attached');

    // Attached docs list should be visible with filename
    const docList = page.locator('#attachedDocsList');
    await expect(docList).toBeVisible();
    await expect(docList).toContainText('compliance_policies.md');

    // Test removing document
    const removeBtn = docList.locator('.md-doc-remove-btn');
    await removeBtn.click();
    await expect(docBadge).toContainText('0 Documents Attached');
  });

  test('AI Assistant Goal blur triggers dynamic rule update without duplicates', async ({ page }) => {
    await page.goto('/');
    const briefInput = page.locator('#briefInput');
    const tbody = page.locator('#requirementsTableBody');

    const initialRowsCount = await tbody.locator('tr').count();
    expect(initialRowsCount).toBeGreaterThan(0);

    // Enter a financial reconciler goal and blur the input
    await briefInput.fill('Build a financial ledger reconciliation agent to verify double spend and balances');
    await briefInput.blur();

    // Verify rows increased
    await expect.poll(async () => await tbody.locator('tr').count()).toBeGreaterThan(initialRowsCount);

    // Verify all rule descriptions are unique (NO DUPLICATES)
    const ruleTexts = await tbody.locator('tr td:nth-child(2)').allTextContents();
    const uniqueTexts = new Set(ruleTexts.map((t) => t.trim().toLowerCase()));
    expect(uniqueTexts.size).toBe(ruleTexts.length);

    // Verify rule IDs are unique
    const ruleIds = await tbody.locator('tr td:nth-child(1) code').allTextContents();
    const uniqueIds = new Set(ruleIds);
    expect(uniqueIds.size).toBe(ruleIds.length);
  });

  test('clicking Generate Rules & Contracts action adds non-duplicate rules', async ({ page }) => {
    await page.goto('/');
    const btnGenerate = page.locator('#btnGenerateMoreRules');
    await expect(btnGenerate).toBeVisible();

    const tbody = page.locator('#requirementsTableBody');
    const initialCount = await tbody.locator('tr').count();

    // Click explicit action
    await btnGenerate.click();

    // Rows count should increase
    const newCount = await tbody.locator('tr').count();
    expect(newCount).toBeGreaterThan(initialCount);

    // Verify zero duplicates
    const ruleTexts = await tbody.locator('tr td:nth-child(2)').allTextContents();
    const uniqueTexts = new Set(ruleTexts.map((t) => t.trim().toLowerCase()));
    expect(uniqueTexts.size).toBe(ruleTexts.length);

    // Clicking again should not create duplicate rules
    await btnGenerate.click();
    const finalRuleTexts = await tbody.locator('tr td:nth-child(2)').allTextContents();
    const finalUniqueTexts = new Set(finalRuleTexts.map((t) => t.trim().toLowerCase()));
    expect(finalUniqueTexts.size).toBe(finalRuleTexts.length);
  });
});
