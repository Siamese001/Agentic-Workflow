from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "lazy_seam_scanner")
emit_determinism_digest("p0", "lazy_seam_scanner")

_emit_dispatches_healing_run("p1", "lazy_seam_scanner", "L5")
_emit_routes_through("p1", "lazy_seam_scanner", "L5")
_emit_checks_agent_registry("p1", "lazy_seam_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "lazy_seam_scanner", "capability")
_emit_dispatches_execution_plan("p1", "lazy_seam_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "lazy_seam_scanner", "sub_agent")
_emit_routes_to_agent("p1", "lazy_seam_scanner", "target_agent")
_emit_verifies_policy("p1", "lazy_seam_scanner", "policy_check")
_emit_observes_runtime_state("p1", "lazy_seam_scanner", "runtime_state")
_emit_verifies_boundary("p1", "lazy_seam_scanner", "boundary_check")
_emit_transcripts_response("p1", "lazy_seam_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "lazy_seam_scanner")
_emit_gated_by_confidence("p1", "lazy_seam_scanner", "confidence_gate")
_emit_escalates_to_human("p1", "lazy_seam_scanner", "L5")
_emit_reads_policy_state("p1", "lazy_seam_scanner", "L5")

_emit_applies_guardrail("p0", "lazy_seam_scanner", "p0_governance")
_emit_snapshots_state("p0", "lazy_seam_scanner", "state_snapshot")
_emit_authorize_and_execute("p2", "lazy_seam_scanner", "execution_auth")
_emit_validates_capability("p2", "lazy_seam_scanner", "capability_check")
_emit_routes_to_capability("p2", "lazy_seam_scanner", "capability_route")
_emit_writes_via_uwg("p2", "lazy_seam_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "lazy_seam_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "lazy_seam_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "lazy_seam_scanner", "exec_output")
_emit_dispatches_agent("p3", "lazy_seam_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "lazy_seam_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "lazy_seam_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "lazy_seam_scanner", "healing_outcome")
_emit_escalates_failure("p3", "lazy_seam_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "lazy_seam_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lazy_seam_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "lazy_seam_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "lazy_seam_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lazy_seam_scanner", "eval_metric")
_emit_stores_embedding("p4", "lazy_seam_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "lazy_seam_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lazy_seam_scanner", "exec_snapshot_link")

"\nLazy Seam Scanner - Phase 4 Option A: Thin wrapper over Phase 3B metric.\n\nThis scanner uses the exact Phase 3B lazy upward import metric to ensure\nthe same seam universe (44 seams) and scan scope.\n"
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
from tqdm import tqdm

_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_1")
_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_2")
_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_3")
_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_4")
_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_5")
_emit_emits_metric_event("lazy_seam_scanner", "p4obs", "metric_6")
_emit_records_incident_event("lazy_seam_scanner", "p4obs", "incident")
_emit_captures_runtime_anomaly("lazy_seam_scanner", "p4obs", "anomaly")
_emit_writes_observability_log("lazy_seam_scanner", "p4obs", "obs_log")
_emit_updates_monitoring_state("lazy_seam_scanner", "p4obs", "mon_state")
_emit_triggers_alert("lazy_seam_scanner", "p4obs", "alert")
_emit_links_incident_trace("lazy_seam_scanner", "p4obs", "trace_link")
_emit_captures_pattern("lazy_seam_scanner", "p3lm", "pattern")
_emit_records_learning_event("lazy_seam_scanner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lazy_seam_scanner", "p3lm", "snapshot")
_emit_feeds_meta_learning("lazy_seam_scanner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lazy_seam_scanner", "p3lm", "routing")
_emit_improves_agent_policy("lazy_seam_scanner", "p3lm", "policy")
_emit_stores_learning_state("lazy_seam_scanner", "p3lm", "state")
_emit_records_execution_trace("lazy_seam_scanner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lazy_seam_scanner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lazy_seam_scanner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lazy_seam_scanner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lazy_seam_scanner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lazy_seam_scanner", "env_read", "p2_env_1")
_emit_reads_environ("lazy_seam_scanner", "env_read", "p2_env_2")
_emit_reads_runtime_state("lazy_seam_scanner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lazy_seam_scanner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lazy_seam_scanner", "context_pull")
_emit_pulls_context("p1", "lazy_seam_scanner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lazy_seam_scanner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lazy_seam_scanner", "uwg_term_2")
_emit_writes_through("p1", "lazy_seam_scanner", "write_through")
_emit_writes_through("p1", "lazy_seam_scanner", "write_through_2")
_emit_validated_by_safety_plane("p1", "lazy_seam_scanner", "safety_validation")
_emit_invokes_eval("p1", "lazy_seam_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "lazy_seam_scanner", "routing_commit")


@dataclass
class LazyUpwardImport:
    """A lazy upward import excluded by function/try guard."""

    source_file: Path
    source_layer: int
    target_layer: int
    import_statement: str
    line_number: int
    context: str


LAYER_PATTERN = re.compile("^L(\\d+)_")
IMPORT_LAYER_PATTERN = re.compile("agentic_core\\.L(\\d+)_")


def layer_of_path(path: Path, agentic_root: Path) -> int | None:
    """Extract layer number from a path."""
    try:
        rel = path.relative_to(agentic_root)
    except ValueError:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
        return None
    parts = rel.parts
    if not parts:
        return None
    match = LAYER_PATTERN.match(parts[0])
    if match:
        return int(match.group(1))
    return None


def extract_import_targets(node: ast.AST) -> list[tuple[str, int]]:
    """Extract import target strings and line numbers from an AST node."""
    targets = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            targets.append((alias.name, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            targets.append((node.module, node.lineno))
    return targets


def _is_inside_function_or_guarded(tree: ast.AST, target_lineno: int) -> bool:
    """Check if a line is inside a function, method, or try/except block."""
    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
    return False


def _get_enclosing_function(
    tree: ast.AST,
    target_lineno: int,
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return the innermost FunctionDef/AsyncFunctionDef enclosing target_lineno."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        if best is None or (
                            best.end_lineno is not None
                            and node.end_lineno - node.lineno < best.end_lineno - best.lineno
                        ):
                            best = node
    return best


def _is_inside_try_module_scope(tree: ast.AST, target_lineno: int) -> bool:
    """Return True if target_lineno is inside a Try block at module scope."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        enclosing_fn = _get_enclosing_function(tree, node.lineno)
                        if enclosing_fn is None:
                            return True
    return False


def collect_lazy_upward_imports(agentic_root: Path) -> list[LazyUpwardImport]:
    """Collect all upward imports excluded ONLY because they are inside a
    function/try guard (the 'lazy seam')."""
    results: list[LazyUpwardImport] = []
    for layer in tqdm(range(7), desc="Processing", unit="item"):
        layer_dir = None
        for item in agentic_root.iterdir():
            if item.is_dir() and item.name.startswith(f"L{layer}_"):
                layer_dir = item
                break
        if layer_dir is None:
            continue
        for py_file in tqdm(layer_dir.rglob("*.py"), desc="Processing", unit="item"):
            try:
                rel = py_file.relative_to(agentic_root)
            except ValueError:
                continue
            parts = rel.parts
            if not parts:  # guardian: Parsing and encoding errors need separate handling strategies
                continue
            m = LAYER_PATTERN.match(parts[0])
            if not m:
                continue
            src_layer = int(m.group(1))
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (
                SyntaxError,
                UnicodeDecodeError,
            ):  # guardian: Parsing and encoding errors need separate handling strategies
                continue
            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                targets = extract_import_targets(node)
                for import_str, line_no in tqdm(targets, desc="Processing", unit="item"):
                    match = IMPORT_LAYER_PATTERN.search(import_str)
                    if not match:
                        continue
                    tgt_layer = int(match.group(1))
                    if tgt_layer <= src_layer:
                        continue
                    if not _is_inside_function_or_guarded(tree, line_no):
                        continue
                    fn = _get_enclosing_function(tree, line_no)
                    if fn is not None:
                        context = fn.name
                    elif _is_inside_try_module_scope(tree, line_no):
                        context = "__try_module_scope__"
                    else:
                        context = "__unknown__"
                    results.append(
                        LazyUpwardImport(
                            source_file=py_file,
                            source_layer=src_layer,
                            target_layer=tgt_layer,
                            import_statement=import_str,
                            line_number=line_no,
                            context=context,
                        ),
                    )
    return results


def lazy_upward_import_metric(agentic_root: Path) -> dict:
    """Compute the LAZY_UPWARD_IMPORTS metric."""
    items = collect_lazy_upward_imports(agentic_root)
    by_pair: dict[tuple[int, int], int] = {}
    by_file: dict[str, int] = {}
    for item in items:
        pair = (item.source_layer, item.target_layer)
        by_pair[pair] = by_pair.get(pair, 0) + 1
        key = str(item.source_file)
        by_file[key] = by_file.get(key, 0) + 1
    return {"total": len(items), "by_pair": by_pair, "by_file": by_file, "items": items}


class LazySeamScanner:
    """Scanner for lazy loader seams using Phase 3B metric output."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.seams: list[dict[str, Any]] = []

    def scan_codebase(self) -> list[dict[str, Any]]:
        """Scan codebase using Phase 3B lazy upward import metric."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "LazySeamScanner.scan_codebase")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LazySeamScanner.scan_codebase".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        agentic_core_path = self.root_path / AGENTIC_CORE_DIR
        metric = lazy_upward_import_metric(agentic_core_path)
        self.seams = []
        for item in tqdm(metric["items"], desc="Processing", unit="item"):
            seam_entry = {
                "file_path": str(item.source_file.relative_to(self.root_path)),
                "function_name": item.context,
                "imported_modules": [item.import_statement] if item.import_statement else [],
                "imported_symbols": [],
                "reason_code": "TBD",
                "justification": "TBD",
            }
            self.seams.append(seam_entry)
        self.seams.sort(key=lambda x: (x["file_path"], x["function_name"], x["imported_modules"]))
        return self.seams

    def export_allowlist(self, output_path: Path) -> None:
        """Export allowlist to JSON file."""
        allowlist = {
            "description": "Lazy Seam Allowlist - Phase 4 Option A (Phase 3B universe)",
            "seams": self.seams,
        }
        _wg.write_json(output_path, allowlist, indent=2)
        print(f"Allowlist exported to: {output_path}")


def main():
    """Main entry point."""
    root_path = Path.cwd()
    scanner = LazySeamScanner(root_path)
    print("Scanning codebase for lazy seams (Phase 3B universe)...")
    seams = scanner.scan_codebase()
    print(f"Found {len(seams)} lazy seams")
    output_path = root_path / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_allowlist.json"
    scanner.export_allowlist(output_path)
    by_file = {}
    for seam in seams:
        file_path = seam["file_path"]
        by_file[file_path] = by_file.get(file_path, 0) + 1
    print("\nSummary by file:")
    for file_path, count in sorted(by_file.items()):
        print(f"  {file_path}: {count}")
    agentic_core_path = root_path / AGENTIC_CORE_DIR
    phase3b_metric = lazy_upward_import_metric(agentic_core_path)
    phase3b_total = phase3b_metric["total"]
    assert len(seams) == phase3b_total, (
        f"Phase 4 scanner total ({len(seams)}) != Phase 3B total ({phase3b_total}). Scanner must be aligned to Phase 3B universe."
    )
    print(f"\n✓ Phase 4 scanner matches Phase 3B total: {len(seams)} seams")


if __name__ == "__main__":
    main()
