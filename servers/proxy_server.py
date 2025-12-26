#!/usr/bin/env python3
"""
MCP Proxy Server

Provides meta-tools that can load and call other MCP servers dynamically.
This enables hot-reload without restarting Claude Code.

Usage:
    python -m mcp_proxy.servers.proxy_server
"""

from fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dynamic_server_loader import get_loader
from utils.mcp_installer import MCPInstaller
from utils.tool_searcher import ToolSearcher

# Initialize FastMCP server
mcp = FastMCP("mcp-proxy")

# Initialize components
mcp_installer = MCPInstaller()
server_loader = get_loader()
tool_searcher = ToolSearcher(server_loader)


@mcp.tool()
def load_mcp_server_dynamically(server_name: str) -> dict:
    """
    Load an MCP server dynamically without restarting Claude Code.

    This tool loads a server from .mcp.json configuration and makes its
    tools available immediately. No restart required!

    Args:
        server_name: Name of the server to load (must be in .mcp.json)

    Returns:
        Dictionary with load status and available tools

    Examples:
        # Load a newly installed server
        load_mcp_server_dynamically("my-new-server")

        # Load after updating .mcp.json
        load_mcp_server_dynamically("updated-server")

    Usage Notes:
        - Server must exist in .mcp.json
        - Tools become available immediately
        - Can load multiple servers simultaneously
        - Use get_loaded_servers() to see what's loaded
    """
    try:
        result = server_loader.load_server(server_name)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load server: {str(e)}"
        }


@mcp.tool()
def call_dynamic_server_tool(
    server_name: str,
    tool_name: str,
    parameters: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Call a tool on a dynamically loaded MCP server.

    This allows calling tools from servers that aren't natively loaded
    by Claude Code. The server is loaded on-demand if needed.

    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        parameters: Dictionary of tool parameters

    Returns:
        Tool execution result

    Examples:
        # Call tool on loaded server
        call_dynamic_server_tool(
            server_name="analytics",
            tool_name="get_metrics",
            parameters={"date": "2024-01-01"}
        )

        # Server loads automatically if needed
        call_dynamic_server_tool(
            server_name="new-server",
            tool_name="process_data",
            parameters={"input": "data.csv"}
        )

    Usage Notes:
        - Server loads automatically if not already loaded
        - Results returned directly from the tool
        - Supports all parameter types (strings, numbers, objects, arrays)
    """
    try:
        result = server_loader.call_tool(server_name, tool_name, parameters)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call tool: {str(e)}"
        }


@mcp.tool()
def get_loaded_servers() -> dict:
    """
    Get information about all dynamically loaded MCP servers.

    Shows which servers are currently loaded, their status, and
    available tools from each server.

    Returns:
        Dictionary with loaded server information

    Example:
        get_loaded_servers()
        # Returns list of loaded servers with their tools

    Usage Notes:
        - Shows only dynamically loaded servers (not native Claude Code servers)
        - Indicates if server process is still running
        - Lists all tools available from each server
    """
    try:
        return server_loader.get_loaded_servers()

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def reload_mcp_server(server_name: str) -> dict:
    """
    Reload an MCP server to pick up changes.

    Useful when a server has been updated or its configuration changed.
    Stops the current server process and starts a new one.

    Args:
        server_name: Name of the server to reload

    Returns:
        Reload status and updated tool list

    Examples:
        # Reload after code update
        reload_mcp_server("my-server")

        # Reload after configuration change
        reload_mcp_server("analytics")

    Usage Notes:
        - Stops and restarts the server process
        - Picks up code changes immediately
        - Refreshes available tools
        - Use this instead of restarting Claude Code
    """
    try:
        return server_loader.reload_server(server_name)

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def unload_mcp_server(server_name: str) -> dict:
    """
    Unload a dynamically loaded MCP server.

    Stops the server process and removes it from the loaded servers list.
    The server can be loaded again later.

    Args:
        server_name: Name of the server to unload

    Returns:
        Unload status

    Example:
        unload_mcp_server("my-server")
    """
    try:
        return server_loader.unload_server(server_name)

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_available_servers() -> dict:
    """
    List all servers configured in .mcp.json.

    Shows all servers that can be loaded dynamically.

    Returns:
        Dictionary with list of available server names
    """
    try:
        servers = server_loader.get_available_servers()
        return {
            "success": True,
            "servers": servers,
            "count": len(servers)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def install_mcp_server_from_git(
    git_url: str,
    server_name: Optional[str] = None,
    server_file: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    requirements_file: Optional[str] = None,
    auto_detect: bool = True
) -> dict:
    """
    Install an MCP server from a git repository and configure it automatically.

    This tool clones a git repository containing an MCP server, installs its
    dependencies, and adds it to the .mcp.json configuration file.

    Args:
        git_url: Git repository URL (supports @branch syntax, e.g., https://github.com/user/repo@main)
        server_name: Name for the server in .mcp.json (default: repo name)
        server_file: Python file to run (default: auto-detect from server.py, main.py, *_server.py)
        env_vars: Dictionary of environment variables to pass to the server
        requirements_file: Path to requirements file (default: requirements.txt)
        auto_detect: Auto-detect server file if not specified (default: True)

    Returns:
        Dictionary with installation status and details

    Examples:
        # Install a public MCP server
        install_mcp_server_from_git("https://github.com/anthropics/mcp-server-example")

        # Install with specific branch
        install_mcp_server_from_git("https://github.com/user/repo@develop")

        # Install with custom configuration
        install_mcp_server_from_git(
            git_url="https://github.com/user/custom-server",
            server_name="my-custom-server",
            server_file="custom_server.py",
            env_vars={"API_KEY": "secret123"},
            requirements_file="deps.txt"
        )

    Usage Notes:
        - Requires git to be installed
        - Server files are installed to ~/.mcp_servers/ by default
        - Dependencies are installed in the current Python environment
        - After installation, use load_mcp_server_dynamically() to load it
    """
    try:
        success = mcp_installer.install_from_git(
            git_url=git_url,
            server_name=server_name,
            server_file=server_file,
            env_vars=env_vars,
            requirements_file=requirements_file,
            auto_detect=auto_detect
        )

        if success:
            final_name = server_name or mcp_installer._parse_git_url(git_url)[0]
            return {
                "success": True,
                "message": f"Successfully installed MCP server from {git_url}",
                "server_name": final_name,
                "next_step": f"Use load_mcp_server_dynamically('{final_name}') to load it"
            }
        else:
            return {
                "success": False,
                "error": "Installation failed. Check the logs for details."
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Installation failed: {str(e)}"
        }


@mcp.tool()
def install_and_load_mcp_server(
    git_url: str,
    server_name: Optional[str] = None,
    server_file: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    requirements_file: Optional[str] = None,
    auto_detect: bool = True
) -> dict:
    """
    Install an MCP server from git AND load it immediately without restart.

    This is the ultimate convenience tool - combines installation and loading
    into a single operation. Install and start using new servers instantly!

    Args:
        git_url: Git repository URL (supports @branch syntax)
        server_name: Name for the server (default: repo name)
        server_file: Python file to run (default: auto-detect)
        env_vars: Environment variables for the server
        requirements_file: Requirements file (default: requirements.txt)
        auto_detect: Auto-detect server file (default: True)

    Returns:
        Dictionary with installation and loading status

    Examples:
        # Install and load in one step
        install_and_load_mcp_server("https://github.com/user/server")

        # With configuration
        install_and_load_mcp_server(
            git_url="https://github.com/user/server@v1.0",
            server_name="my-server",
            env_vars={"API_KEY": "secret"}
        )

    Usage Notes:
        - No restart required!
        - Server tools available immediately after installation
        - Perfect for quick experimentation with new servers
    """
    try:
        # Step 1: Install
        install_result = mcp_installer.install_from_git(
            git_url=git_url,
            server_name=server_name,
            server_file=server_file,
            env_vars=env_vars,
            requirements_file=requirements_file,
            auto_detect=auto_detect
        )

        if not install_result:
            return {
                "success": False,
                "error": "Installation failed"
            }

        # Get the actual server name (might be from repo name)
        final_server_name = server_name or mcp_installer._parse_git_url(git_url)[0]

        # Step 2: Load dynamically
        load_result = server_loader.load_server(final_server_name)

        if load_result.get("success"):
            return {
                "success": True,
                "message": f"Installed and loaded '{final_server_name}' successfully",
                "server_name": final_server_name,
                "tools": load_result.get("tools", []),
                "tool_count": load_result.get("tool_count", 0),
                "note": "Server is ready to use immediately - no restart required!"
            }
        else:
            return {
                "success": False,
                "error": f"Installation succeeded but loading failed: {load_result.get('error')}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to install and load server: {str(e)}"
        }


@mcp.tool()
def list_installed_mcp_servers() -> dict:
    """
    List all installed MCP servers from .mcp.json configuration.

    Returns information about each configured MCP server including:
    - Server name
    - File path
    - Python command
    - Environment variables

    Returns:
        Dictionary with list of installed servers

    Example:
        list_installed_mcp_servers()
        # Returns all servers with their configuration details
    """
    try:
        servers = mcp_installer.list_installed()

        return {
            "success": True,
            "servers": servers,
            "count": len(servers),
            "config_file": str(mcp_installer.config_file)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def uninstall_mcp_server(server_name: str, delete_files: bool = False) -> dict:
    """
    Uninstall an MCP server and optionally delete its files.

    Removes the server from .mcp.json configuration. Can optionally
    delete the server files from disk as well.

    Args:
        server_name: Name of the server to uninstall
        delete_files: If True, delete the server files as well (default: False)

    Returns:
        Dictionary with uninstallation status

    Examples:
        # Remove from config only
        uninstall_mcp_server("my-server")

        # Remove from config and delete files
        uninstall_mcp_server("my-server", delete_files=True)
    """
    try:
        success = mcp_installer.uninstall(server_name, delete_files)

        if success:
            return {
                "success": True,
                "message": f"Successfully uninstalled '{server_name}'",
                "files_deleted": delete_files
            }
        else:
            return {
                "success": False,
                "error": f"Failed to uninstall '{server_name}'"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ========== TOOL SEARCH TOOLS ==========

@mcp.tool()
def search_tools(query: str, max_results: int = 10) -> dict:
    """
    Search for tools across all loaded MCP servers using natural language.

    This is the key discovery tool - describe what you want to do and
    find the right tools without knowing their exact names.

    Args:
        query: Natural language search query (e.g., "send email", "create user", "get metrics")
        max_results: Maximum number of tools to return (default: 10)

    Returns:
        Dictionary with matching tools ranked by relevance

    Examples:
        search_tools("send email")
        search_tools("create user account")
        search_tools("database query")
        search_tools("file operations", max_results=20)

    Usage Notes:
        - Searches tool names and descriptions
        - Works across all loaded servers
        - Load servers first with load_mcp_server_dynamically()
        - Use get_tool_info() for detailed info on a specific tool
    """
    try:
        results = tool_searcher.search_tools(query, max_results)
        return {
            "success": True,
            "query": query,
            "tools": results,
            "count": len(results),
            "tip": "Use call_dynamic_server_tool(server, tool, params) to call any of these tools"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_all_tools() -> dict:
    """
    List all tools available from all loaded MCP servers.

    Provides a complete inventory of every tool you can call.

    Returns:
        Dictionary with all tools organized by server

    Example:
        list_all_tools()
        # Returns complete tool inventory

    Usage Notes:
        - Only shows tools from loaded servers
        - Load more servers with load_mcp_server_dynamically()
        - Use search_tools() to find specific tools
    """
    try:
        tools = tool_searcher.list_all_tools()
        servers = tool_searcher.list_servers()

        return {
            "success": True,
            "tools": tools,
            "count": len(tools),
            "servers": servers,
            "server_count": len(servers)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_tool_info(tool_name: str) -> dict:
    """
    Get detailed information about a specific tool.

    Provides the tool's description, parameters, and which server it belongs to.

    Args:
        tool_name: Name of the tool to look up

    Returns:
        Dictionary with tool details including schema

    Examples:
        get_tool_info("hello_world")
        get_tool_info("send_email")

    Usage Notes:
        - Returns full parameter schema
        - Shows which server provides the tool
        - Use search_tools() first to find tool names
    """
    try:
        info = tool_searcher.get_tool_info(tool_name)

        if info:
            return {
                "success": True,
                "tool": info,
                "call_with": f"call_dynamic_server_tool('{info.get('server')}', '{tool_name}', {{...params...}})"
            }
        else:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "suggestion": "Use search_tools() or list_all_tools() to find available tools"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
