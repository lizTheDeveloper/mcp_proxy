# MCP Proxy - Dynamic MCP Server Loading

**Hot-reload MCP servers without restarting Claude Code.**

## Features

- **Hot-Reload**: Load and reload MCP servers without restart
- **Dynamic Installation**: Install servers from git repositories
- **Programmatic Orchestration**: Call tools dynamically in loops and workflows
- **Context Savings**: Load only the tools you need

## Quick Start

### 1. Install

```bash
git clone https://github.com/lizTheDeveloper/mcp_proxy.git
cd mcp_proxy
pip install -r requirements.txt
```

### 2. Configure

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "mcp-proxy": {
      "command": "python",
      "args": ["-m", "mcp_proxy.servers.proxy_server"],
      "cwd": "/path/to/mcp_proxy",
      "env": {
        "PYTHONPATH": "/path/to/mcp_proxy"
      }
    }
  }
}
```

### 3. Use

After restarting Claude Code once to load the proxy, you can:

```python
# Load any MCP server dynamically (no restart!)
load_mcp_server_dynamically("my-server")

# Call tools on loaded servers
call_dynamic_server_tool("my-server", "tool_name", {"param": "value"})

# Install and load from git in one step
install_and_load_mcp_server("https://github.com/user/mcp-server")
```

## Available Tools

| Tool | Description |
|------|-------------|
| `load_mcp_server_dynamically` | Load a server from .mcp.json |
| `call_dynamic_server_tool` | Call any tool on a loaded server |
| `get_loaded_servers` | List currently loaded servers |
| `reload_mcp_server` | Reload a server to pick up changes |
| `unload_mcp_server` | Stop and unload a server |
| `list_available_servers` | List all configured servers |
| `install_mcp_server_from_git` | Install from git repository |
| `install_and_load_mcp_server` | Install and load in one step |
| `list_installed_mcp_servers` | List all installed servers |
| `uninstall_mcp_server` | Remove a server |

## How It Works

```
Claude Code
    |
    v
MCP Proxy Server (meta-tools)
    |
    v
Dynamic Server Loader (subprocess manager)
    |
    v
Individual MCP Servers (spawned on-demand)
```

The proxy spawns MCP servers as subprocesses and communicates with them using the MCP JSON-RPC protocol over stdin/stdout.

## Usage Patterns

### Hot-Reload During Development

```python
# Load your server
load_mcp_server_dynamically("my-dev-server")

# Test it
call_dynamic_server_tool("my-dev-server", "my_feature", {})

# Make code changes...

# Reload with new code
reload_mcp_server("my-dev-server")

# Test again - no restart needed!
call_dynamic_server_tool("my-dev-server", "my_feature", {})
```

### Programmatic Workflows

```python
# Load the server
load_mcp_server_dynamically("user-management")

# Programmatic workflow
users = call_dynamic_server_tool("user-management", "list_users", {"limit": 100})

for user in users["data"]:
    if user["needs_activation"]:
        call_dynamic_server_tool("user-management", "activate_user", {
            "user_id": user["id"]
        })
```

### Multi-Server Orchestration

```python
# Load multiple servers
for server in ["database", "stripe", "email"]:
    load_mcp_server_dynamically(server)

# Orchestrate across servers
customer = call_dynamic_server_tool("database", "get_customer", {"id": 123})
payment = call_dynamic_server_tool("stripe", "charge", {"amount": 2999})
call_dynamic_server_tool("email", "send_receipt", {"to": customer["email"]})
```

## Creating Custom Servers

Create a FastMCP server and add it to `.mcp.json`:

```python
# my_server.py
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def my_tool(param: str) -> dict:
    """Tool description"""
    return {"success": True, "result": param}

if __name__ == "__main__":
    mcp.run()
```

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["my_server.py"],
      "cwd": "/path/to/server"
    }
  }
}
```

Then load it dynamically:

```python
load_mcp_server_dynamically("my-server")
call_dynamic_server_tool("my-server", "my_tool", {"param": "hello"})
```

## License

MIT
