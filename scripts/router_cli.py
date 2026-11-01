#!/usr/bin/env python3
"""CLI for the iran-mcp router: which iran-mcp server does this task need?

Usage:
    python3 scripts/router_cli.py "قیمت سکه امامی" [--top 3] [--json]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from router import route  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Route an Iranian-web task to the right iran-mcp server.")
    ap.add_argument("query", nargs="+", help="the task, in Persian or English")
    ap.add_argument("--top", type=int, default=3, help="candidates to show (1-5)")
    ap.add_argument("--json", action="store_true", help="raw JSON output")
    args = ap.parse_args()

    results = route(" ".join(args.query), top_k=args.top)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return
    if not results:
        print("no matching iran-mcp server found for this task.")
        return
    for r in results:
        print(f"[{r['score']}] {r['server_id']} — {r['title']} ({r['category']})")
        print(f"    tool:    {r['suggested_tool']}")
        print(f"    install: {r['install']}")
        print(f"    repo:    {r['repo']}")
        print(f"    why:     {r['reason']}")


if __name__ == "__main__":
    main()
