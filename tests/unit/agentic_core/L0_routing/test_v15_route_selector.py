"""Unit tests for v15 §FIXED DECISION ORDER selector.

Covers:
- Decision order steps 0-7 (each step in isolation).
- Cold-start rule (low confidence + grounding -> R3; underspecified -> R5).
- Fallback chain integrity (R5 always last, no self-reference).
- Replay determinism (same signals -> identical digest).
- Managed-workflow blueprint requirement.
- Semantic-cache freshness rejection.
- HITL pause point passthrough.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.v15_route_selector import (
    COLD_START_CONFIDENCE_THRESHOLD,
    RouteSignalsV15,
    select_route_v15,
)
from agentic_core.L0_routing.types.route_contract_v15 import (
    AuthorityScope,
    CachePolicyV15,
    CapabilityClass,
    ConfidenceClass,
    CostTierV15,
    ExecutionFormV15,
    FreshnessClassV15,
    ReasonCodeV15,
    RouteIdV15,
    SandboxClass,
    SideEffectClass,
    SupportTargetV15,
    V15RouteContractError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def authority() -> AuthorityScope:
    return AuthorityScope(
        tenant_scope="tenant-a",
        acl_scope=("read",),
        region_scope="us-east-1",
        capability_class=CapabilityClass.READ_ONLY,
        side_effect_class=SideEffectClass.PURE,
        sandbox_class=SandboxClass.NO_SANDBOX,
    )


def _make_signals(authority: AuthorityScope, **overrides: object) -> RouteSignalsV15:
    """Build a baseline signal bundle; tests override specific fields."""
    base: dict[str, object] = {
        "ingress_ok": True,
        "authority": authority,
        "policy_hash": "policy-1",
        "blueprint_hash": "bp-1",
        "snapshot_id": "snap-1",
        "trace_root": "trace-1",
        "route_span_id": "span-1",
        "replay_key": "replay-1",
        "route_telemetry_event_id": "evt-1",
        "classifier_confidence": 0.80,
        "exact_cache_hit": False,
        "semantic_cache_hit": False,
        "high_risk_action": False,
        "low_risk_reversible_action": False,
        "action_args_need_grounding": False,
        "grounding_required": False,
        "support_target": SupportTargetV15.NONE,
        "multi_step_required": False,
        "cross_step_contract_change": False,
        "parallel_safe_shards": False,
        "iterative_refinement_needed": False,
        "needs_hitl_pause": False,
        "freshness_class": FreshnessClassV15.SLOW_CHANGING,
        "underspecified": False,
        "unsafe": False,
        "hitl_pause_points": (),
        "workflow_blueprint_id": None,
        "base_contract_id": "contract-1",
    }
    base.update(overrides)
    return RouteSignalsV15(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Step 0 — ingress reject / unsafe
# ---------------------------------------------------------------------------


class TestStep0:
    def test_ingress_reject_yields_r5_scope_fail(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(_make_signals(authority, ingress_ok=False))
        assert c.route_id == RouteIdV15.R5_FALLBACK
        assert ReasonCodeV15.SCOPE_FAIL.value in c.reason_codes
        assert c.confidence_class == ConfidenceClass.UNSAFE
        assert c.execution_form == ExecutionFormV15.TERMINAL_SHORTCIRCUIT
        assert c.fallback_chain == ()

    def test_unsafe_yields_r5_policy_block(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(_make_signals(authority, unsafe=True))
        assert c.route_id == RouteIdV15.R5_FALLBACK
        assert ReasonCodeV15.POLICY_BLOCK.value in c.reason_codes


# ---------------------------------------------------------------------------
# Step 1 — exact cache
# ---------------------------------------------------------------------------


class TestStep1:
    def test_exact_cache_hit(self, authority: AuthorityScope) -> None:
        c = select_route_v15(_make_signals(authority, exact_cache_hit=True))
        assert c.route_id == RouteIdV15.R1A_EXACT_CACHE
        assert c.cache_policy == CachePolicyV15.EXACT_ONLY
        assert c.execution_form == ExecutionFormV15.TERMINAL_SHORTCIRCUIT
        assert c.confidence_class == ConfidenceClass.EXACT
        assert c.confidence_score == 1.0
        assert ReasonCodeV15.EXACT_CACHE_HIT.value in c.reason_codes

    def test_exact_cache_dominates_other_signals(
        self,
        authority: AuthorityScope,
    ) -> None:
        # Even with grounding/multi_step set, exact cache wins.
        c = select_route_v15(
            _make_signals(
                authority,
                exact_cache_hit=True,
                grounding_required=True,
                multi_step_required=True,
            ),
        )
        assert c.route_id == RouteIdV15.R1A_EXACT_CACHE


# ---------------------------------------------------------------------------
# Step 2 — semantic cache
# ---------------------------------------------------------------------------


class TestStep2:
    def test_semantic_cache_hit(self, authority: AuthorityScope) -> None:
        c = select_route_v15(_make_signals(authority, semantic_cache_hit=True))
        assert c.route_id == RouteIdV15.R1B_SEMANTIC_CACHE
        assert c.cache_policy == CachePolicyV15.SEMANTIC_OK
        assert ReasonCodeV15.SEMANTIC_CACHE_HIT.value in c.reason_codes

    def test_semantic_cache_rejected_for_live_freshness(
        self,
        authority: AuthorityScope,
    ) -> None:
        # LIVE freshness must NOT short-circuit through R1B per v15 §R1B GUARDS.
        c = select_route_v15(
            _make_signals(
                authority,
                semantic_cache_hit=True,
                freshness_class=FreshnessClassV15.LIVE,
                grounding_required=True,
            ),
        )
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ

    def test_semantic_cache_rejected_for_current_freshness(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                semantic_cache_hit=True,
                freshness_class=FreshnessClassV15.CURRENT,
                grounding_required=True,
            ),
        )
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ


# ---------------------------------------------------------------------------
# Step 3 — HITL high-risk
# ---------------------------------------------------------------------------


class TestStep3HITL:
    def test_high_risk_yields_managed_with_tier_hitl(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                high_risk_action=True,
                workflow_blueprint_id="bp-irreversible",
            ),
        )
        assert c.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW
        assert c.cost_tier == CostTierV15.TIER_HITL
        assert ReasonCodeV15.HITL_REQUIRED.value in c.reason_codes
        assert ReasonCodeV15.ACTION_HIGH_RISK.value in c.reason_codes
        assert "HITL_PRECOMMIT" in c.hitl_pause_points

    def test_high_risk_without_blueprint_raises(
        self,
        authority: AuthorityScope,
    ) -> None:
        with pytest.raises(V15RouteContractError, match="workflow_blueprint_id"):
            select_route_v15(_make_signals(authority, high_risk_action=True))


# ---------------------------------------------------------------------------
# Step 4 — low-risk reversible action (R4)
# ---------------------------------------------------------------------------


class TestStep4Action:
    def test_low_risk_action_yields_r4(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                low_risk_reversible_action=True,
                classifier_confidence=0.90,
            ),
        )
        assert c.route_id == RouteIdV15.R4_SINGLE_ACTION
        assert c.execution_form == ExecutionFormV15.SINGLE_STEP
        assert c.cache_policy == CachePolicyV15.NO_CACHE
        assert ReasonCodeV15.ACTION_LOW_RISK.value in c.reason_codes
        # Fallback must end with R5
        assert c.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK

    def test_action_with_arg_grounding_sets_support_target(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                low_risk_reversible_action=True,
                action_args_need_grounding=True,
                classifier_confidence=0.90,
            ),
        )
        assert c.support_target == SupportTargetV15.ACTION_ARGUMENT_GROUNDING


# ---------------------------------------------------------------------------
# Step 5 — R3 grounded read
# ---------------------------------------------------------------------------


class TestStep5GroundedRead:
    def test_grounded_read_no_workflow_yields_r3(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                grounding_required=True,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ
        assert c.execution_form == ExecutionFormV15.SINGLE_STEP
        assert c.cache_policy == CachePolicyV15.READ_THROUGH
        assert c.support_target == SupportTargetV15.SOURCE_BACKED_SUMMARY
        assert ReasonCodeV15.GROUNDING_REQUIRED.value in c.reason_codes

    def test_freshness_required_added_for_current(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                grounding_required=True,
                freshness_class=FreshnessClassV15.CURRENT,
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ
        assert ReasonCodeV15.FRESHNESS_REQUIRED.value in c.reason_codes

    def test_default_support_target_when_unset(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                grounding_required=True,
                support_target=SupportTargetV15.NONE,
                classifier_confidence=0.80,
            ),
        )
        # Selector substitutes SOURCE_BACKED_SUMMARY as the safe default.
        assert c.support_target == SupportTargetV15.SOURCE_BACKED_SUMMARY


# ---------------------------------------------------------------------------
# Step 6 — managed workflow
# ---------------------------------------------------------------------------


class TestStep6ManagedWorkflow:
    def test_multi_step_yields_managed(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                multi_step_required=True,
                workflow_blueprint_id="bp-multi",
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW
        assert c.execution_form == ExecutionFormV15.MANAGED_WORKFLOW
        assert ReasonCodeV15.MULTI_STEP_REQUIRED.value in c.reason_codes

    def test_cross_step_contract_change_adds_dep_branching(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                multi_step_required=True,
                cross_step_contract_change=True,
                workflow_blueprint_id="bp-multi",
                classifier_confidence=0.80,
            ),
        )
        assert ReasonCodeV15.DEPENDENCY_BRANCHING_REQUIRED.value in c.reason_codes

    def test_grounding_in_workflow_adds_reason(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                multi_step_required=True,
                grounding_required=True,
                support_target=SupportTargetV15.RANKED_CAUSE,
                workflow_blueprint_id="bp-multi",
                classifier_confidence=0.80,
            ),
        )
        assert ReasonCodeV15.GROUNDING_REQUIRED.value in c.reason_codes
        assert c.cache_policy == CachePolicyV15.READ_THROUGH
        assert c.support_target == SupportTargetV15.RANKED_CAUSE

    def test_hitl_pause_in_workflow(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                multi_step_required=True,
                needs_hitl_pause=True,
                hitl_pause_points=("HITL_REVIEW",),
                workflow_blueprint_id="bp-multi",
                classifier_confidence=0.80,
            ),
        )
        assert ReasonCodeV15.HITL_REQUIRED.value in c.reason_codes
        assert "HITL_REVIEW" in c.hitl_pause_points

    def test_iterative_refinement_yields_managed(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                iterative_refinement_needed=True,
                workflow_blueprint_id="bp-iter",
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW

    def test_parallel_shards_yield_managed(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                parallel_safe_shards=True,
                workflow_blueprint_id="bp-par",
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW


# ---------------------------------------------------------------------------
# Step 7 — terminal R5 fallback
# ---------------------------------------------------------------------------


class TestStep7Fallback:
    def test_no_path_yields_r5(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                # No actionable signals
                classifier_confidence=0.80,
            ),
        )
        assert c.route_id == RouteIdV15.R5_FALLBACK
        assert ReasonCodeV15.FALLBACK_SELECTED.value in c.reason_codes


# ---------------------------------------------------------------------------
# Cold-start rule
# ---------------------------------------------------------------------------


class TestColdStartRule:
    def test_low_confidence_underspecified_yields_r5_clarify(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                classifier_confidence=COLD_START_CONFIDENCE_THRESHOLD - 0.1,
                underspecified=True,
            ),
        )
        assert c.route_id == RouteIdV15.R5_FALLBACK
        assert ReasonCodeV15.SUPPORT_WEAK.value in c.reason_codes

    def test_low_confidence_with_grounding_yields_r3(
        self,
        authority: AuthorityScope,
    ) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                classifier_confidence=COLD_START_CONFIDENCE_THRESHOLD - 0.1,
                grounding_required=True,
                # multi_step is False, so cold-start downgrades to R3
            ),
        )
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ
        assert ReasonCodeV15.SUPPORT_WEAK.value in c.reason_codes

    def test_low_confidence_blocks_action_routing(
        self,
        authority: AuthorityScope,
    ) -> None:
        # Cold-start refuses to dispatch action when grounding is needed.
        c = select_route_v15(
            _make_signals(
                authority,
                classifier_confidence=COLD_START_CONFIDENCE_THRESHOLD - 0.1,
                grounding_required=True,
                low_risk_reversible_action=True,
            ),
        )
        # Cold-start picks R3 over R4 when grounding is needed.
        assert c.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ


# ---------------------------------------------------------------------------
# Replay determinism
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    def test_same_signals_same_digest(
        self,
        authority: AuthorityScope,
    ) -> None:
        s1 = _make_signals(
            authority,
            grounding_required=True,
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
            classifier_confidence=0.80,
        )
        s2 = _make_signals(
            authority,
            grounding_required=True,
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
            classifier_confidence=0.80,
        )
        c1 = select_route_v15(s1)
        c2 = select_route_v15(s2)
        assert (
            c1.signatures.deterministic_route_digest
            == c2.signatures.deterministic_route_digest
        )

    def test_different_snapshot_different_digest(
        self,
        authority: AuthorityScope,
    ) -> None:
        s1 = _make_signals(
            authority,
            grounding_required=True,
            classifier_confidence=0.80,
            snapshot_id="snap-A",
        )
        s2 = _make_signals(
            authority,
            grounding_required=True,
            classifier_confidence=0.80,
            snapshot_id="snap-B",
        )
        c1 = select_route_v15(s1)
        c2 = select_route_v15(s2)
        assert (
            c1.signatures.deterministic_route_digest
            != c2.signatures.deterministic_route_digest
        )


# ---------------------------------------------------------------------------
# Validation guards on RouteSignalsV15
# ---------------------------------------------------------------------------


class TestSignalValidation:
    def test_confidence_out_of_range_rejected(
        self,
        authority: AuthorityScope,
    ) -> None:
        with pytest.raises(V15RouteContractError, match="classifier_confidence"):
            select_route_v15(
                _make_signals(authority, classifier_confidence=1.5),
            )

    def test_managed_route_requires_blueprint(
        self,
        authority: AuthorityScope,
    ) -> None:
        with pytest.raises(V15RouteContractError, match="workflow_blueprint_id"):
            select_route_v15(
                _make_signals(
                    authority,
                    multi_step_required=True,
                    workflow_blueprint_id=None,
                    classifier_confidence=0.80,
                ),
            )


# ---------------------------------------------------------------------------
# Fallback chain integrity (every path)
# ---------------------------------------------------------------------------


class TestFallbackChainIntegrity:
    def test_r3_chain_ends_with_r5(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                grounding_required=True,
                classifier_confidence=0.80,
            ),
        )
        assert c.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK

    def test_r4_chain_ends_with_r5(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                low_risk_reversible_action=True,
                classifier_confidence=0.90,
            ),
        )
        assert c.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK

    def test_managed_chain_ends_with_r5(self, authority: AuthorityScope) -> None:
        c = select_route_v15(
            _make_signals(
                authority,
                multi_step_required=True,
                workflow_blueprint_id="bp",
                classifier_confidence=0.80,
            ),
        )
        assert c.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK

    def test_terminal_routes_have_empty_chain(
        self,
        authority: AuthorityScope,
    ) -> None:
        for sig_overrides in (
            {"exact_cache_hit": True},
            {"semantic_cache_hit": True},
            {"unsafe": True},
            {"ingress_ok": False},
        ):
            c = select_route_v15(_make_signals(authority, **sig_overrides))
            assert c.fallback_chain == ()
