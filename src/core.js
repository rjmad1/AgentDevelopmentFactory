import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const CHECKER_ENGINE_VERSION = '0.3.0';

export function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

export function deterministicJsonString(obj) {
  return JSON.stringify(sortKeysRecursively(obj), null, 2);
}

function sortKeysRecursively(value) {
  if (Array.isArray(value)) {
    return value.map(sortKeysRecursively);
  }
  if (value !== null && typeof value === 'object') {
    const sorted = {};
    for (const key of Object.keys(value).sort()) {
      sorted[key] = sortKeysRecursively(value[key]);
    }
    return sorted;
  }
  return value;
}

export function validateIdentifier(id, fieldName = 'identifier') {
  if (typeof id !== 'string' || !/^[a-zA-Z0-9_-]{1,64}$/.test(id)) {
    throw new Error(`INVALID_IDENTIFIER: ${fieldName} "${id}" is invalid. Must be 1-64 alphanumeric, dash, or underscore characters without path separators.`);
  }
  return id;
}

export function assertRealFsContainment(allowedParentDir, targetPath) {
  // 1. Lexical containment check
  const resolvedParent = path.resolve(allowedParentDir);
  const resolvedTarget = path.resolve(targetPath);
  if (resolvedTarget !== resolvedParent && !resolvedTarget.startsWith(resolvedParent + path.sep)) {
    throw new Error(`PATH_TRAVERSAL_DETECTED: Target path "${targetPath}" escapes parent directory "${allowedParentDir}".`);
  }

  // 2. Real filesystem inspection
  let realParent = resolvedParent;
  if (fs.existsSync(resolvedParent)) {
    realParent = fs.realpathSync.native ? fs.realpathSync.native(resolvedParent) : fs.realpathSync(resolvedParent);
  }

  // Walk up from targetPath to allowedParentDir checking existing components
  let current = resolvedTarget;
  const componentsToCheck = [];
  while (current.length >= resolvedParent.length) {
    componentsToCheck.push(current);
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }

  // Check each component from top down
  for (let i = componentsToCheck.length - 1; i >= 0; i--) {
    const comp = componentsToCheck[i];
    if (fs.existsSync(comp)) {
      const lstat = fs.lstatSync(comp);
      if (lstat.isSymbolicLink()) {
        throw new Error(`SYMLINK_ESCAPE_DETECTED: Path contains a symbolic link/junction: "${comp}". Symlink escapes are rejected by containment policy.`);
      }
      const realComp = fs.realpathSync.native ? fs.realpathSync.native(comp) : fs.realpathSync(comp);
      if (realComp !== realParent && !realComp.startsWith(realParent + path.sep)) {
        throw new Error(`FILESYSTEM_ESCAPE_DETECTED: Real filesystem path "${realComp}" escapes allowed directory "${realParent}".`);
      }
    }
  }

  return resolvedTarget;
}

export function getCheckerImplementationHash() {
  const checkRulesDefinition = {
    checkerEngineVersion: CHECKER_ENGINE_VERSION,
    rules: {
      'CHK-STATIC-SCHEMA': 'manifestSchemaValidation_specSha256Match_inputsSha256Match',
      'CHK-REQUIREMENTS-TRIAGE': 'strictSuppliedHumanAssertionValidation_noPromotedInferredDefaults',
      'CHK-EVAL-SUPERVISED-RUNTIME': 'blockedPrerequisiteDeclaration_v1ScopeIndicator',
    },
  };
  return sha256(deterministicJsonString(checkRulesDefinition));
}

export function evaluateEvidenceApplicability(check, currentArtifactHashes, currentCheckerHash) {
  // Check artifact dependencies
  if (check.inputs) {
    if (currentArtifactHashes.requirementsSha256 && check.inputs.requirementsSha256 && currentArtifactHashes.requirementsSha256 !== check.inputs.requirementsSha256) {
      return { isCurrent: false, applicability: 'STALE', reason: 'ARTIFACT_DEPENDENCY_CHANGED: Requirements hash changed from evaluation input.' };
    }
    if (currentArtifactHashes.briefSha256 && check.inputs.briefSha256 && currentArtifactHashes.briefSha256 !== check.inputs.briefSha256) {
      return { isCurrent: false, applicability: 'STALE', reason: 'ARTIFACT_DEPENDENCY_CHANGED: Brief hash changed from evaluation input.' };
    }
    if (currentArtifactHashes.specSha256 && check.inputs.specSha256 && currentArtifactHashes.specSha256 !== check.inputs.specSha256) {
      return { isCurrent: false, applicability: 'STALE', reason: 'ARTIFACT_DEPENDENCY_CHANGED: Specification hash changed from evaluation input.' };
    }
  }

  // Check checker implementation dependency
  if (check.checker && check.checker.implementationSha256) {
    if (currentCheckerHash && check.checker.implementationSha256 !== currentCheckerHash) {
      return { isCurrent: false, applicability: 'STALE', reason: 'CHECKER_IMPLEMENTATION_CHANGED: Checker implementation version/hash changed since check was executed.' };
    }
  }

  return { isCurrent: true, applicability: check.status, reason: 'APPLICABLE: Artifact and checker dependencies match.' };
}

export function verifyEvidenceConsistency(revDir) {
  const eventsLogPath = path.join(revDir, 'check_events.jsonl');
  const evidencePath = path.join(revDir, 'evidence.json');

  if (!fs.existsSync(evidencePath)) {
    return {
      isConsistent: false,
      reason: 'MISSING_EVIDENCE_LEDGER: evidence.json does not exist.',
    };
  }
  if (!fs.existsSync(eventsLogPath)) {
    return {
      isConsistent: false,
      reason: 'MISSING_EVENT_LOG: check_events.jsonl does not exist.',
    };
  }

  const logContent = fs.readFileSync(eventsLogPath, 'utf-8');
  const lines = logContent.split('\n').map(l => l.trim()).filter(Boolean);
  const logEvents = [];
  for (let i = 0; i < lines.length; i++) {
    try {
      logEvents.push(JSON.parse(lines[i]));
    } catch (err) {
      return {
        isConsistent: false,
        reason: `MALFORMED_EVENT_LOG: Line ${i + 1} in check_events.jsonl is not valid JSON (${err.message}).`,
      };
    }
  }

  let evidence;
  try {
    evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf-8'));
  } catch (err) {
    return {
      isConsistent: false,
      reason: `MALFORMED_EVIDENCE_JSON: evidence.json is not valid JSON (${err.message}).`,
    };
  }

  const ledgerEvents = Array.isArray(evidence.events) ? evidence.events : [];

  if (logEvents.length !== ledgerEvents.length) {
    return {
      isConsistent: false,
      reason: `EVENT_COUNT_MISMATCH: Authoritative check_events.jsonl has ${logEvents.length} events, but evidence.json ledger has ${ledgerEvents.length} events.`,
    };
  }

  for (let i = 0; i < logEvents.length; i++) {
    const le = logEvents[i];
    const ee = ledgerEvents[i];
    if (le.eventId !== ee.eventId || le.checkId !== ee.checkId || le.status !== ee.status || le.exitCode !== ee.exitCode) {
      return {
        isConsistent: false,
        reason: `EVENT_DATA_MISMATCH: Event ${i + 1} differs between check_events.jsonl and evidence.json.`,
      };
    }
  }

  // Check consolidated checks
  for (const check of evidence.checks) {
    const checkLogEvents = logEvents.filter(e => e.checkId === check.checkId);
    if ((check.executionCount || 0) !== checkLogEvents.length) {
      return {
        isConsistent: false,
        reason: `EXECUTION_COUNT_MISMATCH: Check "${check.checkId}" executionCount (${check.executionCount}) does not match log event count (${checkLogEvents.length}).`,
      };
    }
    if (checkLogEvents.length > 0) {
      const latest = checkLogEvents[checkLogEvents.length - 1];
      if (check.status !== latest.status) {
        return {
          isConsistent: false,
          reason: `CHECK_STATUS_MISMATCH: Check "${check.checkId}" status in evidence.json (${check.status}) does not match latest log status (${latest.status}).`,
        };
      }
    } else {
      if (check.status !== check.initialStatus) {
        return {
          isConsistent: false,
          reason: `UNEXECUTED_STATUS_MUTATED: Check "${check.checkId}" has 0 log events but status (${check.status}) differs from initialStatus (${check.initialStatus}).`,
        };
      }
    }
  }

  return {
    isConsistent: true,
    totalEvents: logEvents.length,
    reason: 'CONSISTENT: check_events.jsonl audit log matches evidence.json materialized ledger 100%.',
  };
}

export function validateRequirements(requirements) {
  if (!Array.isArray(requirements) || requirements.length === 0) {
    throw new Error('INVALID_REQUIREMENTS: Requirements must be a non-empty array of requirement objects.');
  }

  for (const req of requirements) {
    if (!req.id || typeof req.id !== 'string') {
      throw new Error(`INVALID_REQUIREMENT_ID: Requirement is missing a valid 'id' string.`);
    }
    validateIdentifier(req.id, 'requirement.id');

    if (!req.title || typeof req.title !== 'string') {
      throw new Error(`INVALID_REQUIREMENT_TITLE: Requirement '${req.id}' is missing a valid 'title'.`);
    }
    if (!req.statement || typeof req.statement !== 'string') {
      throw new Error(`INVALID_REQUIREMENT_STATEMENT: Requirement '${req.id}' is missing a valid 'statement'.`);
    }

    const validStatuses = ['CONFIRMED', 'PROPOSED', 'UNRESOLVED'];
    if (!validStatuses.includes(req.status)) {
      throw new Error(`INVALID_REQUIREMENT_STATUS: Requirement '${req.id}' status '${req.status}' must be one of: ${validStatuses.join(', ')}.`);
    }

    if (req.status === 'CONFIRMED') {
      if (!req.confirmation || typeof req.confirmation !== 'object') {
        throw new Error(`CONFIRMATION_RECORD_MISSING: Requirement '${req.id}' is marked CONFIRMED but lacks an explicit supplied human confirmation record.`);
      }

      const { assertionType, authenticated, confirmedBy, confirmedAt, synthetic } = req.confirmation;

      if (assertionType !== 'SUPPLIED_HUMAN_ASSERTION') {
        throw new Error(`INVALID_CONFIRMATION_ASSERTION: Requirement '${req.id}' confirmation must specify assertionType: "SUPPLIED_HUMAN_ASSERTION".`);
      }
      if (authenticated !== false) {
        throw new Error(`AUTHENTICATION_CLAIM_PROHIBITED: Requirement '${req.id}' confirmation must explicitly record authenticated: false (the CLI records supplied assertions; it does not authenticate humans).`);
      }
      if (!confirmedBy || typeof confirmedBy !== 'string' || confirmedBy.trim() === '') {
        throw new Error(`CONFIRMATION_ACTOR_MISSING: Requirement '${req.id}' confirmation record must include a non-empty 'confirmedBy' string.`);
      }
      if (!confirmedAt || typeof confirmedAt !== 'string' || confirmedAt.trim() === '') {
        throw new Error(`CONFIRMATION_TIMESTAMP_MISSING: Requirement '${req.id}' confirmation record must include a non-empty 'confirmedAt' timestamp.`);
      }
      if (synthetic !== true) {
        throw new Error(`SYNTHETIC_PROVENANCE_REQUIRED: Requirement '${req.id}' confirmation must explicitly declare synthetic: true in synthetic demo fixtures. Real user approvals must not be claimed.`);
      }
    } else if (req.status === 'PROPOSED') {
      if (!req.proposedBy || typeof req.proposedBy !== 'string') {
        throw new Error(`PROPOSAL_METADATA_MISSING: Requirement '${req.id}' is marked PROPOSED but lacks 'proposedBy'.`);
      }
      if (!req.rationale || typeof req.rationale !== 'string') {
        throw new Error(`PROPOSAL_RATIONALE_MISSING: Requirement '${req.id}' is marked PROPOSED but lacks 'rationale'.`);
      }
    } else if (req.status === 'UNRESOLVED') {
      if (!req.question || typeof req.question !== 'string') {
        throw new Error(`UNRESOLVED_QUESTION_MISSING: Requirement '${req.id}' is marked UNRESOLVED but lacks 'question'.`);
      }
    }
  }

  return true;
}

export function generateSpecMarkdown({
  revisionId,
  parentRevisionId,
  briefText,
  requirements,
  hashes,
  createdAt,
}) {
  const confirmed = requirements.filter(r => r.status === 'CONFIRMED');
  const proposed = requirements.filter(r => r.status === 'PROPOSED');
  const unresolved = requirements.filter(r => r.status === 'UNRESOLVED');

  let md = `# Agent Specification — Revision ${revisionId}\n\n`;
  md += `**Revision ID:** \`${revisionId}\`  \n`;
  md += `**Parent Revision:** \`${parentRevisionId || 'None (Initial Revision)'}\`  \n`;
  md += `**Created At:** \`${createdAt}\`  \n`;
  md += `**Input SHA-256:** \`${hashes.inputSha256}\`  \n`;
  md += `**Brief SHA-256:** \`${hashes.briefSha256}\`  \n`;
  md += `**Requirements SHA-256:** \`${hashes.requirementsSha256}\`  \n\n`;

  md += `> [!NOTE]\n`;
  md += `> **GOVERNANCE & EVIDENCE BOUNDARY**  \n`;
  md += `> This specification is an inspectable design artifact produced by the Agent Development Factory authoring slice. It distinguishes explicitly confirmed requirements from proposed defaults and open ambiguities. Static/schema validation checks verify only document formatting and manifest completeness; they do not validate agent quality, behavioral safety, or model security. Supervised runtime evaluation is a separate v1 capability and is not executed by this authoring slice.\n\n`;

  md += `---\n\n`;
  md += `## 1. Context & Business Workflow Brief\n\n`;
  md += `\`\`\`text\n${briefText.trim()}\n\`\`\`\n\n`;

  md += `---\n\n`;
  md += `## 2. Requirements & Governance Ledger\n\n`;

  md += `### 2.1 Confirmed Requirements (${confirmed.length})\n\n`;
  if (confirmed.length === 0) {
    md += `*No requirements confirmed yet.*\n\n`;
  } else {
    md += `| ID | Title | Statement | Assertion Type | Confirmed By (Synthetic) | Confirmed At | Note |\n`;
    md += `| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n`;
    for (const r of confirmed) {
      const note = r.confirmation.note || 'None';
      md += `| \`${r.id}\` | **${escapePipes(r.title)}** | ${escapePipes(r.statement)} | \`Supplied (Unauthenticated)\` | \`${escapePipes(r.confirmation.confirmedBy)}\` | \`${escapePipes(r.confirmation.confirmedAt)}\` | ${escapePipes(note)} |\n`;
    }
    md += `\n`;
  }

  md += `### 2.2 Proposed Defaults (Awaiting Human Sign-Off) (${proposed.length})\n\n`;
  if (proposed.length === 0) {
    md += `*No proposed defaults active.*\n\n`;
  } else {
    md += `| ID | Title | Proposed Statement | Proposed By | Inferred Rationale |\n`;
    md += `| :--- | :--- | :--- | :--- | :--- |\n`;
    for (const r of proposed) {
      md += `| \`${r.id}\` | **${escapePipes(r.title)}** | ${escapePipes(r.statement)} | \`${escapePipes(r.proposedBy)}\` | ${escapePipes(r.rationale)} |\n`;
    }
    md += `\n`;
  }

  md += `### 2.3 Unresolved Questions & Ambiguities (${unresolved.length})\n\n`;
  if (unresolved.length === 0) {
    md += `*No unresolved items pending.*\n\n`;
  } else {
    md += `| ID | Title | Open Question | Options / Candidate Paths |\n`;
    md += `| :--- | :--- | :--- | :--- |\n`;
    for (const r of unresolved) {
      const options = Array.isArray(r.options) && r.options.length > 0 ? r.options.join(', ') : 'Open-ended';
      md += `| \`${r.id}\` | **${escapePipes(r.title)}** | ${escapePipes(r.question)} | ${escapePipes(options)} |\n`;
    }
    md += `\n`;
  }

  md += `---\n\n`;
  md += `## 3. Structural Boundaries & Action Permissions\n\n`;
  md += `* **Executable Agent Code:** None generated in this authoring slice. Generated agent code and candidate runners are prohibited by boundary.\n`;
  md += `* **Tool Execution:** No live tools, mock servers, or external network requests are executed.\n`;
  md += `* **Human Confirmation Rule:** Inferred logic and proposed defaults remain explicitly flagged as PROPOSED until a supplied human confirmation record is submitted.\n`;
  md += `* **Supplied Assertion Caveat:** Confirmed requirements record supplied assertions only; they do not authenticate user identity or imply executive authorization.\n\n`;

  return md;
}

function escapePipes(str) {
  return String(str).replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

export function generateManifest({
  revisionId,
  parentRevisionId,
  briefText,
  requirements,
  hashes,
  createdAt,
}) {
  const confirmed = requirements.filter(r => r.status === 'CONFIRMED');
  const proposed = requirements.filter(r => r.status === 'PROPOSED');
  const unresolved = requirements.filter(r => r.status === 'UNRESOLVED');

  return {
    factorySchemaVersion: '0.3.0',
    revisionId,
    parentRevisionId: parentRevisionId || null,
    createdAt,
    hashes: {
      inputSha256: hashes.inputSha256,
      briefSha256: hashes.briefSha256,
      requirementsSha256: hashes.requirementsSha256,
      specSha256: hashes.specSha256,
    },
    brief: {
      length: briefText.length,
      snippet: briefText.trim().slice(0, 200),
    },
    triageSummary: {
      total: requirements.length,
      confirmedCount: confirmed.length,
      proposedCount: proposed.length,
      unresolvedCount: unresolved.length,
    },
    requirements,
    unresolvedItems: unresolved.map(u => ({
      id: u.id,
      title: u.title,
      question: u.question,
      options: u.options || [],
    })),
    artifactFiles: ['spec.md', 'manifest.json', 'evidence.json', 'inputs.json', 'check_events.jsonl'],
  };
}

export function initRevision({
  storeDir,
  revisionId,
  parentRevisionId = null,
  briefPath,
  requirementsPath,
}) {
  validateIdentifier(revisionId, 'revisionId');
  if (parentRevisionId) {
    validateIdentifier(parentRevisionId, 'parentRevisionId');
  }

  // Real filesystem containment for storeDir and revDir
  const resolvedStoreDir = path.resolve(storeDir);
  if (!fs.existsSync(resolvedStoreDir)) {
    fs.mkdirSync(resolvedStoreDir, { recursive: true });
  }

  const revDir = path.join(resolvedStoreDir, revisionId);
  assertRealFsContainment(resolvedStoreDir, revDir);

  // Exclusive directory creation to enforce revision immutability
  try {
    fs.mkdirSync(revDir, { recursive: false });
  } catch (err) {
    if (err.code === 'EEXIST') {
      throw new Error(`REVISION_EXISTS: Revision "${revisionId}" already exists and cannot be overwritten. Revisions are immutable by policy.`);
    }
    throw err;
  }

  const briefText = fs.readFileSync(briefPath, 'utf-8');
  const requirementsRaw = fs.readFileSync(requirementsPath, 'utf-8');
  const requirements = JSON.parse(requirementsRaw);

  validateRequirements(requirements);

  const createdAt = new Date().toISOString();
  const briefSha256 = sha256(briefText);
  const requirementsSha256 = sha256(deterministicJsonString(requirements));
  const inputSha256 = sha256(briefSha256 + requirementsSha256);

  const hashes = {
    briefSha256,
    requirementsSha256,
    inputSha256,
    specSha256: '', // populated below
  };

  // Generate and write spec.md
  const specMd = generateSpecMarkdown({
    revisionId,
    parentRevisionId,
    briefText,
    requirements,
    hashes,
    createdAt,
  });
  hashes.specSha256 = sha256(specMd);
  fs.writeFileSync(path.join(revDir, 'spec.md'), specMd, 'utf-8');

  // Generate and write manifest.json
  const manifest = generateManifest({
    revisionId,
    parentRevisionId,
    briefText,
    requirements,
    hashes,
    createdAt,
  });
  fs.writeFileSync(path.join(revDir, 'manifest.json'), deterministicJsonString(manifest), 'utf-8');

  // Write inputs audit copy
  const inputsAudit = {
    revisionId,
    createdAt,
    brief: briefText,
    requirements,
  };
  fs.writeFileSync(path.join(revDir, 'inputs.json'), deterministicJsonString(inputsAudit), 'utf-8');

  // Initialize empty append-only check event log
  fs.writeFileSync(path.join(revDir, 'check_events.jsonl'), '', 'utf-8');

  const checkerImplementationSha256 = getCheckerImplementationHash();

  // Build evidence ledger
  let checks = [];

  if (parentRevisionId) {
    const parentRevDir = path.join(resolvedStoreDir, parentRevisionId);
    assertRealFsContainment(resolvedStoreDir, parentRevDir);
    if (!fs.existsSync(parentRevDir)) {
      throw new Error(`PARENT_REVISION_NOT_FOUND: Parent revision "${parentRevisionId}" does not exist in store.`);
    }
    const parentManifest = JSON.parse(fs.readFileSync(path.join(parentRevDir, 'manifest.json'), 'utf-8'));
    const parentEvidence = JSON.parse(fs.readFileSync(path.join(parentRevDir, 'evidence.json'), 'utf-8'));

    const currentArtifactHashes = {
      briefSha256,
      requirementsSha256,
      specSha256: hashes.specSha256,
    };

    for (const parentCheck of parentEvidence.checks) {
      const inherited = { ...parentCheck };
      inherited.sourceRevision = parentCheck.sourceRevision || parentRevisionId;
      inherited.executionCount = 0;
      inherited.history = [];

      if (parentCheck.status === 'PASSED' || parentCheck.status === 'FAILED') {
        const evalResult = evaluateEvidenceApplicability(parentCheck, currentArtifactHashes, checkerImplementationSha256);
        if (!evalResult.isCurrent) {
          inherited.initialStatus = 'STALE';
          inherited.status = 'STALE';
          inherited.staleReason = `${evalResult.reason} Prior record in ${parentRevisionId} remains intact; evidence is STALE for ${revisionId}.`;
          inherited.executedAt = parentCheck.executedAt;
          inherited.command = `node src/cli.js run-check --revision ${revisionId} --check ${parentCheck.checkId}`;
        } else {
          inherited.initialStatus = 'PASSED';
          inherited.status = 'PASSED';
          inherited.note = `Inherited unchanged from parent revision ${parentRevisionId}.`;
        }
      }
      checks.push(inherited);
    }
  } else {
    checks = [
      {
        checkId: 'CHK-STATIC-SCHEMA',
        name: 'Manifest Schema & Hash Integrity Check',
        scope: 'Verifies manifest.json structure, required fields, and artifact file hash consistency',
        sourceRevision: revisionId,
        initialStatus: 'NOT RUN',
        status: 'NOT RUN',
        executionCount: 0,
        history: [],
        checker: {
          version: CHECKER_ENGINE_VERSION,
          implementationSha256: checkerImplementationSha256,
          schemaVersion: '0.3.0',
        },
        inputs: {
          manifestSha256: sha256(deterministicJsonString(manifest)),
          specSha256: hashes.specSha256,
          briefSha256: hashes.briefSha256,
          requirementsSha256: hashes.requirementsSha256,
          checkerImplementationSha256,
        },
        command: `node src/cli.js run-check --revision ${revisionId} --check CHK-STATIC-SCHEMA`,
        executedAt: null,
        exitCode: null,
        output: null,
        error: null,
        limitationNotes: 'Verifies static document format and cryptographic file hashes only. Does not prove agent quality or safety.',
      },
      {
        checkId: 'CHK-REQUIREMENTS-TRIAGE',
        name: 'Requirement Provenance & Triage Integrity Check',
        scope: 'Verifies that all CONFIRMED requirements possess explicit human confirmation records and no inferred text was promoted',
        sourceRevision: revisionId,
        initialStatus: 'NOT RUN',
        status: 'NOT RUN',
        executionCount: 0,
        history: [],
        checker: {
          version: CHECKER_ENGINE_VERSION,
          implementationSha256: checkerImplementationSha256,
          schemaVersion: '0.3.0',
        },
        inputs: {
          requirementsSha256,
          checkerImplementationSha256,
        },
        command: `node src/cli.js run-check --revision ${revisionId} --check CHK-REQUIREMENTS-TRIAGE`,
        executedAt: null,
        exitCode: null,
        output: null,
        error: null,
        limitationNotes: 'Verifies triage metadata syntax and confirmed provenance assertions. Does not authenticate human identity.',
      },
      {
        checkId: 'CHK-EVAL-SUPERVISED-RUNTIME',
        name: 'Supervised Runtime Evaluation Harness',
        scope: 'Execution of candidate agent against behavioral test cases and security injection probes',
        sourceRevision: revisionId,
        initialStatus: 'BLOCKED',
        status: 'BLOCKED',
        executionCount: 0,
        history: [],
        checker: {
          version: CHECKER_ENGINE_VERSION,
          implementationSha256: checkerImplementationSha256,
          schemaVersion: '0.3.0',
        },
        inputs: {},
        command: null,
        executedAt: null,
        exitCode: null,
        output: null,
        error: 'PREREQUISITE_BLOCKED: Supervised evaluation harness, container environment, and runtime models are not in scope for this static authoring slice.',
        limitationNotes: 'Prerequisite blocked by policy; not executable by this slice. Retained in ledger to preserve v1 scope visibility.',
      },
    ];
  }

  const evidence = {
    revisionId,
    parentRevisionId: parentRevisionId || null,
    createdAt,
    lastUpdated: createdAt,
    disclaimer: 'Static/schema checks prove only stated structural properties, not agent quality, behavioral safety or security. Supervised runtime evaluation is in v1 product scope but is not built by this static authoring slice.',
    events: [],
    checks,
  };

  fs.writeFileSync(path.join(revDir, 'evidence.json'), deterministicJsonString(evidence), 'utf-8');

  return {
    revisionId,
    parentRevisionId,
    revDir,
    hashes,
    triageSummary: manifest.triageSummary,
    checkSummary: {
      total: checks.length,
      notRun: checks.filter(c => c.status === 'NOT RUN').length,
      passed: checks.filter(c => c.status === 'PASSED').length,
      failed: checks.filter(c => c.status === 'FAILED').length,
      stale: checks.filter(c => c.status === 'STALE').length,
      blocked: checks.filter(c => c.status === 'BLOCKED').length,
    },
  };
}

export function runCheck({
  storeDir,
  revisionId,
  checkId,
  failIntentionally = false,
  customCheckerImplementationHash = null,
}) {
  validateIdentifier(revisionId, 'revisionId');
  validateIdentifier(checkId, 'checkId');

  const resolvedStoreDir = path.resolve(storeDir);
  const revDir = path.join(resolvedStoreDir, revisionId);
  assertRealFsContainment(resolvedStoreDir, revDir);

  if (!fs.existsSync(revDir)) {
    throw new Error(`REVISION_NOT_FOUND: Revision "${revisionId}" does not exist in store.`);
  }

  const evidencePath = path.join(revDir, 'evidence.json');
  const manifestPath = path.join(revDir, 'manifest.json');
  const specPath = path.join(revDir, 'spec.md');
  const inputsPath = path.join(revDir, 'inputs.json');
  const eventsLogPath = path.join(revDir, 'check_events.jsonl');

  const evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf-8'));
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  if (!Array.isArray(evidence.events)) {
    evidence.events = [];
  }

  let check = evidence.checks.find(c => c.checkId === checkId);
  const activeCheckerHash = customCheckerImplementationHash || getCheckerImplementationHash();

  if (!check) {
    if (checkId === 'CHK-FAIL-DEMO') {
      check = {
        checkId: 'CHK-FAIL-DEMO',
        name: 'Honest Failure Demonstration Check',
        scope: 'Demonstrates honest failure detection and error recording',
        sourceRevision: revisionId,
        initialStatus: 'NOT RUN',
        status: 'NOT RUN',
        executionCount: 0,
        history: [],
        checker: {
          version: CHECKER_ENGINE_VERSION,
          implementationSha256: activeCheckerHash,
          schemaVersion: '0.3.0',
        },
        inputs: {},
        command: `node src/cli.js run-check --revision ${revisionId} --check CHK-FAIL-DEMO`,
        executedAt: null,
        exitCode: null,
        output: null,
        error: null,
        limitationNotes: 'Intentional failing check to verify error ledger integrity.',
      };
      evidence.checks.push(check);
    } else {
      throw new Error(`CHECK_NOT_FOUND: Check "${checkId}" is not registered in revision "${revisionId}".`);
    }
  }

  if (check.status === 'BLOCKED') {
    return {
      checkId,
      status: 'BLOCKED',
      exitCode: null,
      message: check.error || 'Check is blocked due to unfulfilled prerequisites.',
    };
  }

  const executedAt = new Date().toISOString();
  let resultStatus = 'FAILED';
  let exitCode = 1;
  let output = null;
  let error = null;

  if (failIntentionally || checkId === 'CHK-FAIL-DEMO') {
    resultStatus = 'FAILED';
    exitCode = 1;
    output = null;
    error = 'HONEST_FAILURE: Check detected intentional violation or missing schema element. Failure recorded honestly without masking.';
  } else if (checkId === 'CHK-STATIC-SCHEMA') {
    try {
      if (!manifest.revisionId || !manifest.hashes || !manifest.requirements) {
        throw new Error('Manifest missing required schema keys.');
      }
      const currentSpecMd = fs.readFileSync(specPath, 'utf-8');
      const calculatedSpecSha = sha256(currentSpecMd);
      if (calculatedSpecSha !== manifest.hashes.specSha256) {
        throw new Error(`Spec hash mismatch: expected ${manifest.hashes.specSha256}, calculated ${calculatedSpecSha}`);
      }

      if (fs.existsSync(inputsPath)) {
        const inputsObj = JSON.parse(fs.readFileSync(inputsPath, 'utf-8'));
        const briefSha = sha256(inputsObj.brief);
        const reqsSha = sha256(deterministicJsonString(inputsObj.requirements));
        if (briefSha !== manifest.hashes.briefSha256) {
          throw new Error(`Brief hash in inputs.json does not match manifest.`);
        }
        if (reqsSha !== manifest.hashes.requirementsSha256) {
          throw new Error(`Requirements hash in inputs.json does not match manifest.`);
        }
      }

      resultStatus = 'PASSED';
      exitCode = 0;
      output = 'PASSED: Manifest JSON schema valid; spec.md & inputs.json SHA-256 verified; artifact integrity confirmed.';
      error = null;
    } catch (err) {
      resultStatus = 'FAILED';
      exitCode = 1;
      output = null;
      error = `SCHEMA_VERIFICATION_FAILED: ${err.message}`;
    }
  } else if (checkId === 'CHK-REQUIREMENTS-TRIAGE') {
    try {
      validateRequirements(manifest.requirements);
      const confirmedCount = manifest.requirements.filter(r => r.status === 'CONFIRMED').length;
      resultStatus = 'PASSED';
      exitCode = 0;
      output = `PASSED: Triage integrity verified (${confirmedCount} confirmed requirements verified with explicit supplied confirmation records; 0 promoted inferred defaults).`;
      error = null;
    } catch (err) {
      resultStatus = 'FAILED';
      exitCode = 1;
      output = null;
      error = `TRIAGE_VERIFICATION_FAILED: ${err.message}`;
    }
  } else {
    resultStatus = 'FAILED';
    exitCode = 2;
    output = null;
    error = `UNSUPPORTED_CHECK: Check '${checkId}' execution logic is not implemented.`;
  }

  // Update check metadata
  if (!check.checker) {
    check.checker = {};
  }
  check.checker.version = CHECKER_ENGINE_VERSION;
  check.checker.implementationSha256 = activeCheckerHash;
  check.checker.schemaVersion = '0.3.0';

  // Record append-only event
  const event = {
    eventId: evidence.events.length + 1,
    checkId,
    executedAt,
    sourceRevision: revisionId,
    checkerImplementationSha256: activeCheckerHash,
    status: resultStatus,
    exitCode,
    output,
    error,
    inputsSha256: check.inputs ? check.inputs.requirementsSha256 || check.inputs.manifestSha256 || null : null,
  };
  evidence.events.push(event);

  // Append to check_events.jsonl
  fs.appendFileSync(eventsLogPath, JSON.stringify(event) + '\n', 'utf-8');

  // Update consolidated check view
  check.status = resultStatus;
  check.executedAt = executedAt;
  check.exitCode = exitCode;
  check.output = output;
  check.error = error;
  check.executionCount = (check.executionCount || 0) + 1;
  if (!Array.isArray(check.history)) {
    check.history = [];
  }
  check.history.push({
    eventId: event.eventId,
    executedAt,
    checkerImplementationSha256: activeCheckerHash,
    status: resultStatus,
    exitCode,
  });

  evidence.lastUpdated = executedAt;
  fs.writeFileSync(evidencePath, deterministicJsonString(evidence), 'utf-8');

  return {
    checkId,
    status: resultStatus,
    exitCode,
    output,
    error,
    executedAt,
    eventId: event.eventId,
    executionCount: check.executionCount,
    checkerImplementationSha256: activeCheckerHash,
  };
}

export function inspectRevision({ storeDir, revisionId }) {
  validateIdentifier(revisionId, 'revisionId');
  const resolvedStoreDir = path.resolve(storeDir);
  const revDir = path.join(resolvedStoreDir, revisionId);
  assertRealFsContainment(resolvedStoreDir, revDir);

  if (!fs.existsSync(revDir)) {
    throw new Error(`REVISION_NOT_FOUND: Revision "${revisionId}" does not exist in store.`);
  }

  const manifest = JSON.parse(fs.readFileSync(path.join(revDir, 'manifest.json'), 'utf-8'));
  const evidence = JSON.parse(fs.readFileSync(path.join(revDir, 'evidence.json'), 'utf-8'));
  const consistencyReport = verifyEvidenceConsistency(revDir);

  return {
    revisionId: manifest.revisionId,
    parentRevisionId: manifest.parentRevisionId,
    createdAt: manifest.createdAt,
    hashes: manifest.hashes,
    triageSummary: manifest.triageSummary,
    consistency: consistencyReport,
    evidenceSummary: {
      total: evidence.checks.length,
      notRun: evidence.checks.filter(c => c.status === 'NOT RUN').length,
      passed: evidence.checks.filter(c => c.status === 'PASSED').length,
      failed: evidence.checks.filter(c => c.status === 'FAILED').length,
      stale: evidence.checks.filter(c => c.status === 'STALE').length,
      blocked: evidence.checks.filter(c => c.status === 'BLOCKED').length,
      totalEventsLogged: evidence.events ? evidence.events.length : 0,
    },
    checks: evidence.checks.map(c => ({
      checkId: c.checkId,
      initialStatus: c.initialStatus || null,
      status: c.status,
      executionCount: c.executionCount || 0,
      exitCode: c.exitCode,
      sourceRevision: c.sourceRevision,
      checkerImplementationSha256: c.checker ? c.checker.implementationSha256 : null,
      staleReason: c.staleReason || null,
      error: c.error || null,
    })),
  };
}
