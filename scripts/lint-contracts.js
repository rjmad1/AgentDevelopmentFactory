import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

console.log('=== [LINT-CONTRACTS] Running Zero-Dependency Contract & Syntax Check ===');

let errorCount = 0;

function checkJsSyntax(relPath) {
  const fullPath = path.join(projectRoot, relPath);
  if (!fs.existsSync(fullPath)) return;
  try {
    execFileSync(process.execPath, ['--check', fullPath], { encoding: 'utf-8' });
    console.log(`[PASS] Syntax valid: ${relPath}`);
  } catch (err) {
    console.error(`[FAIL] Syntax error in ${relPath}:\n`, err.message);
    errorCount++;
  }
}

function checkJsonSyntax(relPath) {
  const fullPath = path.join(projectRoot, relPath);
  if (!fs.existsSync(fullPath)) return;
  try {
    const raw = fs.readFileSync(fullPath, 'utf-8');
    JSON.parse(raw);
    console.log(`[PASS] JSON valid: ${relPath}`);
  } catch (err) {
    console.error(`[FAIL] Invalid JSON in ${relPath}:\n`, err.message);
    errorCount++;
  }
}

function scanDirJson(dirRel) {
  const fullDir = path.join(projectRoot, dirRel);
  if (!fs.existsSync(fullDir)) return;
  const entries = fs.readdirSync(fullDir, { withFileTypes: true });
  for (const entry of entries) {
    const rel = path.join(dirRel, entry.name);
    if (entry.isDirectory()) {
      scanDirJson(rel);
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      checkJsonSyntax(rel);
    }
  }
}

// 1. Check core JS files
checkJsSyntax('src/core.js');
checkJsSyntax('src/cli.js');
checkJsSyntax('src/server.js');
checkJsSyntax('src/eval_judge.js');
checkJsSyntax('src/laya_bridge.js');
checkJsSyntax('ui/app.js');
checkJsSyntax('test/runner.js');
checkJsSyntax('test/evals/runner.js');
checkJsSyntax('test/evals/langsmith-client.js');
checkJsSyntax('scripts/generate-api-docs.js');
checkJsSyntax('scripts/bundle-critic-packet.js');
checkJsSyntax('scripts/bundle-verifier-packet.js');
checkJsSyntax('scripts/bundle-doc-packet.js');
checkJsSyntax('scripts/autonomous-loop.js');
checkJsSyntax('scripts/setup-hooks.js');
checkJsSyntax('scripts/evaluate-product-maturity.js');

// 2. Check JSON files in fixtures, schemas, and evals
scanDirJson('fixtures');
scanDirJson('schemas');
scanDirJson('test/evals');
checkJsonSyntax('package.json');

console.log('======================================================================');
if (errorCount > 0) {
  console.error(`[FAILED] Contract lint found ${errorCount} error(s).`);
  process.exit(1);
} else {
  console.log('[SUCCESS] All contracts, schemas, and source files are syntactically clean.');
  process.exit(0);
}
