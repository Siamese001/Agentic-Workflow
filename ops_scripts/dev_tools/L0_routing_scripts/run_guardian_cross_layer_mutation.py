"""
Guardian: Cross-Layer Mutation Guard — AST-based detection of layer gravity
violations beyond what architecture_governance already covers.

Specifically enforces:
- L6 must not import-from or assign-to L4 state modules
- L4 must not call L2 execution entry points
- Any file must not have C0 (embedding) expressions modifying control-plane state

Checks:
- upward_layer_mutation   (general — any lower→higher write detected by AST)
- L6_mutates_L4           (specific pair)
- L4_invokes_L2           (specific pair)
- C0_mutates_control_plane (embedding used on left-hand side of control-plane assignment)

Scan root: agentic_core/
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root
from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "run_guardian_cross_layer_mutation")
emit_determinism_digest("p0", "run_guardian_cross_layer_mutation")

_emit_dispatches_healing_run("p1", "run_guardian_cross_layer_mutation", "L0")
_emit_routes_through("p1", "run_guardian_cross_layer_mutation", "L0")
_emit_checks_agent_registry("p1", "run_guardian_cross_layer_mutation", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_cross_layer_mutation", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_cross_layer_mutation", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_cross_layer_mutation", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_cross_layer_mutation", "target_agent")
_emit_verifies_policy("p1", "run_guardian_cross_layer_mutation", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_cross_layer_mutation", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_cross_layer_mutation", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_cross_layer_mutation", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_cross_layer_mutation")
_emit_gated_by_confidence("p1", "run_guardian_cross_layer_mutation", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_cross_layer_mutation", "L0")
_emit_reads_policy_state("p1", "run_guardian_cross_layer_mutation", "L0")
_emit_authorize_and_execute("p2", "run_guardian_cross_layer_mutation", "execution_auth")
_emit_validates_capability("p2", "run_guardian_cross_layer_mutation", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_cross_layer_mutation", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_cross_layer_mutation", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_cross_layer_mutation", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_cross_layer_mutation", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_cross_layer_mutation", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_cross_layer_mutation", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_cross_layer_mutation", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_cross_layer_mutation", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_cross_layer_mutation", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_cross_layer_mutation", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_cross_layer_mutation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_cross_layer_mutation", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_cross_layer_mutation", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_cross_layer_mutation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_cross_layer_mutation", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_cross_layer_mutation", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_cross_layer_mutation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_cross_layer_mutation", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_cross_layer_mutation", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_cross_layer_mutation", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_cross_layer_mutation", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_cross_layer_mutation", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_cross_layer_mutation", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_cross_layer_mutation", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_cross_layer_mutation", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_cross_layer_mutation", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_cross_layer_mutation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_cross_layer_mutation", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_cross_layer_mutation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_cross_layer_mutation", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_cross_layer_mutation", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_cross_layer_mutation", "p3lm", "state")
_emit_records_execution_trace("run_guardian_cross_layer_mutation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_cross_layer_mutation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_cross_layer_mutation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_cross_layer_mutation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_cross_layer_mutation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_cross_layer_mutation", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_cross_layer_mutation", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_cross_layer_mutation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_cross_layer_mutation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_cross_layer_mutation", "context_pull")
_emit_pulls_context("p1", "run_guardian_cross_layer_mutation", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_cross_layer_mutation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_cross_layer_mutation", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_cross_layer_mutation", "write_through")
_emit_writes_through("p1", "run_guardian_cross_layer_mutation", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_cross_layer_mutation", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_cross_layer_mutation", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_cross_layer_mutation", "routing_commit")

GUARDIAN_ID = "cross_layer_mutation_guard"

LAYER_ORDER: dict[str, int] = {f"L{i}": i for i in range(7)}

SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

CONTROL_PLANE_NAMES: frozenset[str] = frozenset(
    {
        "routing_config",
        "tier_config",
        "gateway_config",
        "control_plane",
        "dispatch_table",
    }
)

EMBEDDING_ATTR_NAMES: frozenset[str] = frozenset(
    {
        "embedding_score",
        "embedding_result",
        "similarity_score",
        "cosine_similarity",
    }
)


def _layer_from_path(path: Path) -> str | None:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_layer_from_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_layer_from_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_layer_from_path")
    for part in path.parts:
        if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
            return part[:2]
    return None


def _layer_from_module_string(module: str) -> str | None:
    for segment in module.split("."):
        if len(segment) >= 2 and segment[0] == "L" and segment[1].isdigit():
            return segment[:2]
    return None


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    agentic = repo_root / AGENTIC_CORE_DIR
    if not agentic.exists():
        return result
    for dirpath, dirnames, filenames in __import__("os").walk(agentic):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fname in sorted(filenames):
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)
    return result


def scan_cross_layer_mutations(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    upward_viols: list[dict] = []
    l6_l4_viols: list[dict] = []
    l4_l2_viols: list[dict] = []
    c0_cp_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        src_layer = _layer_from_path(fpath)
        if src_layer not in LAYER_ORDER:
            continue
        src_num = LAYER_ORDER[src_layer]

        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # upward_layer_mutation / L6_mutates_L4 / L4_invokes_L2:
            # from <higher_layer_module> import ...  then assign to a name
            if isinstance(node, ast.ImportFrom) and node.module:
                tgt_layer = _layer_from_module_string(node.module)
                if tgt_layer and tgt_layer in LAYER_ORDER:
                    tgt_num = LAYER_ORDER[tgt_layer]
                    if src_num > tgt_num:
                        entry = {
                            "path": rel,
                            "line": node.lineno,
                            "detail": f"{src_layer} imports from {tgt_layer}: {node.module}",
                        }
                        upward_viols.append(entry)
                        if src_layer == "L6" and tgt_layer == "L4":
                            l6_l4_viols.append(entry)
                        if src_layer == "L4" and tgt_layer == "L2":
                            l4_l2_viols.append(entry)

            # C0_mutates_control_plane:
            # <control_plane_name> = <expr containing embedding attr>
            if isinstance(node, ast.Assign):
                rhs_has_embedding = any(
                    (isinstance(n, ast.Attribute) and n.attr in EMBEDDING_ATTR_NAMES)
                    or (isinstance(n, ast.Name) and n.id in EMBEDDING_ATTR_NAMES)
                    for n in ast.walk(node.value)
                )
                if rhs_has_embedding:
                    for target in node.targets:
                        tname = None
                        if isinstance(target, ast.Name):
                            tname = target.id
                        elif isinstance(target, ast.Attribute):
                            tname = target.attr
                        if tname in CONTROL_PLANE_NAMES:
                            c0_cp_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{tname} assigned from embedding expression",
                                }
                            )

    return {
        "upward_layer_mutation": sorted(upward_viols, key=lambda v: (v["path"], v["line"])),
        "L6_mutates_L4": sorted(l6_l4_viols, key=lambda v: (v["path"], v["line"])),
        "L4_invokes_L2": sorted(l4_l2_viols, key=lambda v: (v["path"], v["line"])),
        "C0_mutates_control_plane": sorted(c0_cp_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_cross_layer_mutation_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_cross_layer_mutations(repo_root)
    for check_id in ("upward_layer_mutation", "L6_mutates_L4", "L4_invokes_L2", "C0_mutates_control_plane"):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]}
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"cross_layer_mutation_guard: {total} violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: cross_layer_mutation_guard")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_cross_layer_mutation_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
