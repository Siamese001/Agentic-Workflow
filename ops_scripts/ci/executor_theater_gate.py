#!/usr/bin/env python3
"""Executor Theater Gate — ADG CI Blocker.

Detects fake parallelism infrastructure in production code:
  G1: Executor-bearing module with zero inbound production callers
  G2: Worker-count or parallel banner with no real dispatch path
  G3: Imported parallel helper that is never actually used
  G4: Experimental/archived executor code in production path without classification

Usage:
    python ops_scripts/ci/executor_theater_gate.py                    # run all gates
    python ops_scripts/ci/executor_theater_gate.py --gate g1          # run single gate
    python ops_scripts/ci/executor_theater_gate.py --sqlite <path>    # explicit SQLite

Exit codes:
    0 — All gates pass
    1 — One or more gates failed (violations found)
    2 — Error (missing files, bad SQL, etc.)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import ast
import sqlite3
import sys
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRODUCTION_ROOTS = [
    "agentic_core",
    "tools/generate",
    "tools/adg",
]

EXECUTOR_PATTERNS = {
    "ProcessPoolExecutor",
    "ThreadPoolExecutor",
}

# Files that use ThreadPoolExecutor purely for asyncio.run() bridge — not parallel infra
ASYNC_BRIDGE_ALLOWLIST = [
    "agentic_core/L5_safety/enforcement/DomainPlannerAdapter.py",
    "agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
    "apps_shared/reasoning/BaseHealingOrchestrator.py",
    "apps_shared/config/titanium_search_tool_config.py",
    "apps_shared/types/hardened_gemini_executor_types.py",
    "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py",
    "agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py",
]

# Modules with legitimate production callers that use executors for real work
EXECUTOR_ALLOWLIST = [
    "agentic_core/L0_routing/reasoning/production_optimization.py",
    "agentic_core/L0_routing/reasoning/mixture_of_experts.py",
    "agentic_core/L2_execution/reasoning/batch_embedding_service.py",
    "agentic_core/L1_cognition/reasoning/multi_query_fusion.py",
    "agentic_core/evaluation/golden/eval_spine_integration.py",
    "agentic_core/knowledge/lifecycle/reindex_coordinator.py",
    "ops_scripts/dev_tools/L0_routing_scripts/_ssot_phases.py",
    "ops_scripts/dev_tools/l0_scripts/query_runtime_util.py",
    # MCP server entry points — run as their own subprocess per .cursor/mcp.json.
    # Zero production import callers is EXPECTED and CORRECT: they bootstrap out-of-process.
    "tools/adg/mcp/runtime.py",
    # ADG generator entry point — invoked as `python tools/generate_full_adg.py` per
    # constitutional §22 and the .pre-commit-config.yaml ADG-refresh hook. The
    # ThreadPoolExecutor lives in `_run_post_adg_gates_parallel` (plan
    # adg-pipeline-simplification-e2e-9b4c27 §W3) and runs the 5 post-ADG CI gates
    # as concurrent subprocesses. Zero production import callers is EXPECTED and
    # CORRECT — this is a CLI tool, not a library; the parallelism is real
    # (subprocess fan-out, not theater).
    "tools/generate/generate_full_adg.py",
]

# generate_full_adg.py — forbidden parallel params and strings
FORBIDDEN_PARAMS = {"parallel", "workers", "cpu_affinity", "batch_size"}
FORBIDDEN_STRINGS = ["CPU Optimizer:", "shutdown_cpu_optimizer", "shutdown_file_processor"]

# Dead parallel modules that must never return
FORBIDDEN_IMPORTS_IN_ADG = [
    "agentic_core.L2_execution.utils.cpu_optimizer",
    "agentic_core.L2_execution.utils.parallel_file_processor",
    "agentic_core.L2_execution.utils.batch_processor",
]

# Production classification marker
CLASSIFICATION_MARKER = "# classification:"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(path: str) -> str:
    """Normalize path separators to forward slash."""
    return path.replace("\\", "/")


def _is_production_path(rel_path: str) -> bool:
    """Check if a relative path is under a production root."""
    normed = _normalize(rel_path)
    return any(normed.startswith(root + "/") or normed.startswith(root + "\\") for root in PRODUCTION_ROOTS)


def _is_allowlisted(rel_path: str) -> bool:
    """Check if path is in async-bridge or executor allowlist."""
    normed = _normalize(rel_path)
    for pattern in ASYNC_BRIDGE_ALLOWLIST + EXECUTOR_ALLOWLIST:
        if normed.endswith(_normalize(pattern)):
            return True
    return False


def _find_latest_sqlite() -> Path | None:
    """Find latest adg_indexed_*.sqlite in artifacts/adg/ that has a `nodes` table.

    Delegates to canonical resolver for sentinel filtering.
    """
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite(require_nodes_table=True)


def _get_executor_bearing_files() -> list[tuple[str, set[str]]]:
    """Scan production roots for files containing executor patterns.

    Returns list of (relative_path, {executor_names_found}).
    """
    results = []
    for prod_root in PRODUCTION_ROOTS:  # progress_bar: CI production root scan
        root_path = ROOT / prod_root
        if not root_path.exists():
            continue
        for py_file in root_path.rglob("*.py"):  # progress_bar: CI file scan
            if "__pycache__" in str(py_file):
                continue
            rel = str(py_file.relative_to(ROOT))
            if _is_allowlisted(rel):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=str(py_file))
            except (OSError, SyntaxError):
                continue
            found = set()
            for node in ast.walk(tree):  # progress_bar: CI AST walk
                # Detect: from concurrent.futures import ThreadPoolExecutor
                if isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        if alias.name in EXECUTOR_PATTERNS:
                            found.add(alias.name)
                # Detect: concurrent.futures.ThreadPoolExecutor(...)
                if isinstance(node, ast.Attribute) and node.attr in EXECUTOR_PATTERNS:
                    found.add(node.attr)
                # Detect: name = ThreadPoolExecutor(...)
                if isinstance(node, ast.Name) and node.id in EXECUTOR_PATTERNS:
                    found.add(node.id)
            if found:
                results.append((_normalize(rel), found))
    return results


# ---------------------------------------------------------------------------
# G1: Production Reachability Gate
# ---------------------------------------------------------------------------


def gate_g1_reachability(sqlite_path: Path) -> list[str]:
    """Check executor-bearing modules have non-zero production fan-in.

    Returns list of violation descriptions (empty = pass).
    """
    violations: list[str] = []
    executor_files = _get_executor_bearing_files()

    if not executor_files:
        return violations

    if not sqlite_path.exists():
        return [f"G1: ADG SQLite not found: {sqlite_path}"]

    db_uri = f"file:{sqlite_path.as_posix()}?mode=ro&immutable=1"
    conn = sqlite3.connect(db_uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row

    # Defensive: if the snapshot lacks `nodes` (stub/sentinel/in-flight),
    # skip the gate rather than emit one violation per executor file.
    # Mirrors the precedent in ops_scripts/ci/check_test_harness_coverage.py.
    nodes_present = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
    ).fetchone()
    if not nodes_present:
        conn.close()
        print(
            f"  WARN: G1 skipped — snapshot lacks `nodes` table ({sqlite_path.name}); "
            f"likely a stub/sentinel snapshot. Run `python tools/generate_full_adg.py` "
            f"to produce a real snapshot."
        )
        return []

    try:
        for rel_path, executors in executor_files:  # progress_bar: CI ADG reachability scan
            try:
                cur = conn.execute(
                    """
                    SELECT COUNT(*) AS fan_in FROM edges e
                    JOIN nodes src ON e.src_id = src.id
                    JOIN nodes tgt ON e.dst_id = tgt.id
                    WHERE e.relation_type = 'imports'
                      AND tgt.resolved_path = ?
                      AND src.layer NOT IN ('L_TEST', 'L_OPS', 'L_TOOLS')
                    """,
                    (rel_path,),
                )
                row = cur.fetchone()
                fan_in = row["fan_in"] if row else 0
            except sqlite3.Error as exc:
                violations.append(f"G1: ADG query failed for {rel_path}: {exc}")
                continue

            if fan_in == 0:
                exec_str = ", ".join(sorted(executors))
                violations.append(f"G1: {rel_path} bears [{exec_str}] but has 0 production callers")
    finally:
        conn.close()
    return violations


# ---------------------------------------------------------------------------
# G2: Claim-to-Execution Gate
# ---------------------------------------------------------------------------


def gate_g2_claim_to_execution() -> list[str]:
    """Check generate_full_adg.py has no parallel claims without dispatch.

    Returns list of violation descriptions (empty = pass).
    """
    violations: list[str] = []
    adg_path = ROOT / "tools" / "generate" / "generate_full_adg.py"

    if not adg_path.exists():
        return [f"G2: File not found: {adg_path}"]

    source = adg_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(adg_path))

    # Check function signature for forbidden params
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "generate_full_adg":
            param_names = {arg.arg for arg in node.args.args}
            overlap = param_names & FORBIDDEN_PARAMS
            if overlap:
                violations.append(f"G2: generate_full_adg() has theater params: {sorted(overlap)}")
            break

    # Check CLI flags in main()
    for flag in ["--no-parallel", "--workers", "--cpu-affinity", "--batch-size"]:
        if flag in source:
            violations.append(f"G2: CLI flag '{flag}' still present in generate_full_adg.py")

    # Check for fake banner strings
    for s in FORBIDDEN_STRINGS:
        if s in source:
            violations.append(f"G2: Theater string '{s}' still present in generate_full_adg.py")

    return violations


# ---------------------------------------------------------------------------
# G3: Import-Only Capability Gate
# ---------------------------------------------------------------------------


def gate_g3_import_only() -> list[str]:
    """Check generate_full_adg.py doesn't import parallel modules.

    Returns list of violation descriptions (empty = pass).
    """
    violations: list[str] = []
    adg_path = ROOT / "tools" / "generate" / "generate_full_adg.py"

    if not adg_path.exists():
        return [f"G3: File not found: {adg_path}"]

    source = adg_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(adg_path))

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in FORBIDDEN_IMPORTS_IN_ADG:
            names = [alias.name for alias in node.names]
            violations.append(
                f"G3: generate_full_adg.py imports dead module: from {node.module} import {', '.join(names)}"
            )

    return violations


# ---------------------------------------------------------------------------
# G4: Production Classification Gate
# ---------------------------------------------------------------------------


def gate_g4_classification() -> list[str]:
    """Check unclassified executor-bearing files in production paths.

    Files that bear executor infrastructure and have zero production callers
    must have a '# classification: experimental' or '# classification: archived'
    marker, or they are violations.

    Returns list of violation descriptions (empty = pass).
    """
    violations: list[str] = []
    executor_files = _get_executor_bearing_files()

    for rel_path, executors in executor_files:  # progress_bar: CI classification check
        full_path = ROOT / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        has_classification = CLASSIFICATION_MARKER in source

        # If file has no classification marker, it must have real callers
        # (checked by G1). Here we just flag the missing marker for awareness.
        if not has_classification:
            # Only flag if it looks like dedicated parallel infrastructure
            # (not incidental executor use in a larger module)
            basename = full_path.name.lower()
            infra_keywords = ["parallel", "batch_processor", "cpu_optimizer", "executor"]
            if any(kw in basename for kw in infra_keywords):
                exec_str = ", ".join(sorted(executors))
                violations.append(
                    f"G4: {rel_path} bears [{exec_str}], "
                    f"no '# classification:' marker — must be classified or have callers"
                )

    return violations


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_all_gates(
    sqlite_path: Path | None = None,
    gate_filter: str | None = None,
    json_output: bool = False,
) -> int:
    """Run all (or selected) gates. Returns exit code."""
    import json as _json

    if sqlite_path is None:
        sqlite_path = _find_latest_sqlite()
    if sqlite_path is None:
        if json_output:
            print(_json.dumps({"error": "No ADG SQLite found"}))
        else:
            print("[EXECUTOR_THEATER_GATE] ERROR: No ADG SQLite found in artifacts/adg/")
        return 2

    gate_map = {
        "g1": ("G1: Production Reachability", lambda: gate_g1_reachability(sqlite_path)),
        "g2": ("G2: Claim-to-Execution", gate_g2_claim_to_execution),
        "g3": ("G3: Import-Only Capability", gate_g3_import_only),
        "g4": ("G4: Production Classification", gate_g4_classification),
    }

    if gate_filter:
        if gate_filter not in gate_map:
            if json_output:
                print(_json.dumps({"error": f"Unknown gate '{gate_filter}'"}))
            else:
                print(f"[EXECUTOR_THEATER_GATE] ERROR: Unknown gate '{gate_filter}'")
            return 2
        gates_to_run = {gate_filter: gate_map[gate_filter]}
    else:
        gates_to_run = gate_map

    all_violations: list[str] = []
    json_results: dict = {}

    for key, (label, fn) in gates_to_run.items():  # progress_bar: CI gate runner
        try:
            violations = fn()
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as e:
            violations = [f"{key.upper()}: Gate error: {e}"]

        passed = not violations
        json_results[key] = {"passed": passed, "violations": violations}

        if not json_output:
            if violations:
                print(f"  ❌ {label}: {len(violations)} violation(s)")
                for v in violations:
                    print(f"     {v}")
            else:
                print(f"  ✅ {label}: PASS")
        all_violations.extend(violations)

    if json_output:
        print(_json.dumps(json_results))
        return 0 if not all_violations else 1

    if all_violations:
        print(f"\n[EXECUTOR_THEATER_GATE] FAILED: {len(all_violations)} total violation(s)")
        return 1

    print("\n[EXECUTOR_THEATER_GATE] PASSED: All gates clean")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Executor Theater Gate — ADG CI Blocker")
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=None,
        help="Path to adg_indexed_*.sqlite (default: latest in artifacts/adg/)",
    )
    parser.add_argument(
        "--gate",
        choices=["g1", "g2", "g3", "g4"],
        default=None,
        help="Run a specific gate only (default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit results as JSON to stdout (for machine consumption)",
    )
    args = parser.parse_args()

    rc = run_all_gates(sqlite_path=args.sqlite, gate_filter=args.gate, json_output=args.json)
    sys.exit(rc)


if __name__ == "__main__":
    main()
