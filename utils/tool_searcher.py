"""
Tool Searcher - Dynamic tool discovery for MCP Proxy

Discovers and searches tools from dynamically loaded MCP servers.
"""

from typing import List, Dict, Any, Optional


class ToolSearcher:
    """
    Dynamic tool discovery system for MCP Proxy.

    Searches across tools from dynamically loaded servers.
    """

    def __init__(self, server_loader=None):
        """
        Initialize the tool searcher.

        Args:
            server_loader: DynamicServerLoader instance to get tools from
        """
        self.server_loader = server_loader
        self._cached_tools = {}

    def _get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tools from loaded servers.

        Returns:
            Dictionary mapping tool names to their info
        """
        if not self.server_loader:
            return {}

        all_tools = {}
        loaded = self.server_loader.get_loaded_servers()

        for server in loaded.get("servers", []):
            server_name = server.get("name", "")
            server_tools = self.server_loader.server_tools.get(server_name, {})

            for tool_name, tool_info in server_tools.items():
                all_tools[tool_name] = {
                    "name": tool_name,
                    "server": server_name,
                    "description": tool_info.get("description", ""),
                    "inputSchema": tool_info.get("inputSchema", {})
                }

        return all_tools

    def search_tools(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tools matching the query.

        Args:
            query: Natural language search query
            max_results: Maximum number of tools to return

        Returns:
            List of matching tools with relevance scores
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []

        all_tools = self._get_all_tools()

        for tool_name, tool_info in all_tools.items():
            score = 0
            description = tool_info.get("description", "").lower()

            # Exact tool name match
            if query_lower in tool_name.lower():
                score += 20

            # Word matches in tool name
            for word in query_words:
                if word in tool_name.lower():
                    score += 10

            # Word matches in description
            for word in query_words:
                if word in description:
                    score += 5

            if score > 0:
                results.append({
                    "tool": tool_name,
                    "server": tool_info.get("server", ""),
                    "description": tool_info.get("description", ""),
                    "score": score
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool information dict or None if not found
        """
        all_tools = self._get_all_tools()
        return all_tools.get(tool_name)

    def list_all_tools(self) -> List[Dict[str, str]]:
        """
        List all available tools from loaded servers.

        Returns:
            List of tool info dicts
        """
        all_tools = self._get_all_tools()
        return [
            {
                "name": name,
                "server": info.get("server", ""),
                "description": info.get("description", "")[:100]
            }
            for name, info in sorted(all_tools.items())
        ]

    def list_servers(self) -> List[str]:
        """
        List all loaded servers.

        Returns:
            List of server names
        """
        if not self.server_loader:
            return []

        loaded = self.server_loader.get_loaded_servers()
        return [s.get("name", "") for s in loaded.get("servers", [])]
