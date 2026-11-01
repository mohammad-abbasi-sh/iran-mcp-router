"""MCP stdio server: iran-mcp-router.

Exposes tools for routing Iranian-web tasks to the right iran-mcp server:
  - ``route_task``: task in Persian/English -> best server(s) + tool + install
  - ``list_categories``: categories the router understands, with counts

Run:  python3 mcp_server.py        (stdio transport)

Requires: mcp>=2.2  (pip install "mcp>=2.2,<3")
The routing engine itself (src/router.py) is stdlib-only.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from mcp.server.mcpserver import MCPServer

from router import load_catalog, route

mcp = MCPServer("iran-mcp-router")

_catalog_data = None


def _catalog():
    global _catalog_data
    if _catalog_data is None:
        _catalog_data = load_catalog()
    return _catalog_data


@mcp.tool()
def route_task(query: str, top_k: int = 3) -> str:
    """Route an Iranian-web task to the right iran-mcp MCP server.

    Args:
        query: The task, in Persian or English. Examples:
            "قیمت سکه امامی", "بلیط هواپیما تهران مشهد",
            "dollar price today", "cheapest flight Tehran Mashhad".
        top_k: How many candidate servers to return (1-5).

    Returns:
        JSON list of candidates, each with server_id, title, category,
        suggested_tool, install command, repo URL, score and reason.
        Install the chosen server (e.g. `uvx tgju-mcp`) and call its
        suggested_tool. Servers are read-only and need no sign-in.
    """
    top_k = max(1, min(5, int(top_k)))
    results = route(query, top_k=top_k, catalog=_catalog())
    return json.dumps(results, ensure_ascii=False, indent=1)


@mcp.tool()
def list_categories() -> str:
    """List the task categories the router understands (shopping, travel,
    prices, stocks, food, health, ...), with the server count per category."""
    from collections import Counter

    counts = Counter(s["category"] for s in _catalog()["servers"])
    return json.dumps(
        [
            {"category": cat, "servers": n}
            for cat, n in sorted(counts.items(), key=lambda x: -x[1])
        ],
        ensure_ascii=False,
        indent=1,
    )


if __name__ == "__main__":
    # Fail fast if the catalog is missing or corrupt.
    _catalog()
    mcp.run()
