import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

function getGitOutput(cmd) {
  try {
    return execSync(cmd, { cwd: projectRoot, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return '';
  }
}

console.log('=== [HERMES PACKET] Generating Surgical Critic Review Packet ===');

// 1. Git Head and Diff
const gitHead = getGitOutput('git rev-parse HEAD') || 'UNTRACKED_LOCAL_REVISION';
let unifiedDiff = getGitOutput('git diff HEAD');
if (!unifiedDiff) {
  unifiedDiff = getGitOutput('git diff HEAD~1 HEAD');
}
if (!unifiedDiff) {
  unifiedDiff = '# No active uncommitted or recent commit diff found. Working tree clean.';
}

// 2. Changed Files
let changedFiles = getGitOutput('git diff --name-only HEAD').split('\n').filter(Boolean);
if (changedFiles.length === 0) {
  changedFiles = getGitOutput('git diff --name-only HEAD~1 HEAD').split('\n').filter(Boolean);
}
if (changedFiles.length === 0) {
  changedFiles = ['src/core.js', 'src/cli.js'];
}

// 3. Find latest test summary
const testRunsBase = path.join(projectRoot, 'test-runs');
let testSummary = { passed: 0, failed: 0, blocked: 0, run_id: 'no-runs-detected' };

if (fs.existsSync(testRunsBase)) {
  const runs = fs.readdirSync(testRunsBase)
    .filter(name => fs.statSync(path.join(testRunsBase, name)).isDirectory())
    .sort()
    .reverse();
  for (const r of runs) {
    const summaryPath = path.join(testRunsBase, r, 'test_summary.json');
    if (fs.existsSync(summaryPath)) {
      try {
        const raw = JSON.parse(fs.readFileSync(summaryPath, 'utf-8'));
        testSummary = {
          passed: raw.passed ?? 0,
          failed: raw.failed ?? 0,
          blocked: raw.blocked ?? 0,
          run_id: raw.runId || r
        };
        break;
      } catch {}
    }
  }
}

// 4. Extract referenced requirement IDs
const reqRegex = /REQ-[A-Z0-9_-]+/g;
const reqMatches = new Set(unifiedDiff.match(reqRegex) || []);
const referencedRequirements = Array.from(reqMatches);

// 5. Construct Packet
const packet = {
  packet_version: '1.0.0',
  timestamp: new Date().toISOString(),
  git_head: gitHead,
  changed_files: changedFiles,
  unified_diff: unifiedDiff,
  test_summary: testSummary,
  referenced_requirements: referencedRequirements,
  review_focus: [
    'over_engineering_and_abstractions',
    'security_boundaries_and_sanitization',
    'spec_to_code_drift',
    'reversibility_and_immutability',
    'test_authenticity'
  ]
};

const packetDir = path.join(projectRoot, '.hermes', 'packets');
if (!fs.existsSync(packetDir)) {
  fs.mkdirSync(packetDir, { recursive: true });
}

const outPath = path.join(packetDir, 'critic_packet.json');
const jsonString = JSON.stringify(packet, null, 2);
fs.writeFileSync(outPath, jsonString, 'utf-8');

const byteLength = Buffer.byteLength(jsonString, 'utf-8');
const estimatedTokens = Math.ceil(byteLength / 4);

console.log(`[PACKET CREATED] ${path.relative(projectRoot, outPath)}`);
console.log(`  Payload Size:    ${byteLength} bytes (~${estimatedTokens} tokens)`);
console.log(`  Git Head:        ${gitHead.slice(0, 8)}`);
console.log(`  Changed Files:   ${changedFiles.length}`);
console.log(`  Test Status:     ${testSummary.passed} passed, ${testSummary.failed} failed`);
console.log(`  Requirement IDs: ${referencedRequirements.join(', ') || 'None in diff'}`);
console.log('======================================================================');
