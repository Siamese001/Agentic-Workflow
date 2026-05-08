"""W4 c0-policy-rectification-deferred-f7b2a9 — OTEL C0 Policy Tracing tests.

Verifies that C0 pipeline and PA boundary emit OTEL spans with C0 policy
provenance fields for observability and debugging.

Test categories:
1. C0 preflight OTEL span fields (l1_grounding_required, route_c0_mode, etc.)
2. PA boundary OTEL span fields (c0_mode, evidence_required, etc.)
3. OTEL span emission when emitter provided
4. No span emission when emitter is None (backward compatibility)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.c0_retrieval.preflight import run_preflight
from agentic_core.L0_routing.c0_retrieval.route_contract import (
    C0Mode,
    C0Policy,
    RouteContract,
)
from agentic_core.L1_cognition.c0_context.types import L1C0Advisory
from agentic_core.prompt_governance.prompt_assembly.pa0_boundary import (
    BoundaryCheckResult,
    BoundaryFailReason,
    BoundaryStatus,
    _emit_pa_span_if_present,
    boundary_check,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_emitter():
    """Create a mock OTEL span emitter."""
    emitter = MagicMock()
    span_context = MagicMock()
    span_context.__enter__ = MagicMock(return_value=span_context)
    span_context.__exit__ = MagicMock(return_value=False)
    emitter.span.return_value = span_context
    return emitter


@pytest.fixture
def sample_route_contract() -> RouteContract:
    """Sample route contract with C0 policy."""
    return RouteContract(
        route_id="R3_GROUNDED",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class="current",
        support_target="SOURCE_SUMMARY",
        tenant_scope="tenant_a",
        acl=("read",),
        region="us",
        data_class="standard",
        max_k=10,
        max_hops=2,
        max_parent_expansion=2,
        max_refine_attempts=1,
        max_latency_ms=2000,
        token_budget=4000,
        allowed_sources=frozenset({"docs", "code"}),
        disallowed_sources=frozenset(),
        fallback_policy="caveat",
        route_replay_key="rk1",
        policy_hash="ph1",
        blueprint_hash="bh1",
        c0_policy=C0Policy(
            c0_mode=C0Mode.RETRIEVE_REQUIRED,
            evidence_contract_required=True,
            decision_source="L0_ROUTE_TOPOLOGY",
        ),
    )


@pytest.fixture
def sample_plan_contract() -> dict[str, Any]:
    """Sample L1 plan contract dict."""
    return {
        "plan_id": "plan-001",
        "grounding_required": True,
        "policy_hash": "ph1",
    }


# =============================================================================
# Test Category 1: C0 Preflight OTEL Span Fields
# =============================================================================


class TestC0PreflightOTELSpans:
    """C0 preflight emits OTEL spans with C0 policy provenance fields."""

    def test_preflight_span_includes_l1_grounding_required(
        self, mock_emitter, sample_route_contract
    ):
        """OTEL span includes l1_grounding_required field."""
        plan = L1C0Advisory(
            grounding_required=True,
            confidence=0.9,
            grounding_reason_codes=["REQUIRES_GROUNDING"],
            support_target="SOURCE_SUMMARY",
        )

        run_preflight(sample_route_contract, plan, emitter=mock_emitter)

        # Verify span was called with correct attributes
        mock_emitter.span.assert_called_once()
        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["l1_grounding_required"] is True

    def test_preflight_span_includes_route_c0_mode(
        self, mock_emitter, sample_route_contract
    ):
        """OTEL span includes route_c0_mode field."""
        plan = L1C0Advisory(
            grounding_required=True,
            confidence=0.9,
            grounding_reason_codes=["REQUIRES_GROUNDING"],
            support_target="SOURCE_SUMMARY",
        )

        run_preflight(sample_route_contract, plan, emitter=mock_emitter)

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["route_c0_mode"] == "RETRIEVE_REQUIRED"

    def test_preflight_span_includes_evidence_contract_required(
        self, mock_emitter, sample_route_contract
    ):
        """OTEL span includes evidence_contract_required field."""
        plan = L1C0Advisory(
            grounding_required=True,
            confidence=0.9,
            grounding_reason_codes=["REQUIRES_GROUNDING"],
            support_target="SOURCE_SUMMARY",
        )

        run_preflight(sample_route_contract, plan, emitter=mock_emitter)

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["evidence_contract_required"] is True

    def test_preflight_span_includes_c0_policy_decision_source(
        self, mock_emitter, sample_route_contract
    ):
        """OTEL span includes c0_policy_decision_source field."""
        plan = L1C0Advisory(
            grounding_required=True,
            confidence=0.9,
            grounding_reason_codes=["REQUIRES_GROUNDING"],
            support_target="SOURCE_SUMMARY",
        )

        run_preflight(sample_route_contract, plan, emitter=mock_emitter)

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["c0_policy_decision_source"] == "L0_ROUTE_TOPOLOGY"

    def test_preflight_no_span_when_emitter_none(self, sample_route_contract):
        """No OTEL span emitted when emitter is None (backward compat)."""
        plan = L1C0Advisory(
            grounding_required=True,
            confidence=0.9,
            grounding_reason_codes=["REQUIRES_GROUNDING"],
            support_target="SOURCE_SUMMARY",
        )

        # Should not raise when emitter is None
        result = run_preflight(sample_route_contract, plan, emitter=None)
        assert result is not None


# =============================================================================
# Test Category 2: PA Boundary OTEL Span Fields
# =============================================================================


class TestPABoundaryOTELSpans:
    """PA boundary emits OTEL spans with C0 policy provenance fields."""

    def test_boundary_span_includes_c0_mode(self, mock_emitter):
        """OTEL span includes c0_mode field."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=mock_emitter,
        )

        mock_emitter.span.assert_called()
        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["c0_mode"] == "RETRIEVE_REQUIRED"

    def test_boundary_span_includes_evidence_required(self, mock_emitter):
        """OTEL span includes evidence_required field."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=mock_emitter,
        )

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["evidence_required"] is True

    def test_boundary_span_includes_evidence_present(self, mock_emitter):
        """OTEL span includes evidence_present field."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=mock_emitter,
        )

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["evidence_present"] is True

    def test_boundary_span_includes_c0_policy_source(self, mock_emitter):
        """OTEL span includes c0_policy_source field."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=mock_emitter,
        )

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["c0_policy_source"] == "L0_ROUTE_TOPOLOGY"

    def test_boundary_span_includes_boundary_status(self, mock_emitter):
        """OTEL span includes boundary_status field."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        result = boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=mock_emitter,
        )

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["boundary_status"] == result.status.value

    def test_boundary_no_span_when_emitter_none(self):
        """No OTEL span emitted when emitter is None (backward compat)."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "execution_form": "SINGLE_STEP",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L0_ROUTE_TOPOLOGY",
            },
        }

        # Should not raise when emitter is None
        result = boundary_check(
            route_contract=route_contract,
            plan_contract={"plan_id": "plan-001", "grounding_required": True},
            evidence_contract={"c0_status": "RETRIEVED"},
            execution_metadata={},
            emitter=None,
        )
        assert result.status == BoundaryStatus.PASS


# =============================================================================
# Test Category 3: OTEL Helper Function
# =============================================================================


class TestEmitPaSpanHelper:
    """_emit_pa_span_if_present helper function behavior."""

    def test_helper_noop_when_emitter_none(self):
        """Helper returns early when emitter is None."""
        result = BoundaryCheckResult(
            status=BoundaryStatus.PASS,
            fail_reason=None,
            eligible_for_prompt_assembly=True,
        )

        # Should not raise
        _emit_pa_span_if_present(
            emitter=None,
            result=result,
            c0_mode="RETRIEVE_REQUIRED",
            evidence_required=True,
            evidence_present=True,
            c0_policy_source="L0_ROUTE_TOPOLOGY",
        )

    def test_helper_includes_fail_reason_when_present(self, mock_emitter):
        """Helper includes fail_reason in span when result has one."""
        result = BoundaryCheckResult(
            status=BoundaryStatus.FAIL,
            fail_reason=BoundaryFailReason.MISSING_ROUTE_CONTRACT,
        )

        _emit_pa_span_if_present(
            emitter=mock_emitter,
            result=result,
            c0_mode="NOT_SET",
            evidence_required=False,
            evidence_present=False,
            c0_policy_source="UNKNOWN",
        )

        call_kwargs = mock_emitter.span.call_args[1]
        assert call_kwargs["fail_reason"] == "missing_route_contract"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
