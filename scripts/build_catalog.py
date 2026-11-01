#!/usr/bin/env python3
"""Build the router's catalog from iran-mcp's public servers.json.

Reads /tmp/iran-mcp/servers.json (public catalog data, MIT-licensed) and emits:
  - data/catalog.json : machine-readable catalog for the Python router
  - web/catalog.js    : the same data as a JS embed for the web demo

Single source of truth: both files are generated here, never hand-edited.
Run: python3 scripts/build_catalog.py
"""

import json
import pathlib
import sys

SRC = pathlib.Path("/tmp/iran-mcp/servers.json")
ROOT = pathlib.Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "src"))
from router import CATEGORY_KEYWORDS, INTENT_WORDS, SERVER_RULES  # noqa: E402


def main() -> None:
    if not SRC.exists():
        sys.exit(f"missing source catalog: {SRC} (clone https://github.com/sepehr071/iran-mcp first)")
    raw = json.loads(SRC.read_text(encoding="utf-8"))

    servers = []
    for s in raw:
        servers.append(
            {
                "id": s["name"],
                "title": s.get("title", s["name"]),
                "category": s.get("category", ""),
                "description": s.get("description", ""),
                "site": s.get("site", ""),
                "run": s.get("run", ""),
                "pypi": s.get("pypi", ""),
                "repo": s.get("repository", ""),
                "tools": [
                    {"name": t["name"], "summary": t.get("summary", "")}
                    for t in s.get("tools", [])
                ],
            }
        )

    payload = {"servers": servers}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "web").mkdir(exist_ok=True)
    (ROOT / "data" / "catalog.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (ROOT / "web" / "catalog.js").write_text(
        "window.IRAN_MCP_CATALOG = "
        + json.dumps(payload, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    # JS port of the routing rules -- generated from src/router.py so the
    # web demo and the Python engine can never drift apart.
    (ROOT / "web" / "router_rules.js").write_text(
        "window.IRAN_MCP_ROUTER_RULES = "
        + json.dumps(
            {
                "server_rules": SERVER_RULES,
                "category_keywords": CATEGORY_KEYWORDS,
                "intent_words": INTENT_WORDS,
            },
            ensure_ascii=False,
        )
        + ";\n",
        encoding="utf-8",
    )
    n_tools = sum(len(s["tools"]) for s in servers)
    print(f"wrote data/catalog.json + web/catalog.js: {len(servers)} servers, {n_tools} tools")
    print(f"wrote web/router_rules.js: {len(SERVER_RULES)} server rules, "
          f"{len(CATEGORY_KEYWORDS)} categories")


if __name__ == "__main__":
    main()
