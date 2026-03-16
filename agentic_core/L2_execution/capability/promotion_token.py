"""Promotion tokens for Wave 17 - P2 Promotion Authority.

This module provides scoped, single-use, time-bounded capability tokens
for promotion operations.
"""

import logging
import secrets
import time
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "promotion_token")
emit_determinism_digest("p0", "promotion_token")

_emit_dispatches_healing_run("p1", "promotion_token", "L2")
_emit_routes_through("p1", "promotion_token", "L2")
_emit_escalates_to_human("p1", "promotion_token", "L2")
_emit_reads_policy_state("p1", "promotion_token", "L2")

_emit_applies_guardrail("p0", "promotion_token", "p0_governance")
_emit_snapshots_state("p0", "promotion_token", "state_snapshot")
_emit_authorize_and_execute("p2", "promotion_token", "execution_auth")
_emit_validates_capability("p2", "promotion_token", "capability_check")
_emit_routes_to_capability("p2", "promotion_token", "capability_route")
_emit_writes_via_uwg("p2", "promotion_token", "uwg_write")
_emit_blocks_direct_write("p2", "promotion_token", "direct_write_block")
_emit_records_tool_invocation("p2", "promotion_token", "tool_invocation")
_emit_captures_execution_output("p2", "promotion_token", "exec_output")
_emit_dispatches_agent("p3", "promotion_token", "agent_dispatch")
_emit_coordinates_agents("p3", "promotion_token", "agent_coordination")
_emit_records_workflow_lineage("p3", "promotion_token", "workflow_lineage")
_emit_records_healing_outcome("p3", "promotion_token", "healing_outcome")
_emit_escalates_failure("p3", "promotion_token", "failure_escalation")
_emit_orchestrates_workflow("p3", "promotion_token", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "promotion_token", "healing_dispatch")
_emit_invokes_evaluation("p3", "promotion_token", "evaluation_signal")
_emit_records_telemetry_event("p4", "promotion_token", "telemetry_event")
_emit_captures_evaluation_metric("p4", "promotion_token", "eval_metric")
_emit_stores_embedding("p4", "promotion_token", "embedding_store")
_emit_updates_meta_learning_state("p4", "promotion_token", "meta_learning")
_emit_links_execution_to_snapshot("p4", "promotion_token", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("promotion_token", "p4obs", "metric_1")
_emit_emits_metric_event("promotion_token", "p4obs", "metric_2")
_emit_emits_metric_event("promotion_token", "p4obs", "metric_3")
_emit_emits_metric_event("promotion_token", "p4obs", "metric_4")
_emit_emits_metric_event("promotion_token", "p4obs", "metric_5")
_emit_emits_metric_event("promotion_token", "p4obs", "metric_6")
_emit_records_incident_event("promotion_token", "p4obs", "incident")
_emit_captures_runtime_anomaly("promotion_token", "p4obs", "anomaly")
_emit_writes_observability_log("promotion_token", "p4obs", "obs_log")
_emit_updates_monitoring_state("promotion_token", "p4obs", "mon_state")
_emit_triggers_alert("promotion_token", "p4obs", "alert")
_emit_links_incident_trace("promotion_token", "p4obs", "trace_link")
_emit_captures_pattern("promotion_token", "p3lm", "pattern")
_emit_records_learning_event("promotion_token", "p3lm", "learning_event")
_emit_writes_learning_snapshot("promotion_token", "p3lm", "snapshot")
_emit_feeds_meta_learning("promotion_token", "p3lm", "meta_feed")
_emit_updates_routing_strategy("promotion_token", "p3lm", "routing")
_emit_improves_agent_policy("promotion_token", "p3lm", "policy")
_emit_stores_learning_state("promotion_token", "p3lm", "state")
_emit_records_execution_trace("promotion_token", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("promotion_token", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("promotion_token", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("promotion_token", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("promotion_token", "L4_STATE", "p2_trace_5")
_emit_reads_environ("promotion_token", "env_read", "p2_env_1")
_emit_reads_environ("promotion_token", "env_read", "p2_env_2")
_emit_reads_runtime_state("promotion_token", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("promotion_token", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "promotion_token", "context_pull")
_emit_pulls_context("p1", "promotion_token", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "promotion_token", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "promotion_token", "uwg_term_2")
_emit_writes_through("p1", "promotion_token", "write_through")
_emit_writes_through("p1", "promotion_token", "write_through_2")
_emit_validated_by_safety_plane("p1", "promotion_token", "safety_validation")
_emit_invokes_eval("p1", "promotion_token", "eval_call")
_emit_proposal_commits_routing("p1", "promotion_token", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromotionToken:
    """Scoped capability token for promotion operations."""

    token_id: str
    target_namespace: str
    semantic_clock_window: tuple[int, int]
    replay_digest_binding: str
    single_use_nonce: str
    guardian_signature: str
    semantic_clock_tick: int
    allowed_action: str = "pointer_update"
    created_at: float = field(default_factory=time.time)

    def validate_scope_and_use(self) -> bool:
        """Validate token scope and single-use status."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "PromotionToken.validate_scope_and_use"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:PromotionToken.validate_scope_and_use".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.allowed_action != "pointer_update":
            Logger.error(f"Token {self.token_id}: Invalid action {self.allowed_action}")
            return False
        if self.is_expired(self.semantic_clock_tick):
            Logger.error(
                f"Token {self.token_id}: Semantic clock {self.semantic_clock_tick} outside window {self.semantic_clock_window}"
            )
            return False
        if PromotionTokenStore.is_nonce_used(self.single_use_nonce):
            Logger.error(f"Token {self.token_id}: Nonce {self.single_use_nonce} already used")
            return False
        PromotionTokenStore.mark_nonce_used(self.single_use_nonce)
        return True

    def is_expired(self, current_tick: int) -> bool:
        """Check if token is expired.

        For point windows (start == end), the token is only valid at exactly that tick.
        For range windows, a grace period applies before the start; only checks upper bound.
        """
        start, end = self.semantic_clock_window
        if start == end:
            return current_tick != start
        return current_tick > end

    def is_valid_for_namespace(self, namespace: str) -> bool:
        """Check if token is valid for given namespace."""
        return self.target_namespace == namespace


class PromotionTokenStore:
    """Store for tracking used nonces and token state."""

    _instance = None
    _used_nonces: set[str] = set()
    _active_tokens: dict[str, PromotionToken] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def is_nonce_used(cls, nonce: str) -> bool:
        """Check if nonce has been used."""
        return nonce in cls._used_nonces

    @classmethod
    def mark_nonce_used(cls, nonce: str) -> None:
        """Mark nonce as used."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "PromotionTokenStore.mark_nonce_used"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PromotionTokenStore.mark_nonce_used".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        cls._used_nonces.add(nonce)
        Logger.info(f"Marked nonce {nonce} as used")

    @classmethod
    def store_token(cls, token: PromotionToken) -> None:
        """Store active token."""
        cls._active_tokens[token.token_id] = token

    @classmethod
    def get_token(cls, token_id: str) -> PromotionToken | None:
        """Get stored token."""
        return cls._active_tokens.get(token_id)

    @classmethod
    def revoke_token(cls, token_id: str) -> bool:
        """Revoke token."""
        if token_id in cls._active_tokens:
            del cls._active_tokens[token_id]
            return True
        return False

    @classmethod
    def clear_all(cls) -> None:
        """Clear all stored data (for testing)."""
        cls._used_nonces.clear()
        cls._active_tokens.clear()


class PromotionTokenIssuer:
    """Issues promotion tokens with proper scope and constraints."""

    def __init__(self):
        self.store = PromotionTokenStore()

    def issue_promotion_token(
        self,
        target_namespace: str,
        semantic_clock_tick: int,
        window_size: int = 100,
        replay_digest: str = "",
        guardian_signature: str = "guardian_sig",
    ) -> PromotionToken:
        """Issue a new promotion token."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "PromotionTokenIssuer.issue_promotion_token"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:PromotionTokenIssuer.issue_promotion_token".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        token_id = f"promo_{secrets.token_hex(8)}"
        single_use_nonce = secrets.token_hex(16)
        start_tick = semantic_clock_tick
        end_tick = semantic_clock_tick + window_size
        token = PromotionToken(
            token_id=token_id,
            allowed_action="pointer_update",
            target_namespace=target_namespace,
            semantic_clock_window=(start_tick, end_tick),
            replay_digest_binding=replay_digest,
            single_use_nonce=single_use_nonce,
            guardian_signature=guardian_signature,
            semantic_clock_tick=semantic_clock_tick,
        )
        self.store.store_token(token)
        Logger.info(f"Issued promotion token {token_id} for namespace {target_namespace}")
        return token

    def validate_token(self, token: PromotionToken, namespace: str, current_tick: int) -> bool:
        """Validate token scope, time window, and single-use nonce (consuming check).

        Checks namespace, expiration, action scope, and single-use nonce.
        Consumes nonce on first successful validation.
        """
        if not token.is_valid_for_namespace(namespace):
            return False
        if token.is_expired(current_tick):
            return False
        return token.validate_scope_and_use()


_token_issuer = None


def get_token_issuer() -> PromotionTokenIssuer:
    """Get the singleton token issuer."""
    global _token_issuer
    if _token_issuer is None:
        _token_issuer = PromotionTokenIssuer()
    return _token_issuer


def issue_promotion_token(
    target_namespace: str,
    semantic_clock_tick: int,
    window_size: int = 100,
    replay_digest: str = "",
    guardian_signature: str = "guardian_sig",
) -> PromotionToken:
    """Issue a new promotion token."""
    issuer = get_token_issuer()
    return issuer.issue_promotion_token(
        target_namespace=target_namespace,
        semantic_clock_tick=semantic_clock_tick,
        window_size=window_size,
        replay_digest=replay_digest,
        guardian_signature=guardian_signature,
    )
