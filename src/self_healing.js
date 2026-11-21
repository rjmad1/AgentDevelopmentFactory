/**
 * Autonomous Error Resolution & Self-Healing Mechanisms for Agent Runtimes.
 * Dual-engine parity with Python agent_factory.remediation.self_healing.
 * Enforces fault diagnosis, bounded exponential backoff retries, syntax/format auto-repair,
 * schema drift healing, and fallback degradation while strictly honoring the $0.00 spend ceiling.
 */

import fs from 'node:fs';
import path from 'node:path';

export const FaultCategory = {
  TRANSIENT: 'TRANSIENT',
  SCHEMA_MISMATCH: 'SCHEMA_MISMATCH',
  FORMAT_CORRUPTION: 'FORMAT_CORRUPTION',
  TOOL_EXECUTION_FAILURE: 'TOOL_EXECUTION_FAILURE',
  RESOURCE_STARVATION: 'RESOURCE_STARVATION',
  SECURITY_VIOLATION: 'SECURITY_VIOLATION',
};

export class SelfHealingPolicy {
  constructor({
    maxRetries = 3,
    backoffBaseMs = 50,
    backoffMultiplier = 2.0,
    jitter = true,
    enableFormatRepair = true,
    enableSafeFallback = true,
  } = {}) {
    this.maxRetries = Math.min(Math.max(maxRetries, 1), 5);
    this.backoffBaseMs = backoffBaseMs;
    this.backoffMultiplier = backoffMultiplier;
    this.jitter = jitter;
    this.enableFormatRepair = enableFormatRepair;
    this.enableSafeFallback = enableSafeFallback;
  }
}

export class SelfHealingEngine {
  /**
   * Diagnoses an error and determines recovery category and action.
   * @param {Error|string} err
   * @param {Object} [context]
   */
  static diagnose(err, context = {}) {
    const errStr = err instanceof Error ? err.message : String(err);
    const errName = err?.name || 'Error';

    // 1. Critical Security Boundary Violations (Strictly Unrecoverable)
    const securityTerms = [
      'GuardrailViolation', 'PermissionError', 'CONTAINMENT_VIOLATION',
      'PROMPT_INJECTION', 'SECRET_LEAK', 'TOOL_DISALLOWED', 'UNAUTHORIZED_EFFECT',
      'SANDBOX_CONTAINMENT', 'AST_QUARANTINE_REJECTED'
    ];
    if (securityTerms.some((t) => errStr.includes(t) || errName.includes(t))) {
      return {
        category: FaultCategory.SECURITY_VIOLATION,
        isRecoverable: false,
        suggestedAction: 'HALT_AND_CONTAIN',
        rootCause: 'Operational safety guardrail triggered. Execution blocked by policy.',
        details: { violation: errStr },
      };
    }

    // 2. Format Corruption (Repairable via syntax normalizer)
    const formatTerms = ['SyntaxError', 'Unexpected token', 'Unexpected end of JSON', 'JSON.parse', 'Expected double-quoted property name'];
    if (formatTerms.some((t) => errStr.includes(t) || errName.includes(t))) {
      return {
        category: FaultCategory.FORMAT_CORRUPTION,
        isRecoverable: true,
        suggestedAction: 'AUTONOMOUS_FORMAT_REPAIR',
        rootCause: 'Malformed or corrupted serialization format in agent payload.',
        details: { formatError: errStr },
      };
    }

    // 3. Schema & Type Mismatch
    const schemaTerms = ['ValidationError', 'TypeError', 'Missing mandatory', 'schema mismatch', 'Invalid property'];
    if (schemaTerms.some((t) => errStr.includes(t) || errName.includes(t))) {
      return {
        category: FaultCategory.SCHEMA_MISMATCH,
        isRecoverable: true,
        suggestedAction: 'AUTONOMOUS_SCHEMA_COERCION',
        rootCause: 'Input parameters or output schema did not conform to certified specification.',
        details: { schemaError: errStr },
      };
    }

    // 4. Transient System Faults
    const transientTerms = ['Timeout', 'ETIMEDOUT', 'ECONNREFUSED', 'EAGAIN', 'EBUSY', 'rate limit', 'lock contention'];
    if (transientTerms.some((t) => errStr.includes(t) || errName.includes(t))) {
      return {
        category: FaultCategory.TRANSIENT,
        isRecoverable: true,
        suggestedAction: 'EXPONENTIAL_BACKOFF_RETRY',
        rootCause: 'Transient execution timeout or resource contention.',
        details: { transientError: errStr },
      };
    }

    // 5. Generic Tool Execution Failure
    return {
      category: FaultCategory.TOOL_EXECUTION_FAILURE,
      isRecoverable: true,
      suggestedAction: 'DEGRADED_FALLBACK_RECOVERY',
      rootCause: `Tool or subprocess execution failed: ${errStr.slice(0, 150)}`,
      details: { originalName: errName },
    };
  }

  /**
   * Surgically repairs corrupted JSON strings.
   * @param {string} corruptedText
   * @returns {string}
   */
  static repairJsonFormat(corruptedText) {
    let text = String(corruptedText).trim();

    // Strip markdown code fences
    if (text.includes('```')) {
      const match = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
      if (match) {
        text = match[1].trim();
      } else {
        text = text.replace(/^```(?:json)?|```$/gm, '').trim();
      }
    }

    // Remove trailing commas before closing braces/brackets
    text = text.replace(/,\s*([\}\]])/g, '$1');

    // Balance unclosed delimiters using a reverse closing stack
    const stack = [];
    let inString = false;
    let escape = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === '"' && !escape) {
        inString = !inString;
      } else if (!inString) {
        if (ch === '{') stack.push('}');
        else if (ch === '[') stack.push(']');
        else if (ch === '}' || ch === ']') {
          if (stack.length > 0 && stack[stack.length - 1] === ch) {
            stack.pop();
          }
        }
      }
      if (ch === '\\' && !escape) {
        escape = true;
      } else {
        escape = false;
      }
    }

    while (stack.length > 0) {
      text += stack.pop();
    }

    return text;
  }

  /**
   * Safely parses JSON with autonomous format self-healing.
   * @param {string} payload
   * @returns {{ data: any, wasHealed: boolean }}
   */
  static safeParseJsonWithHealing(payload) {
    try {
      return { data: JSON.parse(payload), wasHealed: false };
    } catch {
      const healedText = this.repairJsonFormat(payload);
      try {
        return { data: JSON.parse(healedText), wasHealed: true };
      } catch {
        const start = healedText.indexOf('{');
        const end = healedText.lastIndexOf('}');
        if (start !== -1 && end > start) {
          try {
            return { data: JSON.parse(healedText.slice(start, end + 1)), wasHealed: true };
          } catch {
            // pass
          }
        }
        throw new Error(`Autonomous format repair unable to safely parse payload: ${payload.slice(0, 80)}...`);
      }
    }
  }

  /**
   * Executes an asynchronous task wrapped with autonomous error resolution.
   * @param {Function} fn
   * @param {Array} [args]
   * @param {Object} [opts]
   * @returns {Promise<{ result: any, events: Array }>}
   */
  static async executeWithHealing(
    fn,
    args = [],
    { policy = new SelfHealingPolicy(), fallbackFactory = null, ledgerFile = null } = {}
  ) {
    const events = [];
    let attempt = 1;
    let lastError = null;

    const delay = (ms) => new Promise((res) => setTimeout(res, ms));

    while (attempt <= policy.maxRetries) {
      const start = Date.now();
      try {
        const result = await fn(...args);
        if (attempt > 1) {
          const rec = {
            timestampIso: new Date().toISOString(),
            attemptNumber: attempt,
            diagnosis: this.diagnose('Transient resolved'),
            actionTaken: `Execution recovered on attempt ${attempt}`,
            success: true,
            durationMs: Date.now() - start,
          };
          events.push(rec);
          this._appendLedger(ledgerFile, rec);
        }
        return { result, events };
      } catch (err) {
        const durationMs = Date.now() - start;
        lastError = err;
        const diagnosis = this.diagnose(err, { attempt });

        // Unrecoverable security violation -> Halt immediately
        if (!diagnosis.isRecoverable) {
          const rec = {
            timestampIso: new Date().toISOString(),
            attemptNumber: attempt,
            diagnosis,
            actionTaken: 'HALT: Security boundary violation cannot be self-healed',
            success: false,
            durationMs,
            errorMessage: err.message,
          };
          events.push(rec);
          this._appendLedger(ledgerFile, rec);
          throw err;
        }

        // Budget exhausted
        if (attempt >= policy.maxRetries) {
          const rec = {
            timestampIso: new Date().toISOString(),
            attemptNumber: attempt,
            diagnosis,
            actionTaken: 'BUDGET_EXHAUSTED: Max retry threshold reached',
            success: false,
            durationMs,
            errorMessage: err.message,
          };
          events.push(rec);
          this._appendLedger(ledgerFile, rec);

          if (policy.enableSafeFallback && fallbackFactory) {
            return { result: fallbackFactory(diagnosis), events };
          }
          throw err;
        }

        // Exponential backoff with optional jitter
        let delayMs = policy.backoffBaseMs * Math.pow(policy.backoffMultiplier, attempt - 1);
        if (policy.jitter) {
          delayMs += Math.random() * delayMs * 0.2;
        }

        const actionDesc = `Applying ${diagnosis.suggestedAction}. Backoff ${Math.round(delayMs)}ms`;
        const rec = {
          timestampIso: new Date().toISOString(),
          attemptNumber: attempt,
          diagnosis,
          actionTaken: actionDesc,
          success: false,
          durationMs,
          errorMessage: err.message,
        };
        events.push(rec);
        this._appendLedger(ledgerFile, rec);

        await delay(delayMs);
        attempt += 1;
      }
    }

    if (policy.enableSafeFallback && fallbackFactory) {
      return { result: fallbackFactory(this.diagnose(lastError || 'Unknown fault')), events };
    }
    throw lastError || new Error('Self-healing budget exhausted.');
  }

  static _appendLedger(ledgerFile, record) {
    if (!ledgerFile) return;
    try {
      const dir = path.dirname(ledgerFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.appendFileSync(ledgerFile, JSON.stringify(record) + '\n', 'utf8');
    } catch {
      // safe fallback
    }
  }
}
