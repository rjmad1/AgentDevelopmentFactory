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

console.log('=== [HERMES PACKET] Generating Surgical Doc Packet for Communicator ===');

const gitHead = getGitOutput('git rev-parse HEAD') || 'UNTRACKED_LOCAL_REVISION';

// 1. Capture CLI usage
let cliHelpText = '';
try {
  cliHelpText = execSync(`"${process.execPath}" src/cli.js`, {
    cwd: projectRoot,
    encoding: 'utf-8',
    stdio: ['ignore', 'pipe', 'pipe']
  }).trim();
} catch (err) {
  cliHelpText = (err.stdout || err.stderr || '').toString().trim();
}

// 2. Extract exported functions from src/core.js
const corePath = path.join(projectRoot, 'src', 'core.js');
const coreSource = fs.readFileSync(corePath, 'utf-8');
const exportRegex = /export\s+function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)/g;
const exportedFunctions = [];
let match;
while ((match = exportRegex.exec(coreSource)) !== null) {
  const name = match[1];
  const params = match[2].trim().replace(/\s+/g, ' ');
  exportedFunctions.push({
    name,
    signature: `function ${name}(${params})`,
    doc: `Exported core domain capability: ${name}`
  });
}

// 3. Extract recent changelog diff or top section
const changelogPath = path.join(projectRoot, 'CHANGELOG.md');
let changelogDiff = '';
if (fs.existsSync(changelogPath)) {
  const diff = getGitOutput('git diff HEAD CHANGELOG.md') || getGitOutput('git diff HEAD~1 HEAD CHANGELOG.md');
  if (diff) {
    changelogDiff = diff;
  } else {
    // Top 30 lines of CHANGELOG.md
    const lines = fs.readFileSync(changelogPath, 'utf-8').split('\n');
    changelogDiff = lines.slice(0, 35).join('\n');
  }
}

const packet = {
  packet_version: '1.0.0',
  timestamp: new Date().toISOString(),
  git_head: gitHead,
  cli_help_text: cliHelpText,
  exported_core_functions: exportedFunctions,
  recent_changelog_diff: changelogDiff
};

const packetDir = path.join(projectRoot, '.hermes', 'packets');
if (!fs.existsSync(packetDir)) {
  fs.mkdirSync(packetDir, { recursive: true });
}

const outPath = path.join(packetDir, 'doc_packet.json');
const jsonString = JSON.stringify(packet, null, 2);
fs.writeFileSync(outPath, jsonString, 'utf-8');

const byteLength = Buffer.byteLength(jsonString, 'utf-8');
const estimatedTokens = Math.ceil(byteLength / 4);

console.log(`[PACKET CREATED] ${path.relative(projectRoot, outPath)}`);
console.log(`  Payload Size:    ${byteLength} bytes (~${estimatedTokens} tokens)`);
console.log(`  Exported Fns:    ${exportedFunctions.length}`);
console.log(`  CLI Help:        ${cliHelpText.split('\n').length} lines`);
console.log('======================================================================');
