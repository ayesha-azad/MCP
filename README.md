# 🚀 TaskFlow & MCP Server

TaskFlow is a modern MERN stack application (MongoDB, Express, React, Node.js) equipped with DevOps infrastructure, GitOps continuous delivery with ArgoCD, Kubernetes manifests (Kustomize), Prometheus monitoring, GitHub Actions CI/CD, and a Python Model Context Protocol (MCP) server.
It is used for testing MCP.

---

## 🛠️ Architecture Overview

- **Frontend**: React + Vite (Nginx for containerized production build)
- **Backend**: Express.js REST API with Mongoose, Prometheus metrics (`/metrics`), health check (`/health`, `/ready`)
- **Database**: MongoDB 7.0
- **MCP Server**: Python MCP server (`mcp-server.py`) exposing TaskFlow CRUD tools & DevOps diagnostic tools
- **CI/CD**: GitHub Actions pipeline (`ci-cd.yaml`, `argocd-sync.yaml`)
- **GitOps**: ArgoCD Application and Project manifests (`argocd/`)
- **Kubernetes**: Base & Dev overlay configuration using Kustomize (`k8s/`)
- **Monitoring**: Prometheus & Grafana dashboard integration

---

## 🚀 Quick Start — Local Development

### Option 1: Docker Compose (Recommended)

Run the complete stack with a single command:

```bash
docker compose up -d
```

Access the services:

- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5001](http://localhost:5001)
- **API Health Check**: [http://localhost:5001/health](http://localhost:5001/health)
- **Prometheus Metrics**: [http://localhost:5001/metrics](http://localhost:5001/metrics)

---

### Option 2: Run Services Manually (Dev Mode)

1. **Start MongoDB**:

   ```bash
   docker run -d --name taskflow-mongo -p 27017:27017 mongo:7.0
   ```

2. **Start Backend**:

   ```bash
   cd backend
   npm install
   npm run dev
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🤖 Running the MCP (Model Context Protocol) Server

The repository includes `mcp-server.py`, an MCP STDIO server that allows AI assistants (such as Claude Desktop or Antigravity) to manage tasks and inspect system health.

### Available Tools:

- `list_tasks`: Retrieves all tasks
- `create_task`: Creates a task (`title`, `description`)
- `update_task`: Updates task state (`task_id`, `completed`, `title`)
- `delete_task`: Deletes a task by ID
- `get_health`: Checks API health status
- `docker_status`: Checks Docker container status
- `k8s_status`: Checks Kubernetes pod status in `taskflow` namespace

### Run directly:

```bash
python3 mcp-server.py
```

---

## 📦 GitHub Actions & DockerHub Setup

To enable automated Docker builds and Kubernetes deployments via GitHub Actions:

1. In your GitHub repository settings (**Settings > Secrets and variables > Actions**):
   - Add **Variable**: `DOCKERHUB_USERNAME` (Your Docker Hub username)
   - Add **Secret**: `DOCKERHUB_TOKEN` (Your Docker Hub Access Token)

2. On every push to `main`, GitHub Actions will:
   - Run tests & build checks
   - Build and push tagged Docker images to Docker Hub (`<username>/taskflow-backend` and `<username>/taskflow-frontend`)
   - Test deployment on a local Kind Kubernetes cluster with ArgoCD and Prometheus.

---

## ☸️ Kubernetes & ArgoCD Deployment

Deploy to Kubernetes using Kustomize:

```bash
kubectl apply -k k8s/overlays/dev
```

Deploy with ArgoCD:

```bash
kubectl apply -f argocd/project.yaml
kubectl apply -f argocd/application.yaml
```
