const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  list: () => request("/tasks"),
  create: (task) =>
    request("/tasks", { method: "POST", body: JSON.stringify(task) }),
  update: (id, patch) =>
    request(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(patch) }),
  remove: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
};
