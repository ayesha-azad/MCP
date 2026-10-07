import { useEffect, useState } from "react";
import { api } from "./api.js";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setLoading(true);
      setTasks(await api.list());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const add = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    await api.create({ title });
    setTitle("");
    load();
  };

  const toggle = async (task) => {
    await api.update(task._id, { completed: !task.completed });
    load();
  };

  const remove = async (id) => {
    await api.remove(id);
    load();
  };

  return (
    <div className="container">
      <header>
        <h1>📋 TaskFlow</h1>
        <p className="subtitle">A MERN stack demo for CI/CD testing</p>
      </header>

      <form onSubmit={add} className="add-form">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
        />
        <button type="submit">Add Task</button>
      </form>

      {error && <div className="error">Error: {error}</div>}
      {loading ? (
        <div className="loading">Loading…</div>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task._id} className={task.completed ? "done" : ""}>
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggle(task)}
              />
              <span>{task.title}</span>
              <button onClick={() => remove(task._id)}>✕</button>
            </li>
          ))}
          {tasks.length === 0 && <li className="empty">No tasks yet.</li>}
        </ul>
      )}

      <footer>
        <span>
          Backend: <code>/api/tasks</code>
        </span>
        <span>
          Version: <code>1.0.0</code>
        </span>
      </footer>
    </div>
  );
}
