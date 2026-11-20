import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const reviewDirName = 'review-pre-inspection-20261120-070800';
const reviewDirPath = path.join(rootDir, reviewDirName);

// 1. Exclusive creation of review child
if (fs.existsSync(reviewDirPath)) {
  console.error(`FATAL: Review directory already exists: ${reviewDirPath}`);
  process.exit(1);
}

try {
  fs.mkdirSync(reviewDirPath, { recursive: false });
} catch (err) {
  console.error(`FATAL: Exclusive directory creation failed: ${err.message}`);
  process.exit(1);
}

// 2. Explicit allowlist of reported files and dependencies
const allowlist = [
  'package.json',
  'src/core.js',
  'src/cli.js',
  'fixtures/synthetic_brief_v1.txt',
  'fixtures/synthetic_requirements_v1.json',
  'fixtures/synthetic_requirements_v2.json',
  'fixtures/synthetic_requirements_unconfirmed.json',
  'fixtures/synthetic_requirements_forbidden_name.json',
  'test/runner.js',
  'store/rev-001/inputs.json',
  'store/rev-001/spec.md',
  'store/rev-001/manifest.json',
  'store/rev-001/evidence.json',
  'store/rev-002/inputs.json',
  'store/rev-002/spec.md',
  'store/rev-002/manifest.json',
  'store/rev-002/evidence.json',
];

const inventory = [];

for (const relPath of allowlist) {
  const fullPath = path.resolve(rootDir, relPath);

  // Reject paths escaping root
  if (!fullPath.startsWith(rootDir)) {
    console.error(`SECURITY ERROR: Path escapes root: ${relPath} -> ${fullPath}`);
    process.exit(1);
  }

  // Reject symlinks/reparse points
  const lstat = fs.lstatSync(fullPath);
  if (lstat.isSymbolicLink()) {
    console.error(`SECURITY ERROR: Symlink/reparse point detected: ${relPath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(fullPath);
  const hash = crypto.createHash('sha256').update(content).digest('hex');
  const size = lstat.size;

  const targetPath = path.join(reviewDirPath, relPath);
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  fs.writeFileSync(targetPath, content);

  inventory.push({
    relativePath: relPath,
    byteSize: size,
    sha256: hash,
  });
}

// Check logs
const potentialLogs = ['cli.log', 'run.log', 'test.log'].filter(f => fs.existsSync(path.join(rootDir, f)));
const logsStatus = potentialLogs.length === 0 ? 'MISSING (No pre-existing standalone log files found in slice root)' : potentialLogs;

const inventoryData = {
  preservedAt: new Date().toISOString(),
  reviewDirectory: reviewDirPath,
  logsStatus,
  fileCount: inventory.length,
  files: inventory,
};

fs.writeFileSync(path.join(reviewDirPath, 'inventory.json'), JSON.stringify(inventoryData, null, 2), 'utf-8');

let md = `# Pre-Inspection Preservation Inventory\n\n`;
md += `**Preserved At:** \`${inventoryData.preservedAt}\`  \n`;
md += `**Review Directory:** \`${reviewDirPath}\`  \n`;
md += `**Logs Status:** \`${logsStatus}\`  \n`;
md += `**Total Files Preserved:** \`${inventory.length}\`  \n\n`;
md += `| File Path | Byte Size | Full SHA-256 Checksum |\n`;
md += `| :--- | :--- | :--- |\n`;
for (const item of inventory) {
  md += `| \`${item.relativePath}\` | ${item.byteSize} | \`${item.sha256}\` |\n`;
}

fs.writeFileSync(path.join(reviewDirPath, 'INVENTORY.md'), md, 'utf-8');

console.log(`[PRESERVATION COMPLETE]`);
console.log(`Preserved ${inventory.length} files to ${reviewDirPath}`);
console.log(`Logs status: ${logsStatus}`);
