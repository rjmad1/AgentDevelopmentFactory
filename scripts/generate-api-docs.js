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
const cliLines = [
  '# Command-Line Interfaces (CLI Reference)',
  '',
  'The Agent Development Factory provides two command-line interfaces corresponding to its dual-tier architecture:',
  '1. **Authoring Front-End CLI (`node src/cli.js`):** Zero-dependency Node.js CLI for requirement triage, immutable revision creation, spec export, MCP tool intake, and evidence verification.',
  '2. **Factory Back-End CLI (`python -m agent_factory.cli`):** Industrial Python CLI for lifecycle orchestration, workspace synthesis, execution sandboxing, and evaluation gates.',
  '',
  '---',
  '',
  '## 1. Authoring Front-End CLI (`src/cli.js`)',
  '',
  'The Factory authoring slice provides a zero-dependency CLI for initializing immutable revisions, running deterministic verification checks, exporting Universal Agent YAML specifications, importing Model Context Protocol (MCP) tools, and platform diagnostics.',
  '',
  '### Synopsis',
  '',
  '```bash',
  'node src/cli.js <command> [options]',
  '```',
  '',
  '---',
  '',
  '### Commands',
  '',
  '#### `init-revision`',
  'Initializes a new immutable revision from a raw brief and structured requirements JSON.',
  '',
  '```bash',
  'node src/cli.js init-revision \\',
  '  --brief <path-to-brief.txt> \\',
  '  --requirements <path-to-requirements.json> \\',
  '  --revision-id <revision-identifier> \\',
  '  [--parent-rev <parent-revision-id>] \\',
  '  [--store <custom-store-path>]',
  '```',
  '',
  '**Options:**',
  '* `--brief <path>`: Path to brief text file.',
  '* `--requirements <path>`: Path to structured requirements JSON.',
  '* `--revision-id <id>`: 1-64 alphanumeric identifier without path traversal.',
  '* `--parent-rev <id>`: Optional parent revision ID.',
  '* `--store <path>`: Custom storage directory (defaults to `./store`).',
  '',
  '---',
  '',
  '#### `run-check`',
  'Executes a deterministic check and records the outcome to `check_events.jsonl` and `evidence.json`.',
  '',
  '```bash',
  'node src/cli.js run-check \\',
  '  --revision <revision-id> \\',
  '  --check <check-id> \\',
  '  [--store <custom-store-path>]',
  '```',
  '',
  '**Available Checks:**',
  '* `CHK-STATIC-SCHEMA`: Verifies syntax and schema alignment.',
  '* `CHK-REQUIREMENTS-TRIAGE`: Validates requirement confirmation assertions and flags inferred defaults.',
  '* `CHK-SPEC-COMPLIANCE`: Validates exported Universal Agent Spec conformity against schema.',
  '* `CHK-TOKEN-BUDGET`: Verifies context window consumption does not exceed 8,000 tokens.',
  '',
  '---',
  '',
  '#### `inspect`',
  'Displays metadata, requirement counts, and check statuses for a given revision.',
  '',
  '```bash',
  'node src/cli.js inspect --revision <revision-id> [--store <path>]',
  '```',
  '',
  '---',
  '',
  '#### `verify-consistency`',
  'Performs an audit between the append-only event log (`check_events.jsonl`) and the materialized ledger (`evidence.json`).',
  '',
  '```bash',
  'node src/cli.js verify-consistency --revision <revision-id> [--store <path>]',
  '```',
  '',
  '---',
  '',
  '#### `scaffold-requirements`',
  'Generates a pre-formatted, valid requirements JSON template with triaged confirmation sections.',
  '',
  '```bash',
  'node src/cli.js scaffold-requirements --output <path> [--title <title>] [--author <author>]',
  '```',
  '',
  '---',
  '',
  '#### `export-agent-spec`',
  'Compiles an immutable revision manifest into a Pydantic-compliant Universal Agent Specification YAML (`agent.yaml`).',
  '',
  '```bash',
  'node src/cli.js export-agent-spec --revision <revision-id> [--output <output-path>] [--store <store-dir>]',
  '```',
  '',
  '---',
  '',
  '#### `import-mcp-tool`',
  'Ingests a Model Context Protocol (MCP) tool schema definition and registers it into the factory capability registry with typed effect permissions.',
  '',
  '```bash',
  'node src/cli.js import-mcp-tool --schema <mcp-tool.json> [--registry <custom-registry.json>] [--effect <effect-level>]',
  '```',
  '',
  '---',
  '',
  '#### `doctor`',
  'Runs platform diagnostics checking Node runtime, Python virtual environment, Specify CLI presence, core schemas, filesystem containment, and port listeners.',
  '',
  '```bash',
  'node src/cli.js doctor',
  '```',
  '',
  '---',
  '',
  '## 2. Factory Back-End CLI (`agent_factory.cli`)',
  '',
  'The Agent Development Factory Command Line Interface (`agent-factory` / `python -m agent_factory.cli`) provides commands for request intake, workspace building, evaluation runs, and candidate packaging.',
  '',
  '### Synopsis',
  '',
  '```bash',
  'python -m agent_factory.cli <command> [options]',
  '```',
  '',
  '### Python Module Reference',
  '',
  '::: agent_factory.cli',
  '    options:',
  '      show_root_heading: true',
  '      show_source: true',
];

fs.writeFileSync(path.join(apiDocsDir, 'cli.md'), cliLines.join('\n') + '\n', 'utf-8');
console.log('[PASS] Generated: docs/api/cli.md');

// Generate docs/index.md for MkDocs landing page
const indexLines = [
  '# Agent Development Factory',
  '',
  '[![Zero-Cost CI/CD](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml/badge.svg)](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml)',
  '[![Pages Deployment](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/docs.yml/badge.svg?branch=gh-pages)](https://rjmad1.github.io/AgentDevelopmentFactory/)',
  '[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)',
  '[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)',
  '[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)',
  '',
  'Welcome to the **Agent Development Factory** documentation portal.',
  '',
  'The Factory transforms natural-language workflow briefs into inspectable, portable, safe, and verifiable **Agent Build Packs**, backed by an append-only evidence ledger, deterministic verification gates, and an asynchronous multi-agent pipeline.',
  '',
  '$$\\text{Brief} \\longrightarrow \\text{Structured Requirements} \\longrightarrow \\text{Inspectable Specification \\& Manifest} \\longrightarrow \\text{Append-Only Evidence Ledger} \\longrightarrow \\text{Deterministic Verification \\& Build}$$',
  '',
  '---',
  '',
  '## 🏛️ Tri-Tier & Three-Plane Architecture',
  '',
  'The factory operates a dual-tier modular architecture that enforces strict separation of responsibilities:',
  '',
  '```text',
  '┌─────────────────────────────────────────────────────────────┐',
  '│                 CONTROL PLANE (Governance)                  │',
  '│  - Request Intake & Triage (CONFIRMED vs PROPOSED)          │',
  '│  - Immutable Revision Stores (SHA-256)                      │',
  '│  - Task Ledger (Append-Only Event Stream)                   │',
  '│  - Orchestrator Engine & State Transitions                  │',
  '└──────────────────────────────┬──────────────────────────────┘',
  '                               │',
  '                               ▼',
  '┌─────────────────────────────────────────────────────────────┐',
  '│                 WORKBENCH PLANE (Execution)                 │',
  '│  - Ephemeral Isolated Workspaces                            │',
  '│  - Deterministic Code Generator & Test Synthesizer          │',
  '│  - Candidate Release Packager & Checksum Verifier           │',
  '└──────────────────────────────┬──────────────────────────────┘',
  '                               │',
  '                               ▼',
  '┌─────────────────────────────────────────────────────────────┐',
  '│                 VERIFICATION & RUNTIME PLANE                │',
  '│  - Sandboxed Local Process Execution                        │',
  '│  - Multi-Metric Graders (ExitCode, Markdown, JSON, AST)     │',
  '│  - Deep Evaluator & LangSmith Observability                 │',
  '│  - Self-Healing Remediation Loop                            │',
  '└─────────────────────────────────────────────────────────────┘',
  '```',
  '',
  '---',
  '',
  '## 📚 Quick Navigation',
  '',
  '### Product Contracts & Specifications',
  '* **[Capability Roadmap](ADF_Capability_Map_Roadmap.md)**: Honest implemented / planned / pending status for every capability, measured against Baseline v1.0.0 (ADF-001…ADF-040).',
  '* **[Evals and Guardrails Specification](adf-evals-and-guardrails.md)**: Operating spec for evals, guardrails, and release criteria.',
  '* **[Product Contract](factory_product_contract.md)**: Reconciled v1 scope, supervised evaluation capability, multi-dimensional evidence architecture, and hard disqualification gates.',
  '* **[Capability & Acceptance Map](factory_capability_and_acceptance_map.md)**: Core capabilities, inputs/outputs, user decision points, and observable criteria.',
  '* **[Paper Interaction Walkthrough](factory_paper_interaction_walkthrough.md)**: Concrete interaction dialogue tracing intake, clarification, spec sign-off, and revision cycles.',
  '* **[Development Pipeline Playbook](DEVELOPMENT_PIPELINE.md)**: The Tri-Tier architecture, Hermes agent fleet, ZipAI token protocol, and developer SOP.',
  '* **[Persona Opportunity Map](factory_persona_opportunity_map.md)**: Persona analysis, Builderpack competitive assessment, and progressive disclosure model.',
  '',
  '### API & Engine References',
  '* **[Authoring Core API (`src/core.js`)](api/core.md)**: Zero-dependency hashing, containment, and triage engine.',
  '* **[Command-Line Interfaces](api/cli.md)**: Complete usage guides for both Node.js and Python CLIs.',
  '* **[Control Plane API](api/control_plane.md)**: Intake, lifecycle, orchestrator, and task ledger.',
  '* **[Evaluations API](api/evals.md)**: Deep Evaluator, LangSmith adapter, metrics, and test runner.',
  '* **[Security Architecture](api/security.md)**: Quarantine sandbox, approval gates, and secret redactor.',
  '',
  '---',
  '',
  '## 📦 Quick Start',
  '',
  '### 1. Authoring CLI (Node.js)',
  '```bash',
  '# Run integrity tests',
  'node test/runner.js',
  '',
  '# Run doctor diagnostic',
  'node src/cli.js doctor',
  '',
  '# Scaffold new requirements template',
  'node src/cli.js scaffold-requirements --output ./requirements.json',
  '',
  '# Initialize a new revision',
  'node src/cli.js init-revision --brief fixtures/synthetic_brief_v1.txt --requirements fixtures/synthetic_requirements_v1.json --revision-id rev-001',
  '',
  '# Export Universal Agent Spec YAML',
  'node src/cli.js export-agent-spec --revision rev-001',
  '```',
  '',
  '### 2. Platform Back-End (Python)',
  '```bash',
  '# Set up Python virtual environment',
  'python -m venv .venv',
  '.venv\\Scripts\\activate',
  'pip install -r requirements.txt',
  '',
  '# Run Python verification suite',
  'pytest tests/',
  '',
  '# Run automated Deep Evaluator',
  'python scripts/run_evals.py',
  '```',
];

fs.writeFileSync(path.join(projectRoot, 'docs', 'index.md'), indexLines.join('\n') + '\n', 'utf-8');
console.log('[PASS] Generated: docs/index.md');
console.log('================================================================');
