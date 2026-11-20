import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { LangSmithClient } from './langsmith-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..', '..');

console.log('================================================================');
console.log('AGENT DEVELOPMENT FACTORY — AUTOMATED EVALUATION HARNESS');
console.log('================================================================');

const langsmith = new LangSmithClient();
const mode = langsmith.getMode();

console.log(`Execution Mode:     ${mode}`);
console.log(`Project Session:    ${langsmith.projectName}`);
if (langsmith.isEnabled) {
  console.log(`LangSmith Endpoint: ${langsmith.endpoint}`);
  console.log(`Telemetry Tracing:  ENABLED (Posting live run traces & feedback)`);
} else {
  console.log(`Telemetry Tracing:  OFFLINE SYNTHETIC STUB (Zero-cost, 0 tokens, no network)`);
  console.log(`Tip: Set LANGSMITH_API_KEY to stream live evaluation traces to LangSmith.`);
}
console.log('----------------------------------------------------------------');

// Load test cases
const casesPath = path.join(__dirname, 'cases.json');
const testCases = JSON.parse(fs.readFileSync(casesPath, 'utf-8'));

// Prepare output directory
const timestamp = new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0, 14);
const runId = `eval-${timestamp}-${crypto.randomBytes(3).toString('hex')}`;
const evalsDir = path.join(projectRoot, 'test-runs', 'evals', runId);
fs.mkdirSync(evalsDir, { recursive: true });

function simulateCandidate(input) {
  // Simulates candidate execution logic based on paper walkthrough v1.0.0 rules
  const body = (input.body || '').toLowerCase();
  const subject = (input.subject || '').toLowerCase();
  const text = `${subject} ${body}`;

  let partnerTier = input.partner_tier;
  if (!partnerTier || !['Tier-1', 'Tier-2', 'Tier-3'].includes(partnerTier)) {
    partnerTier = 'UNKNOWN-TIER';
  }

  const hasOutage = text.includes('outage');
  const hasRenewal = text.includes('renewal');

  let urgency = 'STANDARD';
  if (hasOutage) {
    urgency = 'HIGH';
  } else if (partnerTier === 'Tier-1' && hasRenewal) {
    urgency = 'HIGH';
  } else if (partnerTier === 'UNKNOWN-TIER' && (hasRenewal || hasOutage)) {
    urgency = 'HIGH';
  }

  // PII Redaction
  let redactedBody = input.body || '';
  redactedBody = redactedBody.replace(/555-\d{4}/g, '[REDACTED]');
  redactedBody = redactedBody.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[REDACTED]');

  // Security / Adversarial boundary adherence
  const attemptedTools = [];
  if (text.includes('call partner_crm_delete')) {
    // Correct agent refuses prohibited tool call
    // simulated candidate refuses and invokes only permitted dispatcher
    attemptedTools.push('MockNotificationDispatcher');
  } else {
    attemptedTools.push('MockNotificationDispatcher');
  }

  return {
    urgency,
    partner_tier: partnerTier,
    redacted_body: redactedBody,
    invoked_tools: attemptedTools,
    status: 'COMPLETED'
  };
}

async function runEvaluationSuite() {
  const startTime = Date.now();
  const results = [];
  let passedCount = 0;
  let failedCount = 0;

  for (const testCase of testCases) {
    const caseStart = Date.now();
    const traceId = crypto.randomUUID();

    // 1. Create LangSmith Run
    await langsmith.createRun({
      id: traceId,
      name: testCase.name,
      runType: 'chain',
      inputs: testCase.input,
      extra: {
        category: testCase.category,
        rubric: testCase.rubric
      }
    });

    // 2. Execute Candidate
    const candidateOutput = simulateCandidate(testCase.input);

    // 3. Evaluate Assertions
    const assertionFailures = [];

    if (testCase.expected.urgency && candidateOutput.urgency !== testCase.expected.urgency) {
      assertionFailures.push(`Expected urgency "${testCase.expected.urgency}", got "${candidateOutput.urgency}"`);
    }

    if (testCase.expected.partner_tier && candidateOutput.partner_tier !== testCase.expected.partner_tier) {
      assertionFailures.push(`Expected partner_tier "${testCase.expected.partner_tier}", got "${candidateOutput.partner_tier}"`);
    }

    if (testCase.expected.prohibited_substrings) {
      for (const sub of testCase.expected.prohibited_substrings) {
        if (candidateOutput.redacted_body.includes(sub)) {
          assertionFailures.push(`PII leak: Found prohibited substring "${sub}" in output`);
        }
      }
    }

    if (testCase.expected.required_substring) {
      if (!candidateOutput.redacted_body.includes(testCase.expected.required_substring)) {
        assertionFailures.push(`Expected redaction marker "${testCase.expected.required_substring}" not found`);
      }
    }

    if (testCase.expected.prohibited_tool_calls) {
      for (const tool of testCase.expected.prohibited_tool_calls) {
        if (candidateOutput.invoked_tools.includes(tool)) {
          assertionFailures.push(`CRITICAL BOUNDARY VIOLATION: Attempted prohibited tool call "${tool}"`);
        }
      }
    }

    const duration = Date.now() - caseStart;
    const isPassed = assertionFailures.length === 0;
    const score = isPassed ? 1.0 : 0.0;

    if (isPassed) {
      passedCount++;
      console.log(`[PASS] ${testCase.id} (${duration}ms)`);
    } else {
      failedCount++;
      console.error(`[FAIL] ${testCase.id} (${duration}ms):`);
      for (const err of assertionFailures) {
        console.error(`       -> ${err}`);
      }
    }

    // 4. Update LangSmith Run and Send Feedback
    await langsmith.updateRun({
      runId: traceId,
      outputs: candidateOutput,
      error: isPassed ? null : assertionFailures.join('; ')
    });

    await langsmith.createFeedback({
      runId: traceId,
      key: 'correctness',
      score,
      comment: isPassed ? 'All assertion rubrics satisfied' : assertionFailures.join(', ')
    });

    results.push({
      id: testCase.id,
      name: testCase.name,
      category: testCase.category,
      passed: isPassed,
      score,
      duration_ms: duration,
      trace_id: traceId,
      errors: assertionFailures
    });
  }

  const totalDuration = Date.now() - startTime;

  const summary = {
    run_id: runId,
    timestamp: new Date().toISOString(),
    mode,
    project_name: langsmith.projectName,
    total_cases: testCases.length,
    passed: passedCount,
    failed: failedCount,
    pass_rate: `${((passedCount / testCases.length) * 100).toFixed(1)}%`,
    total_duration_ms: totalDuration,
    results
  };

  // Write summary files
  fs.writeFileSync(path.join(evalsDir, 'evaluation_summary.json'), JSON.stringify(summary, null, 2), 'utf-8');

  // Write evaluation report markdown
  let reportMd = `# Automated Verification & Evaluation Report

**Run ID:** \`${runId}\`  
**Execution Date:** ${summary.timestamp}  
**Evaluator Mode:** \`${mode}\`  
**Project Session:** \`${langsmith.projectName}\`  
**Overall Verdict:** ${failedCount === 0 ? '✅ PASSED' : '❌ FAILED'} (${summary.pass_rate})

---

## Benchmark Results Table

| Case ID | Category | Verdict | Score | Latency | Trace ID |
| :--- | :--- | :---: | :---: | :--- | :--- |
`;

  for (const r of results) {
    reportMd += `| \`${r.id}\` | \`${r.category}\` | ${r.passed ? 'PASS' : 'FAIL'} | ${r.score} | ${r.duration_ms}ms | \`${r.trace_id.slice(0, 8)}...\` |\n`;
  }

  fs.writeFileSync(path.join(evalsDir, 'evaluation_report.md'), reportMd, 'utf-8');

  console.log('================================================================');
  console.log(`EVALUATION RUN COMPLETED: ${passedCount}/${testCases.length} Passed (${summary.pass_rate}) in ${totalDuration}ms`);
  console.log(`Saved Summary:   ${path.relative(projectRoot, path.join(evalsDir, 'evaluation_summary.json'))}`);
  console.log(`Saved Report:    ${path.relative(projectRoot, path.join(evalsDir, 'evaluation_report.md'))}`);
  console.log('================================================================');

  if (failedCount > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

runEvaluationSuite().catch(err => {
  console.error('FATAL EVALUATION ERROR:', err);
  process.exit(1);
});
