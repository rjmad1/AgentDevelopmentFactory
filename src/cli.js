#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { initRevision, runCheck, inspectRevision, verifyEvidenceConsistency } from './core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const defaultStoreDir = path.resolve(__dirname, '..', 'store');

function parseArgs(args) {
  const parsed = {
    command: args[0],
    options: {},
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        parsed.options[key] = next;
        i++;
      } else {
        parsed.options[key] = true;
      }
    }
  }

  return parsed;
}

function printUsage() {
  console.log(`
Agent Development Factory — Bounded Authoring Slice CLI (v0.3.0)

Usage:
  node src/cli.js <command> [options]

Commands:
  init-revision        Initialize a new immutable revision snapshot
    --brief <path>         Path to plain-text workflow brief (required)
    --requirements <path>  Path to structured requirements JSON (required)
    --revision-id <id>     Identifier for this revision (default: rev-<timestamp>)
    --parent-rev <id>      Parent revision ID to link revision history (optional)
    --store <path>         Path to revision storage directory (default: ./store)

  run-check            Execute a bounded static check for a revision
    --revision <id>        Revision identifier (required)
    --check <id>           Check identifier (e.g. CHK-STATIC-SCHEMA, CHK-REQUIREMENTS-TRIAGE)
    --fail                 Force check failure for honest error reporting demo
    --store <path>         Path to revision storage directory (default: ./store)

  inspect              Inspect a revision manifest, consistency, and evidence summary
    --revision <id>        Revision identifier (required)
    --store <path>         Path to revision storage directory (default: ./store)

  verify-consistency   Audit consistency between check_events.jsonl and evidence.json
    --revision <id>        Revision identifier (required)
    --store <path>         Path to revision storage directory (default: ./store)
`);
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  const { command, options } = parseArgs(args);
  const storeDir = options.store ? path.resolve(process.cwd(), options.store) : defaultStoreDir;

  try {
    switch (command) {
      case 'init-revision': {
        if (!options.brief || !options.requirements) {
          console.error('Error: --brief and --requirements are required for init-revision.');
          process.exit(1);
        }

        const briefPath = path.resolve(process.cwd(), options.brief);
        const requirementsPath = path.resolve(process.cwd(), options.requirements);
        const revisionId = options['revision-id'] || `rev-${Date.now()}`;
        const parentRevisionId = options['parent-rev'] || null;

        const result = initRevision({
          storeDir,
          revisionId,
          parentRevisionId,
          briefPath,
          requirementsPath,
        });

        console.log(`[INIT-REVISION SUCCESS]`);
        console.log(`  Revision ID:      ${result.revisionId}`);
        console.log(`  Parent Revision:  ${result.parentRevisionId || 'None (Initial)'}`);
        console.log(`  Location:         ${result.revDir}`);
        console.log(`  Input SHA-256:    ${result.hashes.inputSha256.slice(0, 16)}...`);
        console.log(`  Spec SHA-256:     ${result.hashes.specSha256.slice(0, 16)}...`);
        console.log(`  Requirements:     ${result.triageSummary.confirmedCount} confirmed, ${result.triageSummary.proposedCount} proposed, ${result.triageSummary.unresolvedCount} unresolved`);
        console.log(`  Evidence Status:  ${result.checkSummary.notRun} NOT RUN, ${result.checkSummary.passed} PASSED, ${result.checkSummary.stale} STALE, ${result.checkSummary.blocked} BLOCKED`);
        break;
      }

      case 'run-check': {
        if (!options.revision || !options.check) {
          console.error('Error: --revision and --check are required for run-check.');
          process.exit(1);
        }

        const result = runCheck({
          storeDir,
          revisionId: options.revision,
          checkId: options.check,
          failIntentionally: Boolean(options.fail),
        });

        console.log(`[RUN-CHECK RESULT]`);
        console.log(`  Revision:         ${options.revision}`);
        console.log(`  Check ID:         ${result.checkId}`);
        console.log(`  Status:           ${result.status}`);
        console.log(`  Exit Code:        ${result.exitCode}`);
        console.log(`  Event ID:         #${result.eventId}`);
        console.log(`  Execution Count:  ${result.executionCount}`);
        if (result.output) console.log(`  Output:           ${result.output}`);
        if (result.error) console.log(`  Error:            ${result.error}`);

        if (result.status === 'FAILED') {
          process.exit(result.exitCode || 1);
        }
        break;
      }

      case 'inspect': {
        if (!options.revision) {
          console.error('Error: --revision is required for inspect.');
          process.exit(1);
        }

        const info = inspectRevision({
          storeDir,
          revisionId: options.revision,
        });

        console.log(JSON.stringify(info, null, 2));
        break;
      }

      case 'verify-consistency': {
        if (!options.revision) {
          console.error('Error: --revision is required for verify-consistency.');
          process.exit(1);
        }

        const revDir = path.join(storeDir, options.revision);
        const report = verifyEvidenceConsistency(revDir);
        console.log(JSON.stringify(report, null, 2));

        if (!report.isConsistent) {
          process.exit(1);
        }
        break;
      }

      default:
        console.error(`Unknown command: "${command}"`);
        printUsage();
        process.exit(1);
    }
  } catch (err) {
    console.error(`[CLI ERROR] ${err.message}`);
    process.exit(1);
  }
}

main();
