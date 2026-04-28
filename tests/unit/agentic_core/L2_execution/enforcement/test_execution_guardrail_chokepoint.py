"""Tests for `agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint`.

Covers the Execution surface intersection (23 resolves_callsite edges per
hardened concentration analysis 2026-04-28). Targets the `authorize_and_execute`
P0/L2 chokepoint's fail-closed contract:

    1. Non-ExecutionContext input → ValueError
    2. Missing capability_token → MissingCapabilityToken
    3. Token mismatch → MissingCapabilityToken
    4. Missing policy_hash → MissingPolicyHash
    5. HUMAN_GATED without human_approved → HumanReviewRequired
    6. Custom exception types are PermissionError-derived (fail-closed contract)

Does NOT exercise the post-validation guardrail/UWG path — that requires
broader fixtures (safety audit emitter, observability recorder). The
validation gates above are the chokepoint's primary fail-closed surface.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (  # noqa: E402
    ExecutionBypassAttempt,
    GuardrailDenied,
    HumanReviewRequired,
    MissingCapabilityToken,
    MissingPolicyHash,
    authorize_and_execute,
)
from agentic_core.L4_state.utils.context.execution_context import (  # noqa: E402
    ActionClass,
    ExecutionContext,
)


def _make_ctx(
    *,
    capability_token: str = "token-abc",
    policy_hash: str = "policy-hash-1234567890abcdef",
    action_class: ActionClass = ActionClass.READ_ONLY,
) -> ExecutionContext:
    """Build a valid ExecutionContext for chokepoint tests."""
    return ExecutionContext(
        execution_request_id="req-001",
        run_id="run-001",
        capability_token=capability_token,
        policy_hash=policy_hash,
        guardrail_decision_id="",
        guardrail_decision_hash="",
        execution_input_hash="input-hash-xxxxxxxxxxxxxxxx",
        execution_target_hash="target-hash-xxxxxxxxxxxxxxxx",
        trace_id="trace-001",
        action_class=action_class,
        extra={},
    )


class TestExceptionTypes:
    """All chokepoint exceptions are PermissionError or RuntimeError subclasses
    so callers cannot accidentally swallow them with `except Exception`."""

    def test_guardrail_denied_is_permission_error(self):
        assert issubclass(GuardrailDenied, PermissionError)

    def test_missing_capability_token_is_permission_error(self):
        assert issubclass(MissingCapabilityToken, PermissionError)

    def test_missing_policy_hash_is_permission_error(self):
        assert issubclass(MissingPolicyHash, PermissionError)

    def test_human_review_required_is_permission_error(self):
        assert issubclass(HumanReviewRequired, PermissionError)

    def test_execution_bypass_attempt_is_runtime_error(self):
        assert issubclass(ExecutionBypassAttempt, RuntimeError)


class TestInputValidation:
    """Step 1: validate_execution_context_completeness."""

    def test_non_context_input_raises_value_error(self):
        with pytest.raises(ValueError, match="expected ExecutionContext"):
            authorize_and_execute(
                execution_context={"not": "a context"},  # type: ignore[arg-type]
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
            )

    def test_string_as_context_raises_value_error(self):
        with pytest.raises(ValueError, match="expected ExecutionContext"):
            authorize_and_execute(
                execution_context="not-a-context",  # type: ignore[arg-type]
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
            )


class TestCapabilityTokenGate:
    """Step 2: no anonymous execution."""

    def test_empty_token_raises_missing_capability(self):
        ctx = _make_ctx()
        with pytest.raises(MissingCapabilityToken, match="no capability token"):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="",
                payload={},
            )

    def test_token_mismatch_raises_missing_capability(self):
        ctx = _make_ctx(capability_token="token-correct")
        with pytest.raises(MissingCapabilityToken, match="capability token mismatch"):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-WRONG",
                payload={},
            )


class TestPolicyHashGate:
    """Step 3: no ambient policy."""

    def test_missing_policy_hash_raises(self):
        # ExecutionContext rejects empty policy_hash in __post_init__, so we
        # construct with a valid value then null it out via object.__setattr__
        # to simulate a malformed context reaching the chokepoint (defense-in-
        # depth: chokepoint must check even if construction-time validation
        # was bypassed).
        ctx = _make_ctx()
        object.__setattr__(ctx, "policy_hash", "")
        with pytest.raises(MissingPolicyHash, match="no policy hash"):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
            )


class TestHumanReviewGate:
    """Step 4 + 5: HUMAN_GATED actions require explicit human_approved=True."""

    def test_human_gated_without_approval_raises(self):
        ctx = _make_ctx(action_class=ActionClass.HUMAN_GATED)
        with pytest.raises(HumanReviewRequired, match="HUMAN_GATED action requires human approval"):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
                human_approved=False,
            )

    def test_human_gated_default_human_approved_is_false(self):
        """Default kw value is False — human_approved must be explicit-true."""
        ctx = _make_ctx(action_class=ActionClass.HUMAN_GATED)
        with pytest.raises(HumanReviewRequired):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
            )

    def test_non_human_gated_action_skips_review(self):
        """READ_ONLY is not HUMAN_GATED — should not raise HumanReviewRequired
        even with human_approved=False (different gate fires later)."""
        ctx = _make_ctx(action_class=ActionClass.READ_ONLY)
        # This will fail downstream in guardrail evaluation but NOT with
        # HumanReviewRequired — that's the contract under test.
        try:
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
                human_approved=False,
                safety_plane_available=False,  # forces ERROR → GuardrailDenied
            )
        except HumanReviewRequired:
            pytest.fail("HumanReviewRequired should not fire for READ_ONLY action")
        except (GuardrailDenied, RuntimeError):
            # Expected — downstream guardrail/audit fires; that's another path.
            pass


class TestSafetyPlaneFailClosed:
    """safety_plane_available=False → guardrail returns ERROR → GuardrailDenied."""

    def test_safety_plane_unavailable_blocks_execution(self):
        ctx = _make_ctx()
        with pytest.raises((GuardrailDenied, RuntimeError)):
            authorize_and_execute(
                execution_context=ctx,
                target_callable=lambda x: x,
                capability_token="token-abc",
                payload={},
                safety_plane_available=False,
            )
