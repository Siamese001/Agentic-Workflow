#!/usr/bin/env python3
"""Derive central candidates mechanically from callsites.json and inventory.json."""

import json
from pathlib import Path


def main():
    repo_root = Path.cwd()

    # Load callsites.json
    with open(repo_root / "docs/reports/sub/ast_fuzzy_callsites.json", encoding="utf-8") as f:
        callsites = json.load(f)

    # Load inventory.json
    with open(repo_root / "docs/reports/sub/ast_fuzzy_inventory.json", encoding="utf-8") as f:
        inventory = json.load(f)

    # Build set of candidate names from inventory
    inventory_candidates = set()
    for file_entry in inventory["files"]:
        for candidate in file_entry.get("candidates", []):
            inventory_candidates.add(candidate["name"])

    # Keywords for filtering
    keywords = {
        "parse",
        "ast",
        "dump",
        "hash",
        "normalize",
        "token",
        "similarity",
        "fuzzy",
        "match",
        "compare",
    }

    # Filter and validate candidates
    valid_candidates = []
    for symbol, data in callsites.items():
        # Skip dunder names
        if symbol.startswith("__") and symbol.endswith("__"):
            continue

        # Check keyword match (case-insensitive)
        symbol_lower = symbol.lower()
        if not any(kw in symbol_lower for kw in keywords):
            continue

        # Must have at least 1 definition in callsites.json
        if not data.get("definitions"):
            continue

        # Must appear as candidate name in inventory.json
        if symbol not in inventory_candidates:
            continue

        # Get first definition location
        first_def = data["definitions"][0]
        def_location = f"{first_def['path']}:{first_def['line']}"

        valid_candidates.append(
            {"name": symbol, "refs": data["inbound_ref_count"], "def_location": def_location}
        )

    # Sort by inbound_ref_count DESC, then name ASC
    valid_candidates.sort(key=lambda x: (-x["refs"], x["name"]))

    # Output results
    print(f"Total valid candidates passing gate: {len(valid_candidates)}")
    print()
    for i, c in enumerate(valid_candidates[:10], 1):
        print(f"{i}. {c['name']} ({c['refs']} refs) - {c['def_location']}")


if __name__ == "__main__":
    main()
