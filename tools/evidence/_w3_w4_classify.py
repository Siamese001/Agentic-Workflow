"""W3/W4: Sub-categorize log_and_swallow and silent_exception_swallow entries.

For each entry determines:
- teardown/cleanup context (guardian-exempt candidates)
- has_reraise (already re-raises, broad_exception_catch false-positive)
- best_effort (optional enrichment, cache-miss style)
- re_raise_possible (structural fix candidate)

Usage:
    python tools/evidence/_w3_w4_classify.py
"""
from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

INVENTORY_PATH = Path("artifacts/adg_analysis/p2_high_severity_inventory.csv")

TEARDOWN_KEYWORDS = frozenset(
    ["teardown", "cleanup", "close", "exit", "destroy", "dispose", "finalize", "__del__", "__exit__"],
)
BEST_EFFORT_KEYWORDS = frozenset(
    ["cache", "optional", "enrich", "augment", "fallback", "hint", "suggest", "metric"],
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


def classify_entry(source_file: str, line_no: int, tree: ast.AST) -> str:
    func = get_containing_function(tree, line_no)
    func_lower = func.lower()
    if any(kw in func_lower for kw in TEARDOWN_KEYWORDS):
        return "teardown"
    if any(kw in func_lower for kw in BEST_EFFORT_KEYWORDS):
        return "best_effort"
    return "re_raise_possible"


def process_kind(kind: str, all_entries: list[dict]) -> dict:
    entries = [e for e in all_entries if e["edge_kind"] == kind]
    print(f"\n{'='*60}")
    print(f"Processing: {kind} ({len(entries)} entries)")

    sub_cats: Counter[str] = Counter()
    details: dict[str, list[str]] = {
        "teardown": [],
        "best_effort": [],
        "re_raise_possible": [],
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

        cat = classify_entry(entry["source_file"], int(entry["line_no"] or 0), tree)
        sub_cats[cat] += 1
        func = get_containing_function(tree, int(entry["line_no"] or 0))
        details[cat].append(f"{entry['source_file']}:{entry['line_no']} in {func}()")
        entry["sub_category"] = cat
        entry["containing_function"] = func
        enriched.append(entry)

    print("Sub-category breakdown:")
    for cat, cnt in sub_cats.most_common():
        print(f"  {cat}: {cnt}")

    for cat in ["teardown", "best_effort"]:
        if details[cat]:
            print(f"\n{cat} (first 5):")
            for line in details[cat][:5]:
                print(f"  {line}")

    print("\nre_raise_possible (first 5):")
    for line in details["re_raise_possible"][:5]:
        print(f"  {line}")

    return {"kind": kind, "total": len(entries), "sub_cats": dict(sub_cats), "enriched": enriched}


def main() -> None:
    import csv
    rows = list(csv.DictReader(open(INVENTORY_PATH)))

    results = {}
    for kind in ["log_and_swallow", "silent_exception_swallow"]:
        result = process_kind(kind, rows)
        results[kind] = result

        out_path = Path(f"artifacts/adg_analysis/{kind}_subcategorized.json")
        out_path.write_text(json.dumps(result["enriched"], indent=2))
        print(f"\nEnriched report: {out_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    for kind, result in results.items():
        print(f"\n{kind}: {result['total']} total")
        for cat, cnt in sorted(result["sub_cats"].items(), key=lambda x: -x[1]):
            print(f"  {cat}: {cnt}")


if __name__ == "__main__":
    main()
