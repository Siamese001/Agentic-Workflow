"""W6 c0-policy-rectification-f7b2a9 — Tests for C0 policy contract authority.

Test categories:
1. L1 grounding advisory does not authorize C0 by itself
2. L0 freezes c0_policy into RouteContract
3. C0 preflight obeys RouteContract.c0_policy (no route prefix checks)
4. R1/R5 terminal routes bypass via explicit c0_policy
5. R4 with preloaded context emits BYPASS_PRELOADED_CONTEXT
6. R4 with argument grounding requires C0 retrieval
7. PA fails closed when evidence required but missing
8. PA accepts C0BypassReceipt only when c0_policy allows bypass
9. L3 step-level c0_policy honored in managed workflows
10. Negative: hardcoded bypass without c0_policy fails
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.preflight import (
    BlockedReason,
    C0PreflightStatus,
    EvidenceStandard,
    build_c0_policy,
    run_preflight,
)
from agentic_core.L0_routing.c0_retrieval.route_contract import (
    C0Mode,
    C0DecisionSource,
    C0Policy,
    L1PlanContract,
    RouteContract,
)
from agentic_core.L1_cognition.c0_context.preflight import (
    analyze_grounding_advisory,
)
from agentic_core.L1_cognition.c0_context.types import (
    L1C0Advisory,
    SupportTarget,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    FreshnessClass,
    SourceClass,
    SupportTarget as C0SupportTarget,
)
from agentic_core.prompt_governance.prompt_assembly.pa0_boundary import (
    BoundaryCheckResult,
    BoundaryFailReason,
    BoundaryStatus,
    boundary_check,
)


# =============================================================================
# Test Category 1: L1 grounding advisory does not authorize C0 by itself
# =============================================================================

class TestL1AdvisoryOnly:
    """L1 may declare semantic grounding need, but L0 freezes policy."""

    def test_l1_advisory_declares_grounding_required(self):
        """L1 emits advisory grounding_required, not runtime authority."""
        advisory = analyze_grounding_advisory(
            task_spec="Explain the policy on code reviews",
            query_spec="What is the code review policy?",
        )
        assert isinstance(advisory, L1C0Advisory)
        assert advisory.grounding_required is True
        assert "l1:policy_reference" in advisory.grounding_reason_codes
        assert advisory.confidence > 0.0

    def test_l1_advisory_no_grounding_signals(self):
        """L1 correctly identifies when grounding is not needed."""
        advisory = analyze_grounding_advisory(
            task_spec="Hello",
            query_spec="Hi there",
        )
        assert advisory.grounding_required is False
        assert "l1:no_grounding_signals" in advisory.grounding_reason_codes

    def test_l1_advisory_does_not_emit_preflight_status(self):
        """L1 advisory function does NOT emit C0PreflightStatus (runtime)."""
        advisory = analyze_grounding_advisory(
            task_spec="What is the API?",
            query_spec="Explain the API endpoint",
        )
        # L1 emits L1C0Advisory, not C0PreflightStatus
        assert not hasattr(advisory, "eligible")
        assert not hasattr(advisory, "blocked_reason")


# =============================================================================
# Test Category 2: L0 freezes c0_policy into RouteContract
# =============================================================================

class TestL0FreezesC0Policy:
    """L0 consumes L1 advisory and freezes authoritative C0Policy."""

    def _make_route(self, route_id: str) -> RouteContract:
        return RouteContract(
            route_id=route_id,
            grounding_required=True,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
        )

    def test_l0_builds_bypass_cache_policy(self):
        """R1 routes get BYPASS_CACHE_RETURN policy."""
        route = self._make_route("R1_EXACT_CACHE")
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,  # L1 says yes, but R1 overrides
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "BYPASS_CACHE_RETURN"
        assert policy.decision_source == "CACHE_TERMINAL"
        assert policy.evidence_contract_required is False
        assert "R1" in policy.bypass_reason

    def test_l0_builds_bypass_fallback_policy(self):
        """R5 routes get BYPASS_FALLBACK policy."""
        route = self._make_route("R5_SEMANTIC_FALLBACK")
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "BYPASS_FALLBACK"
        assert policy.decision_source == "FALLBACK_TERMINAL"

    def test_l0_builds_retrieve_required_policy(self):
        """R3 routes get RETRIEVE_REQUIRED policy."""
        route = self._make_route("R3_GROUNDED")
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "RETRIEVE_REQUIRED"
        assert policy.evidence_contract_required is True
        assert policy.decision_source == "L1_PLAN_DERIVED"

    def test_l0_builds_bypass_preloaded_context(self):
        """R4 with grounding_required=False gets BYPASS_PRELOADED_CONTEXT."""
        route = self._make_route("R4_SINGLE_ACTION")
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=False,  # Preloaded context
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "BYPASS_PRELOADED_CONTEXT"
        assert policy.decision_source == "PRELOADED_CONTEXT"
        assert policy.evidence_contract_required is False
        assert policy.preloaded_context_ref is not None

    def test_l0_builds_r4_retrieve_required(self):
        """R4 with grounding_required=True gets RETRIEVE_REQUIRED."""
        route = self._make_route("R4_SINGLE_ACTION")
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,  # Argument needs grounding
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "RETRIEVE_REQUIRED"
        assert policy.evidence_contract_required is True
        assert policy.decision_source == "L1_PLAN_DERIVED"


# =============================================================================
# Test Category 3: C0 preflight obeys RouteContract.c0_policy
# =============================================================================

class TestC0PreflightObeysPolicy:
    """C0 preflight must read frozen c0_policy, not route prefixes."""

    def _make_route_with_policy(self, policy: C0Policy) -> RouteContract:
        return RouteContract(
            route_id="R3_GROUNDED",
            grounding_required=True,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(SourceClass.DOCS,),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
            c0_policy=policy,
        )

    def test_c0_preflight_fails_without_c0_policy(self):
        """C0 preflight FAILS if route.c0_policy is None."""
        route = RouteContract(
            route_id="R3_GROUNDED",
            grounding_required=True,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(SourceClass.DOCS,),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
            c0_policy=None,  # Missing policy
        )
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
        )
        result = run_preflight(route, plan)

        assert result.eligible is False
        assert result.blocked_reason == BlockedReason.ROUTE_DISALLOWS_C0

    def test_c0_preflight_bypasses_per_policy(self):
        """C0 preflight bypasses when c0_policy.c0_mode is bypass."""
        policy = C0Policy(
            grounding_required=False,
            c0_mode="BYPASS_PRELOADED_CONTEXT",
            decision_source="PRELOADED_CONTEXT",
            evidence_contract_required=False,
            bypass_reason="R4 with preloaded context",
        )
        route = self._make_route_with_policy(policy)
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,  # L1 wants grounding, but policy overrides
        )
        result = run_preflight(route, plan)

        assert result.eligible is False
        assert result.blocked_reason == BlockedReason.GROUNDING_NOT_REQUIRED
        assert "BYPASS_PRELOADED_CONTEXT" in result.notes[0]

    def test_c0_preflight_eligible_when_retrieve_required(self):
        """C0 preflight proceeds when c0_policy.c0_mode is RETRIEVE_REQUIRED."""
        policy = C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L1_PLAN_DERIVED",
            evidence_contract_required=True,
        )
        route = self._make_route_with_policy(policy)
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
            user_task_text="What is the policy?",
        )
        result = run_preflight(route, plan)

        assert result.eligible is True
        assert result.blocked_reason is None

    def test_c0_preflight_no_route_prefix_checks(self):
        """C0 preflight does NOT check route_id.startswith('R1_')."""
        # Create a route with R1-like name but RETRIEVE_REQUIRED policy
        policy = C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L1_PLAN_DERIVED",
            evidence_contract_required=True,
        )
        route = RouteContract(
            route_id="R1_MISLEADING_NAME",  # Would have been blocked by old prefix check
            grounding_required=True,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(SourceClass.DOCS,),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
            c0_policy=policy,  # Policy says retrieve, so we retrieve
        )
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
            user_task_text="What is the policy?",
        )
        result = run_preflight(route, plan)

        # Should be eligible because c0_policy says so, not blocked by name
        assert result.eligible is True


# =============================================================================
# Test Category 4 & 5: Terminal routes and R4 bypass modes
# =============================================================================

class TestTerminalRoutesAndR4Modes:
    """Terminal routes and R4 emit correct bypass policies."""

    def test_r1_cache_terminal_policy(self):
        """R1_EXACT_CACHE produces BYPASS_CACHE_RETURN."""
        route = RouteContract(
            route_id="R1_EXACT_CACHE",
            grounding_required=False,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="R5",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
        )
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=True,
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "BYPASS_CACHE_RETURN"
        assert policy.decision_source == "CACHE_TERMINAL"

    def test_r4_bypass_not_grounding_not_required(self):
        """R4 bypass uses BYPASS_PRELOADED_CONTEXT, not GROUNDING_NOT_REQUIRED."""
        route = RouteContract(
            route_id="R4_SINGLE_ACTION",
            grounding_required=False,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="r4-preloaded-ctx",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
        )
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=False,
        )
        policy = build_c0_policy(route, plan)

        assert policy.c0_mode == "BYPASS_PRELOADED_CONTEXT"
        assert policy.bypass_reason != "GROUNDING_NOT_REQUIRED"
        assert "preloaded" in policy.bypass_reason.lower()
        assert policy.preloaded_context_ref == "r4-preloaded-ctx"


# =============================================================================
# Test Category 7 & 8: PA boundary enforcement
# =============================================================================

class TestPABoundaryEnforcement:
    """PA must require evidence or bypass receipt based on c0_policy."""

    def test_pa_fails_closed_missing_evidence_when_required(self):
        """PA FAILS when evidence_contract_required=True but no evidence."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
                "decision_source": "L1_PLAN_DERIVED",
            },
        }
        plan_contract = {"plan_id": "plan-123", "grounding_required": True}
        # Missing evidence_contract

        result = boundary_check(
            plan_contract=plan_contract,
            route_contract=route_contract,
            evidence_contract=None,
        )

        assert result.status == BoundaryStatus.FAIL
        assert result.fail_reason == BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE

    def test_pa_fails_on_bypass_receipt_when_evidence_required(self):
        """PA FAILS if evidence required but got bypass receipt."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
            },
        }
        plan_contract = {"plan_id": "plan-123", "grounding_required": True}
        evidence_contract = {
            "status": "OK",
            "c0_status": "BYPASS",  # This is a bypass receipt, not real evidence
            "c0_bypass_reason": "BYPASS_PRELOADED_CONTEXT",
        }

        result = boundary_check(
            plan_contract=plan_contract,
            route_contract=route_contract,
            evidence_contract=evidence_contract,
        )

        assert result.status == BoundaryStatus.FAIL
        assert result.fail_reason == BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE

    def test_pa_passes_with_evidence_when_required(self):
        """PA PASSES when evidence_contract_required=True and evidence present."""
        route_contract = {
            "route_id": "R3_GROUNDED",
            "c0_policy": {
                "c0_mode": "RETRIEVE_REQUIRED",
                "evidence_contract_required": True,
            },
        }
        plan_contract = {"plan_id": "plan-123", "grounding_required": True}
        evidence_contract = {
            "status": "PASS",
            "c0_status": "RETRIEVED",  # Real evidence
            "contract_id": "evidence-456",
        }

        result = boundary_check(
            plan_contract=plan_contract,
            route_contract=route_contract,
            evidence_contract=evidence_contract,
        )

        assert result.status == BoundaryStatus.PASS
        assert result.eligible_for_prompt_assembly is True

    def test_pa_passes_with_bypass_receipt_when_bypass_mode(self):
        """PA PASSES when c0_mode is bypass and C0BypassReceipt present."""
        route_contract = {
            "route_id": "R4_SINGLE_ACTION",
            "c0_policy": {
                "c0_mode": "BYPASS_PRELOADED_CONTEXT",
                "evidence_contract_required": False,
            },
        }
        plan_contract = {"plan_id": "plan-123", "grounding_required": False}
        evidence_contract = {
            "c0_bypass_reason": "BYPASS_PRELOADED_CONTEXT",
            "grounding_required": False,
        }

        result = boundary_check(
            plan_contract=plan_contract,
            route_contract=route_contract,
            evidence_contract=evidence_contract,
        )

        assert result.status == BoundaryStatus.PASS


# =============================================================================
# Test Category 10: Negative test - hardcoded bypass fails
# =============================================================================

class TestNegativeHardcodedBypass:
    """Hardcoded C0 bypass without RouteContract.c0_policy fails."""

    def test_c0_preflight_fails_without_frozen_policy(self):
        """C0 preflight fails closed when c0_policy is missing."""
        route = RouteContract(
            route_id="R4_SINGLE_ACTION",
            grounding_required=False,
            execution_form="SINGLE_STEP",
            freshness_class=FreshnessClass.CURRENT,
            support_target=C0SupportTarget.SOURCE_SUMMARY,
            tenant_scope="test",
            region="",
            data_class="internal",
            acl_roles=(),
            max_k=20,
            max_hops=1,
            max_parent_expansion=2,
            max_child_expansion=2,
            max_refine_attempts=1,
            max_token_context=4000,
            max_source_classes=7,
            max_latency_ms=5000,
            latency_slo=5000,
            token_budget=4000,
            allowed_sources=(),
            disallowed_sources=(),
            allowed_data_classes=("public", "internal"),
            fallback_policy="caveat",
            route_replay_key="test-key",
            policy_hash="test-hash",
            blueprint_hash="test-blueprint",
            c0_policy=None,  # No frozen policy
        )
        plan = L1PlanContract(
            task_spec="test",
            query_spec="test",
            grounding_required=False,
        )

        result = run_preflight(route, plan)

        # Should fail because no frozen policy
        assert result.eligible is False


# =============================================================================
# C0Policy Validation Tests
# =============================================================================

class TestC0PolicyValidation:
    """C0Policy dataclass enforces consistency."""

    def test_c0_policy_evidence_required_incompatible_with_bypass_mode(self):
        """C0Policy raises if evidence_required=True but mode is bypass."""
        with pytest.raises(ValueError, match="incompatible"):
            C0Policy(
                grounding_required=False,
                c0_mode="BYPASS_CACHE_RETURN",
                decision_source="CACHE_TERMINAL",
                evidence_contract_required=True,  # Incompatible!
                bypass_reason="test",
            )

    def test_c0_policy_bypass_mode_requires_reason(self):
        """C0Policy raises if bypass mode but no bypass_reason."""
        with pytest.raises(ValueError, match="requires bypass_reason"):
            C0Policy(
                grounding_required=False,
                c0_mode="BYPASS_CACHE_RETURN",
                decision_source="CACHE_TERMINAL",
                evidence_contract_required=False,
                bypass_reason="",  # Missing!
            )

    def test_c0_policy_retrieve_required_valid(self):
        """C0Policy validates RETRIEVE_REQUIRED mode."""
        policy = C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L1_PLAN_DERIVED",
            evidence_contract_required=True,
            support_target="SOURCE_SUMMARY",
        )
        assert policy.c0_mode == "RETRIEVE_REQUIRED"


# =============================================================================
# Legacy Backward Compatibility Tests
# =============================================================================

class TestBackwardCompatibility:
        """Legacy code without c0_policy still works during transition."""

        def test_pa_boundary_legacy_grounding_required(self):
            """PA still accepts legacy plan_contract.grounding_required if no c0_policy."""
            route_contract = {
                "route_id": "R3_GROUNDED",
                # No c0_policy field
            }
            plan_contract = {"plan_id": "plan-123", "grounding_required": False}

            result = boundary_check(
                plan_contract=plan_contract,
                route_contract=route_contract,
                evidence_contract=None,
            )

            # Should pass (no evidence required per legacy plan)
            assert result.status == BoundaryStatus.PASS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
