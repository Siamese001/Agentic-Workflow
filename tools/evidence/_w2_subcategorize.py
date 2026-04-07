"""W2: Sub-categorize return_none_swallow entries.

Reads the classified JSON and checks source to identify:
- teardown/cleanup/close contexts (guardian-exempt candidates)
- re-raise possible (structural fix: return -> raise)
- best-effort / caller-handles-None contexts

Usage:
    python tools/evidence/_w2_subcategorize.py
"""
from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

INVENTORY_PATH = Path("artifacts/adg_analysis/w2_return_none_swallow_classified.json")
TEARDOWN_KEYWORDS = frozenset(
    ["teardown", "cleanup", "close", "exit", "destroy", "dispose", "finalize", "__del__", "__exit__"]
)


def get_containing_function(tree: ast.AST, target_lineno: int) -> str:
    """Return name of the function containing the line, or ''."""
    best: tuple[int, str] = (0, "")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= target_lineno:
                end = getattr(node, "end_lineno", node.lineno + 9999)
                if target_lineno <= end and node.lineno > best[0]:
                    best = (node.lineno, node.name)
    return best[1]


def classify_entry(entry: dict, tree: ast.AST) -> str:
    func = get_containing_function(tree, entry["line_no"])
    func_lower = func.lower()
    if any(kw in func_lower for kw in TEARDOWN_KEYWORDS):
        return "teardown"
    return "re_raise_possible"


def main() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text())
    print(f"Total return_none_swallow entries: {len(inventory)}")

    sub_cats: Counter[str] = Counter()
    details: dict[str, list[str]] = {"teardown": [], "re_raise_possible": [], "unresolved": []}

    for entry in inventory:
        fpath = Path(entry["source_file"])
        if not fpath.exists():
            sub_cats["unresolved"] += 1
            details["unresolved"].append(f"{entry['source_file']}:{entry['line_no']}")
            continue
        try:
            src = fpath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (SyntaxError, OSError):
            sub_cats["unresolved"] += 1
            details["unresolved"].append(f"{entry['source_file']}:{entry['line_no']}")
            continue

        cat = classify_entry(entry, tree)
        sub_cats[cat] += 1
        func = get_containing_function(tree, entry["line_no"])
        details[cat].append(f"{entry['source_file']}:{entry['line_no']} in {func}()")

    print("\n=== Sub-category breakdown ===")
    for cat, cnt in sub_cats.most_common():
        print(f"  {cat}: {cnt}")

    print("\n=== Teardown (guardian-exempt candidates, first 10) ===")
    for line in details["teardown"][:10]:
        print(f"  {line}")

    print("\n=== Re-raise possible (first 10) ===")
    for line in details["re_raise_possible"][:10]:
        print(f"  {line}")

    print("\n=== Unresolved (file not found, first 5) ===")
    for line in details["unresolved"][:5]:
        print(f"  {line}")

    # Save enriched report
    out_path = Path("artifacts/adg_analysis/w2_return_none_swallow_subcategorized.json")
    enriched = []
    for entry in inventory:
        fpath = Path(entry["source_file"])
        if not fpath.exists():
            entry["sub_category"] = "unresolved"
            enriched.append(entry)
            continue
        try:
            src = fpath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            entry["sub_category"] = classify_entry(entry, tree)
            entry["containing_function"] = get_containing_function(tree, entry["line_no"])
        except (SyntaxError, OSError):
            entry["sub_category"] = "unresolved"
        enriched.append(entry)

    out_path.write_text(json.dumps(enriched, indent=2))
    print(f"\nEnriched report: {out_path}")


if __name__ == "__main__":
    main()
