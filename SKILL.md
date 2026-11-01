# iran-mcp-router

Route any Iranian-web task to the right iran-mcp MCP server -- before guessing, searching the web, or reading the whole catalog.

## When to use

Use this skill when the user wants something from the Iranian web that an
MCP server might do: prices (gold, coin, currency, phones, cars), flights /
trains / buses / hotels, food delivery, doctors and appointments, the Tehran
stock market, classifieds (Divar/Sheypoor), jobs, maps and directions,
Persian news, sports scores, laws, or similar.

The iran-mcp project publishes 70+ MCP servers with 800+ tools. No agent can
keep that catalog in its head. **Call the router first** -- one cheap,
deterministic call -- instead of reading catalog docs or guessing tool names.

## How to use

### Option A -- MCP server (recommended)

Add to your MCP client config (Claude Code, Cursor, any MCP client):

```json
{
  "mcpServers": {
    "iran-mcp-router": {
      "command": "python3",
      "args": ["/path/to/iran-mcp-router/mcp_server.py"]
    }
  }
}
```

Then call:

- `route_task(query, top_k=3)` -- e.g. `route_task("قیمت سکه امامی")`.
  Returns ranked candidates: `server_id`, `title`, `suggested_tool`,
  `install` (e.g. `uvx tgju-mcp`), `repo`, `score`, `reason`.
- `list_categories()` -- categories the router understands, with counts.

Install the chosen server (`uvx <name>-mcp`) and call its `suggested_tool`.
All routed servers are read-only and need no sign-in.

### Option B -- stdlib script (no MCP setup)

```bash
python3 scripts/router_cli.py "بلیط هواپیما تهران مشهد"   # via src/router.py
```

or in Python:

```python
import sys
sys.path.insert(0, "src")
from router import route
print(route("نوبت دکتر قلب در تهران", top_k=2))
```

## Before / after

**Before** (no router): "قیمت دلار امروز چنده؟" -> the agent reads catalog
docs, guesses `tgju` vs `cbi` vs a web search, and often picks wrong.

**After** (router): one call ->

```json
[
  {
    "server_id": "tgju-mcp",
    "title": "TGJU Prices",
    "suggested_tool": "tj_get_prices",
    "install": "uvx tgju-mcp",
    "repo": "https://github.com/sepehr071/tgju-mcp",
    "reason": "کلیدواژه: دلار"
  }
]
```

-> install `uvx tgju-mcp` -> call `tj_get_prices` -> answer.

## Notes

- Queries work in Persian (نیم‌فاصله and ي/ك variants normalized) and English.
- The router is deterministic: same query, same ranking, every time.
- It routes; it does not fetch. The data comes from the iran-mcp servers.
- Complementary to [sepehr071/iran-mcp](https://github.com/sepehr071/iran-mcp)
  (not affiliated) -- it answers "which server?", they answer the task.
