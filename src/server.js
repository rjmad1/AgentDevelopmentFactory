/**
 * Agent Development Factory — Native HTTP Bridge Server
 * Pure Node.js (node:http, node:fs, node:path) — Zero External Runtime Dependencies
 * Hosts the Material Design Hybrid UI and provides REST API endpoints.
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  runDoctorCheck,
  triageSolutionComplexity,
  estimateTokenAndCostFeasibility,
  generateGuardrailPolicy,
  runAdversarialSecuritySuite,
  evaluateReleaseGates,
} from './core.js';
import { NeMoNistGuardrails } from './guardrails.js';
import { runRedTeamSuite } from './red_team.js';
import { defaultTracer } from './telemetry.js';
import { defaultScalingPool } from './scaling.js';
import { SelfHealingEngine } from './self_healing.js';
import { defaultSyncManager } from './sync.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const uiDir = path.join(projectRoot, 'ui');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (chunk) => {
      raw += chunk;
      if (raw.length > 10 * 1024 * 1024) {
        // 10MB limit
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => {
      if (!raw) return resolve({});
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(new Error(`Invalid JSON payload: ${err.message}`));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, statusCode, data) {
  const payload = JSON.stringify(data, null, 2);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-ADF-HITL-Approval',
  });
  res.end(payload);
}

function sendText(res, statusCode, text) {
  res.writeHead(statusCode, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
  });
  res.end(text);
}

let serverRequestCounter = 0;
const serverBootTimestamp = Date.now();

export function createAppHandler(customStoreDir = null) {
  const storeDir = customStoreDir || path.join(projectRoot, 'store');

  return async function requestHandler(req, res) {
    serverRequestCounter++;
    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;
    const method = req.method.toUpperCase();

    // CORS preflight
    if (method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-ADF-HITL-Approval',
      });
      res.end();
      return;
    }

    // ==========================================
    // REST API ENDPOINTS & SRE PROBES
    // ==========================================

    // GET /healthz (Kubernetes liveness probe)
    if ((pathname === '/healthz' || pathname === '/api/healthz') && method === 'GET') {
      sendJson(res, 200, {
        status: 'healthy',
        service: 'adf-control-plane',
        uptimeSeconds: Math.floor((Date.now() - serverBootTimestamp) / 1000),
        zeroSpendCeilingEnforced: true,
      });
      return;
    }

    // GET /readyz (Kubernetes readiness probe)
    if ((pathname === '/readyz' || pathname === '/api/readyz') && method === 'GET') {
      const scaleStatus = defaultScalingPool.getStatus();
      const cbState = scaleStatus.circuitBreaker ? scaleStatus.circuitBreaker.state : 'CLOSED';
      if (cbState === 'OPEN') {
        sendJson(res, 503, { status: 'not_ready', reason: 'circuit_breaker_open' });
        return;
      }
      sendJson(res, 200, {
        status: 'ready',
        service: 'adf-control-plane',
        uptimeSeconds: Math.floor((Date.now() - serverBootTimestamp) / 1000),
        circuitBreaker: cbState,
      });
      return;
    }

    // GET /metrics (Prometheus scrape exposition endpoint)
    if ((pathname === '/metrics' || pathname === '/api/metrics') && method === 'GET') {
      const scaleStatus = defaultScalingPool.getStatus();
      const uptimeSec = Math.floor((Date.now() - serverBootTimestamp) / 1000);
      const lines = [
        '# HELP agent_factory_http_requests_total Total HTTP requests handled',
        '# TYPE agent_factory_http_requests_total counter',
        `agent_factory_http_requests_total ${serverRequestCounter}`,
        '# HELP agent_factory_uptime_seconds Process uptime in seconds',
        '# TYPE agent_factory_uptime_seconds gauge',
        `agent_factory_uptime_seconds ${uptimeSec}`,
        '# HELP agent_factory_spend_ceiling_usd Spend ceiling in USD',
        '# TYPE agent_factory_spend_ceiling_usd gauge',
        'agent_factory_spend_ceiling_usd 0.00',
        '# HELP agent_factory_scaling_workers Number of workers in scaling pool',
        '# TYPE agent_factory_scaling_workers gauge',
        `agent_factory_scaling_workers ${scaleStatus.currentWorkers}`,
        '# HELP agent_factory_scaling_queue_depth Pending tasks in scaling pool',
        '# TYPE agent_factory_scaling_queue_depth gauge',
        `agent_factory_scaling_queue_depth ${scaleStatus.queuedTasks}`,
        '',
      ];
      const body = lines.join('\n');
      res.writeHead(200, {
        'Content-Type': 'text/plain; version=0.0.4; charset=utf-8',
        'Content-Length': Buffer.byteLength(body),
        'Access-Control-Allow-Origin': '*',
      });
      res.end(body);
      return;
    }

    // GET /api/health
    if (pathname === '/api/health' && method === 'GET') {
      try {
        const docResult = runDoctorCheck({ storeDir });
        sendJson(res, 200, {
          status: 'HEALTHY',
          timestamp: new Date().toISOString(),
          doctorReport: docResult,
          zeroSpendCeilingEnforced: true,
        });
      } catch (err) {
        sendJson(res, 500, { status: 'ERROR', error: err.message });
      }
      return;
    }

    // POST /api/triage
    if (pathname === '/api/triage' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const triageResult = triageSolutionComplexity({
          briefText: body.briefText || '',
        });
        sendJson(res, 200, {
          ...triageResult,
          type: triageResult.solutionType,
          rationale: `${triageResult.reasoning} Pattern: ${triageResult.recommendedPattern}. ${triageResult.simplicityRationale}`,
        });
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/estimate
    if (pathname === '/api/estimate' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const estimateResult = estimateTokenAndCostFeasibility({
          briefText: body.briefText || '',
          baseTokens: body.baseTokens || 1000,
        });
        sendJson(res, 200, estimateResult);
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/guardrails
    if (pathname === '/api/guardrails' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const riskTier = body.riskTier || 'T1';
        let manifestPath = body.manifestPath;

        if (!manifestPath || !fs.existsSync(manifestPath)) {
          const rev001Manifest = path.join(storeDir, 'rev-001', 'manifest.json');
          if (fs.existsSync(rev001Manifest)) {
            manifestPath = rev001Manifest;
          } else if (fs.existsSync(storeDir)) {
            const revs = fs.readdirSync(storeDir).filter((f) => f.startsWith('rev-'));
            for (const r of revs) {
              const candidate = path.join(storeDir, r, 'manifest.json');
              if (fs.existsSync(candidate)) {
                manifestPath = candidate;
                break;
              }
            }
          }
        }

        if (manifestPath && fs.existsSync(manifestPath)) {
          const policyResult = generateGuardrailPolicy({
            riskTier,
            manifestPath,
          });
          sendJson(res, 200, {
            riskTier,
            yaml: policyResult.yamlString,
            policy: policyResult.policy,
          });
        } else {
          const isT0 = riskTier === 'T0';
          const defaultYaml = `# Section 4.3 Canonical Guardrail Policy
agent: "agent-default"
version: "1.0.0"
risk_tier: "${riskTier}"
tools:
  allow:
    - read_public_data
    - compute_metrics
  deny: ${isT0 ? '\n    - write_external_record' : '[]'}
  approval_required: ${!isT0 ? '\n    - write_external_record' : '[]'}
limits:
  max_steps: 20
  max_tokens_per_run: ${isT0 ? 8000 : 50000}
  max_cost_per_run_usd: ${isT0 ? 0.0 : 0.50}
  max_wall_time_s: 60
hitl:
  confirmation_token_required: ${!isT0}
  action_on_escalation: "SUSPEND_AND_ALERT"
zero_spend_ceiling_usd: 0.00`;
          sendJson(res, 200, { riskTier, yaml: defaultYaml });
        }
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/sec-evals
    if (pathname === '/api/sec-evals' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const secResult = runAdversarialSecuritySuite({
          riskTier: body.riskTier || 'T1',
          manifestPath: body.manifestPath || null,
        });
        sendJson(res, 200, secResult);
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/eval-gates
    if (pathname === '/api/eval-gates' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const gatesResult = evaluateReleaseGates({
          riskTier: body.riskTier || 'T1',
          humanReviewConfirmed: Boolean(body.humanReviewConfirmed),
          retryAttempt: Number(body.retryAttempt || 0),
          manifestPath: body.manifestPath || null,
        });
        sendJson(res, 200, gatesResult);
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/eval-judge
    if (pathname === '/api/eval-judge' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const { runLayaJudgeEvaluation } = await import('./eval_judge.js');
        const revId = body.revisionId || 'rev-001';
        const targetDir = body.target ? path.resolve(process.cwd(), body.target) : path.join(projectRoot, 'deployments', 'develop_an_agent_that_analyzes');

        let outputText = body.outputText || '';
        let codeStr = body.codeStr || '';
        if (!outputText) {
          const reportPath = path.join(targetDir, 'artifacts', 'anomaly_report.md');
          if (fs.existsSync(reportPath)) outputText = fs.readFileSync(reportPath, 'utf-8');
        }
        if (!codeStr) {
          const codePath = path.join(targetDir, 'src', 'agent.py');
          if (fs.existsSync(codePath)) codeStr = fs.readFileSync(codePath, 'utf-8');
        }

        const sourceInputs = body.sourceInputs || 'id,value,category\n1,100.0,A\n2,102.0,A\n10,15000.0,A';
        const requirements = body.requirements || [
          { id: 'REQ-01', statement: 'Analyze incoming CSV tabular payloads for numerical anomalies', status: 'CONFIRMED' },
          { id: 'REQ-02', statement: 'Enforce zero-spend paid spend ceiling 0.0', status: 'CONFIRMED' },
          { id: 'REQ-03', statement: 'Write markdown anomaly report into artifacts directory', status: 'CONFIRMED' },
        ];

        const judgeReport = runLayaJudgeEvaluation({
          revisionId: revId,
          outputText,
          sourceInputs,
          requirements,
          codeStr,
          constraints: body.constraints || ['must not delete existing records', 'zero spend cloud API models'],
        });

        sendJson(res, 200, judgeReport);
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // GET /api/guardrails/audit
    if (pathname === '/api/guardrails/audit' && method === 'GET') {
      try {
        const audit = NeMoNistGuardrails.auditCompliance({
          agent_id: parsedUrl.searchParams.get('agent') || 'develop_an_agent_that_analyzes',
          risk_tier: parsedUrl.searchParams.get('tier') || 'T0',
        });
        sendJson(res, 200, audit);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/guardrails/verify
    if (pathname === '/api/guardrails/verify' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const text = body.text || '';
        const action = body.action || '';
        const tool = body.tool || '';
        const permittedTools = body.permittedTools || ['read_local_csv', 'compute_statistics', 'write_workspace_artifact'];

        const violations = [];

        // Input check
        if (text) {
          const inj = NeMoNistGuardrails.checkPromptInjection(text);
          if (inj) violations.push(inj);
          const leak = NeMoNistGuardrails.checkSecretLeaks(text);
          if (leak) violations.push(leak);
        }

        // Action / intent check
        if (action) {
          const drift = NeMoNistGuardrails.checkIntentDrift(action);
          if (drift) violations.push(drift);
        }

        // Tool check
        if (tool) {
          const tErr = NeMoNistGuardrails.validateToolAllowlist(tool, permittedTools);
          if (tErr) violations.push(tErr);
        }

        sendJson(res, 200, {
          passed: violations.length === 0,
          violations,
          sanitizedText: text ? NeMoNistGuardrails.sanitizePii(text) : '',
        });
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // POST /api/redteam/run
    if (pathname === '/api/redteam/run' && method === 'POST') {
      try {
        const report = runRedTeamSuite();
        sendJson(res, 200, report);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/redteam/report
    if (pathname === '/api/redteam/report' && method === 'GET') {
      try {
        const reportFile = path.join(projectRoot, 'reports', 'redteam_report.json');
        if (fs.existsSync(reportFile)) {
          const rep = JSON.parse(fs.readFileSync(reportFile, 'utf-8'));
          sendJson(res, 200, rep);
        } else {
          const fresh = runRedTeamSuite();
          sendJson(res, 200, fresh);
        }
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/traces
    if (pathname === '/api/traces' && method === 'GET') {
      try {
        if (defaultTracer.completedSpans.length === 0) {
          const root = defaultTracer.startSpan('sample_agent_run', { attributes: { agent_id: 'agent_sample' } });
          const s1 = defaultTracer.startSpan('input_rail_screening', { parentContext: root.context });
          s1.end();
          const s2 = defaultTracer.startSpan('dialog_rail_planning', { parentContext: root.context });
          s2.end();
          const s3 = defaultTracer.startSpan('tool_execution:csv_reader', { parentContext: root.context });
          s3.end();
          const s4 = defaultTracer.startSpan('output_rail_verification', { parentContext: root.context });
          s4.end();
          root.end();
        }
        const traces = defaultTracer.getAllTraces();
        sendJson(res, 200, { traces, count: traces.length });
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/traces/:id
    if (pathname.startsWith('/api/traces/') && method === 'GET') {
      try {
        const traceId = pathname.replace('/api/traces/', '');
        const jaeger = defaultTracer.exportJaegerJson(traceId);
        sendJson(res, 200, jaeger);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/scaling
    if (pathname === '/api/scaling' && method === 'GET') {
      try {
        const status = defaultScalingPool.getStatus();
        sendJson(res, 200, status);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/scaling/simulate-spike
    if (pathname === '/api/scaling/simulate-spike' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const tasks = Number(body.numTasks) || 15;
        const failFraction = Number(body.failFraction) || 0;
        const result = await defaultScalingPool.simulateWorkloadSpike({ numTasks: tasks, failFraction });
        sendJson(res, 200, result);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/heal/diagnose
    if (pathname === '/api/heal/diagnose' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const errText = body.error || 'SyntaxError: Unexpected token';
        const diag = SelfHealingEngine.diagnose(errText);
        sendJson(res, 200, diag);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/heal/repair
    if (pathname === '/api/heal/repair' && method === 'POST') {
      try {
        const body = await readJsonBody(req);
        const text = body.text || '{"status": "ok",}';
        const { data, wasHealed } = SelfHealingEngine.safeParseJsonWithHealing(text);
        sendJson(res, 200, { data, wasHealed, repairedText: JSON.stringify(data, null, 2) });
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }

    // GET /api/sync/status
    if (pathname === '/api/sync/status' && method === 'GET') {
      try {
        const audit = defaultSyncManager.auditState({ storeDir });
        sendJson(res, 200, audit);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/sync/reconcile
    if (pathname === '/api/sync/reconcile' && method === 'POST') {
      try {
        const result = defaultSyncManager.reconcileState({ storeDir });
        sendJson(res, 200, result);
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/revisions
    if (pathname === '/api/revisions' && method === 'GET') {
      try {
        if (!fs.existsSync(storeDir)) {
          sendJson(res, 200, { revisions: [] });
          return;
        }
        const entries = fs.readdirSync(storeDir, { withFileTypes: true });
        const revisions = entries
          .filter((e) => e.isDirectory() && e.name.startsWith('rev-'))
          .map((e) => e.name);
        sendJson(res, 200, { revisions });
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/events
    if (pathname === '/api/events' && method === 'GET') {
      try {
        const eventsPath = path.join(storeDir, 'check_events.jsonl');
        if (!fs.existsSync(eventsPath)) {
          sendJson(res, 200, { events: [] });
          return;
        }
        const lines = fs.readFileSync(eventsPath, 'utf-8').trim().split('\n');
        const recent = lines.slice(-50).map((l) => {
          try { return JSON.parse(l); } catch { return null; }
        }).filter(Boolean);
        sendJson(res, 200, { events: recent });
      } catch (err) {
        sendJson(res, 500, { error: err.message });
      }
      return;
    }

    // ==========================================
    // STATIC ASSETS SERVING (UI)
    // ==========================================
    let relativeFile = pathname === '/' ? 'index.html' : pathname;
    if (relativeFile.startsWith('/ui/')) {
      relativeFile = relativeFile.replace('/ui/', '');
    } else if (relativeFile.startsWith('/')) {
      relativeFile = relativeFile.slice(1);
    }

    // Prevent directory traversal
    const safePath = path.resolve(uiDir, relativeFile);
    if (!safePath.startsWith(uiDir)) {
      sendText(res, 403, 'Forbidden: Path escape blocked');
      return;
    }

    if (fs.existsSync(safePath) && fs.statSync(safePath).isFile()) {
      const ext = path.extname(safePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      const content = fs.readFileSync(safePath);
      res.writeHead(200, {
        'Content-Type': contentType,
        'Content-Length': content.length,
        'Cache-Control': 'no-cache',
      });
      res.end(content);
      return;
    }

    // 404
    sendText(res, 404, `Not Found: ${pathname}`);
  };
}

export function startServer(port = 3000, storeDir = null, host = '0.0.0.0') {
  const handler = createAppHandler(storeDir);
  const server = http.createServer(handler);

  return new Promise((resolve, reject) => {
    server.listen(port, host, () => {
      const addr = server.address();
      const actualPort = typeof addr === 'object' && addr ? addr.port : port;
      resolve({
        server,
        port: actualPort,
        url: `http://${host === '0.0.0.0' ? '127.0.0.1' : host}:${actualPort}`,
        close: () => new Promise((res) => server.close(res)),
      });
    });
    server.on('error', reject);
  });
}

// Auto-start server when executed directly: `node src/server.js`
const isMainModule = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename);
if (isMainModule) {
  const port = parseInt(process.env.PORT || process.env.ADF_PORT || '3000', 10);
  const host = process.env.ADF_HOST || '0.0.0.0';
  startServer(port, null, host).then(({ port, url }) => {
    console.log(`[ADF SERVER] Control Plane & Material UI running at http://${host}:${port} (${url})`);
    console.log(`[ADF SERVER] Enforcing strict $0.00 spend ceiling.`);
  }).catch((err) => {
    console.error(`[ADF SERVER] Fatal startup error:`, err);
    process.exit(1);
  });
}

