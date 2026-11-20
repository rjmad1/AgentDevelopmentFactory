import https from 'node:https';
import crypto from 'node:crypto';

export class LangSmithClient {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.LANGSMITH_API_KEY || process.env.LANGCHAIN_API_KEY || null;
    this.endpoint = options.endpoint || process.env.LANGSMITH_ENDPOINT || 'https://api.smith.langchain.com';
    this.projectName = options.projectName || process.env.LANGSMITH_PROJECT || process.env.LANGCHAIN_PROJECT || 'AgentDevelopmentFactory';
    this.isEnabled = Boolean(this.apiKey);
  }

  getMode() {
    return this.isEnabled ? 'LANGSMITH_LIVE_TRACING' : 'OFFLINE_SYNTHETIC_STUB';
  }

  async _request(method, pathStr, body = null) {
    if (!this.isEnabled) {
      return { status: 'offline', mocked: true };
    }

    const url = new URL(pathStr, this.endpoint);
    const postData = body ? JSON.stringify(body) : null;

    return new Promise((resolve, reject) => {
      const req = https.request(url, {
        method,
        headers: {
          'x-api-key': this.apiKey,
          'Content-Type': 'application/json',
          ...(postData ? { 'Content-Length': Buffer.byteLength(postData) } : {})
        },
        timeout: 10000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              resolve(data ? JSON.parse(data) : { success: true });
            } catch {
              resolve({ raw: data });
            }
          } else {
            resolve({ error: `HTTP ${res.statusCode}: ${data}` });
          }
        });
      });

      req.on('error', err => resolve({ error: err.message }));
      req.on('timeout', () => {
        req.destroy();
        resolve({ error: 'Request timed out' });
      });

      if (postData) req.write(postData);
      req.end();
    });
  }

  async createRun({ id, name, runType = 'chain', inputs = {}, extra = {} }) {
    const runId = id || crypto.randomUUID();
    const payload = {
      id: runId,
      name,
      run_type: runType,
      inputs,
      session_name: this.projectName,
      start_time: new Date().toISOString(),
      extra: {
        ...extra,
        runtime: 'AgentDevelopmentFactory-Evaluator',
        version: '0.3.0'
      }
    };

    const res = await this._request('POST', '/runs', payload);
    return { runId, result: res };
  }

  async updateRun({ runId, outputs = {}, error = null }) {
    const payload = {
      outputs,
      error,
      end_time: new Date().toISOString()
    };
    return await this._request('PATCH', `/runs/${runId}`, payload);
  }

  async createFeedback({ runId, key, score, comment = '' }) {
    const payload = {
      run_id: runId,
      key,
      score,
      comment
    };
    return await this._request('POST', '/feedback', payload);
  }
}
