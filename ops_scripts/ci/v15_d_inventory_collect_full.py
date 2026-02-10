#!/usr/bin/env python3
"""
V15 Phase 4 Full Repo-Wide Conformance Inventory.

AST-scans the repo for all runtime entrypoints that match the V15 scope rule,
cross-references against the existing P2 inventory, and classifies each finding.

Output schema version: 4.0.0

Usage:
    python ops_scripts/ci/v15_d_inventory_collect_full.py --out v15_d_inventory_p4.json
    python ops_scripts/ci/v15_d_inventory_collect_full.py --out v15_d_inventory_p4.json --repo-root .
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Directories to scan (relative to repo root)
SCAN_ROOTS = ("agentic_core", "ops_scripts")

# Existing P2 inventory location
P2_INVENTORY_REL = "docs/reports/plans/v15_phase2_wave2_1_runtime_entrypoints.json"

# Guard decorator names we recognise
GUARD_NAMES_DIRECT = frozenset({"v15_runtime_guard"})
GUARD_NAMES_LAZY = frozenset({"_optional_v15_runtime_guard"})


def resolve_repo_root(start: Path | None = None) -> Path:
    """Walk upward from *start* until repo markers are found."""
    cur = (start or Path(__file__)).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


def _node_name(node: ast.expr) -> str | None:
    """Extract simple name from AST Name or Attribute node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def has_v15_guard(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict | None:
    """Check if a function/method has a v15_runtime_guard decorator.

    Returns evidence dict if found, None otherwise.
    """
    for dec in func_node.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        # Shape 1: @v15_runtime_guard("ID")
        fname = _node_name(dec.func)
        if fname in GUARD_NAMES_DIRECT and dec.args:
            arg = dec.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return {
                    "guard_id": arg.value,
                    "shape": "direct",
                    "line": dec.lineno,
                }
        # Shape 2: @_optional_v15_runtime_guard()("ID")
        if isinstance(dec.func, ast.Call):
            inner_name = _node_name(dec.func.func)
            if inner_name in GUARD_NAMES_LAZY and dec.args:
                arg = dec.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    return {
                        "guard_id": arg.value,
                        "shape": "lazy",
                        "line": dec.lineno,
                    }
    return None


def scan_file(filepath: Path, repo_root: Path) -> list[dict]:
    """AST-scan a single Python file for functions/methods and their guard status."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    rel_path = str(filepath.relative_to(repo_root)).replace("\\", "/")
    results: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Determine if this is a method (inside a class)
        class_name = None
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.iter_child_nodes(parent):
                    if child is node:
                        class_name = parent.name
                        break

        symbol = f"{class_name}.{node.name}" if class_name else node.name
        guard = has_v15_guard(node)

        results.append(
            {
                "file": rel_path,
                "symbol": symbol,
                "function_name": node.name,
                "class_name": class_name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "has_guard": guard is not None,
                "guard_info": guard,
            },
        )

    return results


def load_p2_inventory(repo_root: Path) -> dict[str, dict]:
    """Load existing P2 inventory and return a dict keyed by entrypoint ID."""
    inv_path = repo_root / P2_INVENTORY_REL
    if not inv_path.exists():
        return {}
    data = json.loads(inv_path.read_text(encoding="utf-8"))
    return {ep["id"]: ep for ep in data.get("entrypoints", [])}


def collect_full_inventory(repo_root: Path) -> dict:
    """Scan repo and produce full conformance inventory."""
    p2_inv = load_p2_inventory(repo_root)
    p2_ids = set(p2_inv.keys())
    p2_paths = {ep["path"] for ep in p2_inv.values()}

    all_guarded: list[dict] = []
    all_unguarded_in_scope: list[dict] = []
    all_unguarded_out_of_scope: list[dict] = []

    scanned_files = 0

    for scan_root_name in SCAN_ROOTS:
        scan_root = repo_root / scan_root_name
        if not scan_root.is_dir():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            scanned_files += 1
            entries = scan_file(py_file, repo_root)
            rel_path = str(py_file.relative_to(repo_root)).replace("\\", "/")

            for entry in entries:
                if entry["has_guard"]:
                    guard_id = entry["guard_info"]["guard_id"]
                    in_p2 = guard_id in p2_ids
                    all_guarded.append(
                        {
                            **entry,
                            "in_p2_inventory": in_p2,
                            "classification": "WIRED",
                        },
                    )
                else:
                    # Classify: is this file in the P2 inventory scope?
                    in_p2_scope = rel_path in p2_paths
                    # Heuristic: private/dunder methods are generally out of scope
                    fname = entry["function_name"]
                    is_private = fname.startswith("_") and not fname.startswith("__")
                    is_dunder = fname.startswith("__") and fname.endswith("__")
                    is_test = "test" in rel_path.lower()

                    if is_dunder or is_test:
                        classification = "OUT_OF_SCOPE"
                    elif in_p2_scope:
                        classification = "IN_SCOPE_UNGUARDED"
                    elif is_private:
                        classification = "PRIVATE_UNGUARDED"
                    else:
                        classification = "PUBLIC_UNGUARDED"

                    target = (
                        all_unguarded_in_scope
                        if classification == "IN_SCOPE_UNGUARDED"
                        else all_unguarded_out_of_scope
                    )
                    target.append(
                        {
                            **entry,
                            "in_p2_inventory": False,
                            "classification": classification,
                        },
                    )

    # Cross-reference: which P2 inventory IDs are WIRED vs UNWIRED?
    guarded_ids = {e["guard_info"]["guard_id"] for e in all_guarded if e["guard_info"]}
    p2_wired = sorted(p2_ids & guarded_ids)
    p2_already_enforced = sorted(eid for eid, ep in p2_inv.items() if ep.get("already_v15_enforced"))
    p2_unwired = sorted(p2_ids - guarded_ids - set(p2_already_enforced))

    return {
        "schema_version": "4.0.0",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scan_roots": list(SCAN_ROOTS),
        "scanned_files": scanned_files,
        "summary": {
            "total_guarded_functions": len(all_guarded),
            "total_in_scope_unguarded": len(all_unguarded_in_scope),
            "total_out_of_scope": len(all_unguarded_out_of_scope),
            "p2_inventory_total": len(p2_inv),
            "p2_wired": len(p2_wired),
            "p2_already_enforced": len(p2_already_enforced),
            "p2_unwired": len(p2_unwired),
            "p2_unwired_ids": p2_unwired,
        },
        "guarded": all_guarded,
        "in_scope_unguarded": all_unguarded_in_scope,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="V15 Phase 4 Full Repo-Wide Conformance Inventory",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output JSON path",
    )
    args = parser.parse_args()

    repo_root = args.repo_root or resolve_repo_root()
    inventory = collect_full_inventory(repo_root)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    s = inventory["summary"]
    print(f"Scanned {inventory['scanned_files']} files across {SCAN_ROOTS}")
    print(f"  Guarded functions:       {s['total_guarded_functions']}")
    print(f"  In-scope unguarded:      {s['total_in_scope_unguarded']}")
    print(f"  Out-of-scope unguarded:  {s['total_out_of_scope']}")
    print(
        f"  P2 inventory: {s['p2_inventory_total']} total, "
        f"{s['p2_wired']} wired, "
        f"{s['p2_already_enforced']} already enforced, "
        f"{s['p2_unwired']} unwired",
    )
    if s["p2_unwired_ids"]:
        print(f"  P2 UNWIRED IDs: {s['p2_unwired_ids']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
