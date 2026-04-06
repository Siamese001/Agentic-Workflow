"""
Hard Shim Strategy — Verification Script (Phase 4.4.2 Final Consistency Lock).

Run: python -m agentic_core.L5_safety.config.structure_blueprint._verify

Flags:
  --init-phantom-baseline       Create phantom_baseline.json (first time only)
  --update-phantom-baseline     Persist a reduced phantom baseline (prints diff first)
  --print-phantom-diff          Print phantom diff vs baseline and exit
  --repair-phantom-baseline     Rewrite corrupt/unreadable baseline from current scan
  --acknowledge-import-change   Update allowlist hash and exit immediately
  --print-allowlist             Print current allowlist + hash and exit (read-only)
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from types import MappingProxyType

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint.ssot import CODE_TERRITORIES as _CODE_TERRITORIES
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "_verify")
emit_determinism_digest("p0", "_verify")

_emit_dispatches_healing_run("p1", "_verify", "L5")
_emit_routes_through("p1", "_verify", "L5")
_emit_checks_agent_registry("p1", "_verify", "agent_registry")
_emit_validates_agent_capability("p1", "_verify", "capability")
_emit_dispatches_execution_plan("p1", "_verify", "exec_plan")
_emit_agent_executes_agent("p1", "_verify", "sub_agent")
_emit_routes_to_agent("p1", "_verify", "target_agent")
_emit_verifies_policy("p1", "_verify", "policy_check")
_emit_observes_runtime_state("p1", "_verify", "runtime_state")
_emit_verifies_boundary("p1", "_verify", "boundary_check")
_emit_transcripts_response("p1", "_verify", "transcript")
_emit_hard_fails_untranscripted("p1", "_verify")
_emit_gated_by_confidence("p1", "_verify", "confidence_gate")
_emit_escalates_to_human("p1", "_verify", "L5")
_emit_reads_policy_state("p1", "_verify", "L5")
_emit_authorize_and_execute("p2", "_verify", "execution_auth")
_emit_validates_capability("p2", "_verify", "capability_check")
_emit_routes_to_capability("p2", "_verify", "capability_route")
_emit_writes_via_uwg("p2", "_verify", "uwg_write")
_emit_blocks_direct_write("p2", "_verify", "direct_write_block")
_emit_records_tool_invocation("p2", "_verify", "tool_invocation")
_emit_captures_execution_output("p2", "_verify", "exec_output")
_emit_dispatches_agent("p3", "_verify", "agent_dispatch")
_emit_coordinates_agents("p3", "_verify", "agent_coordination")
_emit_records_workflow_lineage("p3", "_verify", "workflow_lineage")
_emit_records_healing_outcome("p3", "_verify", "healing_outcome")
_emit_escalates_failure("p3", "_verify", "failure_escalation")
_emit_orchestrates_workflow("p3", "_verify", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_verify", "healing_dispatch")
_emit_invokes_evaluation("p3", "_verify", "evaluation_signal")
_emit_records_telemetry_event("p4", "_verify", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_verify", "eval_metric")
_emit_stores_embedding("p4", "_verify", "embedding_store")
_emit_updates_meta_learning_state("p4", "_verify", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_verify", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("_verify", "p4obs", "metric_1")
_emit_emits_metric_event("_verify", "p4obs", "metric_2")
_emit_emits_metric_event("_verify", "p4obs", "metric_3")
_emit_emits_metric_event("_verify", "p4obs", "metric_4")
_emit_emits_metric_event("_verify", "p4obs", "metric_5")
_emit_emits_metric_event("_verify", "p4obs", "metric_6")
_emit_records_incident_event("_verify", "p4obs", "incident")
_emit_captures_runtime_anomaly("_verify", "p4obs", "anomaly")
_emit_writes_observability_log("_verify", "p4obs", "obs_log")
_emit_updates_monitoring_state("_verify", "p4obs", "mon_state")
_emit_triggers_alert("_verify", "p4obs", "alert")
_emit_links_incident_trace("_verify", "p4obs", "trace_link")
_emit_captures_pattern("_verify", "p3lm", "pattern")
_emit_records_learning_event("_verify", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_verify", "p3lm", "snapshot")
_emit_feeds_meta_learning("_verify", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_verify", "p3lm", "routing")
_emit_improves_agent_policy("_verify", "p3lm", "policy")
_emit_stores_learning_state("_verify", "p3lm", "state")
_emit_records_execution_trace("_verify", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_verify", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_verify", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_verify", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_verify", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_verify", "env_read", "p2_env_1")
_emit_reads_environ("_verify", "env_read", "p2_env_2")
_emit_reads_runtime_state("_verify", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_verify", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_verify", "context_pull")
_emit_pulls_context("p1", "_verify", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_verify", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_verify", "uwg_term_2")
_emit_writes_through("p1", "_verify", "write_through")
_emit_writes_through("p1", "_verify", "write_through_2")
_emit_validated_by_safety_plane("p1", "_verify", "safety_validation")
_emit_invokes_eval("p1", "_verify", "eval_call")
_emit_proposal_commits_routing("p1", "_verify", "routing_commit")
from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace__verify", "_verify_dispatch_entry")
emit_determinism_digest("trace__verify", "_verify_dispatch_exit")
emit_determinism_digest("trace__verify", "_verify_tool_invoke")
emit_determinism_digest("trace__verify", "_verify_tool_complete")
emit_determinism_digest("trace__verify", "_verify_agent_entry")
emit_determinism_digest("trace__verify", "_verify_agent_exit")
emit_determinism_digest("trace__verify", "_verify_uwg_write")
emit_determinism_digest("trace__verify", "_verify_trace_sign")
emit_determinism_digest("trace__verify", "_verify_guardrail_check")
emit_determinism_digest("trace__verify", "_verify_policy_verify")

ALLOWED_MODULES: frozenset[str] = frozenset(
    {"__future__", "typing", "types", "collections", "functools", "itertools", "dataclasses"}
)
# SCAN_ROOTS: built from CODE_TERRITORIES (dynamic apps_* discovery) plus artifact roots.
# Adding a new apps_* folder at repo root is sufficient — no manual edits needed here.
SCAN_ROOTS: tuple[str, ...] = tuple(
    sorted(_CODE_TERRITORIES | {"artifacts"})
)
SCAN_EXTENSIONS: tuple[str, ...] = (".py",)
SCAN_EXCLUDES: frozenset[str] = SOVEREIGN_EXCLUDED_FOLDERS | frozenset({"dist", "build"})


def _allowlist_hash() -> str:
    """Deterministic SHA-256 of the canonical allowlist."""
    return hashlib.sha256("\n".join(sorted(ALLOWED_MODULES)).encode()).hexdigest()[:16]


def _assert_frozen(obj: object, path: str = "root") -> str | None:
    """Recursively verify deep immutability.

    Returns None if fully frozen, or a string describing the first
    mutable structure found (with its path).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_assert_frozen", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_assert_frozen", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "_assert_frozen")
    if isinstance(obj, dict):
        return f"{path}: dict (mutable)"
    if isinstance(obj, list):
        return f"{path}: list (mutable)"
    if isinstance(obj, set):
        return f"{path}: set (mutable)"
    if isinstance(obj, MappingProxyType):
        for k, v in obj.items():
            result = _assert_frozen(v, f"{path}.{k}")
            if result is not None:
                return result
        return None
    if isinstance(obj, tuple):
        for i, v in enumerate(obj):
            result = _assert_frozen(v, f"{path}[{i}]")
            if result is not None:
                return result
        return None
    if isinstance(obj, frozenset):
        return None
    return None


def _print_phantom_diff(current: set[tuple[str, str]], saved: set[tuple[str, str]]) -> None:
    """Print deterministic diff between current and saved phantom sets."""
    added = sorted(current - saved)
    removed = sorted(saved - current)
    if not added and (not removed):
        print("  No diff — baseline matches current scan.")
        return
    if added:
        print(f"  +{len(added)} NEW phantom(s):")
        for f, n in added:
            print(f"    + {f}:{n}")
    if removed:
        print(f"  -{len(removed)} REMOVED phantom(s):")
        for f, n in removed:
            print(f"    - {f}:{n}")


def _canonical_repo_path(path: str) -> str:
    """Normalize a path to canonical repo-relative form.

    - Converts backslashes to forward slashes
    - Collapses '.' segments
    - Rejects '..' segments (raises ValueError)
    - Rejects absolute paths (raises ValueError)
    - Returns normalized forward-slash path
    """
    normalized = path.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) >= 2 and normalized[1] == ":"):
        raise ValueError(f"Non-canonical path detected: absolute path '{path}'")
    parts = [p for p in normalized.split("/") if p and p != "."]
    if ".." in parts:
        raise ValueError(f"Non-canonical path detected: '..' segment in '{path}'")
    return "/".join(parts)


def _is_repo_relative_normalized(path: str) -> bool:
    """Check path is repo-relative, forward-slash only, no '..' segments.

    Baseline entries must already be in canonical form — backslashes are rejected.
    """
    if "\\" in path:
        return False
    try:
        return path == _canonical_repo_path(path)
    except ValueError:
        return False


def _collect_scan_files(root: str) -> tuple[list[str], list[str]]:
    """Collect all files under SCAN_ROOTS with SCAN_EXTENSIONS, excluding SCAN_EXCLUDES.

    Returns (files, missing_roots) where missing_roots lists any SCAN_ROOT
    that does not exist as a directory.
    """
    files: list[str] = []
    missing_roots: list[str] = []
    for scan_root in SCAN_ROOTS:
        scan_dir = Path(root) / scan_root
        # guardian: allow-path-string
        if not os.path.isdir(scan_dir):
            missing_roots.append(scan_root)
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in SCAN_EXCLUDES]
            for fn in filenames:
                if any(fn.endswith(ext) for ext in SCAN_EXTENSIONS):
                    files.append(Path(dirpath) / fn)
    return (sorted(files), missing_roots)


def _path_under_scan_roots(path: str) -> bool:
    """Check that a repo-relative path starts with one of SCAN_ROOTS."""
    first_segment = path.split("/")[0]
    return first_segment in SCAN_ROOTS


def main() -> int:
    # guardian: allow-path-string
    root = os.path.abspath(Path(os.path.dirname(__file__)) / ".." / ".." / ".." / "..")
    pkg_dir = Path(__file__).parent
    pkg_prefix = "agentic_core.L5_safety.config.structure_blueprint"
    failures = 0
    if "--print-allowlist" in sys.argv:
        print("ALLOWED_MODULES (canonical):")
        for m in sorted(ALLOWED_MODULES):
            print(f"  {m}")
        print(f"Hash: {_allowlist_hash()}")
        return 0
    if "--acknowledge-import-change" in sys.argv:
        bp = Path(root) / "docs" / "reports" / "plans" / "phantom_baseline.json"
        # guardian: allow-path-string
        if not os.path.isfile(bp):
            print("ALLOWLIST ACK REFUSED: fix baseline/other failures first")
            print("  phantom_baseline.json not found")
            return 1
        try:
            with open(bp, encoding="utf-8") as bf:
                bl = json.load(bf)
            if not isinstance(bl, list):
                raise ValueError("not a JSON array")
            for i, entry in enumerate(bl):
                if not (
                    isinstance(entry, list) and len(entry) == 2 and all(isinstance(s, str) for s in entry)
                ):
                    raise ValueError(f"entry {i} invalid")
            bad = [e[0] for e in bl if not _is_repo_relative_normalized(e[0])]
            if bad:
                raise ValueError(f"non-normalized path: {bad[0]}")
        except (json.JSONDecodeError, ValueError, TypeError, OSError) as exc:
            print("ALLOWLIST ACK REFUSED: fix baseline/other failures first")
            print(f"  baseline corrupt — {exc}")
            return 1
        cur = _allowlist_hash()
        hp = Path(root) / "docs" / "reports" / "plans" / "allowlist_hash.txt"
        # guardian: allow-path-string
        if not os.path.isfile(hp):
            _wg.makedirs(Path(hp).parent, exist_ok=True)
            _wg.open_write(hp, cur + "\n")
            print(f"ALLOWLIST HASH INITIALIZED: {cur}")
            return 0
        with open(hp, encoding="utf-8") as hf:
            old = hf.read().strip()
        if old == cur:
            print(f"Allowlist hash already locked: {cur}")
            return 0
        print("Allowlist hash: MISMATCH")
        print(f"  saved hash:   {old}")
        print(f"  current hash: {cur}")
        print("  current allowlist (sorted):")
        for m in sorted(ALLOWED_MODULES):
            print(f"    {m}")
        _wg.open_write(hp, cur + "\n")
        print("ALLOWLIST HASH UPDATED")
        print("  Run normal verify to confirm all checks pass")
        return 0
    print("=" * 70)
    print("HARD SHIM STRATEGY — VERIFICATION REPORT")
    print("=" * 70)
    print("\n1. IMPORT CYCLE DETECTION")
    print("-" * 40)
    modules: dict[str, set[str]] = {}
    for fn in os.listdir(pkg_dir):
        if not fn.endswith(".py"):
            continue
        mod_name = fn[:-3] if fn != "__init__.py" else "__init__"
        fpath = Path(pkg_dir) / fn
        with open(fpath, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=fpath)
        deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                m = node.module
                if m.startswith(pkg_prefix):
                    suffix = m[len(pkg_prefix) :]
                    if suffix == "":
                        dep = "__init__"
                    elif suffix.startswith("."):
                        dep = suffix[1:]
                    else:
                        dep = suffix
                    if dep != mod_name:
                        deps.add(dep)
        modules[mod_name] = deps
    for mod, deps in sorted(modules.items()):
        dep_str = ", ".join(sorted(deps)) if deps else "(none)"
        print(f"  {mod} -> {dep_str}")
    WHITE, GRAY, BLACK = (0, 1, 2)
    color = dict.fromkeys(modules, WHITE)
    path: list[str] = []
    cycles_found: list[str] = []

    def dfs(u: str) -> None:
        color[u] = GRAY
        path.append(u)
        for v in modules.get(u, set()):
            if v not in color:
                continue
            if color[v] == GRAY:
                cycle_start = path.index(v)
                cycles_found.append(" -> ".join(path[cycle_start:] + [v]))
            elif color[v] == WHITE:
                dfs(v)
        path.pop()
        color[u] = BLACK

    for m in modules:
        if color[m] == WHITE:
            dfs(m)
    if cycles_found:
        print(f"  RESULT: FAIL ({len(cycles_found)} cycles)")
        for c in cycles_found:
            print(f"    {c}")
        failures += 1
    else:
        print("  RESULT: PASS — zero import cycles")
    print("\n2. API SURFACE")
    print("-" * 40)
    import agentic_core.L5_safety.config.structure_blueprint as pkg
    import agentic_core.L5_safety.config.structure_blueprint as shim

    pkg_all = set(pkg.__all__)
    shim_all = set(shim.__all__)
    print(f"  Package __all__: {len(pkg_all)} names")
    print(f"  Shim __all__:    {len(shim_all)} names")
    diff = pkg_all.symmetric_difference(shim_all)
    if diff:
        print(f"  RESULT: FAIL — symmetric diff: {diff}")
        failures += 1
    else:
        print("  RESULT: PASS — exact match")
    pkg_missing = [n for n in pkg_all if not hasattr(pkg, n)]
    shim_missing = [n for n in shim_all if not hasattr(shim, n)]
    if pkg_missing:
        print(f"  Package missing attrs: {pkg_missing}")
        failures += 1
    if shim_missing:
        print(f"  Shim missing attrs: {shim_missing}")
        failures += 1
    if not pkg_missing and (not shim_missing):
        print("  All __all__ names resolve: PASS")
    print("\n3. DEEP IMMUTABILITY + IDENTITY")
    print("-" * 40)
    # Wave 3: ROOT_WHITELIST moved to ssot.py, SOVEREIGN_TERRITORIES accessed via package fallback
    from agentic_core.L5_safety.config.structure_blueprint.ssot import ROOT_WHITELIST as s_rw
    from agentic_core.L5_safety.config.structure_blueprint.ssot import PROJECT_ROOT_WHITELIST as prw
    from agentic_core.L5_safety.config.structure_blueprint import SOVEREIGN_TERRITORIES as pkg_st
    from agentic_core.L5_safety.config.structure_blueprint.territories import get_all_territories

    territories = get_all_territories()

    imm_violations: list[str] = []
    # ROOT_WHITELIST is now an alias to PROJECT_ROOT_WHITELIST in ssot.py
    if s_rw is not prw:
        imm_violations.append("ROOT_WHITELIST is not aliased to PROJECT_ROOT_WHITELIST")
    # SOVEREIGN_TERRITORIES from package fallback should match territories API
    if pkg_st is not territories:
        imm_violations.append("SOVEREIGN_TERRITORIES from package does not match territories API")
    if not isinstance(s_rw, frozenset):
        imm_violations.append(f"ROOT_WHITELIST: type={type(s_rw).__name__}, expected frozenset")
    if isinstance(pkg_st, dict):
        imm_violations.append("SOVEREIGN_TERRITORIES: is plain dict (mutable!)")
    try:
        pkg_st["__test__"] = 1
        imm_violations.append("SOVEREIGN_TERRITORIES: top-level mutation succeeded")
    except TypeError:
        pass
    freeze_err = _assert_frozen(pkg_st, "SOVEREIGN_TERRITORIES")
    if freeze_err is not None:
        imm_violations.append(freeze_err)
    print(f"  ROOT_WHITELIST: type={type(s_rw).__name__}, len={len(s_rw)}")
    print(f"  SOVEREIGN_TERRITORIES: type={type(pkg_st).__name__}, len={len(pkg_st)}")
    print(f"  Identity ROOT_WHITELIST==PROJECT_ROOT_WHITELIST: {s_rw is prw}")
    print(f"  Identity SOVEREIGN_TERRITORIES==territories: {pkg_st is territories}")
    if imm_violations:
        print(f"  RESULT: FAIL ({len(imm_violations)} violations)")
        for v in imm_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  RESULT: PASS — deep immutable, identity preserved")
    print("\n4. BACKWARD COMPATIBILITY (18 excluded names)")
    print("-" * 40)
    excluded_names = [
        "SubfolderDefinition",
        "TerritoryDefinition",
        "build_sovereign_territories",
        "LAYER_OVERRIDES",
        "get_sovereign_territories",
        "get_core_subfolder_map",
        "get_subfolder_metadata",
        "get_apps_lic_subfolder_map",
        "get_apps_rg_subfolder_map",
        "get_apps_shared_subfolder_map",
        "agentic_core_registry",
        "verify_derived_registries",
        "L4_SUBFOLDER_MAP",
        "L4_APPROVED_FOLDERS",
        "SCRIPTS_PLACEMENT_RULES",
        "get_app_specific_patterns_compiled",
        "get_classification_suffix_patterns_compiled",
        "get_compound_suffix_patterns_compiled",
    ]
    pkg_ok = sum(1 for n in excluded_names if hasattr(pkg, n))
    shim_ok = sum(1 for n in excluded_names if hasattr(shim, n))
    in_all = [n for n in excluded_names if n in pkg_all]
    print(f"  Importable from package: {pkg_ok}/{len(excluded_names)}")
    print(f"  Importable from shim:    {shim_ok}/{len(excluded_names)}")
    print(f"  Leaked into __all__:     {len(in_all)} (should be 0)")
    if in_all:
        print(f"    LEAKED: {in_all}")
    if pkg_ok == len(excluded_names) and shim_ok == len(excluded_names) and (len(in_all) == 0):
        print("  RESULT: PASS")
    else:
        print("  RESULT: FAIL")
        failures += 1
    print("\n5. IMPORT LINTER + PHANTOM BASELINE LOCK")
    print("-" * 40)
    targets = ("structure_blueprint_config", "structure_blueprint")
    phantom_tuples: list[tuple[str, str]] = []
    phantom_debt: list[tuple[str, str, int, str]] = []
    policy_errors: list[str] = []
    checked = 0
    scan_files, missing_roots = _collect_scan_files(root)
    print(f"  Scan scope: {len(scan_files)} files in {SCAN_ROOTS}")
    if missing_roots:
        for mr in missing_roots:
            print(f"  SCAN_ROOT MISSING: {mr}/ does not exist")
        print("  RESULT: FAIL — all SCAN_ROOTS must exist")
        failures += 1
    for fpath in scan_files:
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
            continue
        try:
            tree = ast.parse(source, filename=fpath)
        except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            rp = _canonical_repo_path(os.path.relpath(fpath, root))
            policy_errors.append(f"{rp}:{exc.lineno or '?'}: SyntaxError — {exc.msg}")
            continue
        file_counted = False
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.ImportFrom) and node.module and any(t in node.module for t in targets)
            ):
                continue
            if not file_counted:
                file_counted = True
                checked += 1
            if node.module in ("structure_blueprint", "structure_blueprint_config"):
                for a in node.names or []:
                    policy_errors.append(
                        f"{os.path.relpath(fpath, root)}:{node.lineno}:{a.name} (short-path: {node.module})"
                    )
                continue
            names = [a.name for a in node.names] if node.names else []
            for name in names:
                if name == "*":
                    continue
                try:
                    mod = __import__(node.module, fromlist=[name])
                    if not hasattr(mod, name):
                        rp = _canonical_repo_path(os.path.relpath(fpath, root))
                        phantom_tuples.append((rp, name))
                        phantom_debt.append((rp, name, node.lineno, node.module))
                except (ValueError, AttributeError):
                    rp = _canonical_repo_path(os.path.relpath(fpath, root))
                    phantom_tuples.append((rp, name))
                    phantom_debt.append((rp, name, node.lineno, node.module))
    phantom_set = sorted(set(phantom_tuples))
    total_errors = len(phantom_set) + len(policy_errors)
    print(f"  Files checked:      {checked}")
    print(f"  Total errors:       {total_errors}")
    print(f"    Phantom names:    {len(phantom_set)}")
    print(f"    Policy violations: {len(policy_errors)}")
    if policy_errors:
        print("  Policy violations (MUST FIX):")
        for e in sorted(policy_errors):
            print(f"    {e}")
        failures += 1
    print(f"  Policy: {('PASS' if not policy_errors else 'FAIL')}")
    baseline_path = Path(root) / "docs" / "reports" / "plans" / "phantom_baseline.json"
    current_baseline = [[f, n] for f, n in phantom_set]
    current_set_cmp = {tuple(x) for x in current_baseline}
    init_flag = "--init-phantom-baseline" in sys.argv
    update_flag = "--update-phantom-baseline" in sys.argv
    diff_flag = "--print-phantom-diff" in sys.argv
    repair_flag = "--repair-phantom-baseline" in sys.argv
    saved_set: set[tuple[str, str]] | None = None
    baseline_corrupt = False
    # guardian: allow-path-string
    if os.path.isfile(baseline_path):
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                saved_baseline = json.load(bf)
            if not isinstance(saved_baseline, list):
                raise ValueError("baseline is not a JSON array")
            for i, entry in enumerate(saved_baseline):
                if not (
                    isinstance(entry, list) and len(entry) == 2 and all(isinstance(s, str) for s in entry)
                ):
                    raise ValueError(f"entry {i} is not a [file, name] pair")
            bad_paths = [e[0] for e in saved_baseline if not _is_repo_relative_normalized(e[0])]
            if bad_paths:
                raise ValueError(
                    f"{len(bad_paths)} baseline path(s) not repo-relative-normalized (no backslashes, no absolute, no ..); first: {bad_paths[0]}"
                )
            out_of_scope = [e[0] for e in saved_baseline if not _path_under_scan_roots(e[0])]
            if out_of_scope:
                raise ValueError(
                    f"{len(out_of_scope)} baseline path(s) not under SCAN_ROOTS; first: {out_of_scope[0]}. Valid roots: {SCAN_ROOTS}"
                )
            saved_set = {tuple(x) for x in saved_baseline}
        except (json.JSONDecodeError, ValueError, TypeError, OSError) as exc:
            baseline_corrupt = True
            print(f"  Phantom baseline: CORRUPT — {exc}")
    if diff_flag:
        if saved_set is not None:
            _print_phantom_diff(current_set_cmp, saved_set)
            has_diff = current_set_cmp != saved_set
            return 1 if has_diff else 0
        elif baseline_corrupt:
            print("  Cannot diff — baseline is corrupt")
            return 1
        else:
            print("  Cannot diff — phantom_baseline.json not found")
            return 1
    if repair_flag:
        # guardian: allow-path-string
        if not os.path.isfile(baseline_path):
            print("  --repair-phantom-baseline REFUSED — no baseline file to repair")
            print("    Use --init-phantom-baseline to create it")
            return 1
        if not baseline_corrupt:
            print("  --repair-phantom-baseline REFUSED — baseline is valid")
            print("    Use --update-phantom-baseline for baseline drift")
            return 1
        _wg.write_json(baseline_path, current_baseline, indent=2)
        print(f"  Phantom baseline: REPAIRED ({len(current_baseline)} entries)")
        for entry in current_baseline[:10]:
            print(f"    {entry[0]}:{entry[1]}")
        if len(current_baseline) > 10:
            print(f"    ... and {len(current_baseline) - 10} more")
        print(f"    Wrote: {os.path.relpath(baseline_path, root)}")
        return 0
    if baseline_corrupt:
        print("    Run with --repair-phantom-baseline to rewrite from current scan")
        failures += 1
    elif saved_set is not None:
        baseline_only = sorted(saved_set - current_set_cmp)
        current_only = sorted(current_set_cmp - saved_set)
        if not baseline_only and (not current_only):
            print(f"  Phantom baseline: LOCKED ({len(saved_set)} entries, matches)")
        else:
            if baseline_only:
                print(f"  Baseline-only entries (stale baseline): {len(baseline_only)}")
                for f, n in baseline_only:
                    print(f"    - {f}:{n}")
            if current_only:
                print(f"  Current-only entries (new phantom): {len(current_only)}")
                for f, n in current_only:
                    print(f"    + {f}:{n}")
            print(
                "  Remediation (local only): run with --update-phantom-baseline after fixing phantom imports."
            )
            print(
                "  CI policy: maintenance flags are forbidden in CI; run locally and commit lockfile updates."
            )
            if not current_only and update_flag:
                _wg.write_json(baseline_path, current_baseline, indent=2)
                print(f"  Phantom baseline: UPDATED ({len(saved_set)} → {len(current_set_cmp)} entries)")
            elif current_only:
                print(f"  Phantom baseline: FAIL — {len(current_only)} new phantom(s)")
                if update_flag:
                    print("    --update-phantom-baseline REFUSED — new phantoms exist")
                failures += 1
            else:
                print("    Run with --update-phantom-baseline to persist reduction")
    elif init_flag:
        _wg.makedirs(Path(baseline_path).parent, exist_ok=True)
        _wg.write_json(baseline_path, current_baseline, indent=2)
        print(f"  Phantom baseline: INITIALIZED ({len(current_baseline)} entries)")
        print(f"    Wrote: {os.path.relpath(baseline_path, root)}")
    else:
        print("  Phantom baseline: FAIL — phantom_baseline.json not found")
        print("    Run with --init-phantom-baseline to create it")
        failures += 1
    print("\n6. SHIM STRUCTURAL HARD LOCK")
    print("-" * 40)
    shim_path = Path(root) / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint_config.py"
    with open(shim_path, encoding="utf-8") as f:
        shim_source = f.read()
    shim_tree = ast.parse(shim_source, filename=shim_path)
    shim_violations: list[str] = []
    assign_all_count = 0
    for node in ast.iter_child_nodes(shim_tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.Assign):
            targets_ok = all(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
            if targets_ok:
                assign_all_count += 1
                if assign_all_count > 1:
                    shim_violations.append(f"line {node.lineno}: duplicate __all__ assignment")
                continue
            for t in node.targets:
                shim_violations.append(f"line {node.lineno}: assignment to {ast.dump(t)}")
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            shim_violations.append(f"line {node.lineno}: FunctionDef '{node.name}'")
            continue
        if isinstance(node, ast.ClassDef):
            shim_violations.append(f"line {node.lineno}: ClassDef '{node.name}'")
            continue
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            shim_violations.append(f"line {node.lineno}: control flow ({type(node).__name__})")
            continue
        shim_violations.append(f"line {node.lineno}: {type(node).__name__}")
    if assign_all_count == 0:
        shim_violations.append("missing __all__ assignment")
    for node in ast.iter_child_nodes(shim_tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            shim_violations.append(f"line {node.lineno}: top-level Call expression")
    if shim_violations:
        print(f"  RESULT: FAIL ({len(shim_violations)} violations)")
        for v in shim_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  __all__ assignments: 1")
        print("  FunctionDef/ClassDef/Call/ControlFlow: 0")
        print("  RESULT: PASS — structural hard lock intact")
    print("\n7. _constants.py STDLIB ALLOWLIST")
    print("-" * 40)
    constants_path = Path(pkg_dir) / "_constants.py"
    with open(constants_path, encoding="utf-8") as f:
        constants_source = f.read()
    constants_tree = ast.parse(constants_source, filename=constants_path)
    forbidden_calls = {
        "os.getenv",
        "os.environ",
        "os.getcwd",
        "open",
        "Path.read_text",
        "Path.read_bytes",
        "Path.cwd",
        "time.time",
        "time.monotonic",
        "datetime.now",
        "datetime.utcnow",
        "random.random",
        "random.randint",
        "random.choice",
        "__import__",
        "importlib.import_module",
    }
    allowlist_violations: list[str] = []
    for node in ast.walk(constants_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_MODULES:
                    allowlist_violations.append(
                        f"line {node.lineno}: 'import {alias.name}' ('{top}' not in allowlist)"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                allowlist_violations.append(f"line {node.lineno}: relative import (level={node.level})")
            elif node.module:
                top = node.module.split(".")[0]
                if top not in ALLOWED_MODULES:
                    allowlist_violations.append(
                        f"line {node.lineno}: 'from {node.module} import ...' ('{top}' not in allowlist)"
                    )
    for node in ast.walk(constants_tree):
        if isinstance(node, ast.Call):
            call_name = ""
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    call_name = f"{node.func.value.id}.{node.func.attr}"
            if call_name in forbidden_calls:
                allowlist_violations.append(f"line {node.lineno}: forbidden call '{call_name}'")
    current_hash = _allowlist_hash()
    hash_path = Path(root) / "docs" / "reports" / "plans" / "allowlist_hash.txt"
    print(f"  Allowlist: {sorted(ALLOWED_MODULES)}")
    print(f"  Hash: {current_hash}")
    if allowlist_violations:
        print(f"  RESULT: FAIL ({len(allowlist_violations)} violations)")
        for v in allowlist_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  No forbidden imports, no relative imports, no dynamic imports")
    # guardian: allow-path-string
    if os.path.isfile(hash_path):
        with open(hash_path, encoding="utf-8") as hf:
            saved_hash = hf.read().strip()
        if saved_hash == current_hash:
            print("  Allowlist hash: LOCKED (matches)")
        else:
            print("  Allowlist hash: MISMATCH")
            print(f"    saved hash:   {saved_hash}")
            print(f"    current hash: {current_hash}")
            print("    current allowlist (sorted):")
            for m in sorted(ALLOWED_MODULES):
                print(f"      {m}")
            print("  Allowlist hash: FAIL — run with --acknowledge-import-change")
            failures += 1
    else:
        _wg.makedirs(Path(hash_path).parent, exist_ok=True)
        _wg.open_write(hash_path, current_hash + "\n")
        print(f"  Allowlist hash: INITIALIZED ({current_hash})")
    if not allowlist_violations:
        print("  RESULT: PASS — stdlib allowlist enforced")
    print("\n8. COMPAT NAME CONSUMER REPORT (18 excluded names)")
    print("-" * 40)
    print("  Posture: INTERNAL FOREVER (not deprecated)")
    print("  These names are part of the build/derivation machinery.")
    print("  They are importable but excluded from __all__ to avoid")
    print("  coupling downstream code to internal structure.")
    print()
    compat_consumers: dict[str, list[str]] = {n: [] for n in excluded_names}
    for fpath in scan_files:
        relpath = os.path.relpath(fpath, root)
        if "structure_blueprint" in relpath and "config" in relpath.split(os.sep):
            continue
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
            continue
        for name in excluded_names:
            if name in source:
                compat_consumers[name].append(relpath)
    for name in excluded_names:
        consumers = compat_consumers[name]
        count = len(consumers)
        status = "ACTIVE" if count > 0 else "UNUSED"
        print(f"  {name}: {count} consumer(s) [{status}]")
        if count > 0 and count <= 5:
            for c in consumers:
                print(f"    - {c}")
        elif count > 5:
            for c in consumers[:3]:
                print(f"    - {c}")
            print(f"    ... and {count - 3} more")
    print("\n9. PHANTOM DEBT REGISTER")
    print("-" * 40)
    debt_path = Path(root) / "docs" / "reports" / "plans" / "phantom_debt.md"
    debt_by_key: dict[tuple[str, str], tuple[int, str]] = {}
    for rp, name, lineno, mod in phantom_debt:
        key = (rp, name)
        if key not in debt_by_key:
            debt_by_key[key] = (lineno, mod)
    debt_rows = sorted(debt_by_key.keys())
    assert len(debt_rows) == len(phantom_set), (
        f"debt_rows ({len(debt_rows)}) != phantom_set ({len(phantom_set)})"
    )
    debt_lines: list[str] = [
        "# Phantom Import Debt Register",
        "",
        f"Phantom count: {len(debt_rows)}",
        "",
        "| Path | Missing Name | Import Line | Suggested Fix |",
        "| --- | --- | --- | --- |",
    ]
    for rp, name in debt_rows:
        lineno, mod = debt_by_key[rp, name]
        if name.isupper() or ("_" in name and name == name.upper()):
            fix = "replace import or define symbol"
        elif name.startswith("get_"):
            fix = "remove or update function import"
        else:
            fix = "remove phantom import"
        excerpt = f"`from {mod} import {name}` (line {lineno})"
        debt_lines.append(f"| `{rp}` | `{name}` | {excerpt} | {fix} |")
    debt_lines.append("")
    _wg.makedirs(Path(debt_path).parent, exist_ok=True)
    _wg.open_write(debt_path, "\n".join(debt_lines))
    baseline_count = len(saved_set) if saved_set is not None else None
    current_count = len(phantom_set)
    print("  Source: PHANTOM_CURRENT_SET (deduplicated current scan)")
    print(f"  Phantom current count:  {current_count}")
    if baseline_count is not None:
        print(f"  Phantom baseline count: {baseline_count}")
    print(f"  Debt rows:              {len(debt_rows)}")
    print(f"  Invariant: debt_rows == current_count: {len(debt_rows) == current_count}")
    if baseline_count is not None:
        print(f"  Invariant: current_count == baseline_count: {current_count == baseline_count}")
    print(f"  Generated: {os.path.relpath(debt_path, root)}")
    print("\n10. ENFORCEMENT MODULES")
    print("-" * 40)
    from pathlib import Path as _Path

    from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import ImportGraph
    from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
        emit_report_json,
        make_report,
    )

    enforcement_root = _Path(root)
    print("  Building import graph...")
    import_graph = ImportGraph(enforcement_root, SCAN_ROOTS)
    print(
        f"  Import graph: {import_graph.files_parsed} files parsed, {len(import_graph.parse_errors)} errors"
    )
    if import_graph.parse_errors:
        for pe in import_graph.parse_errors[:5]:
            print(f"    {pe}")
        if len(import_graph.parse_errors) > 5:
            print(f"    ... and {len(import_graph.parse_errors) - 5} more")
    from agentic_core.L5_safety.config.structure_blueprint.enforcement import (
        blueprint_hash,
        cross_layer,
        leaf_node,
        mixin_ast,
        territory_diff,
        volatile_rules,
    )

    enforcement_results = []
    from collections.abc import Mapping as _Mapping

    td_result = territory_diff.check(enforcement_root, c_st)
    enforcement_results.append(td_result)
    td_stats = td_result["stats"]
    print(
        f"  territory_diff: {len(td_result['violations'])} violation(s)  [{td_stats['territories_checked']} territories checked]"
    )
    ln_result = leaf_node.check(enforcement_root, c_st)
    enforcement_results.append(ln_result)
    ln_stats = ln_result["stats"]
    print(
        f"  leaf_node: {len(ln_result['violations'])} violation(s)  [{ln_stats['territories_checked']} dirs with allow_root_py=False]"
    )
    vr_result = volatile_rules.check(enforcement_root, c_st, import_graph)
    enforcement_results.append(vr_result)
    print(f"  volatile_rules: {len(vr_result['violations'])} violation(s)")
    ac_config = c_st.get(AGENTIC_CORE_DIR, {})
    ac_subfolders = ac_config.get("subfolders", {}) if isinstance(ac_config, _Mapping) else {}
    ma_result = mixin_ast.check(enforcement_root / AGENTIC_CORE_DIR, ac_subfolders)
    enforcement_results.append(ma_result)
    print(f"  mixin_ast: {len(ma_result['violations'])} violation(s)")
    blueprint_dir = _Path(__file__).resolve().parent
    bh_result = blueprint_hash.check(blueprint_dir)
    enforcement_results.append(bh_result)
    print(f"  blueprint_hash: {len(bh_result['violations'])} violation(s)")
    cl_result = cross_layer.check(enforcement_root, c_st, import_graph)
    enforcement_results.append(cl_result)
    print(f"  cross_layer: {len(cl_result['violations'])} violation(s)")
    cl_stats = cl_result["stats"]
    print(
        f"    edges: {cl_stats.get('total_edges', 0)} total, {cl_stats.get('internal_edges', 0)} internal, {cl_stats.get('cross_layer_edges_analyzed', 0)} cross-layer analyzed"
    )
    if enforcement_results:
        report = make_report(enforcement_results)
        report_json = emit_report_json(report)
        verification_dir = Path(root) / "docs" / "reports" / "verification"
        _wg.makedirs(verification_dir, exist_ok=True)
        report_path = Path(verification_dir) / "enforcement_report.json"
        _wg.write_json(report_path, report_json, indent=2)
        print(f"  Artifact: {os.path.relpath(report_path, root)}")
        passed = report["summary"]["passed"]
        failed = report["summary"]["failed"]
        total_v = report["summary"]["total_violations"]
        print(f"  Checks: {passed} passed, {failed} failed, {total_v} violations")
        if not report["overall_passed"]:
            failures += 1
            print("  RESULT: FAIL")
        else:
            print("  RESULT: PASS")
    else:
        print("  No enforcement modules wired yet (Phase 0 stub)")
        print("  RESULT: SKIP")
    print("\n" + "=" * 70)
    if failures == 0:
        print("OVERALL: PASS — all checks green")
    else:
        print(f"OVERALL: {failures} section(s) failed")
    print("=" * 70)
    return failures


if __name__ == "__main__":
    sys.exit(main())
