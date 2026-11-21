/**
 * Auto-Scaling Infrastructure & Concurrency Governance Engine.
 * Dual-engine parity with Python agent_factory.scaling.
 * Manages workload spikes, queue backpressure, worker pool scaling,
 * and circuit breaker protection while enforcing the $0.00 spend ceiling.
 */

export const CircuitState = {
  CLOSED: 'CLOSED',
  OPEN: 'OPEN',
  HALF_OPEN: 'HALF_OPEN',
};

export class CircuitBreakerError extends Error {
  constructor(msg = 'CIRCUIT_BREAKER_OPEN: Service degraded. Execution rejected.') {
    super(msg);
    this.name = 'CircuitBreakerError';
  }
}

export class QueueBackpressureError extends Error {
  constructor(msg = 'QUEUE_BACKPRESSURE_LIMIT: Capacity exceeded.') {
    super(msg);
    this.name = 'QueueBackpressureError';
  }
}

export class CircuitBreaker {
  /**
   * @param {Object} [opts]
   * @param {number} [opts.failureRateThreshold] e.g. 0.25 (25%)
   * @param {number} [opts.windowSize] e.g. 20
   * @param {number} [opts.recoveryMs] e.g. 3000ms
   * @param {number} [opts.consecutiveSuccessesToClose] e.g. 3
   */
  constructor({
    failureRateThreshold = 0.25,
    windowSize = 20,
    recoveryMs = 3000,
    consecutiveSuccessesToClose = 3,
  } = {}) {
    this.failureRateThreshold = failureRateThreshold;
    this.windowSize = windowSize;
    this.recoveryMs = recoveryMs;
    this.consecutiveSuccessesToClose = consecutiveSuccessesToClose;

    this.state = CircuitState.CLOSED;
    this.history = []; // boolean: true = success, false = fail
    this.lastStateChange = Date.now();
    this.halfOpenSuccesses = 0;
  }

  canExecute() {
    const now = Date.now();
    if (this.state === CircuitState.CLOSED) {
      return true;
    }

    if (this.state === CircuitState.OPEN) {
      if (now - this.lastStateChange >= this.recoveryMs) {
        this.state = CircuitState.HALF_OPEN;
        this.lastStateChange = now;
        this.halfOpenSuccesses = 0;
        return true;
      }
      return false;
    }

    if (this.state === CircuitState.HALF_OPEN) {
      return true;
    }

    return false;
  }

  recordSuccess() {
    this.history.push(true);
    if (this.history.length > this.windowSize) {
      this.history.shift();
    }

    if (this.state === CircuitState.HALF_OPEN) {
      this.halfOpenSuccesses += 1;
      if (this.halfOpenSuccesses >= this.consecutiveSuccessesToClose) {
        this.state = CircuitState.CLOSED;
        this.lastStateChange = Date.now();
        this.history = [];
      }
    }
  }

  recordFailure() {
    this.history.push(false);
    if (this.history.length > this.windowSize) {
      this.history.shift();
    }

    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
      this.lastStateChange = Date.now();
      return;
    }

    if (this.state === CircuitState.CLOSED && this.history.length >= 5) {
      const fails = this.history.filter((s) => !s).length;
      const rate = fails / this.history.length;
      if (rate >= this.failureRateThreshold) {
        this.state = CircuitState.OPEN;
        this.lastStateChange = Date.now();
      }
    }
  }

  getMetrics() {
    const total = this.history.length;
    const fails = this.history.filter((s) => !s).length;
    const rate = total > 0 ? fails / total : 0;
    return {
      state: this.state,
      historyLength: total,
      failRate: Math.round(rate * 1000) / 1000,
      isHealthy: this.state === CircuitState.CLOSED,
    };
  }
}

export class AutoscalingWorkerPool {
  /**
   * @param {Object} [opts]
   * @param {number} [opts.minWorkers]
   * @param {number} [opts.maxWorkers]
   * @param {number} [opts.scaleUpThresholdQueueDepth]
   * @param {number} [opts.workerIncrement]
   * @param {number} [opts.maxQueueDepth]
   * @param {number} [opts.circuitBreakerFailureRate]
   */
  constructor({
    minWorkers = 1,
    maxWorkers = 16,
    scaleUpThresholdQueueDepth = 3,
    workerIncrement = 2,
    maxQueueDepth = 100,
    circuitBreakerFailureRate = 0.25,
    circuitBreakerRecoveryMs = 3000,
  } = {}) {
    this.minWorkers = minWorkers;
    this.maxWorkers = maxWorkers;
    this.scaleUpThresholdQueueDepth = scaleUpThresholdQueueDepth;
    this.workerIncrement = workerIncrement;
    this.maxQueueDepth = maxQueueDepth;

    this.circuitBreaker = new CircuitBreaker({
      failureRateThreshold: circuitBreakerFailureRate,
      recoveryMs: circuitBreakerRecoveryMs,
    });

    this.currentWorkers = minWorkers;
    this.activeTasks = 0;
    this.queue = [];
    this.completedTasks = 0;
    this.failedTasks = 0;
    this.isRunning = true;
  }

  _autoscale() {
    if (
      this.queue.length >= this.scaleUpThresholdQueueDepth &&
      this.currentWorkers < this.maxWorkers
    ) {
      this.currentWorkers = Math.min(
        this.maxWorkers,
        this.currentWorkers + this.workerIncrement
      );
    }
  }

  _pump() {
    if (!this.isRunning) return;

    while (this.activeTasks < this.currentWorkers && this.queue.length > 0) {
      const item = this.queue.shift();
      if (!item) break;

      this.activeTasks += 1;
      const { fn, args, resolve, reject } = item;

      (async () => {
        try {
          const res = await fn(...args);
          this.circuitBreaker.recordSuccess();
          this.completedTasks += 1;
          resolve(res);
        } catch (err) {
          this.circuitBreaker.recordFailure();
          this.failedTasks += 1;
          reject(err);
        } finally {
          this.activeTasks -= 1;
          // Scale down if idle and queue empty
          if (this.queue.length === 0 && this.activeTasks === 0 && this.currentWorkers > this.minWorkers) {
            this.currentWorkers = this.minWorkers;
          }
          this._pump();
        }
      })();
    }
  }

  /**
   * Submits asynchronous task for execution.
   * @param {Function} fn
   * @param  {...any} args
   * @returns {Promise<any>}
   */
  submit(fn, ...args) {
    if (!this.circuitBreaker.canExecute()) {
      return Promise.reject(new CircuitBreakerError());
    }

    if (this.queue.length >= this.maxQueueDepth) {
      return Promise.reject(new QueueBackpressureError());
    }

    return new Promise((resolve, reject) => {
      this.queue.push({ fn, args, resolve, reject });
      this._autoscale();
      this._pump();
    });
  }

  getStatus() {
    const utilization = this.currentWorkers > 0 ? this.activeTasks / this.currentWorkers : 0;
    return {
      currentWorkers: this.currentWorkers,
      minWorkers: this.minWorkers,
      maxWorkers: this.maxWorkers,
      activeTasks: this.activeTasks,
      queuedTasks: this.queue.length,
      completedTasks: this.completedTasks,
      failedTasks: this.failedTasks,
      utilizationPct: Math.round(utilization * 1000) / 10,
      circuitBreaker: this.circuitBreaker.getMetrics(),
    };
  }

  /**
   * Simulates burst workload spike.
   * @param {Object} [opts]
   * @param {number} [opts.numTasks]
   * @param {number} [opts.taskDurationMs]
   * @param {number} [opts.failFraction]
   * @returns {Promise<Object>}
   */
  async simulateWorkloadSpike({ numTasks = 15, taskDurationMs = 30, failFraction = 0 } = {}) {
    const initialStatus = this.getStatus();
    let peakWorkers = initialStatus.currentWorkers;

    const delay = (ms) => new Promise((res) => setTimeout(res, ms));
    const promises = [];

    for (let i = 0; i < numTasks; i++) {
      const shouldFail = failFraction > 0 && i % Math.round(1 / failFraction) === 0;
      const taskPromise = this.submit(async () => {
        await delay(taskDurationMs);
        if (shouldFail) throw new Error(`Simulated fault in task ${i}`);
        return `result_${i}`;
      });

      if (this.currentWorkers > peakWorkers) {
        peakWorkers = this.currentWorkers;
      }
      promises.push(taskPromise.catch((e) => ({ error: e.message })));
    }

    const results = await Promise.all(promises);
    const succeeded = results.filter((r) => !r.error).length;
    const failed = results.filter((r) => r.error).length;
    const finalStatus = this.getStatus();

    return {
      tasksInjected: numTasks,
      tasksSucceeded: succeeded,
      tasksFailed: failed,
      initialWorkers: initialStatus.currentWorkers,
      peakWorkers,
      scaledUp: peakWorkers > initialStatus.currentWorkers,
      finalWorkers: finalStatus.currentWorkers,
      circuitBreakerStatus: finalStatus.circuitBreaker,
    };
  }

  shutdown() {
    this.isRunning = false;
    this.queue = [];
  }
}

export const defaultScalingPool = new AutoscalingWorkerPool();
