/**
 * Distributed Tracing & Structured JSON Lines Logging Engine.
 * Dual-engine parity with Python agent_factory.observability.
 * Implements W3C TraceContext standard (traceparent: 00-{trace_id}-{span_id}-{flags})
 * and Jaeger / OpenTelemetry compatible causal trace export.
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const SpanStatus = {
  UNSET: 'UNSET',
  OK: 'OK',
  ERROR: 'ERROR',
};

export const SpanKind = {
  INTERNAL: 'INTERNAL',
  SERVER: 'SERVER',
  CLIENT: 'CLIENT',
  PRODUCER: 'PRODUCER',
  CONSUMER: 'CONSUMER',
};

export const LogLevel = {
  DEBUG: 10,
  INFO: 20,
  WARN: 30,
  ERROR: 40,
  CRITICAL: 50,
};

export class TraceContext {
  /**
   * @param {Object} [options]
   * @param {string} [options.traceId] 32 hex chars (128-bit)
   * @param {string} [options.spanId] 16 hex chars (64-bit)
   * @param {string|null} [options.parentSpanId]
   * @param {string} [options.traceFlags]
   */
  constructor({ traceId, spanId, parentSpanId = null, traceFlags = '01' } = {}) {
    this.traceId = traceId || crypto.randomBytes(16).toString('hex');
    this.spanId = spanId || crypto.randomBytes(8).toString('hex');
    this.parentSpanId = parentSpanId;
    this.traceFlags = traceFlags;
  }

  /**
   * Formats into W3C TraceContext traceparent string.
   * @returns {string} e.g. "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
   */
  toTraceparent() {
    return `00-${this.traceId}-${this.spanId}-${this.traceFlags}`;
  }

  /**
   * Parses standard W3C traceparent header.
   * @param {string} header
   * @returns {TraceContext}
   */
  static fromTraceparent(header) {
    if (!header || typeof header !== 'string') {
      return new TraceContext();
    }
    const parts = header.trim().split('-');
    if (parts.length >= 4 && parts[0] === '00' && parts[1].length === 32 && parts[2].length === 16) {
      return new TraceContext({
        traceId: parts[1],
        spanId: parts[2],
        traceFlags: parts[3],
      });
    }
    return new TraceContext();
  }

  /**
   * Creates child context maintaining same traceId and linking spanId as parentSpanId.
   * @returns {TraceContext}
   */
  createChild() {
    return new TraceContext({
      traceId: this.traceId,
      spanId: crypto.randomBytes(8).toString('hex'),
      parentSpanId: this.spanId,
      traceFlags: this.traceFlags,
    });
  }
}

export class Span {
  /**
   * @param {Tracer} tracer
   * @param {string} name
   * @param {TraceContext} context
   * @param {string} [kind]
   * @param {Record<string, any>} [attributes]
   */
  constructor(tracer, name, context, kind = SpanKind.INTERNAL, attributes = {}) {
    this.tracer = tracer;
    this.name = name;
    this.context = context;
    this.kind = kind;
    this.attributes = { ...attributes };
    this.events = [];
    this.status = SpanStatus.UNSET;
    this.errorMessage = null;

    this.startHr = process.hrtime.bigint();
    this.startTimeIso = new Date().toISOString();
    this.endTimeIso = null;
    this.durationMs = 0;
  }

  setAttribute(key, value) {
    this.attributes[key] = value;
    return this;
  }

  addEvent(name, attributes = {}) {
    this.events.push({
      name,
      timestampIso: new Date().toISOString(),
      attributes: { ...attributes },
    });
    return this;
  }

  setStatus(status, errorMsg = null) {
    this.status = status;
    if (errorMsg) {
      this.errorMessage = errorMsg;
    }
    return this;
  }

  recordError(err) {
    const msg = err instanceof Error ? err.message : String(err);
    this.status = SpanStatus.ERROR;
    this.errorMessage = msg;
    this.addEvent('exception', {
      'exception.message': msg,
      'exception.type': err?.name || 'Error',
    });
    return this;
  }

  end() {
    if (this.endTimeIso) return this.toJSON(); // already ended
    const endHr = process.hrtime.bigint();
    this.durationMs = Number(endHr - this.startHr) / 1e6;
    this.endTimeIso = new Date().toISOString();
    if (this.status === SpanStatus.UNSET) {
      this.status = SpanStatus.OK;
    }

    const record = this.toJSON();
    this.tracer._recordCompletedSpan(record);
    return record;
  }

  toJSON() {
    return {
      name: this.name,
      serviceName: this.tracer.serviceName,
      kind: this.kind,
      traceId: this.context.traceId,
      spanId: this.context.spanId,
      parentSpanId: this.context.parentSpanId,
      startTimeIso: this.startTimeIso,
      endTimeIso: this.endTimeIso,
      durationMs: Math.round(this.durationMs * 100) / 100,
      status: this.status,
      errorMessage: this.errorMessage,
      attributes: this.attributes,
      events: this.events,
    };
  }
}

export class Tracer {
  /**
   * @param {Object} [options]
   * @param {string} [options.serviceName]
   * @param {string} [options.storageFile]
   */
  constructor({ serviceName = 'adf-engine', storageFile = null } = {}) {
    this.serviceName = serviceName;
    this.storageFile = storageFile;
    this.completedSpans = [];
  }

  /**
   * Starts a new span.
   * @param {string} name
   * @param {Object} [opts]
   * @param {TraceContext} [opts.parentContext]
   * @param {string} [opts.kind]
   * @param {Record<string, any>} [opts.attributes]
   * @returns {Span}
   */
  startSpan(name, { parentContext = null, kind = SpanKind.INTERNAL, attributes = {} } = {}) {
    const context = parentContext ? parentContext.createChild() : new TraceContext();
    return new Span(this, name, context, kind, attributes);
  }

  _recordCompletedSpan(record) {
    this.completedSpans.push(record);
    if (this.storageFile) {
      try {
        const dir = path.dirname(this.storageFile);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.appendFileSync(this.storageFile, JSON.stringify(record) + '\n', 'utf8');
      } catch {
        // safe fallback
      }
    }
  }

  getSpansForTrace(traceId) {
    return this.completedSpans.filter((s) => s.traceId === traceId);
  }

  getAllTraces() {
    const grouped = {};
    for (const span of this.completedSpans) {
      if (!grouped[span.traceId]) {
        grouped[span.traceId] = [];
      }
      grouped[span.traceId].push(span);
    }
    return Object.entries(grouped).map(([traceId, spans]) => {
      const root = spans.find((s) => !s.parentSpanId) || spans[0];
      const durationTotal = spans.reduce((sum, s) => sum + s.durationMs, 0);
      const hasError = spans.some((s) => s.status === SpanStatus.ERROR);
      return {
        traceId,
        rootSpanName: root?.name || 'unknown',
        startTimeIso: root?.startTimeIso || new Date().toISOString(),
        spanCount: spans.length,
        durationMs: Math.round(durationTotal * 100) / 100,
        status: hasError ? 'ERROR' : 'OK',
        spans,
      };
    });
  }

  exportJaegerJson(traceId) {
    const spans = this.getSpansForTrace(traceId);
    return {
      data: [
        {
          traceID: traceId,
          spans: spans.map((s) => ({
            traceID: s.traceId,
            spanID: s.spanId,
            operationName: s.name,
            references: s.parentSpanId
              ? [{ refType: 'CHILD_OF', traceID: s.traceId, spanID: s.parentSpanId }]
              : [],
            startTime: s.startTimeIso,
            duration: Math.round(s.durationMs * 1000), // microseconds
            tags: Object.entries(s.attributes).map(([k, v]) => ({
              key: k,
              type: typeof v === 'number' ? 'float64' : 'string',
              value: String(v),
            })),
            logs: s.events.map((e) => ({
              timestamp: e.timestampIso,
              fields: [{ key: 'event', value: e.name }],
            })),
            process: { serviceName: s.serviceName },
          })),
        },
      ],
    };
  }
}

export class StructuredLogger {
  /**
   * @param {Object} [options]
   * @param {string} [options.serviceName]
   * @param {string} [options.logFile]
   * @param {number} [options.minLevel]
   * @param {boolean} [options.writeStdout]
   */
  constructor({
    serviceName = 'adf-engine',
    logFile = null,
    minLevel = LogLevel.INFO,
    writeStdout = true,
  } = {}) {
    this.serviceName = serviceName;
    this.logFile = logFile;
    this.minLevel = minLevel;
    this.writeStdout = writeStdout;
    this._boundContext = {};
    this.history = [];
  }

  bind(context = {}) {
    const clone = new StructuredLogger({
      serviceName: this.serviceName,
      logFile: this.logFile,
      minLevel: this.minLevel,
      writeStdout: this.writeStdout,
    });
    clone._boundContext = { ...this._boundContext, ...context };
    clone.history = this.history;
    return clone;
  }

  bindTrace(traceContext) {
    if (!traceContext) return this;
    return this.bind({
      traceId: traceContext.traceId,
      spanId: traceContext.spanId,
      parentSpanId: traceContext.parentSpanId,
    });
  }

  log(levelName, levelValue, message, extra = {}) {
    if (levelValue < this.minLevel) return null;

    const merged = { ...this._boundContext, ...extra };
    const traceId = merged.traceId || null;
    const spanId = merged.spanId || null;
    const agentId = merged.agentId || null;
    delete merged.traceId;
    delete merged.spanId;
    delete merged.agentId;

    let errPayload = null;
    if (merged.error) {
      const err = merged.error;
      errPayload = err instanceof Error ? { type: err.name, message: err.message } : { message: String(err) };
      delete merged.error;
    }

    const record = {
      timestampIso: new Date().toISOString(),
      level: levelName,
      serviceName: this.serviceName,
      message,
      traceId,
      spanId,
      agentId,
      attributes: merged,
      error: errPayload,
    };

    this.history.push(record);
    const line = JSON.stringify(record);

    if (this.writeStdout) {
      process.stdout.write(line + '\n');
    }

    if (this.logFile) {
      try {
        const dir = path.dirname(this.logFile);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.appendFileSync(this.logFile, line + '\n', 'utf8');
      } catch {
        // safe fallback
      }
    }

    return record;
  }

  debug(msg, extra) {
    return this.log('DEBUG', LogLevel.DEBUG, msg, extra);
  }
  info(msg, extra) {
    return this.log('INFO', LogLevel.INFO, msg, extra);
  }
  warn(msg, extra) {
    return this.log('WARN', LogLevel.WARN, msg, extra);
  }
  error(msg, extra) {
    return this.log('ERROR', LogLevel.ERROR, msg, extra);
  }
}

// Global default telemetry instances
export const defaultTracer = new Tracer({ serviceName: 'adf-authoring-engine' });
export const defaultLogger = new StructuredLogger({ serviceName: 'adf-authoring-engine', writeStdout: false });
