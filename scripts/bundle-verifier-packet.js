import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { getCheckerImplementationHash } from '../src/core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function getGitOutput(cmd) {
  try {
    return execSync(cmd, { cwd: projectRoot, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return '';
  }
}

console.log('=== [HERMES PACKET] Generating Deterministic Verifier Evidence Packet ===');

const gitHead = getGitOutput('git rev-parse HEAD') || 'UNTRACKED_LOCAL_REVISION';

// Find latest test run and log
const testRunsBase = path.join(projectRoot, 'test-runs');
let executionMetrics = {
  total_runs: 0,
  latest_run_id: 'none',
  passed: 0,
  failed: 0,
  log_hash: 'none'
};
let manifestSnapshot = {};
let unverifiedAssumptions = [];

if (fs.existsSync(testRunsBase)) {
  const runs = fs.readdirSync(testRunsBase)
    .filter(name => fs.statSync(path.join(testRunsBase, name)).isDirectory())
    .sort()
    .reverse();
  
  executionMetrics.total_runs = runs.length;
  if (runs.length > 0) {
    const latestRun = runs[0];
    executionMetrics.latest_run_id = latestRun;

    const summaryPath = path.join(testRunsBase, latestRun, 'test_summary.json');
    if (fs.existsSync(summaryPath)) {
      try {
        const sum = JSON.parse(fs.readFileSync(summaryPath, 'utf-8'));
        executionMetrics.passed = sum.passed ?? 0;
        executionMetrics.failed = sum.failed ?? 0;
      } catch {}
    }

    const logPath = path.join(testRunsBase, latestRun, 'test_execution.log');
    if (fs.existsSync(logPath)) {
      const logContent = fs.readFileSync(logPath);
      executionMetrics.log_hash = sha256(logContent);
    }

    // Look for manifest in test store
    const storeDir = path.join(testRunsBase, latestRun, 'store');
    if (fs.existsSync(storeDir)) {
      const revs = fs.readdirSync(storeDir).sort().reverse();
      if (revs.length > 0) {
        const manifestPath = path.join(storeDir, revs[0], 'manifest.json');
        if (fs.existsSync(manifestPath)) {
          try {
            manifestSnapshot = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
            if (manifestSnapshot.assumptions) {
              unverifiedAssumptions = manifestSnapshot.assumptions.filter(a => a.status !== 'VERIFIED').map(a => a.description || a.id);
            }
          } catch {}
        }
      }
    }
  }
}

const checkerHash = getCheckerImplementationHash();

const packet = {
  packet_version: '1.0.0',
  timestamp: new Date().toISOString(),
  git_head: gitHead,
  manifest_snapshot: manifestSnapshot,
  execution_metrics: executionMetrics,
  checker_implementation_hash: checkerHash,
  unverified_assumptions: unverifiedAssumptions
};

const packetDir = path.join(projectRoot, '.hermes', 'packets');
if (!fs.existsSync(packetDir)) {
  fs.mkdirSync(packetDir, { recursive: true });
}

const outPath = path.join(packetDir, 'verifier_packet.json');
const jsonString = JSON.stringify(packet, null, 2);
fs.writeFileSync(outPath, jsonString, 'utf-8');

const byteLength = Buffer.byteLength(jsonString, 'utf-8');
const estimatedTokens = Math.ceil(byteLength / 4);

console.log(`[PACKET CREATED] ${path.relative(projectRoot, outPath)}`);
console.log(`  Payload Size:    ${byteLength} bytes (~${estimatedTokens} tokens)`);
console.log(`  Latest Run ID:   ${executionMetrics.latest_run_id}`);
console.log(`  Log Hash (SHA):  ${executionMetrics.log_hash.slice(0, 12)}...`);
console.log(`  Checker Hash:    ${checkerHash.slice(0, 12)}...`);
console.log('======================================================================');
