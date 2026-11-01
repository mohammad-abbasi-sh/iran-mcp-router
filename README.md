<div align="center">

# iran-mcp-router

**Which iran-mcp server does this task need? Ask the router, not the catalog.**

[فارسی](README-fa.md)

</div>

The [iran-mcp](https://github.com/sepehr071/iran-mcp) project gives AI agents
the Iranian web: 71 MCP servers, 883 tools -- Torob prices, Divar classifieds,
TSETMC stocks, TGJU gold/currency, Snappfood, Paziresh24 doctors, flights,
maps, news and more. But no agent can keep 883 tools in its head, and guessing
the right server wastes context and gets it wrong.

`iran-mcp-router` is a tiny deterministic router: give it a task in Persian or
English, get back the right server, the tool to call first, and the install
command. One cheap call instead of reading the whole catalog.

```bash
$ python3 scripts/router_cli.py "قیمت سکه امامی"
[6] tgju-mcp — TGJU Prices (prices)
    tool:    tj_get_prices
    install: uvx tgju-mcp
    repo:    https://github.com/sepehr071/tgju-mcp
    why:     کلیدواژه: سکه
```

```bash
$ python3 scripts/router_cli.py "cheapest flight from Tehran to Mashhad"
[3] mrbilit-mcp — MrBilit (travel)
    tool:    mb_search_flights
    install: uvx mrbilit-mcp
```

## How it works

1. **Persian-aware normalization** (stdlib only): NFKC, Arabic `ي/ك` →
   Persian `ی/ک`, Persian/Arabic-Indic digits → ASCII, ZWNJ removed, so
   `مي‌خوام`, `میخوام` and `می‌خواهم` all match the same way.
2. **Weighted keyword routing**: hand-authored keyword sets per server
   (weight 3), server-name aliases (weight 4), category fallbacks (weight 1).
   Word-boundary aware -- `ارز` (currency) never fires inside `ارزون` (cheap).
3. **Intent-refined tool choice**: "ارزون‌ترین گوشی" → `tb_cheapest`,
   not just `tb_search`; "تاریخچه قیمت" → the history tool.
4. Deterministic: same query → same ranking, every time. Each result carries
   its `reason` (which keywords matched), so the choice is explainable.

The catalog (`data/catalog.json`, 71 servers / 883 tools) is generated from
iran-mcp's public `servers.json` by `scripts/build_catalog.py` -- single
source of truth, no hand-edited data, no invented tool names.

## Install

**Claude Code** (MCP server):

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

Needs `pip install "mcp>=2.2,<3"`. Then call `route_task(query, top_k=3)`.

**Claude.ai**: upload `dist/iran-mcp-router-claude-ai.zip` as a skill.

**Cursor**: the repo ships `.cursor/rules/iran-mcp-router.mdc` -- it tells the
agent to route before guessing. Copy that file into your project's
`.cursor/rules/`.

**Windsurf / Cline / Continue**: use the MCP server config above (any MCP
client works), or point the agent at `SKILL.md`.

**No MCP setup?** The engine is stdlib-only:

```bash
python3 scripts/router_cli.py "نوبت دکتر قلب در تهران"
```

## Web demo

Open `index.html` -- a self-contained, offline RTL demo (Persian-first dark
design). Type a task, get ranked server cards with copy-paste install
commands. No external requests.

## Tests

```bash
python3 -m unittest discover -s tests   # 22 tests, stdlib only
```

Covers normalization edge cases (نیم‌فاصله, ي/ك, Persian digits) and routing
cases in Persian and English.

## Roadmap

- More servers as the iran-mcp catalog grows (regenerate via build script)
- Confidence scores calibrated on real query logs
- Optional write-capable routing if iran-mcp ever adds authed servers

## Credit

Complementary to [sepehr071/iran-mcp](https://github.com/sepehr071/iran-mcp)
-- it answers *"which server?"*, they answer the task itself. Not affiliated;
all server/tool names and install commands come from their public catalog
(MIT). Thanks to Sepehr Radmard for building the ecosystem this routes over.

## License

MIT
