#!/usr/bin/env python3
"""
TaskFlow Model Context Protocol (MCP) Server

Exposes TaskFlow API management and DevOps monitoring tools over the MCP STDIO protocol.
"""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import subprocess

BACKEND_URL = "http://localhost:5000"

def call_backend(endpoint, method="GET", data=None):
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body) if res_body else {"status": "ok"}
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to backend at {url}: {e}"}

# Core Tool Functions
def tool_list_tasks():
    return call_backend("/api/tasks")

def tool_create_task(title: str, description: str = ""):
    return call_backend("/api/tasks", method="POST", data={"title": title, "description": description})

def tool_update_task(task_id: str, completed: bool = None, title: str = None, description: str = None):
    payload = {}
    if completed is not None:
        payload["completed"] = completed
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    return call_backend(f"/api/tasks/{task_id}", method="PUT", data=payload)

def tool_delete_task(task_id: str):
    return call_backend(f"/api/tasks/{task_id}", method="DELETE")

def tool_get_health():
    return call_backend("/health")

def tool_docker_status():
    try:
        result = subprocess.run(["docker", "ps", "--format", "json"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {"error": result.stderr}
        lines = [line for line in result.stdout.strip().split("\n") if line]
        containers = [json.loads(line) for line in lines]
        return {"containers": containers}
    except Exception as e:
        return {"error": str(e)}

def tool_k8s_status():
    try:
        result = subprocess.run(["kubectl", "get", "pods", "-n", "taskflow", "-o", "json"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {"error": result.stderr}
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

# FastMCP integration or fallback to built-in JSON-RPC STDIO Server
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("TaskFlow MCP Server")

    @mcp.tool()
    def list_tasks():
        """List all tasks from the TaskFlow database."""
        return json.dumps(tool_list_tasks(), indent=2)

    @mcp.tool()
    def create_task(title: str, description: str = ""):
        """Create a new task in TaskFlow."""
        return json.dumps(tool_create_task(title, description), indent=2)

    @mcp.tool()
    def update_task(task_id: str, completed: bool = None, title: str = None, description: str = None):
        """Update an existing task in TaskFlow."""
        return json.dumps(tool_update_task(task_id, completed, title, description), indent=2)

    @mcp.tool()
    def delete_task(task_id: str):
        """Delete a task by ID from TaskFlow."""
        return json.dumps(tool_delete_task(task_id), indent=2)

    @mcp.tool()
    def get_health():
        """Check the health status of the backend API."""
        return json.dumps(tool_get_health(), indent=2)

    @mcp.tool()
    def docker_status():
        """Get the status of running Docker containers."""
        return json.dumps(tool_docker_status(), indent=2)

    @mcp.tool()
    def k8s_status():
        """Get the Kubernetes pods in the taskflow namespace."""
        return json.dumps(tool_k8s_status(), indent=2)

    def run():
        mcp.run()

except ImportError:
    # Standard MCP JSON-RPC Server
    TOOLS_DEF = [
        {
            "name": "list_tasks",
            "description": "List all tasks from the TaskFlow database.",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "create_task",
            "description": "Create a new task in TaskFlow.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the task"},
                    "description": {"type": "string", "description": "Optional details"}
                },
                "required": ["title"]
            }
        },
        {
            "name": "update_task",
            "description": "Update an existing task.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "completed": {"type": "boolean"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "delete_task",
            "description": "Delete a task by ID.",
            "inputSchema": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"]
            }
        },
        {
            "name": "get_health",
            "description": "Check the health status of the backend API.",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "docker_status",
            "description": "Get status of running Docker containers.",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "k8s_status",
            "description": "Get Kubernetes pod status for taskflow namespace.",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        }
    ]

    def handle_request(req):
        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "taskflow-mcp-server", "version": "1.0.0"}
                }
            }
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_DEF}
            }
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "list_tasks":
                res = tool_list_tasks()
            elif name == "create_task":
                res = tool_create_task(args.get("title", ""), args.get("description", ""))
            elif name == "update_task":
                res = tool_update_task(args.get("task_id"), args.get("completed"), args.get("title"), args.get("description"))
            elif name == "delete_task":
                res = tool_delete_task(args.get("task_id"))
            elif name == "get_health":
                res = tool_get_health()
            elif name == "docker_status":
                res = tool_docker_status()
            elif name == "k8s_status":
                res = tool_k8s_status()
            else:
                res = {"error": f"Unknown tool: {name}"}

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                }
            }
        return None

    def run():
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                response = handle_request(req)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_res = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    run()
