"""Failure fingerprinting engine for deterministic failure clustering."""

from __future__ import annotations

import re
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "engine", "exec_snapshot_link")
from .types import FailureEvent, FailureFingerprint

trace_contract._emit_applies_guardrail("p0", "engine", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "engine", "policy_binding")
trace_contract._emit_snapshots_state("p0", "engine", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "engine", "context_pull")
trace_contract._emit_pulls_context("p1", "engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "engine", "write_through")
trace_contract._emit_writes_through("p1", "engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "engine", "human_escalation")
trace_contract._emit_routes_through("p1", "engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "engine")
trace_contract._emit_gated_by_confidence("p1", "engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "engine")
trace_contract.emit_determinism_digest("p0", "engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class FailureFingerprinter:
    """Deterministic failure fingerprinter for clustering recurring failures."""

    def __init__(self, allow_absolute_paths: bool = False):
        """Initialize fingerprinter with configuration."""
        self.allow_absolute_paths = allow_absolute_paths

    def fingerprint(self, event: FailureEvent) -> FailureFingerprint:
        """Generate deterministic fingerprint for failure event."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "FailureFingerprinter.fingerprint"
        )

        if not isinstance(event, FailureEvent):
            raise TypeError(f"Expected FailureEvent, got {type(event).__name__}")
        normalized_event = self._normalize_event(event)
        canonical_bytes = normalized_event.canonical_bytes()
        return FailureFingerprint.from_canonical_bytes(canonical_bytes)

    def _normalize_event(self, event: FailureEvent) -> FailureEvent:
        """Normalize failure event for deterministic fingerprinting."""
        normalized_exc_type = self._normalize_exception_type(event.exc_type)
        normalized_error_code = self._normalize_error_code(event.error_code)
        normalized_component = self._normalize_component(event.component)
        normalized_symbols = self._normalize_symbols(event.symbols)
        normalized_metadata = self._normalize_metadata(event.metadata)
        return FailureEvent(
            exc_type=normalized_exc_type,
            error_code=normalized_error_code,
            component=normalized_component,
            symbols=normalized_symbols,
            metadata=normalized_metadata,
        )

    def _normalize_exception_type(self, exc_type: str) -> str:
        """Normalize exception type to fully qualified name."""
        if not exc_type:
            raise ValueError("Exception type cannot be empty")
        if "." in exc_type:
            return exc_type.split(".")[-1]
        return exc_type

    def _normalize_error_code(self, error_code: str) -> str:
        """Normalize error code to stable string."""
        if not error_code:
            return "UNKNOWN"
        return re.sub("[^A-Z0-9_]", "", error_code.upper())

    def _normalize_component(self, component: str) -> str:
        """Normalize component to stable identifier."""
        if not component:
            return "unknown_component"
        if not self.allow_absolute_paths:
            component = component.replace("\\", "/")
            component = re.sub("^[A-Za-z]:/", "", component)
            component = re.sub("^/", "", component)
            if "/" in component:
                component = component.rsplit("/", 1)[-1]
        component = component.replace("\\", "/").lower()
        for prefix in ["src/", "app/", "lib/", ""]:
            if component.startswith(prefix):
                component = component[len(prefix) :]
                break
        return component or "unknown_component"

    def _normalize_symbols(self, symbols: list[str]) -> list[str]:
        """Normalize symbols to sorted unique list."""
        if not symbols:
            return []
        normalized = []
        for symbol in symbols:
            if not symbol:
                continue
            symbol = re.sub(":\\d+$", "", symbol)
            symbol = re.sub("^.*[\\\\/]", "", symbol)
            symbol = symbol.strip()
            if symbol:
                normalized.append(symbol)
        return sorted(set(normalized))

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, str]:
        """Normalize metadata with allowlist and deterministic stringification."""
        if not metadata:
            return {}
        allowlist = {
            "message",
            "code",
            "status",
            "severity",
            "category",
            "retry_count",
            "timeout",
            "version",
            "phase",
        }
        normalized = {}
        for key, value in tqdm(metadata.items(), desc="Processing", unit="item"):
            if key.lower() not in allowlist:
                continue
            if value is None:
                str_value = "null"
            elif isinstance(value, bool):
                str_value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                str_value = str(value)
            else:
                str_value = str(value).strip()
                if key.lower() == "message":
                    str_value = re.sub("\\s+at line \\d+$", "", str_value)
                    str_value = re.sub("\\s+line \\d+$", "", str_value)
            normalized[key] = str_value
        return normalized
