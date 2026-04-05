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
