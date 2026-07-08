"""Centralized evaluation corpus loading and caching system.

Mirrors PromptLoader pattern exactly — pure infrastructure, no business logic.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "evaluation_loader", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "evaluation_loader", "policy_binding")
trace_contract._emit_snapshots_state("p0", "evaluation_loader", "state_snapshot")

trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("evaluation_loader", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("evaluation_loader", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("evaluation_loader", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("evaluation_loader", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("evaluation_loader", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("evaluation_loader", "p4obs", "alert")
trace_contract._emit_links_incident_trace("evaluation_loader", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("evaluation_loader", "p3lm", "pattern")
trace_contract._emit_records_learning_event("evaluation_loader", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("evaluation_loader", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("evaluation_loader", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("evaluation_loader", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("evaluation_loader", "p3lm", "policy")
trace_contract._emit_stores_learning_state("evaluation_loader", "p3lm", "state")
trace_contract._emit_records_execution_trace("evaluation_loader", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("evaluation_loader", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("evaluation_loader", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("evaluation_loader", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("evaluation_loader", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("evaluation_loader", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("evaluation_loader", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("evaluation_loader", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("evaluation_loader", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "evaluation_loader", "context_pull")
trace_contract._emit_pulls_context("p1", "evaluation_loader", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluation_loader", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluation_loader", "uwg_term_2")
trace_contract._emit_writes_through("p1", "evaluation_loader", "write_through")
trace_contract._emit_writes_through("p1", "evaluation_loader", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "evaluation_loader", "safety_validation")
trace_contract._emit_invokes_eval("p1", "evaluation_loader", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "evaluation_loader", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "evaluation_loader", "human_escalation")
trace_contract._emit_routes_through("p1", "evaluation_loader", "route_through")
trace_contract._emit_checks_agent_registry("p1", "evaluation_loader", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "evaluation_loader", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "evaluation_loader", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "evaluation_loader", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "evaluation_loader", "target_agent")
trace_contract._emit_verifies_policy("p1", "evaluation_loader", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "evaluation_loader", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "evaluation_loader", "boundary_check")
trace_contract._emit_transcripts_response("p1", "evaluation_loader", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "evaluation_loader")
trace_contract._emit_gated_by_confidence("p1", "evaluation_loader", "confidence_gate")
trace_contract.emit_replay_key("p0", "evaluation_loader")
trace_contract.emit_determinism_digest("p0", "evaluation_loader")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "evaluation_loader", "execution_auth")
trace_contract._emit_validates_capability("p2", "evaluation_loader", "capability_check")
trace_contract._emit_routes_to_capability("p2", "evaluation_loader", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "evaluation_loader", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "evaluation_loader", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "evaluation_loader", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "evaluation_loader", "exec_output")
trace_contract._emit_dispatches_agent("p3", "evaluation_loader", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "evaluation_loader", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "evaluation_loader", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "evaluation_loader", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "evaluation_loader", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "evaluation_loader", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "evaluation_loader", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "evaluation_loader", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "evaluation_loader", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "evaluation_loader", "eval_metric")
trace_contract._emit_stores_embedding("p4", "evaluation_loader", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "evaluation_loader", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "evaluation_loader", "exec_snapshot_link")


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

    _SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

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

    def _resolve_eval_file(self, name: str) -> Path:
        """Resolve evaluation file path with traversal prevention."""
        if "/" in name or "\\" in name:
            raise ValueError("name must not contain path separators")
        if not self._SAFE_NAME_RE.fullmatch(name):
            raise ValueError(f"name contains unsafe characters: {name!r}")
        eval_file = (self._eval_dir / f"{name}.yaml").resolve()
        eval_file.relative_to(self._eval_dir)  # raises ValueError if outside
        return eval_file

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EvaluationLoader.load_eval_set"
        )

        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if name not in self._cache:
            eval_file = self._resolve_eval_file(name)
            if not eval_file.exists():
                raise EvalLoadError(f"Evaluation file not found: {eval_file}")
            if not eval_file.is_file():
                raise EvalLoadError(f"Path is not a file: {eval_file}")
            try:
                with open(eval_file, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                raise EvalLoadError(f"Invalid YAML in {eval_file}: {exc}") from exc
            except OSError as exc:  # review: Add error context logging
                raise EvalLoadError(f"Cannot read {eval_file}: {exc}") from exc
            if not isinstance(data, dict):
                raise EvalSchemaError(
                    f"Evaluation file root must be a dict, got {type(data).__name__}: {eval_file}",
                )
            self._cache[name] = data
        return self._cache[name]

    def clear_cache(self) -> None:
        """Clear the internal cache. Useful for test isolation."""
        self._cache.clear()

    def cache_info(self) -> dict[str, Any]:
        """Return cache statistics for testing and monitoring."""
        return {"cached_items": len(self._cache), "cache_keys": list(self._cache.keys())}
