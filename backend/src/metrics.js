import client from "prom-client";

// Enable default metrics (CPU, memory, event loop lag, etc.)
client.collectDefaultMetrics({ prefix: "taskflow_" });

export const httpRequestDuration = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "Duration of HTTP requests in seconds",
  labelNames: ["method", "route", "status_code"],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
});

export const httpRequestTotal = new client.Counter({
  name: "http_requests_total",
  help: "Total number of HTTP requests",
  labelNames: ["method", "route", "status_code"],
});

export const taskOperations = new client.Counter({
  name: "taskflow_task_operations_total",
  help: "Total task operations performed",
  labelNames: ["operation"],
});

export const registry = client.register;
