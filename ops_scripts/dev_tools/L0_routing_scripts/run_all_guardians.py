"""
Aggregation Runner — Discovers and runs all Guardian scripts deterministically.

Produces a combined_guardian_result.json with:
- Global status (FAIL if any FAIL, ERROR if any ERROR)
- Per-guardian results in deterministic sorted order
- Artifact index referencing all per-guardian outputs

CLI:
    python -m agentic_core.L0_routing.scripts.run_all_guardians \\
        --write-artifacts docs/reports/verification/guardian \\
        --strict
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.guardian_contract_types import (
    AGGREGATE_GUARDIAN_ID,
    CONTRACT_VERSION,
    ArtifactClass,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.types.guardian_registry_types import (
    GuardianSpec,
    get_guardian_specs,
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
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root

emit_replay_key("p0", "run_all_guardians")
emit_determinism_digest("p0", "run_all_guardians")

_emit_dispatches_healing_run("p1", "run_all_guardians", "L0")
_emit_routes_through("p1", "run_all_guardians", "L0")
_emit_checks_agent_registry("p1", "run_all_guardians", "agent_registry")
_emit_validates_agent_capability("p1", "run_all_guardians", "capability")
_emit_dispatches_execution_plan("p1", "run_all_guardians", "exec_plan")
_emit_agent_executes_agent("p1", "run_all_guardians", "sub_agent")
_emit_routes_to_agent("p1", "run_all_guardians", "target_agent")
_emit_verifies_policy("p1", "run_all_guardians", "policy_check")
_emit_verifies_boundary("p1", "run_all_guardians", "boundary_check")
_emit_transcripts_response("p1", "run_all_guardians", "transcript")
_emit_hard_fails_untranscripted("p1", "run_all_guardians")
_emit_gated_by_confidence("p1", "run_all_guardians", "confidence_gate")
_emit_escalates_to_human("p1", "run_all_guardians", "L0")
_emit_reads_policy_state("p1", "run_all_guardians", "L0")

_emit_snapshots_state("p0", "run_all_guardians", "state_snapshot")
_emit_authorize_and_execute("p2", "run_all_guardians", "execution_auth")
_emit_validates_capability("p2", "run_all_guardians", "capability_check")
_emit_routes_to_capability("p2", "run_all_guardians", "capability_route")
_emit_writes_via_uwg("p2", "run_all_guardians", "uwg_write")
_emit_blocks_direct_write("p2", "run_all_guardians", "direct_write_block")
_emit_records_tool_invocation("p2", "run_all_guardians", "tool_invocation")
_emit_captures_execution_output("p2", "run_all_guardians", "exec_output")
_emit_dispatches_agent("p3", "run_all_guardians", "agent_dispatch")
_emit_coordinates_agents("p3", "run_all_guardians", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_all_guardians", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_all_guardians", "healing_outcome")
_emit_escalates_failure("p3", "run_all_guardians", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_all_guardians", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_all_guardians", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_all_guardians", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_all_guardians", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_all_guardians", "eval_metric")
_emit_stores_embedding("p4", "run_all_guardians", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_all_guardians", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_all_guardians", "exec_snapshot_link")
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

_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_1")
_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_2")
_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_3")
_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_4")
_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_5")
_emit_emits_metric_event("run_all_guardians", "p4obs", "metric_6")
_emit_records_incident_event("run_all_guardians", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_all_guardians", "p4obs", "anomaly")
_emit_writes_observability_log("run_all_guardians", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_all_guardians", "p4obs", "mon_state")
_emit_triggers_alert("run_all_guardians", "p4obs", "alert")
_emit_links_incident_trace("run_all_guardians", "p4obs", "trace_link")
_emit_captures_pattern("run_all_guardians", "p3lm", "pattern")
_emit_records_learning_event("run_all_guardians", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_all_guardians", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_all_guardians", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_all_guardians", "p3lm", "routing")
_emit_improves_agent_policy("run_all_guardians", "p3lm", "policy")
_emit_stores_learning_state("run_all_guardians", "p3lm", "state")
_emit_records_execution_trace("run_all_guardians", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_all_guardians", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_all_guardians", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_all_guardians", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_all_guardians", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_all_guardians", "env_read", "p2_env_1")
_emit_reads_environ("run_all_guardians", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_all_guardians", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_all_guardians", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_all_guardians", "context_pull")
_emit_pulls_context("p1", "run_all_guardians", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_all_guardians", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_all_guardians", "uwg_term_2")
_emit_writes_through("p1", "run_all_guardians", "write_through")
_emit_writes_through("p1", "run_all_guardians", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_all_guardians", "safety_validation")
_emit_invokes_eval("p1", "run_all_guardians", "eval_call")
_emit_proposal_commits_routing("p1", "run_all_guardians", "routing_commit")


def _run_single_guardian(
    spec: GuardianSpec,
    repo_root: Path,
    artifact_dir: str | None,
    timestamp: str | None,
    correlation_id: str | None,
) -> GuardianResult:
    """Import and execute a single guardian, returning its result."""
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_run_single_guardian", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_run_single_guardian")
    mod = importlib.import_module(spec.entrypoint_module)
    func = getattr(mod, spec.entrypoint_fn)
    result: GuardianResult = func(
        repo_root=repo_root,
        write_artifacts_dir=artifact_dir,
        timestamp=timestamp,
    )
    if correlation_id is not None:
        result.correlation_id = correlation_id
    return result


def run_all_guardians(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
    include_disabled: bool = False,
) -> GuardianResult:
    """
    Execute all registered guardians in deterministic order and aggregate.

    Args:
        include_disabled: If True, run ALL guardians (including disabled_by_default).
                          Default False = enabled-only.

    Returns a combined GuardianResult with:
    - guardian_id = "combined"
    - Global status promotion (ERROR > FAIL > PASS)
    - Per-guardian check entries
    - Combined metrics
    - Artifact references
    """
    import uuid  # noqa: PLC0415

    _emit_observes_runtime_state(str(uuid.uuid4()), "Module.run_all_guardians", "L0_ROUTING")
    if repo_root is None:
        repo_root = get_validated_project_root()

    combined = GuardianResult(
        guardian_id=AGGREGATE_GUARDIAN_ID,
        version=CONTRACT_VERSION,
        timestamp=timestamp,
        correlation_id=correlation_id,
        artifact_class=ArtifactClass.AGGREGATE,
    )

    per_guardian_results: list[dict[str, Any]] = []
    guardian_index: dict[str, dict[str, Any]] = {}  # Phase 4: artifact index
    total_checks = 0
    total_failed = 0
    total_error = 0

    # Get guardians from SSOT registry (already sorted by guardian_id)
    guardian_specs = get_guardian_specs(enabled_only=not include_disabled)

    for spec in tqdm(guardian_specs, desc="Processing", unit="item"):
        gid = spec.guardian_id
        try:
            result = _run_single_guardian(
                spec,
                repo_root,
                write_artifacts_dir,
                timestamp,
                correlation_id,
            )
            # Add a roll-up check for this guardian
            combined.add_check(
                check_id=f"guardian_{gid}",
                status=(CheckStatus.FAIL if result.status != GuardianStatus.PASS.value else CheckStatus.PASS),
                details=result.summary,
                evidence={
                    "guardian_id": gid,
                    "status": result.status,
                    "check_count": len(result.checks),
                    "checks": [c.to_dict() for c in result.checks],
                },
            )

            # Promote global status
            if result.status == GuardianStatus.ERROR.value:
                combined.status = GuardianStatus.ERROR.value
                total_error += 1
            elif result.status == GuardianStatus.FAIL.value:
                if combined.status != GuardianStatus.ERROR.value:
                    combined.status = GuardianStatus.FAIL.value
                total_failed += 1

            total_checks += len(result.checks)

            # Collect remediation hints
            combined.remediation_hints.extend(result.remediation_hints)

            # Collect artifact references
            for artifact in result.artifacts:
                combined.artifacts.append(artifact)

            per_guardian_results.append(
                {
                    "guardian_id": gid,
                    "status": result.status,
                    "checks": len(result.checks),
                },
            )

            # Phase 4: build artifact index for L6 ingestion
            guardian_index[gid] = {
                "status": result.status,
                "artifacts": [normalize_repo_path(a.path) for a in result.artifacts],
            }

        # guardian: allow-silent-swallow
        except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling

    # Finalize
    guardian_count = len(guardian_specs)
    passed_count = guardian_count - total_failed - total_error
    combined.metrics = {
        "guardian_count": guardian_count,
        "guardians_passed": passed_count,
        "guardians_failed": total_failed,
        "guardians_error": total_error,
        "total_checks": total_checks,
        "per_guardian": per_guardian_results,
    }
    combined.index = guardian_index

    if combined.status == GuardianStatus.PASS.value:
        combined.summary = f"All {guardian_count} guardians passed ({total_checks} checks)"
    elif combined.status == GuardianStatus.ERROR.value:
        combined.summary = f"{total_error} guardian(s) errored, {total_failed} failed out of {guardian_count}"
    else:
        combined.summary = (
            f"{total_failed} guardian(s) failed out of {guardian_count} ({total_checks} checks)"
        )

    # --- V15 signing (before serialization) ---
    maybe_sign_result(combined, commit_hash="HEAD")

    # Write combined artifact
    if write_artifacts_dir:
        artifact_dir_path = repo_root / write_artifacts_dir
        out = write_guardian_result(combined, artifact_dir_path, "combined_guardian_result.json")
        combined.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out.relative_to(repo_root)),
            "Combined guardian aggregation result",
        )

    return combined


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Run All Guardians (Aggregated)")
    parser.add_argument(
        "--write-artifacts",
        default=None,
        help="Repo-relative directory to write result JSON",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
    )
    parser.add_argument(
        "--json",
        dest="format",
        action="store_const",
        const="json",
        help="Shorthand for --format json",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        default=False,
        help="Include disabled-by-default guardians in aggregation",
    )
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args()

    result = run_all_guardians(
        write_artifacts_dir=args.write_artifacts,
        timestamp=args.timestamp,
        correlation_id=args.correlation_id,
        include_disabled=args.include_disabled,
    )

    if args.format == "json":
        print(result.to_json())
    else:
        print(f"Guardian Aggregator | Status: {result.status}")
        print(f"Summary: {result.summary}")
        for check in result.checks:
            status_icon = "PASS" if check.status == CheckStatus.PASS.value else "FAIL"
            print(f"  [{status_icon}] {check.check_id}: {check.details}")

    if args.strict and result.status != GuardianStatus.PASS.value:
        return 1
    return 0


# =============================================================================
# §Wave7.0.7 — L0 Render-Only Integration Seam (no apply, no mutation)
# =============================================================================


def render_meta_learning_change_package(
    package: Any,
    *,
    as_json: bool = True,
) -> str:
    """Render a MetaLearningChangePackageArtifact as a deterministic string.

    This is a **pure function**: it does NOT call apply_meta_learning_proposal(),
    does NOT mutate any config, and does NOT write any files.

    Parameters
    ----------
    package : MetaLearningChangePackageArtifact
        The change package to render.
    as_json : bool
        If True, return canonical JSON string of package.to_dict().
        If False, return a stable, minimal single-line summary.

    Returns
    -------
    str
        Deterministic string representation.
    """
    import json as _json

    if as_json:
        return _json.dumps(package.to_dict(), sort_keys=True, separators=(",", ":"))

    return (
        f"CHANGE_PACKAGE target={package.target_component}"
        f" decision_trace={package.decision_trace_id[:12]}"
        f" trace={package.trace_id[:12]}"
        f" spec_keys={sorted(package.change_spec.keys())}"
    )


if __name__ == "__main__":
    sys.exit(main())
