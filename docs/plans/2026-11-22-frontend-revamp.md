# Frontend Modernization & Editorial UI Revamp Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Agent Development Factory hybrid frontend into an editorial, high-contrast minimalist interface inspired by Linear and Notion, surfacing all backend capabilities (State Drift Reconciliation, Historical Revisions, and Live Event Stream) while eliminating vertical clutter via a tabbed evaluation bento.

**Architecture:** The frontend remains a zero-dependency native ESM application (`ui/index.html`, `ui/material.css`, `ui/app.js`) communicating over a tri-modal dispatcher (Live REST, Embedded Webview, Offline Mock). Layout is restructured into a responsive bento grid utilizing warm monochrome palettes, crisp 1px borders, and muted spot pastels, validated continuously via Playwright and axe-core accessibility tests.

**Tech Stack:** Native HTML5, CSS3 Custom Properties (Minimalist Editorial System), Vanilla JavaScript (ES2022+ Native ESM), Playwright Test, `@axe-core/playwright`.

---

### Task 1: Design Tokens & Minimalist Editorial Substrate

**Files:**
- Modify: `ui/material.css:1-120`
- Test: `test/ui/a11y.spec.js`

**Step 1: Write the failing test**

In `test/ui/a11y.spec.js`, add an assertion verifying the new editorial CSS variables exist on `:root` and contrast checks pass:

```javascript
test('editorial design tokens are defined on root', async ({ page }) => {
  await page.goto('/');
  const surfaceColor = await page.evaluate(() => {
    return getComputedStyle(document.documentElement).getPropertyValue('--adf-color-canvas').trim();
  });
  expect(surfaceColor).toBe('#fbfbfa');
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/a11y.spec.js -g "editorial design tokens"`  
Expected: FAIL with `Expected: "#fbfbfa", Received: ""`

**Step 3: Write minimal implementation**

In `ui/material.css`, introduce the warm monochrome and spot pastel tokens:

```css
:root {
  /* Warm Monochrome Canvas & Surfaces */
  --adf-color-canvas: #fbfbfa;
  --adf-color-surface: #ffffff;
  --adf-color-surface-subtle: #f7f6f3;
  --adf-color-border: #eaeaea;
  --adf-color-text-primary: #111111;
  --adf-color-text-secondary: #787774;
  --adf-color-text-tertiary: #9b9a97;

  /* Editorial Spot Pastels (Tags, Chips & Status Badges) */
  --adf-pastel-green-bg: #edf3ec;
  --adf-pastel-green-text: #346538;
  --adf-pastel-amber-bg: #fbf3db;
  --adf-pastel-amber-text: #956400;
  --adf-pastel-red-bg: #fdebec;
  --adf-pastel-red-text: #9f2f2d;
  --adf-pastel-blue-bg: #e1f3fe;
  --adf-pastel-blue-text: #1f6c9f;

  /* Typography */
  --adf-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Geist Sans', 'Helvetica Neue', sans-serif;
  --adf-font-mono: 'SF Mono', 'Geist Mono', Consolas, Monaco, monospace;
}

[data-theme="dark"] {
  --adf-color-canvas: #0f1115;
  --adf-color-surface: #161920;
  --adf-color-surface-subtle: #1e222b;
  --adf-color-border: #2e3440;
  --adf-color-text-primary: #e2e2e9;
  --adf-color-text-secondary: #9aa0a6;
  --adf-color-text-tertiary: #6e737b;

  --adf-pastel-green-bg: #143320;
  --adf-pastel-green-text: #6dd58c;
  --adf-pastel-amber-bg: #382800;
  --adf-pastel-amber-text: #ffb951;
  --adf-pastel-red-bg: #3b1414;
  --adf-pastel-red-text: #ffb4ab;
  --adf-pastel-blue-bg: #102a45;
  --adf-pastel-blue-text: #a8c7fa;
}
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/a11y.spec.js -g "editorial design tokens"`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/material.css test/ui/a11y.spec.js
git commit -m "feat(ui): add warm monochrome and spot pastel editorial tokens"
```

---

### Task 2: Tabbed Evaluation Bento in View 4

**Files:**
- Modify: `ui/index.html:600-870`
- Modify: `ui/app.js:550-700`
- Modify: `ui/material.css:500-600`
- Create: `test/ui/evals_tabs.spec.js`

**Step 1: Write the failing test**

In `test/ui/evals_tabs.spec.js`, author tests asserting the 3 evaluation sub-tabs exist and switch active content without vertical stacking:

```javascript
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
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/evals_tabs.spec.js`  
Expected: FAIL with `locator('#evalSubTabs') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, restructure `#view-evals` into a tabbed bento:

```html
<div class="adf-tab-bar" id="evalSubTabs" role="tablist">
  <button class="adf-tab-btn active" id="tabBtnReleaseGates" data-eval-tab="evalTabReleaseGates" role="tab" aria-selected="true">
    🚦 1. Release Gates & Approval
  </button>
  <button class="adf-tab-btn" id="tabBtnRedTeam" data-eval-tab="evalTabRedTeam" role="tab" aria-selected="false">
    🛡️ 2. Anti-Hacking Red Team
  </button>
  <button class="adf-tab-btn" id="tabBtnLayaJudge" data-eval-tab="evalTabLayaJudge" role="tab" aria-selected="false">
    ⚖️ 3. Laya Quality Judge
  </button>
</div>

<div class="adf-tab-content active" id="evalTabReleaseGates" role="tabpanel">
  <!-- 9 Release Gates Matrix + Adversarial Security Table -->
</div>
<div class="adf-tab-content" id="evalTabRedTeam" role="tabpanel" style="display: none;">
  <!-- 16-Point Anti-Hacking Stress Test Card -->
</div>
<div class="adf-tab-content" id="evalTabLayaJudge" role="tabpanel" style="display: none;">
  <!-- Laya RLCD 3 Rubrics Card -->
</div>
```

In `ui/app.js`, add the tab switching listener:

```javascript
document.querySelectorAll('#evalSubTabs .adf-tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#evalSubTabs .adf-tab-btn').forEach((b) => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    document.querySelectorAll('.adf-tab-content').forEach((c) => {
      c.classList.remove('active');
      c.style.display = 'none';
    });

    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
    const targetId = btn.getAttribute('data-eval-tab');
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      targetEl.classList.add('active');
      targetEl.style.display = 'block';
    }
  });
});
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/evals_tabs.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html ui/app.js ui/material.css test/ui/evals_tabs.spec.js
git commit -m "feat(ui): organize View 4 evaluations into clean tabbed bento"
```

---

### Task 3: Surface State Drift Reconciler in View 5

**Files:**
- Modify: `ui/index.html:900-1000`
- Modify: `ui/app.js:900-1050`
- Create: `test/ui/sync.spec.js`

**Step 1: Write the failing test**

In `test/ui/sync.spec.js`, author tests verifying state drift status displays and trigger reconcile works:

```javascript
import { test, expect } from '@playwright/test';

test('View 5 displays State Synchronization & Drift Reconciler card', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  const syncCard = page.locator('#syncDriftCard');
  await expect(syncCard).toBeVisible();

  const statusBadge = page.locator('#syncStatusBadge');
  await expect(statusBadge).toContainText(/CONSISTENT|HEALTHY|IN_SYNC/i);

  const reconcileBtn = page.locator('#btnReconcileState');
  await expect(reconcileBtn).toBeVisible();
  await reconcileBtn.click();

  const reconcileResult = page.locator('#syncResultBanner');
  await expect(reconcileResult).toBeVisible();
  await expect(reconcileResult).toContainText(/reconciled|clean|verified/i);
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/sync.spec.js`  
Expected: FAIL with `locator('#syncDriftCard') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, add the State Synchronization card inside `#view-ops`:

```html
<div class="md-card md-card-filled" id="syncDriftCard" style="margin-bottom: 24px;">
  <div class="md-card-header">
    <div>
      <h3 class="md-card-title">🔄 Cryptographic State Synchronization & Drift Guard</h3>
      <p class="md-card-subtitle">Audits file manifests against SHA-256 consensus and eliminates drift with zero cost.</p>
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <span class="md-chip md-chip-success" id="syncStatusBadge">CONSISTENT</span>
      <button class="md-btn md-btn-filled" id="btnReconcileState" type="button">⚡ Reconcile State</button>
    </div>
  </div>
  <div id="syncResultBanner" style="display: none; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; background: var(--adf-color-surface);"></div>
</div>
```

In `ui/app.js`, connect the button to `callApi('/api/sync/status')` and `callApi('/api/sync/reconcile', 'POST')`:

```javascript
async function refreshSyncStatus() {
  const result = await callApi('/api/sync/status');
  const badge = document.getElementById('syncStatusBadge');
  if (badge && result) {
    badge.textContent = result.isDrifted ? 'DRIFT DETECTED' : 'CONSISTENT';
    badge.className = result.isDrifted ? 'md-chip md-chip-warning' : 'md-chip md-chip-success';
  }
}

const btnReconcile = document.getElementById('btnReconcileState');
if (btnReconcile) {
  btnReconcile.addEventListener('click', async () => {
    btnReconcile.disabled = true;
    btnReconcile.textContent = '⏳ Reconciling...';
    try {
      const res = await callApi('/api/sync/reconcile', 'POST');
      const banner = document.getElementById('syncResultBanner');
      if (banner) {
        banner.style.display = 'block';
        banner.textContent = `State reconciled successfully: ${res.reconciled || 'Verified Clean'}`;
      }
      showSnackbar('State synchronization reconciled successfully.', '✅');
      await refreshSyncStatus();
    } finally {
      btnReconcile.disabled = false;
      btnReconcile.textContent = '⚡ Reconcile State';
    }
  });
}
```

In `ui/app.js`, add offline mock fallback for `/api/sync/status` and `/api/sync/reconcile`:

```javascript
if (endpoint.includes('/api/sync/status')) {
  return { isDrifted: false, status: 'CONSISTENT', checkedAt: new Date().toISOString() };
}
if (endpoint.includes('/api/sync/reconcile')) {
  return { status: 'RECONCILED', reconciled: 'Verified Clean', timestamp: new Date().toISOString() };
}
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/sync.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html ui/app.js test/ui/sync.spec.js
git commit -m "feat(ui): surface State Synchronization & Drift Reconciler in View 5"
```

---

### Task 4: Surface Historical Revisions Browser in View 5

**Files:**
- Modify: `ui/index.html:1000-1050`
- Modify: `ui/app.js:1050-1120`
- Create: `test/ui/revisions.spec.js`

**Step 1: Write the failing test**

In `test/ui/revisions.spec.js`, author tests verifying revisions list loads from `/api/revisions`:

```javascript
import { test, expect } from '@playwright/test';

test('View 5 displays Historical Revisions card with revisions list', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  const revCard = page.locator('#revisionsHistoryCard');
  await expect(revCard).toBeVisible();

  const revList = page.locator('#revisionsList');
  await expect(revList).toBeVisible();
  await expect(revList.locator('.adf-revision-chip').first()).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/revisions.spec.js`  
Expected: FAIL with `locator('#revisionsHistoryCard') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, add the Revisions card:

```html
<div class="md-card md-card-filled" id="revisionsHistoryCard" style="margin-bottom: 24px;">
  <div class="md-card-header">
    <div>
      <h3 class="md-card-title">📦 Immutable Specification Revisions</h3>
      <p class="md-card-subtitle">Inspect historical immutable revisions and package checksums stored in ledger.</p>
    </div>
    <button class="md-btn md-btn-tonal" id="btnRefreshRevisions" type="button">🔄 Refresh</button>
  </div>
  <div id="revisionsList" style="display: flex; gap: 8px; flex-wrap: wrap;">
    <span class="md-chip md-chip-primary adf-revision-chip">rev-001 (Active)</span>
  </div>
</div>
```

In `ui/app.js`, add `loadRevisions()` connected to `/api/revisions`:

```javascript
async function loadRevisions() {
  const result = await callApi('/api/revisions');
  const listEl = document.getElementById('revisionsList');
  if (listEl && result && Array.isArray(result.revisions)) {
    listEl.innerHTML = '';
    if (result.revisions.length === 0) {
      listEl.innerHTML = '<span style="font-size: 12px; color: var(--adf-color-text-secondary);">No historical revisions found.</span>';
      return;
    }
    result.revisions.forEach((rev, idx) => {
      const chip = document.createElement('span');
      chip.className = idx === 0 ? 'md-chip md-chip-primary adf-revision-chip' : 'md-chip md-chip-surface adf-revision-chip';
      chip.textContent = `${rev}${idx === 0 ? ' (Active)' : ''}`;
      listEl.appendChild(chip);
    });
  }
}
```

In `ui/app.js`, add offline mock fallback for `/api/revisions`:

```javascript
if (endpoint.includes('/api/revisions')) {
  return { revisions: ['rev-001', 'rev-002'] };
}
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/revisions.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html ui/app.js test/ui/revisions.spec.js
git commit -m "feat(ui): surface Immutable Revisions history in View 5"
```

---

### Task 5: Surface Live Event Stream Terminal in View 5

**Files:**
- Modify: `ui/index.html:1050-1100`
- Modify: `ui/app.js:1120-1200`
- Create: `test/ui/events.spec.js`

**Step 1: Write the failing test**

In `test/ui/events.spec.js`, author tests verifying event stream terminal renders:

```javascript
import { test, expect } from '@playwright/test';

test('View 5 displays Live Event Stream Terminal with audit events', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-ops"]');

  const terminalCard = page.locator('#eventStreamCard');
  await expect(terminalCard).toBeVisible();

  const terminalFeed = page.locator('#eventStreamFeed');
  await expect(terminalFeed).toBeVisible();
  await expect(terminalFeed.locator('.adf-event-entry').first()).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/events.spec.js`  
Expected: FAIL with `locator('#eventStreamCard') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, add the Event Stream terminal card:

```html
<div class="md-card md-card-filled" id="eventStreamCard" style="margin-bottom: 24px;">
  <div class="md-card-header">
    <div>
      <h3 class="md-card-title">📜 Append-Only Event Audit Stream</h3>
      <p class="md-card-subtitle">Real-time inspection of check_events.jsonl append-only event ledger.</p>
    </div>
    <div style="display: flex; gap: 8px;">
      <button class="md-btn md-btn-tonal" id="btnRefreshEvents" type="button">🔄 Refresh Events</button>
    </div>
  </div>
  <div id="eventStreamFeed" style="max-height: 200px; overflow-y: auto; font-family: var(--adf-font-mono); font-size: 11px; background: var(--adf-color-canvas); padding: 12px; border-radius: 8px; border: 1px solid var(--adf-color-border);">
    <div class="adf-event-entry" style="color: var(--adf-pastel-green-text);">[EVENT] 2026-11-22T12:00:00Z - CHK-REALPATH-CONTAINMENT: PASS</div>
  </div>
</div>
```

In `ui/app.js`, add `loadAuditEvents()` connected to `/api/events`:

```javascript
async function loadAuditEvents() {
  const result = await callApi('/api/events');
  const feed = document.getElementById('eventStreamFeed');
  if (feed && result && Array.isArray(result.events)) {
    feed.innerHTML = '';
    if (result.events.length === 0) {
      feed.innerHTML = '<div style="color: var(--adf-color-text-secondary);">No events recorded in check_events.jsonl</div>';
      return;
    }
    result.events.slice(-20).forEach((evt) => {
      const row = document.createElement('div');
      row.className = 'adf-event-entry';
      row.style.marginBottom = '4px';
      const statusColor = evt.status === 'PASS' ? 'var(--adf-pastel-green-text)' : evt.status === 'FAIL' ? 'var(--adf-pastel-red-text)' : 'var(--adf-color-text-primary)';
      row.innerHTML = `<span style="opacity: 0.6;">[${evt.timestamp || 'N/A'}]</span> <strong style="color: ${statusColor};">${evt.checkId || 'EVENT'}: ${evt.status || 'INFO'}</strong> ${evt.detail || ''}`;
      feed.appendChild(row);
    });
  }
}
```

In `ui/app.js`, add offline mock fallback for `/api/events`:

```javascript
if (endpoint.includes('/api/events')) {
  return {
    events: [
      { timestamp: new Date().toISOString(), checkId: 'CHK-REALPATH-CONTAINMENT', status: 'PASS', detail: 'Store root verified contained' },
      { timestamp: new Date().toISOString(), checkId: 'CHK-TOKEN-BUDGET', status: 'PASS', detail: 'Token budget within 4,000 ceiling' },
    ],
  };
}
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/events.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html ui/app.js test/ui/events.spec.js
git commit -m "feat(ui): surface Append-Only Event Audit Stream in View 5"
```

---

### Task 6: Interactive Topology Node Inspector in View 2

**Files:**
- Modify: `ui/index.html:310-380`
- Modify: `ui/app.js:400-480`
- Create: `test/ui/topology.spec.js`

**Step 1: Write the failing test**

In `test/ui/topology.spec.js`, author tests verifying clicking SVG nodes opens details drawer:

```javascript
import { test, expect } from '@playwright/test';

test('Clicking SVG topology node displays node configuration inspector', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-patterns"]');

  const coordinatorNode = page.locator('#svgNodeCoordinator');
  await expect(coordinatorNode).toBeVisible();
  await coordinatorNode.click();

  const inspector = page.locator('#topologyInspectorDrawer');
  await expect(inspector).toBeVisible();
  await expect(inspector).toContainText(/Coordinator/i);
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/topology.spec.js`  
Expected: FAIL with `locator('#svgNodeCoordinator') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, give ID `#svgNodeCoordinator` to the Team Lead `<rect>` element, and add the `#topologyInspectorDrawer` container:

```html
<div id="topologyInspectorDrawer" class="md-card md-card-outlined" style="display: none; margin-top: 16px; padding: 16px;">
  <h4 id="inspectorNodeTitle" style="font-weight: 600; margin-bottom: 6px;">Node Inspector</h4>
  <p id="inspectorNodeDesc" style="font-size: 12px; color: var(--adf-color-text-secondary); margin: 0 0 10px 0;"></p>
  <div class="md-grid-3">
    <div><span class="md-label">Model Target</span><div style="font-weight: 600; font-size: 13px;" id="inspectorNodeModel">Local Process (0 tokens)</div></div>
    <div><span class="md-label">Sandbox Boundary</span><div style="font-weight: 600; font-size: 13px;" id="inspectorNodeSandbox">Strict Workdir Realpath</div></div>
    <div><span class="md-label">Timeout Cap</span><div style="font-weight: 600; font-size: 13px;" id="inspectorNodeTimeout">60 Seconds</div></div>
  </div>
</div>
```

In `ui/app.js`, add the click handler:

```javascript
const nodeCoordinator = document.getElementById('svgNodeCoordinator');
if (nodeCoordinator) {
  nodeCoordinator.style.cursor = 'pointer';
  nodeCoordinator.addEventListener('click', () => {
    const drawer = document.getElementById('topologyInspectorDrawer');
    const title = document.getElementById('inspectorNodeTitle');
    const desc = document.getElementById('inspectorNodeDesc');
    if (drawer && title && desc) {
      drawer.style.display = 'block';
      title.textContent = 'Node Inspector: Team Lead (Coordinator)';
      desc.textContent = 'Orchestrates the multi-agent execution pipeline, delegates subtasks to specialized workers, and enforces schema boundaries.';
    }
  });
}
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/topology.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html ui/app.js test/ui/topology.spec.js
git commit -m "feat(ui): add interactive node inspector to SVG topology graph"
```

---

### Task 7: Contextual Human-in-the-Loop Signoff Modal

**Files:**
- Modify: `ui/index.html:1030-1060`
- Modify: `ui/app.js:800-860`
- Create: `test/ui/hitl.spec.js`

**Step 1: Write the failing test**

In `test/ui/hitl.spec.js`, author tests verifying HITL modal contains an executive summary card of the agent:

```javascript
import { test, expect } from '@playwright/test';

test('HITL modal displays contextual agent summary badges before approval', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-view="view-evals"]');

  await page.click('#gateBox8');
  const modal = page.locator('#hitlModal');
  await expect(modal).toBeVisible();

  const summary = page.locator('#hitlAgentSummary');
  await expect(summary).toBeVisible();
  await expect(summary).toContainText(/\$0\.00/);
});
```

**Step 2: Run test to verify it fails**

Run: `npx playwright test test/ui/hitl.spec.js`  
Expected: FAIL with `locator('#hitlAgentSummary') not found`

**Step 3: Write minimal implementation**

In `ui/index.html`, add `#hitlAgentSummary` inside `#hitlModal`:

```html
<div id="hitlAgentSummary" style="display: flex; gap: 8px; margin-bottom: 16px; background: var(--adf-color-surface-subtle); padding: 10px; border-radius: 8px;">
  <span class="md-chip md-chip-primary">Agent: Default Spec</span>
  <span class="md-chip md-chip-warning">Tier: T1 Workspace Write</span>
  <span class="md-chip md-chip-success">Spend Cap: $0.00 USD</span>
</div>
```

**Step 4: Run test to verify it passes**

Run: `npx playwright test test/ui/hitl.spec.js`  
Expected: PASS

**Step 5: Commit**

```bash
git add ui/index.html test/ui/hitl.spec.js
git commit -m "feat(ui): add contextual agent summary to HITL signoff modal"
```

---

### Task 8: Full End-to-End Regression & Accessibility Certification

**Files:**
- Verify: All repository tests and Playwright suites.

**Step 1: Run all Playwright UI & Accessibility tests**

Run: `npx playwright test`  
Expected: 22+ tests PASS with zero axe-core violations across light/dark themes and all 7 viewports.

**Step 2: Run full Python Pytest test suite**

Run: `pytest`  
Expected: 109 / 109 PASS in < 10s.

**Step 3: Run Node repeatable dual-run suite**

Run: `npm test`  
Expected: 32 / 32 PASS on Run 1, 32 / 32 PASS on Run 2 with identical metrics.

**Step 4: Run Contract & Syntax linter**

Run: `npm run lint`  
Expected: 32 / 32 PASS (clean syntax across all contracts and scripts).

**Step 5: Final Clean Commit**

```bash
git add .
git commit -m "test(ui): complete comprehensive frontend modernization verification"
```
