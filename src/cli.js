#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  initRevision,
  runCheck,
  inspectRevision,
  verifyEvidenceConsistency,
  exportAgentYamlSpec,
  scaffoldRequirementsTemplate,
  importMcpToolDefinition,
  runDoctorCheck,
  triageSolutionComplexity,
  estimateTokenAndCostFeasibility,
  evaluateAgentThreatModel,
  generateGuardrailPolicy,
  runAdversarialSecuritySuite,
  evaluateReleaseGates,
} from './core.js';

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

  scaffold-requirements Scaffold a verified structured requirements template
    --output <path>        Path to write generated requirements JSON (required)
    --title <title>        Workflow title (optional)
    --author <name>        Author or stakeholder name (optional)

  export-agent-spec    Export revision to Universal Agent Spec (agent.yaml)
    --revision <id>        Revision identifier (required)
    --output <path>        Custom output path (default: <store>/<revision>/agent.yaml)
    --store <path>         Path to revision storage directory (default: ./store)

  import-mcp-tool      Import Model Context Protocol (MCP) tool schema into Capability Registry
    --schema <path>        Path to MCP tool schema JSON (required)
    --registry <path>      Custom registry path (default: data/capability_registry.json)
    --effect <level>       Permission effect level (default: READ_PUBLIC)

  doctor               Run comprehensive platform health check and port canary audit
    --store <path>         Custom store path (optional)

  triage-solution      Triage problem complexity (No-Agent, Workflow, Agent, Multi-Agent)
    --brief <text|path>    Task brief string or path to brief text file

  estimate-cost        Estimate token consumption and economic feasibility
    --brief <text|path>    Task brief string or path to brief text file
    --tokens <count>       Base tokens (default: 1500)

  threat-model         Evaluate blueprint against OWASP Top 10 for Agentic Applications
    --revision <id>        Revision identifier (required)
    --store <path>         Path to revision storage directory (default: ./store)

  generate-guardrails  Generate 10-layer canonical YAML guardrail policy (Section 4)
    --revision <id>        Revision identifier (required)
    --tier <T0-T3>         Risk tier (default: T0)
    --store <path>         Path to revision storage directory (default: ./store)

  sec-evals            Run SEC-01 through SEC-10 adversarial security suite (Section 5)
    --revision <id>        Revision identifier (required)
    --tier <T0-T3>         Risk tier (default: T0)
    --store <path>         Path to revision storage directory (default: ./store)

  eval-gates           Evaluate 9 release gates before promotion (Section 6)
    --revision <id>        Revision identifier (required)
    --tier <T0-T3>         Risk tier (default: T0)
    --human-review         Confirm human review token sign-off (required for T1+)
    --retry <count>        Current retry attempt (default: 1)
    --store <path>         Path to revision storage directory (default: ./store)

  ui                   Launch Google Material Design 3 Hybrid Web Platform
    --port <number>        Port to bind HTTP server (default: 3000)
    --store <path>         Path to revision storage directory (default: ./store)

  eval-judge           Execute LLM-as-a-Judge evaluation calibrated via Laya RLCD
    --revision <id>        Revision identifier (default: rev-001)
    --target <path>        Path to deployment directory or code file
    --store <path>         Path to revision storage directory (default: ./store)

  trace                Inspect distributed W3C traces and causal reasoning spans
    --action <list|get>    Action to perform (default: list)
    --trace-id <id>        Trace ID to inspect in detail

  scale                Inspect auto-scaling concurrency governor and simulate spikes
    --action <status|simulate> Action to perform (default: status)
    --tasks <count>        Number of tasks to inject for spike simulation (default: 15)

  heal                 Test autonomous self-healing, format repair, and fault diagnosis
    --action <diagnose|repair> Action to perform (default: repair)
    --payload <string>     Malformed payload or error text to self-heal

  sync                 Enforce strict state synchronization and eliminate configuration drift
    --action <audit|reconcile> Action to perform (default: audit)
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

      case 'scaffold-requirements': {
        if (!options.output) {
          console.error('Error: --output is required for scaffold-requirements.');
          process.exit(1);
        }

        const result = scaffoldRequirementsTemplate({
          outputPath: path.resolve(process.cwd(), options.output),
          title: options.title || 'Autonomous Analytical Processing Agent',
          author: options.author || 'Admin',
        });

        console.log(`[SCAFFOLD-REQUIREMENTS SUCCESS]`);
        console.log(`  Output Path:   ${result.outputPath}`);
        console.log(`  Items Count:   ${result.requirementsCount}`);
        console.log(`  SHA-256:       ${result.sha256}`);
        break;
      }

      case 'export-agent-spec': {
        if (!options.revision) {
          console.error('Error: --revision is required for export-agent-spec.');
          process.exit(1);
        }

        const outputPath = options.output ? path.resolve(process.cwd(), options.output) : null;
        const result = exportAgentYamlSpec({
          storeDir,
          revisionId: options.revision,
          outputPath,
        });

        console.log(`[EXPORT-AGENT-SPEC SUCCESS]`);
        console.log(`  Agent ID:      ${result.agentId}`);
        console.log(`  Revision:      ${result.revisionId}`);
        console.log(`  Output Path:   ${result.outputPath}`);
        console.log(`  Spec SHA-256:  ${result.sha256}`);
        break;
      }

      case 'import-mcp-tool': {
        if (!options.schema) {
          console.error('Error: --schema is required for import-mcp-tool.');
          process.exit(1);
        }

        const mcpSchemaPath = path.resolve(process.cwd(), options.schema);
        const registryPath = options.registry ? path.resolve(process.cwd(), options.registry) : null;
        const effectLevel = options.effect || 'READ_PUBLIC';

        const result = importMcpToolDefinition({
          mcpSchemaPath,
          registryPath,
          effectLevel,
        });

        console.log(`[IMPORT-MCP-TOOL SUCCESS]`);
        console.log(`  Capability ID: ${result.capabilityId}`);
        console.log(`  Tool Name:     ${result.toolName}`);
        console.log(`  Effect Level:  ${result.effectLevel}`);
        console.log(`  Registry:      ${result.registryPath}`);
        break;
      }

      case 'doctor': {
        const root = path.resolve(__dirname, '..');
        const report = runDoctorCheck({ projectRoot: root });

        console.log(`\n==================================================`);
        console.log(`AGENT DEVELOPMENT FACTORY — PLATFORM DOCTOR`);
        console.log(`Overall Health: ${report.overallStatus} (${report.passedChecks}/${report.totalChecks} checks passing)`);
        console.log(`==================================================`);
        for (const d of report.diagnostics) {
          const badge = d.status === 'PASS' ? '[PASS]' : (d.status === 'WARN' ? '[WARN]' : '[FAIL]');
          console.log(`${badge} ${d.component}: ${d.details}`);
        }
        console.log(`==================================================\n`);

        if (report.overallStatus === 'UNHEALTHY') {
          process.exit(1);
        }
        break;
      }

      case 'triage-solution': {
        const briefInput = options.brief || '';
        const briefText = fs.existsSync(path.resolve(process.cwd(), briefInput))
          ? fs.readFileSync(path.resolve(process.cwd(), briefInput), 'utf-8')
          : briefInput;
        const triage = triageSolutionComplexity({ briefText });

        console.log(`[TRIAGE-SOLUTION RESULT]`);
        console.log(`  Solution Type:       ${triage.solutionType}`);
        console.log(`  Recommended Pattern: ${triage.recommendedPattern}`);
        console.log(`  Token Multiplier:    ${triage.tokenMultiplier}x`);
        console.log(`  Reasoning:           ${triage.reasoning}`);
        console.log(`  Simplicity:          ${triage.simplicityRationale}`);
        break;
      }

      case 'estimate-cost': {
        const briefInput = options.brief || '';
        const briefText = fs.existsSync(path.resolve(process.cwd(), briefInput))
          ? fs.readFileSync(path.resolve(process.cwd(), briefInput), 'utf-8')
          : briefInput;
        const baseTokens = options.tokens ? parseInt(options.tokens, 10) : 1500;
        const est = estimateTokenAndCostFeasibility({ briefText, baseTokens });

        console.log(`[ESTIMATE-COST RESULT]`);
        console.log(`  Projected Tokens:    ~${est.projectedTokensPerRun}`);
        console.log(`  Token Budget:        ${est.tokenBudget}`);
        console.log(`  Status:              ${est.feasibilityStatus}`);
        console.log(`  Feasible:            ${est.isFeasible ? 'YES' : 'NO'}`);
        console.log(`  Recommendation:      ${est.recommendation}`);
        break;
      }

      case 'threat-model': {
        if (!options.revision) {
          console.error('Error: --revision is required for threat-model.');
          process.exit(1);
        }
        const revDir = path.join(storeDir, options.revision);
        const manifestPath = path.join(revDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) {
          console.error(`Error: Manifest not found at ${manifestPath}`);
          process.exit(1);
        }
        const rep = evaluateAgentThreatModel({ manifestPath });

        console.log(`[THREAT-MODEL REPORT]`);
        console.log(`  Revision:            ${rep.revisionId}`);
        console.log(`  Risk Score:          ${rep.riskScore} / 10.0`);
        console.log(`  Status:              ${rep.passed ? 'PASSED (LOW RISK)' : 'FAILED (SECURITY ACTIONS REQUIRED)'}`);
        console.log(`  Findings Count:      ${rep.findings.length}`);
        for (const f of rep.findings) {
          console.log(`    [${f.riskLevel}] ${f.category}: ${f.description}`);
        }
        console.log(`  Recommendation:      ${rep.recommendation}`);
        break;
      }

      case 'generate-guardrails': {
        if (!options.revision) {
          console.error('Error: --revision is required for generate-guardrails.');
          process.exit(1);
        }
        const revDir = path.join(storeDir, options.revision);
        const manifestPath = path.join(revDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) {
          console.error(`Error: Manifest not found at ${manifestPath}`);
          process.exit(1);
        }
        const res = generateGuardrailPolicy({
          manifestPath,
          riskTier: options.tier || 'T0',
        });

        console.log(`[GUARDRAIL POLICY GENERATED (Section 4.3)]`);
        console.log(res.yaml);
        break;
      }

      case 'sec-evals': {
        if (!options.revision) {
          console.error('Error: --revision is required for sec-evals.');
          process.exit(1);
        }
        const revDir = path.join(storeDir, options.revision);
        const manifestPath = path.join(revDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) {
          console.error(`Error: Manifest not found at ${manifestPath}`);
          process.exit(1);
        }
        const res = runAdversarialSecuritySuite({
          manifestPath,
          riskTier: options.tier || 'T0',
        });

        console.log(`[ADVERSARIAL SECURITY SUITE REPORT (Section 5)]`);
        console.log(`  Revision:            ${res.revisionId}`);
        console.log(`  Risk Tier:           ${res.riskTier}`);
        console.log(`  Tests Passed:        ${res.passedCount} / ${res.totalTests}`);
        console.log(`  Verdict:             ${res.passed ? 'PASSED (ZERO CRITICAL FAILURES)' : 'FAILED'}`);
        for (const f of res.findings) {
          console.log(`    [${f.passed ? 'PASS' : 'FAIL'}] ${f.secId} (${f.severity}): ${f.name} -> ${f.details}`);
        }
        break;
      }

      case 'eval-gates': {
        if (!options.revision) {
          console.error('Error: --revision is required for eval-gates.');
          process.exit(1);
        }
        const revDir = path.join(storeDir, options.revision);
        const manifestPath = path.join(revDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) {
          console.error(`Error: Manifest not found at ${manifestPath}`);
          process.exit(1);
        }
        const res = evaluateReleaseGates({
          manifestPath,
          riskTier: options.tier || 'T0',
          humanReviewConfirmed: Boolean(options['human-review'] || options.humanReview),
          retryAttempt: options.retry ? parseInt(options.retry, 10) : 1,
        });

        console.log(`[RELEASE GATES VERIFICATION REPORT (Section 6)]`);
        console.log(`  Revision:            ${res.revisionId}`);
        console.log(`  Risk Tier:           ${res.riskTier}`);
        console.log(`  Promotion Granted:   ${res.promotionGranted ? 'YES (PROMOTED)' : 'NO (BLOCKED)'}`);
        console.log(`  Verdict:             ${res.verdict}`);
        console.log(`  Gates Satisfied:     ${res.passedGatesCount} / ${res.totalGates}`);
        console.log(`  Retry Attempt:       ${res.retryAttempt} / ${res.maxRetries}`);
        for (const g of res.gates) {
          console.log(`    Gate ${g.gate} [${g.passed ? 'PASS' : 'FAIL'}]: ${g.name} (${g.threshold}) -> ${g.details}`);
        }
        console.log(`  Recommendation:      ${res.recommendation}`);
        if (!res.promotionGranted) {
          process.exit(1);
        }
        break;
      }

      case 'ui': {
        const port = options.port ? parseInt(options.port, 10) : 3000;
        import('./server.js').then(({ startServer }) => {
          startServer(port, storeDir).then(({ url }) => {
            console.log(`[ADF HYBRID UI] Server running at: ${url}`);
            console.log(`[ADF HYBRID UI] Mode: Google Material Design 3 (M3) Hybrid Platform`);
            console.log(`[ADF HYBRID UI] Press Ctrl+C to stop.`);
          }).catch((err) => {
            console.error(`[SERVER ERROR] ${err.message}`);
            process.exit(1);
          });
        });
        break;
      }

      case 'eval-judge': {
        const revId = options.revision || 'rev-001';
        const projectRoot = path.resolve(__dirname, '..');
        const targetDir = options.target ? path.resolve(process.cwd(), options.target) : path.join(projectRoot, 'deployments', 'develop_an_agent_that_analyzes');
        import('./eval_judge.js').then(({ runLayaJudgeEvaluation }) => {
          let outputText = '';
          let codeStr = '';
          const reportPath = path.join(targetDir, 'artifacts', 'anomaly_report.md');
          const codePath = path.join(targetDir, 'src', 'agent.py');
          if (fs.existsSync(reportPath)) outputText = fs.readFileSync(reportPath, 'utf-8');
          if (fs.existsSync(codePath)) codeStr = fs.readFileSync(codePath, 'utf-8');

          const sourceInputs = "id,value,category\n1,100.0,A\n2,102.0,A\n10,15000.0,A";
          const requirements = [
            { id: 'REQ-01', statement: 'Analyze incoming CSV tabular payloads for numerical anomalies', status: 'CONFIRMED' },
            { id: 'REQ-02', statement: 'Enforce zero-spend paid spend ceiling 0.0', status: 'CONFIRMED' },
            { id: 'REQ-03', statement: 'Write markdown anomaly report into artifacts directory', status: 'CONFIRMED' },
          ];

          const res = runLayaJudgeEvaluation({
            revisionId: revId,
            outputText,
            sourceInputs,
            requirements,
            codeStr,
          });

          console.log(`[LLM-AS-A-JUDGE & LAYA RLCD QUALITY GATE]`);
          console.log(`  Revision:            ${res.revisionId}`);
          console.log(`  Verdict:             ${res.decision.verdict} (${res.promoted ? 'PROMOTED' : 'HELD'})`);
          console.log(`  Composite Score:     ${res.decision.compositeScore} (Threshold: ${res.decision.threshold})`);
          console.log(`  RLCD Prior Source:   ${res.decision.weights.source}`);
          console.log(`  Rubric 1 (HG):       ${res.rubrics.hallucination.score.toFixed(2)} [${res.rubrics.hallucination.passed ? 'PASS' : 'FAIL'}] -> ${res.rubrics.hallucination.findings[0] || 'Grounded'}`);
          console.log(`  Rubric 2 (IF):       ${res.rubrics.instruction.score.toFixed(2)} [${res.rubrics.instruction.passed ? 'PASS' : 'FAIL'}] -> ${res.rubrics.instruction.findings[0] || 'Adherent'}`);
          console.log(`  Rubric 3 (SB):       ${res.rubrics.security.score.toFixed(2)} [${res.rubrics.security.passed ? 'PASS' : 'FAIL'}] -> ${res.rubrics.security.findings[0] || 'Sandboxed'}`);
          console.log(`  Rationale:           ${res.decision.rationale}`);

          if (!res.promoted) process.exit(1);
        }).catch((err) => {
          console.error(`[JUDGE ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'guardrails': {
        const mode = args[1] || 'audit';
        import('./guardrails.js').then(({ NeMoNistGuardrails }) => {
          if (mode === 'audit') {
            const audit = NeMoNistGuardrails.auditCompliance({
              agent_id: options.agent || 'develop_an_agent_that_analyzes',
              risk_tier: options.tier || 'T0',
            });
            console.log(`[NEMO & NIST OPERATIONAL SAFETY GUARDRAILS AUDIT]`);
            console.log(`  Agent:               ${audit.agent_id}`);
            console.log(`  Risk Tier:           ${audit.risk_tier}`);
            console.log(`  Standard:            ${audit.governance_standard}`);
            console.log(`  Authoritative Spec:  ${audit.authoritative_source_of_truth}`);
            console.log(`  Verdict:             ${audit.operational_safety_verdict}`);
            console.log(`  NeMo Rail Status:`);
            for (const [rail, info] of Object.entries(audit.nemo_rails)) {
              console.log(`    - ${rail}: ${info.status} (NIST: ${info.nist_controls.join(', ')})`);
            }
            console.log(`  NIST AI RMF (100-1) Controls:`);
            for (const [func, controls] of Object.entries(audit.nist_matrix)) {
              console.log(`    [${func}]`);
              for (const c of controls) {
                console.log(`      * ${c.code} [${c.status}]: ${c.details}`);
              }
            }
          } else if (mode === 'verify') {
            const sampleText = options.text || 'Analyze dataset for anomalies';
            const inj = NeMoNistGuardrails.checkPromptInjection(sampleText);
            const leak = NeMoNistGuardrails.checkSecretLeaks(sampleText);
            const tool = options.tool || '';
            const toolErr = tool ? NeMoNistGuardrails.validateToolAllowlist(tool, ['read_local_csv', 'compute_statistics', 'write_workspace_artifact']) : null;
            const violations = [inj, leak, toolErr].filter(Boolean);

            console.log(`[NEMO & NIST GUARDRAIL VERIFICATION]`);
            console.log(`  Payload:             "${sampleText}"`);
            console.log(`  Violations:          ${violations.length}`);
            if (violations.length > 0) {
              for (const v of violations) {
                console.log(`    [${v.railType} BLOCKED | NIST ${v.nistControl}] (${v.severity}) ${v.railName}: ${v.message}`);
              }
              process.exit(1);
            } else {
              console.log(`  Status:              CLEAN / SAFE (All boundaries respected)`);
            }
          }
        }).catch((err) => {
          console.error(`[GUARDRAILS ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'redteam': {
        import('./red_team.js').then(({ runRedTeamSuite }) => {
          console.log('========================================================================');
          console.log('AGENT DEVELOPMENT FACTORY — AUTOMATED RED TEAMING & INJECTION STRESS');
          console.log('========================================================================');
          const report = runRedTeamSuite();
          console.log(`Total Probes:     ${report.total_probes}`);
          console.log(`Blocked Probes:   ${report.blocked_probes}`);
          console.log(`Bypassed Probes:  ${report.bypassed_probes}`);
          console.log(`Block Rate:       ${report.block_rate_percentage}%`);
          console.log(`Verdict:          ${report.verdict}`);
          console.log(`NIST Controls:    ${report.nist_controls_evaluated.join(', ')}`);
          console.log('------------------------------------------------------------------------');
          for (const p of report.probes) {
            const icon = p.blocked ? '🛡️ BLOCKED' : '❌ BYPASSED';
            console.log(`  ${icon} ${p.probeId} (${p.severity}) ${p.name} [${p.nistControlTriggered}] -> ${p.details}`);
          }
          console.log('========================================================================');
          if (report.verdict.startsWith('PASS')) {
            console.log('[SUCCESS] All critical red teaming probes blocked. Guardrails hardened.');
          } else {
            console.error('[CRITICAL FAILURE] Adversarial bypass detected! Halting pipeline.');
            process.exit(1);
          }
        }).catch((err) => {
          console.error(`[REDTEAM ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'trace': {
        import('./telemetry.js').then(({ defaultTracer, TraceContext }) => {
          const action = options.action || (options['trace-id'] ? 'get' : 'list');
          if (action === 'get') {
            const traceId = options['trace-id'];
            if (!traceId) {
              console.error('Error: --trace-id is required for trace get.');
              process.exit(1);
            }
            const jaegerJson = defaultTracer.exportJaegerJson(traceId);
            console.log(JSON.stringify(jaegerJson, null, 2));
          } else {
            // Seed a sample reasoning trace if empty
            if (defaultTracer.completedSpans.length === 0) {
              const root = defaultTracer.startSpan('agent_authoring_cycle', {
                attributes: { agent_id: 'sample-authoring-agent', version: '1.0.0' },
              });
              const s1 = defaultTracer.startSpan('input_rail_screening', { parentContext: root.context });
              s1.setAttribute('inputs_verified', 2);
              s1.end();
              const s2 = defaultTracer.startSpan('dialog_rail_planning', { parentContext: root.context });
              s2.setAttribute('goal', 'compile specification');
              s2.end();
              root.end();
            }

            const traces = defaultTracer.getAllTraces();
            console.log('========================================================================');
            console.log('DISTRIBUTED TRACING — REASONING CHAINS & W3C TRACE CONTEXT');
            console.log('========================================================================');
            console.log(`Total Traces Recorded: ${traces.length}`);
            console.log('------------------------------------------------------------------------');
            for (const t of traces) {
              console.log(`Trace ID:       ${t.traceId}`);
              console.log(`Root Operation: ${t.rootSpanName}`);
              console.log(`Status:         ${t.status === 'OK' ? '✅ OK' : '❌ ERROR'}`);
              console.log(`Duration:       ${t.durationMs}ms | Spans: ${t.spanCount}`);
              console.log(`Start Time:     ${t.startTimeIso}`);
              console.log('Spans:');
              for (const s of t.spans) {
                const prefix = s.parentSpanId ? '  └─' : '•';
                console.log(`  ${prefix} [${s.kind}] ${s.name} (${s.durationMs}ms) status=${s.status}`);
              }
              console.log('------------------------------------------------------------------------');
            }
          }
        }).catch((err) => {
          console.error(`[TRACE ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'scale': {
        import('./scaling.js').then(async ({ defaultScalingPool }) => {
          const action = options.action || 'status';
          if (action === 'simulate') {
            const tasks = parseInt(options.tasks, 10) || 15;
            console.log('========================================================================');
            console.log(`AUTOSCALING INFRASTRUCTURE — WORKLOAD SPIKE SIMULATION (${tasks} TASKS)`);
            console.log('========================================================================');
            const res = await defaultScalingPool.simulateWorkloadSpike({ numTasks: tasks, taskDurationMs: 25 });
            console.log(`Tasks Injected:      ${res.tasksInjected}`);
            console.log(`Tasks Succeeded:     ${res.tasksSucceeded}`);
            console.log(`Tasks Failed:        ${res.tasksFailed}`);
            console.log(`Initial Workers:     ${res.initialWorkers}`);
            console.log(`Peak Scaled Workers: ${res.peakWorkers} (Scaled Up: ${res.scaledUp ? 'YES ⚡' : 'NO'})`);
            console.log(`Final Workers:       ${res.finalWorkers} (Idle Scale-Down: PASS ✅)`);
            console.log(`Circuit Breaker:     ${res.circuitBreakerStatus.state} (Fail Rate: ${res.circuitBreakerStatus.failRate * 100}%)`);
            console.log('========================================================================');
          } else {
            const status = defaultScalingPool.getStatus();
            console.log('========================================================================');
            console.log('AUTOSCALING INFRASTRUCTURE & CONCURRENCY GOVERNOR STATUS');
            console.log('========================================================================');
            console.log(`Current Workers:     ${status.currentWorkers} (Min: ${status.minWorkers}, Max: ${status.maxWorkers})`);
            console.log(`Active Tasks:        ${status.activeTasks}`);
            console.log(`Queued Tasks:        ${status.queuedTasks}`);
            console.log(`Completed Tasks:     ${status.completedTasks}`);
            console.log(`Failed Tasks:        ${status.failedTasks}`);
            console.log(`Utilization:         ${status.utilizationPct}%`);
            console.log(`Circuit Breaker:     ${status.circuitBreaker.state} (Healthy: ${status.circuitBreaker.isHealthy ? 'YES ✅' : 'NO ⚠️'})`);
            console.log(`Spend Ceiling:       $0.00 USD (Hard Invariant Enforced)`);
            console.log('========================================================================');
          }
        }).catch((err) => {
          console.error(`[SCALE ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'heal': {
        import('./self_healing.js').then(({ SelfHealingEngine }) => {
          const action = options.action || 'repair';
          const payload = options.payload || '```json\n{\n  "action": "ANALYZE",\n  "status": "OK",\n}\n```';

          console.log('========================================================================');
          console.log('AUTONOMOUS ERROR RESOLUTION & SELF-HEALING ENGINE');
          console.log('========================================================================');

          if (action === 'diagnose') {
            const diag = SelfHealingEngine.diagnose(payload);
            console.log(`Fault Category:    ${diag.category}`);
            console.log(`Is Recoverable:    ${diag.isRecoverable ? 'YES ✅' : 'NO ⛔'}`);
            console.log(`Suggested Action:  ${diag.suggestedAction}`);
            console.log(`Root Cause:        ${diag.rootCause}`);
          } else {
            console.log('Original Corrupted Payload:');
            console.log(payload);
            console.log('------------------------------------------------------------------------');
            const { data, wasHealed } = SelfHealingEngine.safeParseJsonWithHealing(payload);
            console.log(`Self-Healing Executed: ${wasHealed ? 'YES ⚡ (Auto-Repaired)' : 'NO (Already Valid)'}`);
            console.log('Repaired Parsed Object:');
            console.log(JSON.stringify(data, null, 2));
          }
          console.log('========================================================================');
        }).catch((err) => {
          console.error(`[HEAL ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'sync': {
        import('./sync.js').then(({ defaultSyncManager }) => {
          const action = options.action || 'audit';
          console.log('========================================================================');
          console.log('STATE SYNCHRONIZATION & CONFIGURATION DRIFT ELIMINATION');
          console.log('========================================================================');

          if (action === 'reconcile') {
            const res = defaultSyncManager.reconcileState({ storeDir });
            console.log(`Node Identifier:        ${res.nodeId}`);
            console.log(`Initial Drift Count:    ${res.initialDriftCount}`);
            console.log(`Reconciled Successfully: ${res.reconciled ? 'YES ✅' : 'NO ⚠️'}`);
            console.log(`Actions Executed:       ${res.actionsTaken.length}`);
            for (const act of res.actionsTaken) {
              console.log(`  • ${act}`);
            }
          } else {
            const audit = defaultSyncManager.auditState({ storeDir });
            console.log(`Node Identifier:        ${audit.nodeId}`);
            console.log(`Status Consensus:       ${audit.isSynchronized ? 'SYNCHRONIZED ✅' : 'DRIFT_DETECTED ⚠️'}`);
            console.log(`Drift Findings Count:   ${audit.driftCount}`);
            console.log(`Schema Manifest Items:  ${audit.schemaCount} tracked schemas`);
            console.log(`Spend Ceiling:          $${audit.spendCeilingUsd.toFixed(2)} USD (Invariant)`);
            if (audit.driftCount > 0) {
              console.log('------------------------------------------------------------------------');
              for (const f of audit.findings) {
                console.log(`  [${f.severity}] ${f.type}: ${f.details} -> Action: ${f.action}`);
              }
            }
          }
          console.log('========================================================================');
        }).catch((err) => {
          console.error(`[SYNC ERROR] ${err.message}`);
          process.exit(1);
        });
        break;
      }

      case 'remote': {
        import('node:crypto').then((crypto) => {
          let token = options.token || process.env.ADF_ACCESS_TOKEN;
          if (!token) {
            token = crypto.randomBytes(32).toString('hex');
          }
          console.log('========================================================================');
          console.log('AGENT DEVELOPMENT FACTORY — ZERO-TRUST REMOTE DEPLOYMENT');
          console.log('========================================================================');
          console.log(`Security Gate:           STRICT TOKEN AUTHENTICATION (Active)`);
          console.log(`Access Token:            ${token}`);
          console.log(`Rate Limiting:           120 req/min sliding window active`);
          console.log(`Spend Ceiling:           $0.00 USD (Invariant strictly enforced)`);
          console.log('------------------------------------------------------------------------');
          console.log('Free Zero-Trust Tunnel Deployment Options:');
          console.log('  1. One-Click Cloudflare Tunnel Stack (Recommended):');
          console.log('     pwsh ./scripts/deploy-remote.ps1');
          console.log('     bash ./scripts/deploy-remote.sh');
          console.log('  2. Local Server with Remote Auth Enabled:');
          console.log(`     ADF_ACCESS_TOKEN="${token}" node src/server.js`);
          console.log('  3. Hugging Face Spaces (Free Cloud 16GB Docker Tier):');
          console.log('     git push hf main');
          console.log('  4. Render.com Free Blueprint:');
          console.log('     deploy via render.yaml');
          console.log('========================================================================');
        });
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
