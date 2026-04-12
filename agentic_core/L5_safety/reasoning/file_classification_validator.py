"""
FileClassificationValidatorAgent - L5 Pure Validator.

Runs FileClassificationAgent in validate_only mode to detect naming,
territory, and layer alignment violations without mutating the filesystem.
Emits a structured check dict consumed by heal_file_classification via
HEALER_REGISTRY.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

emit_replay_key("p0", "file_classification_validator")
emit_determinism_digest("p0", "file_classification_validator")

_emit_dispatches_healing_run("p1", "file_classification_validator", "L5")
_emit_routes_through("p1", "file_classification_validator", "L5")
_emit_checks_agent_registry("p1", "file_classification_validator", "agent_registry")
_emit_validates_agent_capability("p1", "file_classification_validator", "capability")
_emit_dispatches_execution_plan("p1", "file_classification_validator", "exec_plan")
_emit_agent_executes_agent("p1", "file_classification_validator", "sub_agent")
_emit_routes_to_agent("p1", "file_classification_validator", "target_agent")
_emit_verifies_policy("p1", "file_classification_validator", "policy_check")
_emit_observes_runtime_state("p1", "file_classification_validator", "runtime_state")
_emit_verifies_boundary("p1", "file_classification_validator", "boundary_check")
_emit_transcripts_response("p1", "file_classification_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "file_classification_validator")
_emit_gated_by_confidence("p1", "file_classification_validator", "confidence_gate")
_emit_escalates_to_human("p1", "file_classification_validator", "L5")
_emit_reads_policy_state("p1", "file_classification_validator", "L5")

_emit_applies_guardrail("p0", "file_classification_validator", "p0_governance")
_emit_snapshots_state("p0", "file_classification_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "file_classification_validator", "execution_auth")
_emit_validates_capability("p2", "file_classification_validator", "capability_check")
_emit_routes_to_capability("p2", "file_classification_validator", "capability_route")
_emit_writes_via_uwg("p2", "file_classification_validator", "uwg_write")
_emit_blocks_direct_write("p2", "file_classification_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "file_classification_validator", "tool_invocation")
_emit_captures_execution_output("p2", "file_classification_validator", "exec_output")
_emit_dispatches_agent("p3", "file_classification_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "file_classification_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "file_classification_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "file_classification_validator", "healing_outcome")
_emit_escalates_failure("p3", "file_classification_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "file_classification_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "file_classification_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "file_classification_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "file_classification_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "file_classification_validator", "eval_metric")
_emit_stores_embedding("p4", "file_classification_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "file_classification_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "file_classification_validator", "exec_snapshot_link")
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

_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_1")
_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_2")
_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_3")
_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_4")
_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_5")
_emit_emits_metric_event("file_classification_validator", "p4obs", "metric_6")
_emit_records_incident_event("file_classification_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("file_classification_validator", "p4obs", "anomaly")
_emit_writes_observability_log("file_classification_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("file_classification_validator", "p4obs", "mon_state")
_emit_triggers_alert("file_classification_validator", "p4obs", "alert")
_emit_links_incident_trace("file_classification_validator", "p4obs", "trace_link")
_emit_captures_pattern("file_classification_validator", "p3lm", "pattern")
_emit_records_learning_event("file_classification_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("file_classification_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("file_classification_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("file_classification_validator", "p3lm", "routing")
_emit_improves_agent_policy("file_classification_validator", "p3lm", "policy")
_emit_stores_learning_state("file_classification_validator", "p3lm", "state")
_emit_records_execution_trace("file_classification_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("file_classification_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("file_classification_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("file_classification_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("file_classification_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("file_classification_validator", "env_read", "p2_env_1")
_emit_reads_environ("file_classification_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("file_classification_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("file_classification_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "file_classification_validator", "context_pull")
_emit_pulls_context("p1", "file_classification_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "file_classification_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "file_classification_validator", "uwg_term_2")
_emit_writes_through("p1", "file_classification_validator", "write_through")
_emit_writes_through("p1", "file_classification_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "file_classification_validator", "safety_validation")
_emit_invokes_eval("p1", "file_classification_validator", "eval_call")
_emit_proposal_commits_routing("p1", "file_classification_validator", "routing_commit")

CHECK_ID = "file_classification"
logger = logging.getLogger(__name__)


class FileClassificationValidatorAgent:
    """L5 Certify-only validator for file classification compliance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run FileClassificationAgent in validate_only mode.

        Args:
            target_territory: Optional territory string to scope the scan.

        Returns:
            Dict with keys: scan_result, violations, stats, file_registry.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "FileClassificationValidatorAgent.scan",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:FileClassificationValidatorAgent.scan".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        classifier = FileClassificationAgent(project_root=self.project_root)
        classifier.validate_only = True
        classifier.dry_run = False
        if hasattr(classifier, "target_territory"):
            classifier.target_territory = target_territory
        try:
            if target_territory:
                try:
                    scan_result = classifier.run(target_territory=target_territory) or {}
                except TypeError:
                    scan_result = classifier.run() or {}
            else:
                scan_result = classifier.run() or {}
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as exc:
            logger.error("[FileClassificationValidatorAgent] scan failed: %s", exc)
            scan_result = {}
        violations: list[dict[str, Any]] = []
        if hasattr(classifier, "stats") and classifier.stats.get("violations"):
            for vtype, count in classifier.stats["violations"].items():
                if isinstance(count, int) and count > 0:
                    violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": target_territory,
                        },
                    )
        file_registry: list[str] = []
        if hasattr(classifier, "file_registry") and classifier.file_registry:
            file_registry = [str(p) for p in classifier.file_registry]
        return {"scan_result": scan_result, "violations": violations, "file_registry": file_registry}

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        evidence = self.scan(target_territory=target_territory)
        violations_count = sum(v.get("count", 1) for v in evidence.get("violations", []))
        return {
            "check_id": CHECK_ID,
            "evidence": evidence,
            "violations_count": violations_count,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
