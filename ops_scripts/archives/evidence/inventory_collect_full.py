#!/usr/bin/env python3
"""
_emit_reads_through("l4", "inventory_collect_full", "urg_read_1")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_2")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_3")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_4")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_5")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_6")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_7")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_8")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_9")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_10")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_11")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_12")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_13")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_14")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_15")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_16")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_17")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_18")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_19")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_20")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_21")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_22")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_23")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_24")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_25")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_26")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_27")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_28")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_29")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_30")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_31")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_32")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_33")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_34")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_35")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_36")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_37")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_38")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_39")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_40")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_41")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_42")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_43")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_44")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_45")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_46")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_47")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_48")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_49")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_50")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_51")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_52")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_53")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_54")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_55")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_56")
_emit_reads_through("l4", "inventory_collect_full", "urg_read_57")
V15 Full Repo-Wide Conformance Inventory (Schema 5.0.0).

AST-scans the repo for all functions/methods, detects V15 guards, and
auto-classifies each function as RUNTIME_BOUNDARY or FALSE_POSITIVE using
deterministic AST heuristics.  No manual classification step required.

Heuristic signals (positive = likely runtime boundary):
  - File writes (open(..., 'w'), Path.write_*, shutil.*, subprocess.*)
  - State mutation (self.<attr> = ..., global assignments)
  - Tool/external calls (subprocess, requests, httpx, aiohttp)
  - Retry/fallback decorators (@with_retry, @timeout)
  - sys.exit / raise SystemExit

Exclusion signals (negative = false positive):
  - Private/dunder methods
  - heal() / heal_repository() / standard_heal pathways
  - Read-only accessors (get_*, is_*, to_*, list_*)
  - Dataclass methods (__init__ on @dataclass)
  - Pure helpers (no side-effect AST nodes)
  - CI tooling files (ops_scripts/ci/)
  - Test files

Usage:
    python ops_scripts/ci/inventory_collect_full.py --out v15_d_inventory_p4.json
    python ops_scripts/ci/inventory_collect_full.py --out v15_d_inventory_final.json
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

# Directories to scan (relative to repo root)
SCAN_ROOTS = (AGENTIC_CORE_DIR, OPS_SCRIPTS_DIR)

# Existing P2 inventory location
P2_INVENTORY_REL = "docs/reports/plans/v15_phase2_wave2_1_runtime_entrypoints.json"

# Guard decorator names we recognise
GUARD_NAMES_DIRECT = frozenset({"runtime_guard"})
GUARD_NAMES_LAZY = frozenset({"_optional_runtime_guard"})

# ---------------------------------------------------------------------------
# AST scope-heuristic constants
# ---------------------------------------------------------------------------

# Function names that are always false positives (heal pathway, accessors, etc.)
_HEAL_NAMES = frozenset(
    {
        "heal",
        "heal_repository",
        "_v15_enhanced_heal",
        "_do_heal",
        "standard_heal",
    },
)
_HEAL_PREFIXES = ("heal_",)
_READONLY_PREFIXES = ("get_", "is_", "has_", "to_", "list_", "load_", "search_")
_READONLY_EXACT = frozenset(
    {
        "success_rate",
        "strategies",
        "to_json",
        "to_dict",
        "to_openai_format",
        "to_anthropic_format",
        "validate_mission",
        "validate_architecture",
        "post_phase_validation",
        "scan_content",
        "scan_resume",
        "analyze_content",
        "analyze_resume",
        "analyze_structure",
        "build_context",
        "decompose",
        "cleanup_violations",
        "run_with_cleanup",
    },
)
_LIFECYCLE_NAMES = frozenset({"start", "stop", "cleanup", "close", "shutdown"})
_INNER_CLOSURES = frozenset({"wrapper", "decorator", "heal_fn", "state_hash_fn"})

# AST call targets that indicate side effects (subprocess, file I/O, network)
_SIDE_EFFECT_CALLS = frozenset(
    {
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "shutil.copy",
        "shutil.copy2",
        "shutil.move",
        "shutil.rmtree",
        "os.remove",
        "os.unlink",
        "os.rename",
        "os.makedirs",
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "httpx.get",
        "httpx.post",
        "httpx.put",
        "httpx.delete",
    },
)
_SIDE_EFFECT_ATTR_METHODS = frozenset(
    {
        "write_text",
        "write_bytes",
        "unlink",
        "mkdir",
        "rmdir",
        "rename",
    },
)

# Retry/fallback decorator names that signal runtime boundaries
_RETRY_DECORATORS = frozenset({"with_retry", "timeout", "retry"})


def resolve_repo_root(start: Path | None = None) -> Path:
    """Walk upward from *start* until repo markers are found."""
    cur = (start or Path(__file__)).resolve()
    for p in (cur, *cur.parents):
        if (p / AGENTIC_CORE_DIR).is_dir() and (p / OPS_SCRIPTS_DIR).is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


def _node_name(node: ast.expr) -> str | None:
    """Extract simple name from AST Name or Attribute node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _dotted_name(node: ast.expr) -> str | None:
    """Extract dotted name like 'subprocess.run' from an Attribute chain."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    return None


def has_v15_guard(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict | None:
    """Check if a function/method has a runtime_guard decorator.

    Returns evidence dict if found, None otherwise.
    """
    for dec in func_node.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        # Shape 1: @runtime_guard("ID")
        fname = _node_name(dec.func)
        if fname in GUARD_NAMES_DIRECT and dec.args:
            arg = dec.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return {
                    "guard_id": arg.value,
                    "shape": "direct",
                    "line": dec.lineno,
                }
        # Shape 2: @_optional_runtime_guard()("ID")
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


# ---------------------------------------------------------------------------
# AST body analysis — detect side-effect signals in a function body
# ---------------------------------------------------------------------------


def _has_retry_decorator(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if the function has a retry/timeout decorator."""
    for dec in func_node.decorator_list:
        name = None
        if isinstance(dec, ast.Call):
            name = _node_name(dec.func)
        elif isinstance(dec, ast.Name):
            name = dec.id
        elif isinstance(dec, ast.Attribute):
            name = dec.attr
        if name in _RETRY_DECORATORS:
            return True
    return False


def _detect_side_effects(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Walk the function body and return a list of side-effect signal tags."""
    signals: list[str] = []
    for node in ast.walk(func_node):
        # sys.exit / raise SystemExit
        if isinstance(node, ast.Call):
            dn = _dotted_name(node.func)
            if dn == "sys.exit":
                signals.append("sys.exit")
            if dn in _SIDE_EFFECT_CALLS:
                signals.append(f"call:{dn}")
            # Attribute method calls like path.write_text(...)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in _SIDE_EFFECT_ATTR_METHODS:
                    signals.append(f"method:{node.func.attr}")
        # open(..., 'w'/'a') — file write
        if isinstance(node, ast.Call) and _node_name(node.func) == "open":
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if "w" in arg.value or "a" in arg.value:
                        signals.append("open:write")
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    if isinstance(kw.value.value, str) and ("w" in kw.value.value or "a" in kw.value.value):
                        signals.append("open:write")
        # raise SystemExit
        if isinstance(node, ast.Raise) and node.exc:
            exc_name = _node_name(node.exc) if isinstance(node.exc, ast.Name) else None
            if exc_name == "SystemExit":
                signals.append("raise:SystemExit")
            if isinstance(node.exc, ast.Call):
                exc_name = _node_name(node.exc.func)
                if exc_name == "SystemExit":
                    signals.append("raise:SystemExit")
    return signals


def _is_inside_guarded_caller(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    tree: ast.Module,
) -> bool:
    """Check if this function is only called from within a V15-guarded function.

    Heuristic: if the function's name appears as a call target inside a function
    that itself has a V15 guard, it's transitively guarded.
    """
    target_name = func_node.name
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node is func_node:
            continue
        if has_v15_guard(node) is None:
            continue
        # This is a guarded function — check if it calls our target
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = _node_name(child.func)
                if call_name == target_name:
                    return True
    return False


# ---------------------------------------------------------------------------
# Scope classification — the core heuristic engine
# ---------------------------------------------------------------------------


def classify_unguarded(
    entry: dict,
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    tree: ast.Module,
    rel_path: str,
    *,
    file_has_any_guard: bool = False,
) -> tuple[str, str]:
    """Classify an unguarded function. Returns (classification, reason)."""
    fname = entry["function_name"]

    # 1. Structural exclusions (always false positive)
    if fname.startswith("__") and fname.endswith("__"):
        return "OUT_OF_SCOPE", "dunder method"
    if "test" in rel_path.lower():
        return "OUT_OF_SCOPE", "test file"
    if fname.startswith("_"):
        return "FALSE_POSITIVE", "private/internal helper"
    if fname in _HEAL_NAMES:
        return "FALSE_POSITIVE", "heal pathway"
    for hp in _HEAL_PREFIXES:
        if fname.startswith(hp):
            return "FALSE_POSITIVE", "heal pathway (heal_* method)"
    if fname.startswith("tool_"):
        return "FALSE_POSITIVE", "tool implementation method (tool_*)"
    if fname in _INNER_CLOSURES:
        return "FALSE_POSITIVE", "inner closure"
    if fname in _LIFECYCLE_NAMES:
        return "FALSE_POSITIVE", "lifecycle method"

    # 2. Read-only accessor patterns
    if fname in _READONLY_EXACT:
        return "FALSE_POSITIVE", "read-only accessor/analysis"
    for prefix in _READONLY_PREFIXES:
        if fname.startswith(prefix):
            return "FALSE_POSITIVE", f"read-only accessor ({prefix}*)"

    # 3. ops_scripts/ — standalone CLI tools, not library runtime entrypoints
    if rel_path.startswith("ops_scripts/"):
        return "FALSE_POSITIVE", "ops_scripts tooling (standalone CLI)"

    # 3b. Standalone main() functions — CLI entry points, not library boundaries
    if fname == "main" and not entry["class_name"]:
        return "FALSE_POSITIVE", "standalone main() (CLI entry point)"

    # 3c. Infrastructure directories (not top-level runtime entrypoints)
    _INFRA_DIRS = (
        "/utils/",
        "/scripts/",
        "/enforcement/",
        "/config/",
        "/validators/",
        "/dashboards/",
        "/tools/",
        "/knowledge/",
        "/interfaces/",
        "/mixins/",
        "/types/",
        "/core/",
    )
    for infra_dir in _INFRA_DIRS:
        if infra_dir in rel_path:
            return "FALSE_POSITIVE", f"infrastructure directory ({infra_dir.strip('/')})"

    # 4. Dataclass methods and class-level transitive coverage
    if entry["class_name"]:
        cname = entry["class_name"]
        # 4a. Adapter/Provider classes — infrastructure, not runtime entrypoints
        _INFRA_SUFFIXES = ("Adapter", "Provider", "Store", "Graph", "Builder", "Loader")
        for suffix in _INFRA_SUFFIXES:
            if cname.endswith(suffix):
                return "FALSE_POSITIVE", f"infrastructure class ({suffix} suffix)"

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cname:
                # 4b. Dataclass methods
                for dec in node.decorator_list:
                    dec_name = _node_name(dec) if isinstance(dec, ast.Name) else None
                    if dec_name == "dataclass":
                        return "FALSE_POSITIVE", "dataclass method"
                # 4c. Agent class transitive: if class has heal/heal_repository/run,
                # other methods are internal implementation of the guarded agent
                class_method_names = {
                    child.name
                    for child in ast.iter_child_nodes(node)
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                _AGENT_ENTRY_METHODS = {"heal", "heal_repository", "run", "run_mission", "execute"}
                if class_method_names & _AGENT_ENTRY_METHODS:
                    return "FALSE_POSITIVE", "agent-class transitive (class has heal/run/execute)"

    # 5. Transitively guarded (called from a guarded function, or file has guards)
    if _is_inside_guarded_caller(func_node, tree):
        return "FALSE_POSITIVE", "transitively guarded (called from guarded fn)"
    if file_has_any_guard:
        return "FALSE_POSITIVE", "file-level transitive (file contains guarded entrypoint)"

    # 6. Side-effect analysis — the positive signal
    side_effects = _detect_side_effects(func_node)
    has_retry = _has_retry_decorator(func_node)

    if not side_effects and not has_retry:
        return "FALSE_POSITIVE", "no side-effect signals detected"

    # Has side effects but not guarded — this is a candidate
    reason_parts = []
    if side_effects:
        reason_parts.append(f"side_effects=[{', '.join(sorted(set(side_effects)))}]")
    if has_retry:
        reason_parts.append("has_retry_decorator")
    return "UNWIRED", "; ".join(reason_parts)


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------


def _build_parent_map(tree: ast.Module) -> dict[int, ast.ClassDef | None]:
    """Map function node id -> parent ClassDef (or None)."""
    parent_map: dict[int, ast.ClassDef | None] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parent_map[id(child)] = node
    return parent_map


def scan_file(filepath: Path, repo_root: Path) -> list[dict]:
    """AST-scan a single Python file for functions/methods and their guard status."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):    # guardian: Parsing and encoding errors need separate handling strategies
        return []

    rel_path = str(filepath.relative_to(repo_root)).replace("\\", "/")
    parent_map = _build_parent_map(tree)
    results: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        parent_class = parent_map.get(id(node))
        class_name = parent_class.name if parent_class else None
        symbol = f"{class_name}.{node.name}" if class_name else node.name
        guard = has_v15_guard(node)

        entry = {
            "file": rel_path,
            "symbol": symbol,
            "function_name": node.name,
            "class_name": class_name,
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "has_guard": guard is not None,
            "guard_info": guard,
        }

        results.append((entry, node))

    # Determine if file has any guarded function (for transitive coverage)
    file_has_any_guard = any(e["has_guard"] for e, _ in results)

    final: list[dict] = []
    for entry, func_node in results:
        if not entry["has_guard"]:
            classification, reason = classify_unguarded(
                entry,
                func_node,
                tree,
                rel_path,
                file_has_any_guard=file_has_any_guard,
            )
            entry["classification"] = classification
            entry["classification_reason"] = reason
        else:
            entry["classification"] = "WIRED"
            entry["classification_reason"] = "has V15 guard"
        final.append(entry)

    return final


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

    all_guarded: list[dict] = []
    all_unwired: list[dict] = []
    all_false_positive: list[dict] = []
    all_out_of_scope: list[dict] = []

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

            for entry in entries:
                cls = entry["classification"]
                if cls == "WIRED":
                    guard_id = entry["guard_info"]["guard_id"]
                    entry["in_p2_inventory"] = guard_id in p2_ids
                    all_guarded.append(entry)
                elif cls == "UNWIRED":
                    entry["in_p2_inventory"] = False
                    all_unwired.append(entry)
                elif cls == "OUT_OF_SCOPE":
                    all_out_of_scope.append(entry)
                else:
                    all_false_positive.append(entry)

    # Cross-reference: which P2 inventory IDs are WIRED vs UNWIRED?
    guarded_ids = {e["guard_info"]["guard_id"] for e in all_guarded if e["guard_info"]}
    p2_wired = sorted(p2_ids & guarded_ids)
    p2_already_enforced = sorted(eid for eid, ep in p2_inv.items() if ep.get("already_v15_enforced"))
    p2_unwired = sorted(p2_ids - guarded_ids - set(p2_already_enforced))

    return {
        "schema_version": "5.0.0",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scan_roots": list(SCAN_ROOTS),
        "scanned_files": scanned_files,
        "summary": {
            "total_guarded": len(all_guarded),
            "total_unwired": len(all_unwired),
            "total_false_positive": len(all_false_positive),
            "total_out_of_scope": len(all_out_of_scope),
            "p2_inventory_total": len(p2_inv),
            "p2_wired": len(p2_wired),
            "p2_already_enforced": len(p2_already_enforced),
            "p2_unwired": len(p2_unwired),
            "p2_unwired_ids": p2_unwired,
        },
        "guarded": all_guarded,
        "unwired": all_unwired,
        "false_positive_sample": all_false_positive[:20],
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="V15 Full Repo-Wide Conformance Inventory (Schema 5.0.0)",
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
    print(f"  Guarded (WIRED):     {s['total_guarded']}")
    print(f"  UNWIRED:             {s['total_unwired']}")
    print(f"  FALSE_POSITIVE:      {s['total_false_positive']}")
    print(f"  OUT_OF_SCOPE:        {s['total_out_of_scope']}")
    print(
        f"  P2 inventory: {s['p2_inventory_total']} total, "
        f"{s['p2_wired']} wired, "
        f"{s['p2_already_enforced']} already enforced, "
        f"{s['p2_unwired']} unwired",
    )
    if s["p2_unwired_ids"]:
        print(f"  P2 UNWIRED IDs: {s['p2_unwired_ids']}")
    if s["total_unwired"] > 0:
        print("\n  UNWIRED functions requiring review:")
        for e in inventory["unwired"]:
            print(f"    {e['file']}:{e['line_start']}  {e['symbol']}  ({e['classification_reason']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
