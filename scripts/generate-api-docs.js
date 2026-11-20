import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

console.log('=== [DOCS-GEN] Generating API & Module Docs from Source Code ===');

const corePath = path.join(projectRoot, 'src', 'core.js');
const coreSource = fs.readFileSync(corePath, 'utf-8');

const apiDocsDir = path.join(projectRoot, 'docs', 'api');
if (!fs.existsSync(apiDocsDir)) {
  fs.mkdirSync(apiDocsDir, { recursive: true });
}

// Extract JSDocs and function signatures
const functionRegex = /(?:\/\*\*([\s\S]*?)\*\/\s*)?export\s+function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)/g;
const functions = [];
let match;

while ((match = functionRegex.exec(coreSource)) !== null) {
  const rawJsDoc = match[1] || '';
  const fnName = match[2];
  const params = match[3].trim().replace(/\s+/g, ' ');

  // Parse JSDoc lines
  const lines = rawJsDoc.split('\n').map(l => l.replace(/^\s*\*\s?/, '').trim()).filter(Boolean);
  const descriptionLines = [];
  const paramDocs = [];
  let returnDoc = '';
  const throwsDocs = [];

  for (const line of lines) {
    if (line.startsWith('@param')) {
      paramDocs.push(line.replace('@param', '').trim());
    } else if (line.startsWith('@returns') || line.startsWith('@return')) {
      returnDoc = line.replace(/@returns?/, '').trim();
    } else if (line.startsWith('@throws') || line.startsWith('@throw')) {
      throwsDocs.push(line.replace(/@throws?/, '').trim());
    } else if (!line.startsWith('@')) {
      descriptionLines.push(line);
    }
  }

  functions.push({
    name: fnName,
    signature: `function ${fnName}(${params})`,
    description: descriptionLines.join(' ') || `Domain function: \`${fnName}\`.`,
    params: paramDocs,
    returns: returnDoc,
    throws: throwsDocs
  });
}

// Generate docs/api/core.md
let coreMd = `# Core API Reference (\`src/core.js\`)

The \`core.js\` module provides the foundational deterministic engine for the Agent Development Factory. It handles revision lifecycle, state immutability, cryptographic hashing, real filesystem containment, and append-only evidence auditing.

---

## Exported Functions Summary

| Function | Signature | Description |
| :--- | :--- | :--- |
`;

for (const fn of functions) {
  coreMd += `| [\`${fn.name}\`](#${fn.name.toLowerCase()}) | \`${fn.signature}\` | ${fn.description.slice(0, 80)}${fn.description.length > 80 ? '...' : ''} |\n`;
}

coreMd += `\n---\n\n## Function Details\n\n`;

for (const fn of functions) {
  coreMd += `### \`${fn.name}\`\n\n`;
  coreMd += `\`\`\`javascript\n${fn.signature}\n\`\`\`\n\n`;
  coreMd += `${fn.description}\n\n`;

  if (fn.params.length > 0) {
    coreMd += `**Parameters:**\n\n`;
    for (const p of fn.params) {
      coreMd += `* \`${p}\`\n`;
    }
    coreMd += `\n`;
  }

  if (fn.returns) {
    coreMd += `**Returns:** \`${fn.returns}\`\n\n`;
  }

  if (fn.throws.length > 0) {
    coreMd += `**Throws / Errors:**\n\n`;
    for (const t of fn.throws) {
      coreMd += `* \`${t}\`\n`;
    }
    coreMd += `\n`;
  }

  coreMd += `---\n\n`;
}

fs.writeFileSync(path.join(apiDocsDir, 'core.md'), coreMd, 'utf-8');
console.log(`[PASS] Generated: docs/api/core.md (${functions.length} functions documented)`);

// Generate docs/api/cli.md
const cliMd = `# Command-Line Interface (\`src/cli.js\`)

The Factory authoring slice provides a zero-dependency CLI for initializing immutable revisions, running deterministic verification checks, and auditing evidence logs.

---

## Synopsis

\`\`\`bash
node src/cli.js <command> [options]
\`\`\`

---

## Commands

### \`init-revision\`
Initializes a new immutable revision from a raw brief and structured requirements JSON.

\`\`\`bash
node src/cli.js init-revision \\
  --brief <path-to-brief.txt> \\
  --requirements <path-to-requirements.json> \\
  --revision-id <revision-identifier> \\
  [--parent-rev <parent-revision-id>] \\
  [--store-dir <custom-store-path>]
\`\`\`

**Options:**
* \`--brief <path>\`: Path to brief text file.
* \`--requirements <path>\`: Path to structured requirements JSON.
* \`--revision-id <id>\`: 1-64 alphanumeric identifier without path traversal.
* \`--parent-rev <id>\`: Optional parent revision ID.
* \`--store-dir <path>\`: Custom storage directory (defaults to \`./store\`).

---

### \`run-check\`
Executes a deterministic check and records the outcome to \`check_events.jsonl\` and \`evidence.json\`.

\`\`\`bash
node src/cli.js run-check \\
  --revision <revision-id> \\
  --check <check-id> \\
  [--store-dir <custom-store-path>]
\`\`\`

**Available Checks:**
* \`CHK-STATIC-SCHEMA\`: Verifies syntax and schema alignment.
* \`CHK-REQUIREMENTS-TRIAGE\`: Validates requirement confirmation assertions and flags inferred defaults.

---

### \`inspect\`
Displays metadata, requirement counts, and check statuses for a given revision.

\`\`\`bash
node src/cli.js inspect --revision <revision-id> [--store-dir <path>]
\`\`\`

---

### \`verify-consistency\`
Performs an audit between the append-only event log (\`check_events.jsonl\`) and the materialized ledger (\`evidence.json\`).

\`\`\`bash
node src/cli.js verify-consistency --revision <revision-id> [--store-dir <path>]
\`\`\`
`;

fs.writeFileSync(path.join(apiDocsDir, 'cli.md'), cliMd, 'utf-8');
console.log(`[PASS] Generated: docs/api/cli.md`);

// Generate docs/index.md for MkDocs landing page
const indexMd = `# Agent Development Factory Documentation

Welcome to the **Agent Development Factory** documentation portal.

The Factory transforms natural-language workflow briefs into inspectable, portable, and verifiable **Agent Build Packs**, backed by an append-only evidence ledger and an asynchronous multi-agent pipeline.

$$\\text{Brief} \\longrightarrow \\text{Structured Requirements} \\longrightarrow \\text{Inspectable Specification \\& Manifest} \\longrightarrow \\text{Append-Only Evidence Ledger} \\longrightarrow \\text{Immutable Revisions}$$

---

## Quick Navigation

* **[Product Contract](factory_product_contract.md)**: Reconciled v1 scope, supervised evaluation capability, multi-dimensional evidence architecture, and hard disqualification gates.
* **[Capability & Acceptance Map](factory_capability_and_acceptance_map.md)**: 6 core capabilities, inputs/outputs, user decision points, and observable criteria.
* **[Paper Interaction Walkthrough](factory_paper_interaction_walkthrough.md)**: Concrete interaction dialogue tracing intake, clarification, spec sign-off, Branch A (untested export), Branch B (supervised evaluation), and revision cycles.
* **[Development Pipeline Playbook](DEVELOPMENT_PIPELINE.md)**: The Tri-Tier architecture, Hermes agent fleet, ZipAI token protocol, and developer SOP.
* **[Persona Opportunity Map](factory_persona_opportunity_map.md)**: Persona analysis, Builderpack competitive assessment, and progressive disclosure model.
* **[Core API Reference](api/core.md)**: Exported functions in \`src/core.js\`.
* **[CLI Reference](api/cli.md)**: Command-line interface usage in \`src/cli.js\`.
`;

fs.writeFileSync(path.join(projectRoot, 'docs', 'index.md'), indexMd, 'utf-8');
console.log(`[PASS] Generated: docs/index.md`);
console.log('================================================================');
