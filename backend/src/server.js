import "dotenv/config";
import express from "express";
import cors from "cors";
import morgan from "morgan";
import { connectDB } from "./config/db.js";
import taskRoutes from "./routes/tasks.js";
import { registry, httpRequestDuration, httpRequestTotal } from "./metrics.js";

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use(morgan("combined"));

// Request timing middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path;
    httpRequestDuration.observe(
      { method: req.method, route, status_code: res.statusCode },
      duration,
    );
    httpRequestTotal.inc({
      method: req.method,
      route,
      status_code: res.statusCode,
    });
  });
  next();
});

// Health checks
app.get("/health", (req, res) => res.json({ status: "ok" }));
app.get("/ready", (req, res) => res.json({ status: "ready" }));

// Prometheus metrics endpoint
app.get("/metrics", async (req, res) => {
  res.set("Content-Type", registry.contentType);
  res.end(await registry.metrics());
});

// Routes
app.use("/api/tasks", taskRoutes);

// Root
app.get("/", (req, res) => {
  res.json({ name: "TaskFlow API", version: "1.0.0" });
});

connectDB().then(() => {
  app.listen(PORT, () => console.log(`🚀 Backend listening on :${PORT}`));
});
