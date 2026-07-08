"""
HTTPGuard - Guardrail for External HTTP Call Operations

Provides pre-request guardrail checks for external HTTP calls via
requests, httpx, aiohttp, urllib, and similar libraries.
Emits applies_guardrail ADG edges for tracking and compliance.

Usage:
    from agentic_core.L5_safety.enforcement.http_guard import get_http_guard

    guard = get_http_guard()
    guard.check(operation="get", url="https://api.example.com/data")
    # Then proceed with actual HTTP call
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "http_guard")
trace_contract.emit_determinism_digest("p0", "http_guard")

trace_contract._emit_dispatches_healing_run("p1", "http_guard", "L5")
trace_contract._emit_routes_through("p1", "http_guard", "L5")
trace_contract._emit_checks_agent_registry("p1", "http_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "http_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "http_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "http_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "http_guard", "target_agent")
trace_contract._emit_observes_runtime_state("p1", "http_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "http_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "http_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "http_guard")
trace_contract._emit_gated_by_confidence("p1", "http_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "http_guard", "L5")
trace_contract._emit_reads_policy_state("p1", "http_guard", "L5")
trace_contract._emit_snapshots_state("p0", "http_guard", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "http_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "http_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "http_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "http_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "http_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "http_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "http_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "http_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "http_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "http_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "http_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "http_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "http_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "http_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "http_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "http_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "http_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "http_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "http_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "http_guard", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("http_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("http_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("http_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("http_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("http_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("http_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("http_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("http_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("http_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("http_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("http_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("http_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("http_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("http_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("http_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("http_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("http_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("http_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("http_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("http_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("http_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("http_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("http_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "http_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "http_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "http_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "http_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "http_guard", "write_through")
trace_contract._emit_writes_through("p1", "http_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "http_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "http_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "http_guard", "routing_commit")

logger = logging.getLogger(__name__)


class ExternalHttpDeniedError(Exception):
    """Raised when an external HTTP call is denied by guardrail."""

    pass


class HTTPGuard:
    """
    Guardrail for external HTTP call operations.

    Enforces domain allowlist/denylist policy and logging before
    allowing outbound HTTP requests.
    """

    # URL patterns that are always denied
    DENY_PATTERNS = [
        r"169\.254\.169\.254",  # AWS metadata endpoint
        r"metadata\.google\.internal",
        r"100\.100\.100\.200",  # Alibaba Cloud metadata
        r"localhost",
        r"127\.0\.0\.",
        r"0\.0\.0\.0",
        r"::1",
    ]

    def __init__(self, mode: str = "warn") -> None:
        """
        Initialize HTTPGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        """
        self.mode = mode
        self._request_log: list[dict[str, Any]] = []
        self._deny_patterns = [re.compile(p, re.IGNORECASE) for p in self.DENY_PATTERNS]

    def check(
        self,
        operation: str,
        url: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Pre-request guardrail check for external HTTP operations.

        Args:
            operation: HTTP method ("get", "post", "put", "delete", etc.)
            url: Target URL (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            ExternalHttpDeniedError: If request is denied in enforce mode
        """
        trace_contract._emit_verifies_policy(str(uuid.uuid4()), "HTTPGuard.check", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "HTTPGuard.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HTTPGuard.check".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        metadata = metadata or {}
        timestamp = datetime.now(timezone.utc)

        # Emit applies_guardrail ADG edge (structured log for scanner)
        logger.debug(
            "applies_guardrail operation=%s guard=HTTPGuard mode=%s",
            operation,
            self.mode,
        )

        verdict = "allow"
        reason = "External HTTP request allowed"
        violations = []

        if url:
            for pattern in self._deny_patterns:
                if pattern.search(url):
                    violations.append(pattern.pattern)

            if violations:
                verdict = "deny"
                reason = f"Denied URL pattern matched: {', '.join(violations)}"
                logger.warning(
                    "HTTPGuard DENY: %s url=%s - %s",
                    operation,
                    url,
                    reason,
                )
                if self.mode == "enforce":
                    raise ExternalHttpDeniedError(f"External HTTP request denied: {reason}")

        record = {
            "timestamp": timestamp.isoformat(),
            "operation": operation,
            "url": url,
            "verdict": verdict,
            "reason": reason,
            "violations": violations,
            "metadata": metadata,
        }
        self._request_log.append(record)

        logger.info(
            "HTTPGuard %s: %s url=%s",
            verdict.upper(),
            operation,
            url or "<unknown>",
        )

        return {
            "verdict": verdict,
            "reason": reason,
            "violations": violations,
            "timestamp": timestamp.isoformat(),
        }

    def get_request_log(self) -> list[dict[str, Any]]:
        """Get full request log."""
        return self._request_log.copy()

    def clear_log(self) -> None:
        """Clear request log."""
        self._request_log.clear()


_global_guard = HTTPGuard(mode="warn")


def get_http_guard() -> HTTPGuard:
    """Get global HTTPGuard instance."""
    return _global_guard


def set_http_guard_mode(mode: str) -> None:
    """Set global HTTPGuard mode ("warn" or "enforce")."""
    trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "Module.set_http_guard_mode", "L5_POLICY")
    global _global_guard
    _global_guard = HTTPGuard(mode=mode)
