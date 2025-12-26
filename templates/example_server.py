#!/usr/bin/env python3
"""
Example MCP Server Template

Use this as a starting point for creating your own MCP servers.
"""

from fastmcp import FastMCP
from typing import Dict, List, Optional

# Initialize FastMCP server with a unique name
mcp = FastMCP("example-server")


@mcp.tool()
def hello_world(name: str = "World") -> dict:
    """
    A simple hello world tool.

    Args:
        name: Name to greet (default: "World")

    Returns:
        Dictionary with greeting message
    """
    return {
        "success": True,
        "message": f"Hello, {name}!"
    }


@mcp.tool()
def add_numbers(a: int, b: int) -> dict:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the sum
    """
    return {
        "success": True,
        "result": a + b
    }


@mcp.tool()
def list_items(items: List[str], filter_prefix: Optional[str] = None) -> dict:
    """
    Process a list of items with optional filtering.

    Args:
        items: List of strings to process
        filter_prefix: Optional prefix to filter items

    Returns:
        Dictionary with filtered items
    """
    if filter_prefix:
        filtered = [item for item in items if item.startswith(filter_prefix)]
    else:
        filtered = items

    return {
        "success": True,
        "items": filtered,
        "count": len(filtered)
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
