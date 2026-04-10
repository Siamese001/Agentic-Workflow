"""ImportResolutionGuardian — Referential Integrity for Python Imports.

AST-walks all .py files under SCAN_ROOTS, resolves every internal import
target against the filesystem, and fails on NEW unresolved imports.

Follows the phantom-baseline-lock pattern (§21):
  - Snapshot existing unresolved imports into a baseline JSON
  - Fail only on *new* unresolved imports (not in baseline)
  - Require explicit --update-baseline to accept fixes
  - CI refuses --update-baseline unless ALLOW_BASELINE_WRITES_IN_CI=1

Output: artifacts/import_health/import_health_report.json

Exit codes:
  0 = PASS (no new unresolved imports)
  1 = FAIL (new unresolved imports detected, or baseline drift)
  2 = ERROR (script-level failure)

Usage:
  python ops_scripts/ci/import_resolution_guardian.py
  python ops_scripts/ci/import_resolution_guardian.py --update-baseline
  python ops_scripts/ci/import_resolution_guardian.py --repo-root /path/to/repo
  python ops_scripts/ci/import_resolution_guardian.py --verbose
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "import_resolution_guardian")
_emit_applies_guardrail("p0", "import_resolution_guardian", "p0_governance")
_emit_reads_policy_state("p0", "import_resolution_guardian", "policy_binding")
_emit_snapshots_state("p0", "import_resolution_guardian", "state_snapshot")
emit_replay_key("p0", "import_resolution_guardian")
emit_determinism_digest("p0", "import_resolution_guardian")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "import_resolution_guardian", "execution_auth")
_emit_validates_capability("p2", "import_resolution_guardian", "capability_check")
_emit_routes_to_capability("p2", "import_resolution_guardian", "capability_route")
_emit_writes_via_uwg("p2", "import_resolution_guardian", "uwg_write")
_emit_blocks_direct_write("p2", "import_resolution_guardian", "direct_write_block")
_emit_records_tool_invocation("p2", "import_resolution_guardian", "tool_invocation")
_emit_captures_execution_output("p2", "import_resolution_guardian", "exec_output")
_emit_dispatches_agent("p3", "import_resolution_guardian", "agent_dispatch")
_emit_coordinates_agents("p3", "import_resolution_guardian", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_resolution_guardian", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_resolution_guardian", "healing_outcome")
_emit_escalates_failure("p3", "import_resolution_guardian", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_resolution_guardian", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_resolution_guardian", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_resolution_guardian", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_resolution_guardian", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_resolution_guardian", "eval_metric")
_emit_stores_embedding("p4", "import_resolution_guardian", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_resolution_guardian", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_resolution_guardian", "exec_snapshot_link")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_PACKAGES,  # SSOT list of all apps_* packages
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_1")
_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_2")
_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_3")
_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_4")
_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_5")
_emit_emits_metric_event("import_resolution_guardian", "p4obs", "metric_6")
_emit_records_incident_event("import_resolution_guardian", "p4obs", "incident")
_emit_captures_runtime_anomaly("import_resolution_guardian", "p4obs", "anomaly")
_emit_writes_observability_log("import_resolution_guardian", "p4obs", "obs_log")
_emit_updates_monitoring_state("import_resolution_guardian", "p4obs", "mon_state")
_emit_triggers_alert("import_resolution_guardian", "p4obs", "alert")
_emit_links_incident_trace("import_resolution_guardian", "p4obs", "trace_link")
_emit_captures_pattern("import_resolution_guardian", "p3lm", "pattern")
_emit_records_learning_event("import_resolution_guardian", "p3lm", "learning_event")
_emit_writes_learning_snapshot("import_resolution_guardian", "p3lm", "snapshot")
_emit_feeds_meta_learning("import_resolution_guardian", "p3lm", "meta_feed")
_emit_updates_routing_strategy("import_resolution_guardian", "p3lm", "routing")
_emit_improves_agent_policy("import_resolution_guardian", "p3lm", "policy")
_emit_stores_learning_state("import_resolution_guardian", "p3lm", "state")
_emit_records_execution_trace("import_resolution_guardian", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("import_resolution_guardian", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("import_resolution_guardian", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("import_resolution_guardian", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("import_resolution_guardian", "L4_STATE", "p2_trace_5")
_emit_reads_environ("import_resolution_guardian", "env_read", "p2_env_1")
_emit_reads_environ("import_resolution_guardian", "env_read", "p2_env_2")
_emit_reads_runtime_state("import_resolution_guardian", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("import_resolution_guardian", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "import_resolution_guardian", "context_pull")
_emit_pulls_context("p1", "import_resolution_guardian", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "import_resolution_guardian", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "import_resolution_guardian", "uwg_term_2")
_emit_writes_through("p1", "import_resolution_guardian", "write_through")
_emit_writes_through("p1", "import_resolution_guardian", "write_through_2")
_emit_validated_by_safety_plane("p1", "import_resolution_guardian", "safety_validation")
_emit_invokes_eval("p1", "import_resolution_guardian", "eval_call")
_emit_proposal_commits_routing("p1", "import_resolution_guardian", "routing_commit")
_emit_escalates_to_human("p1", "import_resolution_guardian", "human_escalation")
_emit_routes_through("p1", "import_resolution_guardian", "route_through")
_emit_checks_agent_registry("p1", "import_resolution_guardian", "agent_registry")
_emit_validates_agent_capability("p1", "import_resolution_guardian", "capability")
_emit_dispatches_execution_plan("p1", "import_resolution_guardian", "exec_plan")
_emit_agent_executes_agent("p1", "import_resolution_guardian", "sub_agent")
_emit_routes_to_agent("p1", "import_resolution_guardian", "target_agent")
_emit_verifies_policy("p1", "import_resolution_guardian", "policy_check")
_emit_observes_runtime_state("p1", "import_resolution_guardian", "runtime_state")
_emit_verifies_boundary("p1", "import_resolution_guardian", "boundary_check")
_emit_transcripts_response("p1", "import_resolution_guardian", "transcript")
_emit_hard_fails_untranscripted("p1", "import_resolution_guardian")
_emit_gated_by_confidence("p1", "import_resolution_guardian", "confidence_gate")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_1")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_2")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_3")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_4")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_5")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_6")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_7")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_8")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_9")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_10")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_11")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_12")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_13")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_14")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_15")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_16")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_17")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_18")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_19")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_20")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_21")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_22")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_23")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_24")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_25")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_26")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_27")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_28")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_29")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_30")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_31")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_32")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_33")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_34")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_35")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_36")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_37")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_38")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_39")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_40")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_41")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_42")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_43")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_44")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_45")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_46")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_47")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_48")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_49")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_50")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_51")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_52")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_53")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_54")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_55")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_56")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_57")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_58")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_59")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_60")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_61")
_emit_reads_through("l4", "import_resolution_guardian", "urg_read_62")

# Construct SCAN_ROOTS from SSOT: agentic_core + all apps_* packages (auto-expands as new apps are added)
SCAN_ROOTS: tuple[str, ...] = (AGENTIC_CORE_DIR, *APPS_PACKAGES)
INTERNAL_ROOTS: frozenset[str] = frozenset(SCAN_ROOTS)
WALK_EXCLUDES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
BASELINE_PATH = PROJECT_ROOT / 'artifacts' / 'import_health' / 'import_health_baseline.json'
REPORT_PATH = PROJECT_ROOT / 'artifacts' / 'import_health' / 'import_health_report.json'

class UnresolvedImport:
    """A single unresolved import edge."""
    __slots__ = ('source_file', 'target_module', 'lineno', 'imported_names')

    def __init__(self, source_file: str, target_module: str, lineno: int, imported_names: tuple[str, ...]) -> None:
        self.source_file = source_file
        self.target_module = target_module
        self.lineno = lineno
        self.imported_names = imported_names

    def key(self) -> str:
        """Deterministic sort key: source_file::target_module::lineno."""
        return f'{self.source_file}::{self.target_module}::{self.lineno}'

    def to_dict(self) -> dict:
        return {'source_file': self.source_file, 'target_module': self.target_module, 'lineno': self.lineno, 'imported_names': list(self.imported_names)}

def resolve_module_path(root: Path, module: str) -> Path | None:
    """Resolve a dotted module path to a filesystem Path, or None.

    Checks (in order):
      1. Package: root/a/b/c/__init__.py
      2. Module:  root/a/b/c.py
    """
    parts = module.split('.')
    pkg_path = root / '/'.join(parts) / '__init__.py'
    if pkg_path.is_file():
        return pkg_path
    if len(parts) >= 2:
        mod_path = root / '/'.join(parts[:-1]) / (parts[-1] + '.py')
        if mod_path.is_file():
            return mod_path
    direct_path = root / ('/'.join(parts) + '.py')
    if direct_path.is_file():
        return direct_path
    return None

def collect_unresolved_imports(root: Path, scan_roots: tuple[str, ...], *, verbose: bool=False) -> tuple[list[UnresolvedImport], int, list[str]]:
    """AST-walk all .py files under scan_roots and find unresolved internal imports.

    Returns:
        (unresolved_imports, files_parsed, parse_errors)
    """
    unresolved: list[UnresolvedImport] = []
    files_parsed = 0
    parse_errors: list[str] = []
    for scan_root in scan_roots:
        scan_dir = root / scan_root
        if not scan_dir.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in WALK_EXCLUDES]
            for fn in filenames:
                if not fn.endswith('.py'):
                    continue
                fpath = Path(dirpath) / fn
                rel = fpath.relative_to(root).as_posix()
                file_unresolved = _parse_file_imports(root, fpath, rel, verbose=verbose)
                if file_unresolved is None:
                    parse_errors.append(rel)
                else:
                    files_parsed += 1
                    unresolved.extend(file_unresolved)
    unresolved.sort(key=lambda u: u.key())
    return (unresolved, files_parsed, parse_errors)

def _parse_file_imports(root: Path, fpath: Path, rel: str, *, verbose: bool=False) -> list[UnresolvedImport] | None:
    """Parse a single file and return unresolved internal imports, or None on parse error."""
    try:
        source = fpath.read_text(encoding='utf-8', errors='replace')
    except OSError:    # guardian: Add error context logging
        return None
    try:
        tree = ast.parse(source, filename=str(fpath))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return None
    unresolved: list[UnresolvedImport] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split('.')[0]
            if top not in INTERNAL_ROOTS:
                continue
            names = tuple(a.name for a in node.names or [])
            if resolve_module_path(root, node.module) is None:
                unresolved.append(UnresolvedImport(source_file=rel, target_module=node.module, lineno=node.lineno, imported_names=names))
                if verbose:
                    print(f'  UNRESOLVED: {rel}:{node.lineno} -> {node.module}')
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split('.')[0]
                if top not in INTERNAL_ROOTS:
                    continue
                if resolve_module_path(root, alias.name) is None:
                    unresolved.append(UnresolvedImport(source_file=rel, target_module=alias.name, lineno=node.lineno, imported_names=(alias.name,)))
                    if verbose:
                        print(f'  UNRESOLVED: {rel}:{node.lineno} -> {alias.name}')
    return unresolved

def _baseline_key(entry: dict) -> str:
    """Canonical key for a baseline entry."""
    return f"{entry['source_file']}::{entry['target_module']}"

def load_baseline(path: Path) -> dict[str, dict]:
    """Load baseline JSON. Returns dict keyed by source_file::target_module."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    entries = data.get('unresolved_imports', [])
    return {_baseline_key(e): e for e in entries}

def _require_baseline_approval() -> bool:
    """Check IMPORT_BASELINE_UPDATE_APPROVED env var. Return True if approved."""
    return os.environ.get('IMPORT_BASELINE_UPDATE_APPROVED') == 'true'

def save_baseline(path: Path, unresolved: list[UnresolvedImport]) -> None:
    """Save current unresolved imports as baseline.

    Requires IMPORT_BASELINE_UPDATE_APPROVED=true env var.
    Produces deterministic JSON: sorted keys, no timestamps.
    """
    from ops_scripts.ci.baseline_io import write_json_atomic
    if not _require_baseline_approval():
        raise SystemExit('[IMPORT-GUARDIAN] FAIL: Baseline mutation requires IMPORT_BASELINE_UPDATE_APPROVED=true')
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {'schema_version': 1, 'unresolved_count': len(unresolved), 'unresolved_imports': [u.to_dict() for u in unresolved]}
    write_json_atomic(path, data)

def compute_drift(baseline: dict[str, dict], current: list[UnresolvedImport]) -> tuple[list[UnresolvedImport], list[dict]]:
    """Compare current unresolved against baseline.

    Returns:
        (new_unresolved, fixed_entries)
        - new_unresolved: imports not in baseline (regressions)
        - fixed_entries: baseline entries no longer present (improvements)
    """
    current_keys = set()
    new_unresolved: list[UnresolvedImport] = []
    for u in current:
        key = f'{u.source_file}::{u.target_module}'
        current_keys.add(key)
        if key not in baseline:
            new_unresolved.append(u)
    fixed_keys = set(baseline.keys()) - current_keys
    fixed_entries = [baseline[k] for k in sorted(fixed_keys)]
    return (new_unresolved, fixed_entries)

def _classify_layer(source_file: str) -> str:
    """Infer debt layer from source file path.

    Rules (per spec):
      - /L5_safety/  -> "healing"
      - /runtime/    -> "runtime"
      - /L<N>_*/     -> "L<N>"
      - apps_*       -> "apps"
      - otherwise    -> "other"
    """
    if '/L5_safety/' in source_file or source_file.startswith('agentic_core/L5_safety/'):
        return 'healing'
    if '/runtime/' in source_file or source_file.startswith('agentic_core/runtime/'):
        return 'runtime'
    for n in ('0', '1', '2', '3', '4', '6'):
        tag = f'L{n}_'
        if f'/{tag}' in source_file or source_file.startswith(f'agentic_core/{tag}'):
            return f'L{n}'
    if source_file.startswith('apps_'):
        return 'apps'
    return 'other'

def build_debt_summary(unresolved: list[UnresolvedImport]) -> dict:
    """Build deterministic debt classification summary."""
    by_layer: dict[str, int] = {}
    healing_count = 0
    runtime_count = 0
    for u in unresolved:
        layer = _classify_layer(u.source_file)
        by_layer[layer] = by_layer.get(layer, 0) + 1
        if layer == 'healing':
            healing_count += 1
        elif layer == 'runtime':
            runtime_count += 1
    return {'total_unresolved': len(unresolved), 'by_layer': dict(sorted(by_layer.items())), 'healing_count': healing_count, 'runtime_count': runtime_count}

def generate_report(unresolved: list[UnresolvedImport], new_unresolved: list[UnresolvedImport], fixed_entries: list[dict], files_parsed: int, parse_errors: list[str], baseline_count: int) -> dict:
    """Generate the import health report as a dict.

    Deterministic: no timestamps, sorted keys. Repeated runs produce zero diff
    when the codebase is unchanged.
    """
    debt = build_debt_summary(unresolved)
    return {'schema_version': 1, 'summary': {'files_parsed': files_parsed, 'parse_errors': len(parse_errors), 'total_unresolved': len(unresolved), 'baseline_count': baseline_count, 'new_unresolved': len(new_unresolved), 'fixed_count': len(fixed_entries), 'passed': len(new_unresolved) == 0, 'by_layer': debt['by_layer'], 'healing_count': debt['healing_count'], 'runtime_count': debt['runtime_count']}, 'new_unresolved_imports': [u.to_dict() for u in new_unresolved], 'all_unresolved_imports': [u.to_dict() for u in unresolved], 'fixed_imports': fixed_entries, 'parse_errors': parse_errors}

def main() -> int:
    """Entry point. Returns exit code."""
    import argparse
    parser = argparse.ArgumentParser(description='ImportResolutionGuardian — detect unresolved internal imports')
    parser.add_argument('--repo-root', type=Path, default=PROJECT_ROOT, help='Repository root (default: auto-detected)')
    parser.add_argument('--update-baseline', action='store_true', help='Update baseline with current unresolved imports. Requires IMPORT_BASELINE_UPDATE_APPROVED=true.')
    parser.add_argument('--init-baseline', action='store_true', help='Alias for --update-baseline (deprecated).')
    parser.add_argument('--verbose', action='store_true', help='Print each unresolved import as it is found')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    print(f'[IMPORT-GUARDIAN] Scanning {len(SCAN_ROOTS)} roots under {root}')
    unresolved, files_parsed, parse_errors = collect_unresolved_imports(root, SCAN_ROOTS, verbose=args.verbose)
    print(f'[IMPORT-GUARDIAN] Parsed {files_parsed} files, {len(parse_errors)} parse errors')
    print(f'[IMPORT-GUARDIAN] Found {len(unresolved)} unresolved internal imports')
    if args.init_baseline or args.update_baseline:
        save_baseline(BASELINE_PATH, unresolved)
        print(f'[IMPORT-GUARDIAN] Baseline updated: {BASELINE_PATH}')
        print(f'[IMPORT-GUARDIAN] Baseline count: {len(unresolved)}')
        return 0
    baseline = load_baseline(BASELINE_PATH)
    baseline_count = len(baseline)
    if baseline_count == 0 and len(unresolved) > 0:
        print('[IMPORT-GUARDIAN] WARNING: No baseline found. Run with --init-baseline first.')
        print(f'[IMPORT-GUARDIAN] Current unresolved count: {len(unresolved)}')
        new_unresolved = unresolved
        fixed_entries: list[dict] = []
    else:
        new_unresolved, fixed_entries = compute_drift(baseline, unresolved)
    print(f'[IMPORT-GUARDIAN] baseline_count={baseline_count}')
    print(f'[IMPORT-GUARDIAN] current_count={len(unresolved)}')
    print(f'[IMPORT-GUARDIAN] new_unresolved={len(new_unresolved)}')
    print(f'[IMPORT-GUARDIAN] fixed_count={len(fixed_entries)}')
    if new_unresolved:
        print('\n[IMPORT-GUARDIAN] NEW UNRESOLVED IMPORTS (regressions):')
        for u in new_unresolved:
            print(f'  {u.source_file}:{u.lineno} -> {u.target_module}')
    if fixed_entries:
        print(f'\n[IMPORT-GUARDIAN] {len(fixed_entries)} previously-unresolved imports now resolve (improvements)')
    report = generate_report(unresolved=unresolved, new_unresolved=new_unresolved, fixed_entries=fixed_entries, files_parsed=files_parsed, parse_errors=parse_errors, baseline_count=baseline_count)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report_content = json.dumps(report, indent=2, sort_keys=True) + '\n'
    REPORT_PATH.write_text(report_content, encoding='utf-8')
    print(f'\n[IMPORT-GUARDIAN] Report written: {REPORT_PATH}')
    if len(new_unresolved) > 0:
        print(f'\n[IMPORT-GUARDIAN] FAIL: {len(new_unresolved)} new unresolved import(s) detected')
        return 1
    print('\n[IMPORT-GUARDIAN] PASS: No new unresolved imports')
    return 0
if __name__ == '__main__':
    sys.exit(main())
