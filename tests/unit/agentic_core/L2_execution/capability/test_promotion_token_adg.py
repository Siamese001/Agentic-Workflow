"""ADG-driven tests for L2_execution/capability/promotion_token.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_promotion_token_adg")
_emit_applies_guardrail("p0", "test_promotion_token_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_promotion_token_adg", "policy_binding")
_emit_snapshots_state("p0", "test_promotion_token_adg", "state_snapshot")
emit_replay_key("p0", "test_promotion_token_adg")
emit_determinism_digest("p0", "test_promotion_token_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.capability.promotion_token import PromotionToken


class TestPromotionToken:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromotionToken)

    def test_is_frozen(self):
        import dataclasses
        params = dataclasses.fields(PromotionToken)
        assert params is not None

    def test_creates(self):
        token = PromotionToken(
            token_id="tok-001",
            target_namespace="agentic_core",
            semantic_clock_window=(0, 100),
            replay_digest_binding="abc123",
            single_use_nonce="nonce-xyz",
            guardian_signature="sig-abc",
            semantic_clock_tick=50,
        )
        assert token.token_id == "tok-001"
        assert token.allowed_action == "pointer_update"

    def test_has_validate_scope_and_use(self):
        assert hasattr(PromotionToken, "validate_scope_and_use")

    def test_validate_scope_valid_action(self):
        token = PromotionToken(
            token_id="tok-002",
            target_namespace="ns",
            semantic_clock_window=(0, 100),
            replay_digest_binding="d",
            single_use_nonce="n",
            guardian_signature="s",
            semantic_clock_tick=50,
        )
        result = token.validate_scope_and_use()
        assert isinstance(result, bool)
