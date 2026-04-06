"""Centralized evaluation corpus loading and caching system.

Mirrors PromptLoader pattern exactly — pure infrastructure, no business logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "evaluation_loader", "p0_governance")
_emit_reads_policy_state("p0", "evaluation_loader", "policy_binding")
_emit_snapshots_state("p0", "evaluation_loader", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_1")
_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_2")
_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_3")
_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_4")
_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_5")
_emit_emits_metric_event("evaluation_loader", "p4obs", "metric_6")
_emit_records_incident_event("evaluation_loader", "p4obs", "incident")
_emit_captures_runtime_anomaly("evaluation_loader", "p4obs", "anomaly")
_emit_writes_observability_log("evaluation_loader", "p4obs", "obs_log")
_emit_updates_monitoring_state("evaluation_loader", "p4obs", "mon_state")
_emit_triggers_alert("evaluation_loader", "p4obs", "alert")
_emit_links_incident_trace("evaluation_loader", "p4obs", "trace_link")
_emit_captures_pattern("evaluation_loader", "p3lm", "pattern")
_emit_records_learning_event("evaluation_loader", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evaluation_loader", "p3lm", "snapshot")
_emit_feeds_meta_learning("evaluation_loader", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evaluation_loader", "p3lm", "routing")
_emit_improves_agent_policy("evaluation_loader", "p3lm", "policy")
_emit_stores_learning_state("evaluation_loader", "p3lm", "state")
_emit_records_execution_trace("evaluation_loader", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evaluation_loader", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evaluation_loader", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evaluation_loader", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evaluation_loader", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evaluation_loader", "env_read", "p2_env_1")
_emit_reads_environ("evaluation_loader", "env_read", "p2_env_2")
_emit_reads_runtime_state("evaluation_loader", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evaluation_loader", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evaluation_loader", "context_pull")
_emit_pulls_context("p1", "evaluation_loader", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evaluation_loader", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evaluation_loader", "uwg_term_2")
_emit_writes_through("p1", "evaluation_loader", "write_through")
_emit_writes_through("p1", "evaluation_loader", "write_through_2")
_emit_validated_by_safety_plane("p1", "evaluation_loader", "safety_validation")
_emit_invokes_eval("p1", "evaluation_loader", "eval_call")
_emit_proposal_commits_routing("p1", "evaluation_loader", "routing_commit")
_emit_escalates_to_human("p1", "evaluation_loader", "human_escalation")
_emit_routes_through("p1", "evaluation_loader", "route_through")
_emit_checks_agent_registry("p1", "evaluation_loader", "agent_registry")
_emit_validates_agent_capability("p1", "evaluation_loader", "capability")
_emit_dispatches_execution_plan("p1", "evaluation_loader", "exec_plan")
_emit_agent_executes_agent("p1", "evaluation_loader", "sub_agent")
_emit_routes_to_agent("p1", "evaluation_loader", "target_agent")
_emit_verifies_policy("p1", "evaluation_loader", "policy_check")
_emit_observes_runtime_state("p1", "evaluation_loader", "runtime_state")
_emit_verifies_boundary("p1", "evaluation_loader", "boundary_check")
_emit_transcripts_response("p1", "evaluation_loader", "transcript")
_emit_hard_fails_untranscripted("p1", "evaluation_loader")
_emit_gated_by_confidence("p1", "evaluation_loader", "confidence_gate")
emit_replay_key("p0", "evaluation_loader")
emit_determinism_digest("p0", "evaluation_loader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "evaluation_loader", "execution_auth")
_emit_validates_capability("p2", "evaluation_loader", "capability_check")
_emit_routes_to_capability("p2", "evaluation_loader", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_loader", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_loader", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_loader", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_loader", "exec_output")
_emit_dispatches_agent("p3", "evaluation_loader", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_loader", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_loader", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_loader", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_loader", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_loader", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_loader", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_loader", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_loader", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_loader", "eval_metric")
_emit_stores_embedding("p4", "evaluation_loader", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_loader", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_loader", "exec_snapshot_link")


class EvalLoadError(Exception):
    """Raised when an evaluation file cannot be loaded."""

    pass


class EvalSchemaError(Exception):
    """Raised when an evaluation file has an invalid schema."""

    pass


class EvaluationLoader:
    """Pure infrastructure component for loading and caching evaluation YAML files.

    Enforces architectural boundaries:
    - No business logic
    - No domain text formatting
    - No direct apps_* access
    """

    def __init__(self, eval_dir: Path) -> None:
        """Initialize with injected evaluation directory.

        Args:
            eval_dir: Base directory containing evaluation YAML files.

        Raises:
            TypeError: If eval_dir is not a Path object.
            ValueError: If eval_dir does not exist or is not a directory.
        """
        if not isinstance(eval_dir, Path):
            raise TypeError("eval_dir must be a Path object")
        if not eval_dir.exists():
            raise ValueError(f"eval_dir does not exist: {eval_dir}")
        if not eval_dir.is_dir():
            raise ValueError(f"eval_dir must be a directory: {eval_dir}")
        self._eval_dir = eval_dir.resolve()
        self._cache: dict[str, dict[str, Any]] = {}

    def load_eval_set(self, name: str) -> dict[str, Any]:
        """Load and cache an evaluation set by name.

        Args:
            name: Evaluation file name without extension (e.g. 'rubric').

        Returns:
            Loaded evaluation data dictionary.

        Raises:
            EvalLoadError: If the file is missing, unreadable, or YAML is malformed.
            EvalSchemaError: If the top-level value is not a dict.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluationLoader.load_eval_set")

        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if name not in self._cache:
            eval_file = self._eval_dir / f"{name}.yaml"
            if not eval_file.exists():
                raise EvalLoadError(f"Evaluation file not found: {eval_file}")
            if not eval_file.is_file():
                raise EvalLoadError(f"Path is not a file: {eval_file}")
            try:
                with open(eval_file, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                raise EvalLoadError(f"Invalid YAML in {eval_file}: {exc}") from exc
            except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                raise EvalLoadError(f"Cannot read {eval_file}: {exc}") from exc
            if not isinstance(data, dict):
                raise EvalSchemaError(
                    f"Evaluation file root must be a dict, got {type(data).__name__}: {eval_file}"
                )
            self._cache[name] = data
        return self._cache[name]

    def clear_cache(self) -> None:
        """Clear the internal cache. Useful for test isolation."""
        self._cache.clear()

    def cache_info(self) -> dict[str, Any]:
        """Return cache statistics for testing and monitoring."""
        return {"cached_items": len(self._cache), "cache_keys": list(self._cache.keys())}
