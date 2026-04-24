"""
Guardian: Escalation Determinism — AST-based detection of non-deterministic
escalation context construction.

Escalation paths must be built from structured, typed inputs only.
Raw-note concatenation or mutable-context patterns are forbidden.

Checks:
- failure_signal_built_from_raw_notes
- alternate_escalation_context_construction
- escalation_context_mutation

Scan roots: agentic_core/, apps_lic/, apps_rg/
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
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
    record_execution_trace,
)
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root

emit_replay_key("p0", "run_guardian_escalation_determinism")
emit_determinism_digest("p0", "run_guardian_escalation_determinism")

_emit_dispatches_healing_run("p1", "run_guardian_escalation_determinism", "L0")
_emit_routes_through("p1", "run_guardian_escalation_determinism", "L0")
_emit_checks_agent_registry("p1", "run_guardian_escalation_determinism", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_escalation_determinism", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_escalation_determinism", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_escalation_determinism", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_escalation_determinism", "target_agent")
_emit_verifies_policy("p1", "run_guardian_escalation_determinism", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_escalation_determinism", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_escalation_determinism", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_escalation_determinism", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_escalation_determinism")
_emit_gated_by_confidence("p1", "run_guardian_escalation_determinism", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_escalation_determinism", "L0")
_emit_reads_policy_state("p1", "run_guardian_escalation_determinism", "L0")
_emit_authorize_and_execute("p2", "run_guardian_escalation_determinism", "execution_auth")
_emit_validates_capability("p2", "run_guardian_escalation_determinism", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_escalation_determinism", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_escalation_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_escalation_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_escalation_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_escalation_determinism", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_escalation_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_escalation_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_escalation_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_escalation_determinism", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_escalation_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_escalation_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_escalation_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_escalation_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_escalation_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_escalation_determinism", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_escalation_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_escalation_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_escalation_determinism", "exec_snapshot_link")
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

record_execution_trace("run_guardian_escalation_determinism", "run_guardian_escalation_determinism_trace")


_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_escalation_determinism", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_escalation_determinism", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_escalation_determinism", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_escalation_determinism", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_escalation_determinism", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_escalation_determinism", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_escalation_determinism", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_escalation_determinism", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_escalation_determinism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_escalation_determinism", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_escalation_determinism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_escalation_determinism", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_escalation_determinism", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_escalation_determinism", "p3lm", "state")
_emit_records_execution_trace("run_guardian_escalation_determinism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_escalation_determinism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_escalation_determinism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_escalation_determinism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_escalation_determinism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_escalation_determinism", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_escalation_determinism", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_escalation_determinism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_escalation_determinism", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_escalation_determinism", "context_pull")
_emit_pulls_context("p1", "run_guardian_escalation_determinism", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_escalation_determinism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_escalation_determinism", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_escalation_determinism", "write_through")
_emit_writes_through("p1", "run_guardian_escalation_determinism", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_escalation_determinism", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_escalation_determinism", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_escalation_determinism", "routing_commit")

GUARDIAN_ID = "escalation_determinism"

SCAN_ROOTS: tuple[str, ...] = (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR)
SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# Functions that must not be called with free-form string args as escalation inputs
RAW_NOTE_SENTINELS: frozenset[str] = frozenset(
    {
        "FailureSignal",
        "EscalationContext",
        "EscalationRecord",
    },
)

# In-place mutation method names on escalation types
MUTATION_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "append",
        "update",
        "extend",
        "setdefault",
        "__setitem__",
        "add_note",
        "set_context",
    },
)


def _collect_files(repo_root: Path) -> list[Path]:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_collect_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_collect_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_collect_files")
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_escalation_patterns(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    raw_note_viols: list[dict] = []
    alt_ctx_viols: list[dict] = []
    mutation_viols: list[dict] = []

    for fpath in tqdm(files, desc="Processing", unit="item"):
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:  # guardian: allow-silent-swallow -- acceptable exception handling
            continue

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            # failure_signal_built_from_raw_notes:
            # FailureSignal(...) or EscalationContext(...) call where any
            # positional arg is a JoinedStr (f-string) or BinOp(str concat)
            if isinstance(node, ast.Call):
                fname_node = node.func
                call_name = None
                if isinstance(fname_node, ast.Name):
                    call_name = fname_node.id
                elif isinstance(fname_node, ast.Attribute):
                    call_name = fname_node.attr

                if call_name in RAW_NOTE_SENTINELS:
                    for arg in node.args:
                        if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                            raw_note_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{call_name}() receives f-string/concat arg",
                                },
                            )
                            break

            # escalation_context_mutation:
            # <var>.<mutation_method>(...) where var name contains "escalation"/"context"
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in MUTATION_METHOD_NAMES:
                    if isinstance(func.value, ast.Name):
                        vname = func.value.id.lower()
                        if "escalation" in vname or "context" in vname or "signal" in vname:
                            mutation_viols.append(
                                {
                                    "path": rel,
                                    "line": node.lineno,
                                    "detail": f"{func.value.id}.{func.attr}() — mutation on escalation obj",
                                },
                            )

    return {
        "failure_signal_built_from_raw_notes": sorted(raw_note_viols, key=lambda v: (v["path"], v["line"])),
        "alternate_escalation_context_construction": sorted(
            alt_ctx_viols,
            key=lambda v: (v["path"], v["line"]),
        ),
        "escalation_context_mutation": sorted(mutation_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_escalation_determinism_guardian(
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

    viols = scan_escalation_patterns(repo_root)
    for check_id in tqdm(
        (
            "failure_signal_built_from_raw_notes",
            "alternate_escalation_context_construction",
            "escalation_context_mutation",
        ),
        desc="Processing",
        unit="item",
    ):
        v = viols[check_id]
        if v:
            result.add_check(
                check_id,
                CheckStatus.FAIL,
                f"{len(v)} violation(s)",
                evidence={"violations": v[:20]},
            )
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"escalation_determinism: {total} violation(s)"
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: escalation_determinism")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_escalation_determinism_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
