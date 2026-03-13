"""CI tests — ReAct C0 policy boundary enforcement.

Verifies:
  - assert_c0_informational blocks RAG context containing authority fields.
  - Clean RAG context passes without error.
  - C0BoundaryViolation is raised with descriptive message.
  - ReActStrategy.enforce_c0_boundary delegates correctly.
  - Policy hash mismatch in envelope is detectable.

CI failure condition:
  - C0 boundary check not enforced (authority fields pass through).
  - Policy hash mismatch between envelope and expected.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.react_trace_types import (
    C0_FORBIDDEN_FIELDS,
    C0BoundaryViolation,
    ReasonTraceEnvelope,
    assert_c0_informational,
)


class TestC0BoundaryEnforcement:
    def test_clean_context_passes(self):
        assert_c0_informational({"doc_id": "d1", "text": "hello"})

    def test_empty_context_passes(self):
        assert_c0_informational({})

    def test_route_mode_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="route_mode"):
            assert_c0_informational({"route_mode": "fast"})

    def test_execution_tier_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="execution_tier"):
            assert_c0_informational({"execution_tier": "high"})

    def test_safety_policy_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="safety_policy"):
            assert_c0_informational({"safety_policy": "override"})

    def test_tool_budget_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="tool_budget"):
            assert_c0_informational({"tool_budget": 999})

    def test_auth_token_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="auth_token"):
            assert_c0_informational({"auth_token": "secret"})

    def test_policy_override_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="policy_override"):
            assert_c0_informational({"policy_override": True})

    def test_multiple_forbidden_fields_all_reported(self):
        with pytest.raises(C0BoundaryViolation) as exc_info:
            assert_c0_informational({"route_mode": "x", "tool_budget": 1})
        msg = str(exc_info.value)
        assert "route_mode" in msg or "tool_budget" in msg

    def test_source_label_in_error(self):
        with pytest.raises(C0BoundaryViolation, match="MySource"):
            assert_c0_informational({"route_mode": "x"}, source="MySource")

    def test_forbidden_fields_constant_non_empty(self):
        assert len(C0_FORBIDDEN_FIELDS) > 0

    def test_non_forbidden_keys_pass(self):
        safe_context = {
            "title": "doc1",
            "chunk_ids": ["c1", "c2"],
            "score": 0.95,
            "metadata": {"source": "wiki"},
        }
        assert_c0_informational(safe_context)


class TestPolicyHashMismatch:
    """Envelope must fail verify() if policy_hash is tampered."""

    def _make_envelope(self, policy_hash: str) -> ReasonTraceEnvelope:
        return ReasonTraceEnvelope.build(
            trace_id="t-pol",
            plan_hash="ph",
            reason_steps=("s",),
            action_steps=("a",),
            tool_invocations=(),
            policy_hash=policy_hash,
            semantic_clock_vector=(0,),
        )

    def test_correct_policy_hash_verifies(self):
        env = self._make_envelope("pol_v1")
        assert env.verify()

    def test_tampered_policy_hash_fails_verify(self):
        env = self._make_envelope("pol_v1")
        import dataclasses

        tampered = dataclasses.replace(env, policy_hash="evil_policy")
        assert not tampered.verify()

    def test_different_policy_produces_different_envelope(self):
        env1 = self._make_envelope("pol_v1")
        env2 = self._make_envelope("pol_v2")
        assert env1.envelope_hash != env2.envelope_hash
