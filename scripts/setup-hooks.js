#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const gitHooksDir = path.join(projectRoot, '.git', 'hooks');

if (!fs.existsSync(gitHooksDir)) {
  console.log('[SKIP] .git/hooks directory not found. Are you in a Git repository?');
  process.exit(0);
}

const preCommitHook = `#!/bin/sh
# Agent Development Factory - Autonomous Pre-Commit Hook
echo "=== [GIT HOOK] Running Autonomous Pipeline Validation ==="
node scripts/autonomous-loop.js --once
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "❌ Pre-commit validation failed. Fix errors before committing."
  exit $EXIT_CODE
fi

# Auto-stage regenerated docs if modified
git add docs/api/ docs/index.md 2>/dev/null || true
exit 0
`;

const hookPath = path.join(gitHooksDir, 'pre-commit');
fs.writeFileSync(hookPath, preCommitHook, { encoding: 'utf-8', mode: 0o755 });

console.log(`[PASS] Installed autonomous pre-commit hook at: ${path.relative(projectRoot, hookPath)}`);
