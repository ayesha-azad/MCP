import { Router } from "express";
import Task from "../models/Task.js";
import { taskOperations } from "../metrics.js";

const router = Router();

// List all tasks
router.get("/", async (req, res) => {
  const tasks = await Task.find().sort({ createdAt: -1 });
  res.json(tasks);
});

// Get one task
router.get("/:id", async (req, res) => {
  const task = await Task.findById(req.params.id);
  if (!task) return res.status(404).json({ error: "Task not found" });
  res.json(task);
});

// Create task
router.post("/", async (req, res) => {
  try {
    const task = await Task.create(req.body);
    taskOperations.inc({ operation: "create" });
    res.status(201).json(task);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Update task
router.put("/:id", async (req, res) => {
  const task = await Task.findByIdAndUpdate(req.params.id, req.body, {
    new: true,
  });
  if (!task) return res.status(404).json({ error: "Task not found" });
  taskOperations.inc({ operation: "update" });
  res.json(task);
});

// Delete task
router.delete("/:id", async (req, res) => {
  const task = await Task.findByIdAndDelete(req.params.id);
  if (!task) return res.status(404).json({ error: "Task not found" });
  taskOperations.inc({ operation: "delete" });
  res.json({ message: "Task deleted" });
});

export default router;
