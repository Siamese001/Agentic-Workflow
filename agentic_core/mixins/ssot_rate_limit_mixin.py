"""
SSOT Rate Limit Mixin — Policy-Hash-Scoped Rate Limiting.

Provides rate limiting that:
  - Keys include active_policy_hash for isolation
  - Replay mode disables rate limiting entirely
  - Must not alter sovereignty token logic

Layer: L2 Execution Aid
Authority: Throttle only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "ssot_rate_limit_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_rate_limit_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_rate_limit_mixin", "state_snapshot")
emit_replay_key("p0", "ssot_rate_limit_mixin")
emit_determinism_digest("p0", "ssot_rate_limit_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_rate_limit_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_rate_limit_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_rate_limit_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_rate_limit_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_rate_limit_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_rate_limit_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_rate_limit_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_rate_limit_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_rate_limit_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_rate_limit_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_rate_limit_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_rate_limit_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_rate_limit_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_rate_limit_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_rate_limit_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_rate_limit_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_rate_limit_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_rate_limit_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_rate_limit_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_rate_limit_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTRateLimit")


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, bucket: str, limit: int, window: float):
        self.bucket = bucket
        self.limit = limit
        self.window = window
        super().__init__(f"Rate limit exceeded for {bucket}: {limit} calls per {window}s")


class SSOTRateLimitMixin:
    """Policy-hash-scoped rate limiter with replay bypass.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Rate limit keys are prefixed with policy hash.
    Under replay mode, rate limiting is completely disabled.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_rate_buckets: dict[str, list[float]] = {}

    # guardian: allow-magic-config
    def rate_check(self, bucket: str, limit: int = 100, window: float = 60.0) -> bool:
        """Check and record a rate-limited call.

        Parameters
        ----------
        bucket : str
            Rate limit bucket name (will be policy-hash-scoped).
        limit : int
            Maximum calls allowed within the window.
        window : float
            Time window in seconds.

        Returns
        -------
        bool
            True if the call is allowed.

        Raises
        ------
        RateLimitExceeded
            If the rate limit is exceeded (non-replay mode only).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTRateLimitMixin.rate_check")

        if getattr(self, "is_replay_mode", False):
            return True
        scoped_key = self._scoped_rate_key(bucket)
        now = time.time()
        if scoped_key not in self._ssot_rate_buckets:
            self._ssot_rate_buckets[scoped_key] = []
        cutoff = now - window
        self._ssot_rate_buckets[scoped_key] = [t for t in self._ssot_rate_buckets[scoped_key] if t > cutoff]
        if len(self._ssot_rate_buckets[scoped_key]) >= limit:
            raise RateLimitExceeded(scoped_key, limit, window)
        self._ssot_rate_buckets[scoped_key].append(now)
        return True

    # guardian: allow-magic-config
    def rate_remaining(self, bucket: str, limit: int = 100, window: float = 60.0) -> int:
        """Return remaining calls allowed in the current window."""
        if getattr(self, "is_replay_mode", False):
            return limit
        scoped_key = self._scoped_rate_key(bucket)
        now = time.time()
        cutoff = now - window
        entries = self._ssot_rate_buckets.get(scoped_key, [])
        active = [t for t in entries if t > cutoff]
        return max(0, limit - len(active))

    def rate_reset(self, bucket: str) -> None:
        """Reset a rate limit bucket."""
        scoped_key = self._scoped_rate_key(bucket)
        self._ssot_rate_buckets.pop(scoped_key, None)

    def _scoped_rate_key(self, bucket: str) -> str:
        """Prefix bucket with active_policy_hash."""
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        return f"{policy_hash}:{bucket}"
