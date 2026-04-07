"""W5: Sub-categorize broad_exception_catch entries.

For each entry checks AST to determine:
- has_reraise: body ends with raise (guardian-exempt candidate with justification)
- teardown: in cleanup/close/exit context
- best_effort: cache/optional/fallback context
- narrows_possible: single-type exception could be narrowed
- re_raise_possible: structural fix candidate

Usage:
    python tools/evidence/_w5_bec_classify.py
"""
from __future__ import annotations

import ast
import csv
import json
from collections import Counter
from pathlib import Path

INVENTORY_PATH = Path("artifacts/adg_analysis/p2_high_severity_inventory.csv")
TARGET_KIND = "broad_exception_catch"

TEARDOWN_KEYWORDS = frozenset(
    ["teardown", "cleanup", "close", "exit", "destroy", "dispose", "finalize", "__del__", "__exit__"],
)
BEST_EFFORT_KEYWORDS = frozenset(
    ["cache", "optional", "enrich", "augment", "fallback", "hint", "suggest", "metric", "log"],
)


def get_containing_function(tree: ast.AST, target_lineno: int) -> str:
    best: tuple[int, str] = (0, "")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= target_lineno:
                end = getattr(node, "end_lineno", node.lineno + 9999)
                if target_lineno <= end and node.lineno > best[0]:
                    best = (node.lineno, node.name)
    return best[1]


def handler_body_has_reraise(handler: ast.ExceptHandler) -> bool:
    """Return True if the except body contains a bare raise statement."""
    for node in ast.walk(handler):
        if isinstance(node, ast.Raise) and node.exc is None:
            return True
    return False


def classify_bec(source_file: str, line_no: int, tree: ast.AST) -> str:
    func = get_containing_function(tree, line_no)
    func_lower = func.lower()

    # Check if exception handler at this line re-raises
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.lineno == line_no:
            if handler_body_has_reraise(node):
                return "has_reraise"

    if any(kw in func_lower for kw in TEARDOWN_KEYWORDS):
        return "teardown"
    if any(kw in func_lower for kw in BEST_EFFORT_KEYWORDS):
        return "best_effort"
    return "narrows_possible"


def main() -> None:
    rows = list(csv.DictReader(open(INVENTORY_PATH)))
    entries = [r for r in rows if r["edge_kind"] == TARGET_KIND]
    print(f"broad_exception_catch total: {len(entries)}")

    sub_cats: Counter[str] = Counter()
    details: dict[str, list[str]] = {
        "has_reraise": [],
        "teardown": [],
        "best_effort": [],
        "narrows_possible": [],
        "unresolved": [],
    }
    enriched = []

    for entry in entries:
        fpath = Path(entry["source_file"])
        if not fpath.exists():
            sub_cats["unresolved"] += 1
            details["unresolved"].append(f"{entry['source_file']}:{entry['line_no']}")
            entry["sub_category"] = "unresolved"
            enriched.append(entry)
            continue
        try:
            src = fpath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (SyntaxError, OSError):
            sub_cats["unresolved"] += 1
            details["unresolved"].append(f"{entry['source_file']}:{entry['line_no']}")
            entry["sub_category"] = "unresolved"
            enriched.append(entry)
            continue

        cat = classify_bec(entry["source_file"], int(entry["line_no"] or 0), tree)
        sub_cats[cat] += 1
        func = get_containing_function(tree, int(entry["line_no"] or 0))
        details[cat].append(f"{entry['source_file']}:{entry['line_no']} in {func}()")
        entry["sub_category"] = cat
        entry["containing_function"] = func
        enriched.append(entry)

    print("\n=== Sub-category breakdown ===")
    for cat, cnt in sub_cats.most_common():
        print(f"  {cat}: {cnt}")

    for cat in ["has_reraise", "teardown", "best_effort"]:
        if details[cat]:
            print(f"\n{cat} (first 5):")
            for line in details[cat][:5]:
                print(f"  {line}")

    print("\nnarrows_possible (first 5):")
    for line in details["narrows_possible"][:5]:
        print(f"  {line}")

    if details["unresolved"]:
        print("\nunresolved (first 5):")
        for line in details["unresolved"][:5]:
            print(f"  {line}")

    out_path = Path("artifacts/adg_analysis/broad_exception_catch_subcategorized.json")
    out_path.write_text(json.dumps(enriched, indent=2))
    print(f"\nEnriched report: {out_path}")
    print(f"Total: {len(enriched)} entries")


if __name__ == "__main__":
    main()
