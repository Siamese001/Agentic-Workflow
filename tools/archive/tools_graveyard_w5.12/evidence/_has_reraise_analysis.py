"""Analyse has_reraise broad_exception_catch entries.

For each entry, inspects the except handler body to determine:
- What the handler does between catch and re-raise (log? transform? nothing?)
- Whether the exception variable is used (except Exception as e:)
- Whether the body is truly just re-raise (1 statement) or has side effects

This guides the narrowing strategy:
- Pure re-raise (no body except raise): remove handler entirely or use 'raise' at call site
- Log + re-raise: keep handler, narrow type to Exception (already broad, add comment)
- Transform + re-raise: keep handler, narrow where possible

Usage:
    python tools/evidence/_has_reraise_analysis.py
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

CANDIDATES_PATH = Path("artifacts/adg_analysis/hitl_guardian_candidates.json")


def count_handler_stmts(handler: ast.ExceptHandler) -> int:
    return len(handler.body)


def handler_is_pure_reraise(handler: ast.ExceptHandler) -> bool:
    """True if the handler body is exactly one bare raise."""
    if len(handler.body) != 1:
        return False
    stmt = handler.body[0]
    return isinstance(stmt, ast.Raise) and stmt.exc is None


def handler_has_log(handler: ast.ExceptHandler) -> bool:
    for node in ast.walk(handler):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in (
                "error",
                "warning",
                "exception",
                "info",
                "debug",
            ):
                return True
            if isinstance(func, ast.Name) and func.id in ("print",):
                return True
    return False


def get_containing_function(tree: ast.AST, target_lineno: int) -> str:
    best: tuple[int, str] = (0, "")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= target_lineno:
                end = getattr(node, "end_lineno", node.lineno + 9999)
                if target_lineno <= end and node.lineno > best[0]:
                    best = (node.lineno, node.name)
    return best[1]


def main() -> None:
    candidates = json.loads(CANDIDATES_PATH.read_text())
    reraise_entries = [c for c in candidates if c["sub_category"] == "has_reraise"]
    print(f"has_reraise entries: {len(reraise_entries)}")

    sub_cats: Counter[str] = Counter()
    enriched = []

    for entry in reraise_entries:
        fpath = Path(entry["source_file"])
        if not fpath.exists():
            entry["reraise_type"] = "unresolved"
            sub_cats["unresolved"] += 1
            enriched.append(entry)
            continue
        try:
            src = fpath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (SyntaxError, OSError):
            entry["reraise_type"] = "unresolved"
            sub_cats["unresolved"] += 1
            enriched.append(entry)
            continue

        line_no = int(entry["line_no"])
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.lineno == line_no:
                found = True
                if handler_is_pure_reraise(node):
                    entry["reraise_type"] = "pure_reraise"
                    sub_cats["pure_reraise"] += 1
                elif handler_has_log(node):
                    entry["reraise_type"] = "log_then_reraise"
                    sub_cats["log_then_reraise"] += 1
                else:
                    entry["reraise_type"] = "transform_then_reraise"
                    sub_cats["transform_then_reraise"] += 1
                entry["stmt_count"] = count_handler_stmts(node)
                entry["func"] = get_containing_function(tree, line_no)
                break

        if not found:
            entry["reraise_type"] = "handler_not_found"
            sub_cats["handler_not_found"] += 1

        enriched.append(entry)

    print("\n=== Reraise type breakdown ===")
    for cat, cnt in sub_cats.most_common():
        print(f"  {cat}: {cnt}")

    # Show examples of pure_reraise (candidates for handler removal)
    pure = [e for e in enriched if e.get("reraise_type") == "pure_reraise"]
    print(f"\n=== pure_reraise (first 10 of {len(pure)}) — remove handler or leave as-is ===")
    for e in pure[:10]:
        print(f"  {e['source_file']}:{e['line_no']}  in {e.get('func', '')}()")

    log_rr = [e for e in enriched if e.get("reraise_type") == "log_then_reraise"]
    print(f"\n=== log_then_reraise (first 10 of {len(log_rr)}) — keep, narrow type acceptable ===")
    for e in log_rr[:10]:
        print(f"  {e['source_file']}:{e['line_no']}  in {e.get('func', '')}()")

    out = Path("artifacts/adg_analysis/has_reraise_enriched.json")
    out.write_text(json.dumps(enriched, indent=2))
    print(f"\nEnriched: {out}  ({len(enriched)} entries)")


if __name__ == "__main__":
    main()
