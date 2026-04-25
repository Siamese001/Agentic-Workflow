"""Unit tests for v15 L0 RouteContract types.

Covers:
- Closed-vocabulary enums (RouteIdV15, ExecutionFormV15, FreshnessClassV15,
  CachePolicyV15, SupportTargetV15, CostTierV15, ReasonCodeV15,
  ConfidenceClass, WriteAuthority, CapabilityClass, SideEffectClass,
  SandboxClass).
- V15RouteContract validity rules (route↔form coherence, cache_policy
  whitelist, fallback_chain rules, R5-last invariant, write_authority,
  managed-workflow blueprint requirement, TIER_HITL incompatibility).
- HMAC sign / verify (round-trip, idempotency, wrong-key rejection).
- Deterministic route digest (replay invariant, order-independence of
  reason_codes, sensitivity to authority and provenance changes).
- Manifest hash (sensitivity to inputs, idempotency).
- ``load_secret_key_from_env`` failure modes.
- ``_classify_confidence`` mapping.
"""

from __future__ import annotations

import os

import pytest

from agentic_core.L0_routing.types.route_contract_v15 import (
    AuthorityScope,
    CachePolicyV15,
    CapabilityClass,
    ConfidenceClass,
    CostTierV15,
    ExecutionFormV15,
    FallbackEntryV15,
    FreshnessClassV15,
    ReasonCodeV15,
    RouteIdV15,
    RouteSLOV15,
    SafeResponseType,
    SandboxClass,
    SideEffectClass,
    SignaturesV15,
    SupportTargetV15,
    TelemetryKeysV15,
    V15RouteContract,
    V15RouteContractError,
    WriteAuthority,
    _classify_confidence,
    compute_deterministic_route_digest,
    compute_manifest_hash,
    load_secret_key_from_env,
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


@pytest.fixture
def slo_terminal() -> RouteSLOV15:
    return RouteSLOV15(
        max_latency_ms=500,
        max_cost=0.0,
        max_tokens=0,
        max_retrieval_passes=0,
        max_graph_hops=0,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=0,
    )


@pytest.fixture
def slo_r3() -> RouteSLOV15:
    return RouteSLOV15(
        max_latency_ms=15_000,
        max_cost=0.05,
        max_tokens=8_000,
        max_retrieval_passes=2,
        max_graph_hops=2,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=512,
    )


def _telem(digest: str) -> TelemetryKeysV15:
    return TelemetryKeysV15(
        trace_root="trace-root",
        route_span_id="span-1",
        route_digest=digest,
        policy_hash="policy-h",
        blueprint_hash="bp-h",
        snapshot_id="snap-h",
        replay_key="replay-k",
        route_telemetry_event_id="evt-1",
    )


def _sigs(digest: str) -> SignaturesV15:
    return SignaturesV15(
        manifest_hash="mh-1",
        deterministic_route_digest=digest,
        hmac_sig="",
    )


def _r1a(authority: AuthorityScope, slo: RouteSLOV15) -> V15RouteContract:
    """Build a minimal-valid R1A contract."""
    digest = "0" * 64
    return V15RouteContract(
        contract_version="v15.0.0",
        route_id=RouteIdV15.R1A_EXACT_CACHE,
        execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
        confidence_score=1.0,
        confidence_class=ConfidenceClass.EXACT,
        reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
        freshness_class=FreshnessClassV15.SLOW_CHANGING,
        cache_policy=CachePolicyV15.EXACT_ONLY,
        support_target=SupportTargetV15.NONE,
        cost_tier=CostTierV15.TIER_S,
        fallback_chain=(),
        slo=slo,
        authority=authority,
        telemetry_keys=_telem(digest),
        signatures=_sigs(digest),
    )


def _r3(authority: AuthorityScope, slo: RouteSLOV15) -> V15RouteContract:
    """Build a minimal-valid R3 contract with a proper fallback chain."""
    digest = "1" * 64
    return V15RouteContract(
        contract_version="v15.0.0",
        route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
        execution_form=ExecutionFormV15.SINGLE_STEP,
        confidence_score=0.80,
        confidence_class=ConfidenceClass.MEDIUM,
        reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
        freshness_class=FreshnessClassV15.RECENT,
        cache_policy=CachePolicyV15.READ_THROUGH,
        support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
        cost_tier=CostTierV15.TIER_M,
        fallback_chain=(
            FallbackEntryV15(RouteIdV15.R3_SIMPLE_GROUNDED_READ, CostTierV15.TIER_L),
            FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
        ),
        slo=slo,
        authority=authority,
        telemetry_keys=_telem(digest),
        signatures=_sigs(digest),
    )


# ---------------------------------------------------------------------------
# Closed-vocabulary enums
# ---------------------------------------------------------------------------


class TestClosedVocabularies:
    def test_route_id_has_exactly_six_members(self) -> None:
        assert len(RouteIdV15) == 6

    def test_execution_form_has_exactly_three_members(self) -> None:
        assert len(ExecutionFormV15) == 3

    def test_freshness_has_exactly_five_members(self) -> None:
        assert len(FreshnessClassV15) == 5

    def test_cache_policy_has_exactly_five_members(self) -> None:
        assert len(CachePolicyV15) == 5

    def test_cost_tier_has_tier_hitl(self) -> None:
        assert CostTierV15.TIER_HITL.value == "TIER_HITL"

    def test_support_target_has_v15_action_grounding(self) -> None:
        assert SupportTargetV15.ACTION_ARGUMENT_GROUNDING.value == "ACTION_ARGUMENT_GROUNDING"

    def test_reason_code_count(self) -> None:
        # 19 codes per v15 schema
        assert len(ReasonCodeV15) == 19

    def test_write_authority_default_is_none_until_uwg(self) -> None:
        assert WriteAuthority.NONE_UNTIL_UWG.value == "NONE_UNTIL_UWG"


# ---------------------------------------------------------------------------
# AuthorityScope validation
# ---------------------------------------------------------------------------


class TestAuthorityScope:
    def test_construction_ok(self, authority: AuthorityScope) -> None:
        assert authority.write_authority == WriteAuthority.NONE_UNTIL_UWG

    def test_empty_tenant_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="tenant_scope"):
            AuthorityScope(
                tenant_scope="",
                acl_scope=(),
                region_scope="us-east-1",
                capability_class=CapabilityClass.READ_ONLY,
                side_effect_class=SideEffectClass.PURE,
                sandbox_class=SandboxClass.NO_SANDBOX,
            )

    def test_acl_scope_max_length(self) -> None:
        with pytest.raises(V15RouteContractError, match="acl_scope"):
            AuthorityScope(
                tenant_scope="t",
                acl_scope=tuple(f"acl-{i}" for i in range(65)),
                region_scope="r",
                capability_class=CapabilityClass.READ_ONLY,
                side_effect_class=SideEffectClass.PURE,
                sandbox_class=SandboxClass.NO_SANDBOX,
            )


# ---------------------------------------------------------------------------
# RouteSLOV15 validation
# ---------------------------------------------------------------------------


class TestRouteSLOV15:
    def test_negative_latency_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="max_latency_ms"):
            RouteSLOV15(
                max_latency_ms=-1,
                max_cost=0.0,
                max_tokens=0,
                max_retrieval_passes=0,
                max_graph_hops=0,
                max_tool_calls=0,
                max_iterations=0,
                reserve_for_exit_eval=0,
            )

    def test_nan_cost_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="max_cost"):
            RouteSLOV15(
                max_latency_ms=100,
                max_cost=float("nan"),
                max_tokens=0,
                max_retrieval_passes=0,
                max_graph_hops=0,
                max_tool_calls=0,
                max_iterations=0,
                reserve_for_exit_eval=0,
            )

    def test_inf_cost_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="max_cost"):
            RouteSLOV15(
                max_latency_ms=100,
                max_cost=float("inf"),
                max_tokens=0,
                max_retrieval_passes=0,
                max_graph_hops=0,
                max_tool_calls=0,
                max_iterations=0,
                reserve_for_exit_eval=0,
            )

    def test_ceiling_breach_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="max_iterations"):
            RouteSLOV15(
                max_latency_ms=100,
                max_cost=0.0,
                max_tokens=0,
                max_retrieval_passes=0,
                max_graph_hops=0,
                max_tool_calls=0,
                max_iterations=99_999,
                reserve_for_exit_eval=0,
            )

    def test_bool_rejected_as_int_field(self) -> None:
        # bool is technically int in Python — explicit guard required.
        with pytest.raises(V15RouteContractError, match="max_tokens"):
            RouteSLOV15(
                max_latency_ms=100,
                max_cost=0.0,
                max_tokens=True,  # type: ignore[arg-type]
                max_retrieval_passes=0,
                max_graph_hops=0,
                max_tool_calls=0,
                max_iterations=0,
                reserve_for_exit_eval=0,
            )


# ---------------------------------------------------------------------------
# V15RouteContract — coherence rules
# ---------------------------------------------------------------------------


class TestRouteFormCoherence:
    def test_r1a_with_single_step_form_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "x" * 64
        with pytest.raises(V15RouteContractError, match="execution_form"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_r3_with_terminal_form_rejected(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "y" * 64
        with pytest.raises(V15RouteContractError, match="execution_form"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestCachePolicyWhitelist:
    def test_r1a_must_be_exact_only(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "z" * 64
        with pytest.raises(V15RouteContractError, match="cache_policy"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.SEMANTIC_OK,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_r4_with_exact_only_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "a" * 64
        with pytest.raises(V15RouteContractError, match="cache_policy"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R4_SINGLE_ACTION,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.ACTION_LOW_RISK.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestFallbackChainRules:
    def test_non_terminal_requires_chain(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "b" * 64
        with pytest.raises(V15RouteContractError, match="non-terminal"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_r5_must_be_last_in_chain(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "c" * 64
        with pytest.raises(V15RouteContractError, match="last entry"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(
                    FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
                    FallbackEntryV15(
                        RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                        CostTierV15.TIER_L,
                    ),
                ),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_self_referential_chain_rejected(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "d" * 64
        with pytest.raises(V15RouteContractError, match="self-referential"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(
                    FallbackEntryV15(
                        RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                        CostTierV15.TIER_M,
                    ),
                    FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
                ),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_r5_terminal_must_have_empty_chain(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "e" * 64
        with pytest.raises(V15RouteContractError, match="empty fallback_chain"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R5_FALLBACK,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=0.0,
                confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
                reason_codes=(ReasonCodeV15.FALLBACK_SELECTED.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.NO_CACHE,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(
                    FallbackEntryV15(
                        RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                        CostTierV15.TIER_M,
                    ),
                ),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_r5_must_appear_exactly_once(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "f" * 64
        with pytest.raises(V15RouteContractError, match="exactly once"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.8,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(
                    FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_M),
                    FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
                ),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestWriteAuthority:
    def test_l0_must_emit_none_until_uwg(
        self,
        slo_terminal: RouteSLOV15,
    ) -> None:
        bad_authority = AuthorityScope(
            tenant_scope="t",
            acl_scope=("read",),
            region_scope="r",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
            write_authority=WriteAuthority.UWG_CLEARED,
        )
        digest = "g" * 64
        with pytest.raises(V15RouteContractError, match="NONE_UNTIL_UWG"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=bad_authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestManagedWorkflowGuards:
    def test_managed_route_requires_blueprint(
        self,
        authority: AuthorityScope,
    ) -> None:
        slo = RouteSLOV15(
            max_latency_ms=120_000,
            max_cost=1.0,
            max_tokens=64_000,
            max_retrieval_passes=4,
            max_graph_hops=4,
            max_tool_calls=4,
            max_iterations=4,
            reserve_for_exit_eval=2_048,
        )
        digest = "h" * 64
        with pytest.raises(V15RouteContractError, match="workflow_blueprint_id"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3R4_MANAGED_WORKFLOW,
                execution_form=ExecutionFormV15.MANAGED_WORKFLOW,
                confidence_score=0.7,
                confidence_class=ConfidenceClass.MEDIUM,
                reason_codes=(ReasonCodeV15.MULTI_STEP_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_L,
                fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
                slo=slo,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
                workflow_blueprint_id=None,
            )


class TestTierHITLRules:
    def test_tier_hitl_rejected_on_r1a(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "i" * 64
        with pytest.raises(V15RouteContractError, match="TIER_HITL"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_HITL,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestR5RequiresReason:
    def test_r5_with_empty_reasons_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "j" * 64
        with pytest.raises(V15RouteContractError, match="reason_code"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R5_FALLBACK,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=0.0,
                confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
                reason_codes=(),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.NO_CACHE,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestSafeResponseType:
    """v15 §R5 CONTRACT — safe_response_type required on R5, forbidden elsewhere."""

    def test_r5_without_safe_response_type_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "p" * 64
        with pytest.raises(V15RouteContractError, match="safe_response_type"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R5_FALLBACK,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=0.0,
                confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
                reason_codes=(ReasonCodeV15.FALLBACK_SELECTED.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.NO_CACHE,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
                # safe_response_type omitted -> rejection
            )

    @pytest.mark.parametrize(
        "srt",
        [
            SafeResponseType.CLARIFY,
            SafeResponseType.ABSTAIN,
            SafeResponseType.REFUSE,
            SafeResponseType.SAFE_PARTIAL,
        ],
    )
    def test_r5_accepts_all_four_categories(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
        srt: SafeResponseType,
    ) -> None:
        digest = "q" * 64
        contract = V15RouteContract(
            contract_version="v15.0.0",
            route_id=RouteIdV15.R5_FALLBACK,
            execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
            confidence_score=0.0,
            confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
            reason_codes=(ReasonCodeV15.FALLBACK_SELECTED.value,),
            freshness_class=FreshnessClassV15.SLOW_CHANGING,
            cache_policy=CachePolicyV15.NO_CACHE,
            support_target=SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_S,
            fallback_chain=(),
            slo=slo_terminal,
            authority=authority,
            telemetry_keys=_telem(digest),
            signatures=_sigs(digest),
            safe_response_type=srt,
        )
        assert contract.safe_response_type is srt

    def test_safe_response_type_rejected_on_non_r5_route(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "r" * 64
        with pytest.raises(V15RouteContractError, match="safe_response_type"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
                safe_response_type=SafeResponseType.ABSTAIN,  # forbidden on R1A
            )


class TestReasonCodeVocabulary:
    def test_unknown_reason_code_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        digest = "k" * 64
        with pytest.raises(V15RouteContractError, match="vocabulary"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R1A_EXACT_CACHE,
                execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
                confidence_score=1.0,
                confidence_class=ConfidenceClass.EXACT,
                reason_codes=("not_in_vocabulary",),
                freshness_class=FreshnessClassV15.SLOW_CHANGING,
                cache_policy=CachePolicyV15.EXACT_ONLY,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                fallback_chain=(),
                slo=slo_terminal,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )


class TestConfidenceClassDerivation:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (1.0, ConfidenceClass.EXACT),
            (0.99, ConfidenceClass.HIGH),
            (0.85, ConfidenceClass.HIGH),
            (0.70, ConfidenceClass.MEDIUM),
            (0.45, ConfidenceClass.LOW),
            (0.10, ConfidenceClass.INSUFFICIENT_SUPPORT),
            (0.0, ConfidenceClass.INSUFFICIENT_SUPPORT),
        ],
    )
    def test_classification(self, score: float, expected: ConfidenceClass) -> None:
        assert _classify_confidence(score) is expected

    def test_class_must_match_score(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        digest = "m" * 64
        with pytest.raises(V15RouteContractError, match="confidence_class"):
            V15RouteContract(
                contract_version="v15.0.0",
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                confidence_score=0.95,
                confidence_class=ConfidenceClass.LOW,  # disagrees
                reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
                freshness_class=FreshnessClassV15.RECENT,
                cache_policy=CachePolicyV15.READ_THROUGH,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
                slo=slo_r3,
                authority=authority,
                telemetry_keys=_telem(digest),
                signatures=_sigs(digest),
            )

    def test_unsafe_class_bypasses_score_check(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        # UNSAFE is set explicitly by the policy block path; score may be
        # anything in [0,1].
        digest = "n" * 64
        contract = V15RouteContract(
            contract_version="v15.0.0",
            route_id=RouteIdV15.R5_FALLBACK,
            execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
            confidence_score=0.99,
            confidence_class=ConfidenceClass.UNSAFE,
            reason_codes=(
                ReasonCodeV15.POLICY_BLOCK.value,
                ReasonCodeV15.FALLBACK_SELECTED.value,
            ),
            freshness_class=FreshnessClassV15.SLOW_CHANGING,
            cache_policy=CachePolicyV15.NO_CACHE,
            support_target=SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_S,
            fallback_chain=(),
            slo=slo_terminal,
            authority=authority,
            telemetry_keys=_telem(digest),
            signatures=_sigs(digest),
            safe_response_type=SafeResponseType.REFUSE,
        )
        assert contract.confidence_class is ConfidenceClass.UNSAFE


# ---------------------------------------------------------------------------
# HMAC sign / verify
# ---------------------------------------------------------------------------


class TestHMACSignVerify:
    def test_sign_then_verify(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        contract = _r1a(authority, slo_terminal)
        secret = b"k" * 32
        signed = contract.sign(secret)
        assert signed.signatures.hmac_sig != ""
        assert signed.verify(secret) is True

    def test_verify_with_wrong_key(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        signed = _r1a(authority, slo_terminal).sign(b"k" * 32)
        assert signed.verify(b"x" * 32) is False

    def test_unsigned_verify_returns_false(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        assert _r1a(authority, slo_terminal).verify(b"k" * 32) is False

    def test_empty_secret_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        contract = _r1a(authority, slo_terminal)
        with pytest.raises(V15RouteContractError, match="non-empty"):
            contract.sign(b"")

    def test_non_bytes_secret_rejected(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        contract = _r1a(authority, slo_terminal)
        with pytest.raises(V15RouteContractError, match="bytes"):
            contract.sign("not-bytes")  # type: ignore[arg-type]

    def test_sign_idempotent_for_same_payload(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        contract = _r1a(authority, slo_terminal)
        secret = b"k" * 32
        sig1 = contract.sign(secret).signatures.hmac_sig
        sig2 = contract.sign(secret).signatures.hmac_sig
        assert sig1 == sig2


# ---------------------------------------------------------------------------
# Deterministic route digest — replay invariant
# ---------------------------------------------------------------------------


class TestDeterministicDigest:
    def _digest(
        self,
        authority: AuthorityScope,
        *,
        reason_codes: tuple[str, ...] = (ReasonCodeV15.GROUNDING_REQUIRED.value,),
        snapshot_id: str = "snap-1",
        policy_hash: str = "policy-1",
        blueprint_hash: str = "bp-1",
    ) -> str:
        return compute_deterministic_route_digest(
            route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
            execution_form=ExecutionFormV15.SINGLE_STEP,
            cache_policy=CachePolicyV15.READ_THROUGH,
            freshness_class=FreshnessClassV15.RECENT,
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
            cost_tier=CostTierV15.TIER_M,
            reason_codes=reason_codes,
            fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
            authority=authority,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            snapshot_id=snapshot_id,
        )

    def test_same_inputs_same_digest(self, authority: AuthorityScope) -> None:
        d1 = self._digest(authority)
        d2 = self._digest(authority)
        assert d1 == d2
        assert len(d1) == 64

    def test_reason_code_order_independent(
        self,
        authority: AuthorityScope,
    ) -> None:
        d1 = self._digest(
            authority,
            reason_codes=(
                ReasonCodeV15.GROUNDING_REQUIRED.value,
                ReasonCodeV15.SUPPORT_WEAK.value,
            ),
        )
        d2 = self._digest(
            authority,
            reason_codes=(
                ReasonCodeV15.SUPPORT_WEAK.value,
                ReasonCodeV15.GROUNDING_REQUIRED.value,
            ),
        )
        assert d1 == d2

    def test_snapshot_change_changes_digest(
        self,
        authority: AuthorityScope,
    ) -> None:
        d1 = self._digest(authority, snapshot_id="snap-1")
        d2 = self._digest(authority, snapshot_id="snap-2")
        assert d1 != d2

    def test_policy_change_changes_digest(
        self,
        authority: AuthorityScope,
    ) -> None:
        d1 = self._digest(authority, policy_hash="p-1")
        d2 = self._digest(authority, policy_hash="p-2")
        assert d1 != d2

    def test_authority_change_changes_digest(
        self,
        authority: AuthorityScope,
    ) -> None:
        other = AuthorityScope(
            tenant_scope="tenant-b",
            acl_scope=("read",),
            region_scope="us-east-1",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
        )
        d1 = self._digest(authority)
        d2 = self._digest(other)
        assert d1 != d2

    def test_acl_order_independent(self) -> None:
        a1 = AuthorityScope(
            tenant_scope="t",
            acl_scope=("read", "list"),
            region_scope="r",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
        )
        a2 = AuthorityScope(
            tenant_scope="t",
            acl_scope=("list", "read"),
            region_scope="r",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
        )
        d1 = self._digest(a1)
        d2 = self._digest(a2)
        assert d1 == d2


# ---------------------------------------------------------------------------
# Manifest hash
# ---------------------------------------------------------------------------


class TestManifestHash:
    def test_idempotent(self) -> None:
        m1 = compute_manifest_hash(
            contract_version="v15.0.0",
            route_digest="d" * 64,
            policy_hash="p",
            blueprint_hash="b",
            snapshot_id="s",
        )
        m2 = compute_manifest_hash(
            contract_version="v15.0.0",
            route_digest="d" * 64,
            policy_hash="p",
            blueprint_hash="b",
            snapshot_id="s",
        )
        assert m1 == m2
        assert len(m1) == 64

    def test_changes_with_input(self) -> None:
        m1 = compute_manifest_hash(
            contract_version="v15.0.0",
            route_digest="a" * 64,
            policy_hash="p",
            blueprint_hash="b",
            snapshot_id="s",
        )
        m2 = compute_manifest_hash(
            contract_version="v15.0.0",
            route_digest="b" * 64,
            policy_hash="p",
            blueprint_hash="b",
            snapshot_id="s",
        )
        assert m1 != m2

    def test_empty_input_rejected(self) -> None:
        with pytest.raises(V15RouteContractError):
            compute_manifest_hash(
                contract_version="",
                route_digest="d" * 64,
                policy_hash="p",
                blueprint_hash="b",
                snapshot_id="s",
            )


# ---------------------------------------------------------------------------
# load_secret_key_from_env
# ---------------------------------------------------------------------------


class TestLoadSecretKey:
    def test_unset_var_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AGENTIC_V15_ROUTE_HMAC_KEY", raising=False)
        with pytest.raises(V15RouteContractError, match="unset or empty"):
            load_secret_key_from_env()

    def test_short_key_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AGENTIC_V15_ROUTE_HMAC_KEY", "short")
        with pytest.raises(V15RouteContractError, match="too short"):
            load_secret_key_from_env()

    def test_whitespace_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(
            "AGENTIC_V15_ROUTE_HMAC_KEY",
            "  " + "k" * 32 + "  \n",
        )
        key = load_secret_key_from_env()
        assert len(key) == 32

    def test_custom_var_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_KEY", "k" * 24)
        key = load_secret_key_from_env(env_var="MY_KEY")
        assert len(key) == 24


# ---------------------------------------------------------------------------
# Smoke: full contract construction
# ---------------------------------------------------------------------------


class TestSmokeFullConstruction:
    def test_r1a_construct_sign_verify(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        contract = _r1a(authority, slo_terminal)
        signed = contract.sign(b"k" * 32)
        assert signed.verify(b"k" * 32)
        # sanity — round-trip preserves payload
        assert signed.route_id == RouteIdV15.R1A_EXACT_CACHE
        assert signed.confidence_class == ConfidenceClass.EXACT

    def test_r3_full_chain(
        self,
        authority: AuthorityScope,
        slo_r3: RouteSLOV15,
    ) -> None:
        contract = _r3(authority, slo_r3)
        assert contract.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK
        assert contract.execution_form == ExecutionFormV15.SINGLE_STEP

    def test_canonical_json_excludes_hmac(
        self,
        authority: AuthorityScope,
        slo_terminal: RouteSLOV15,
    ) -> None:
        signed = _r1a(authority, slo_terminal).sign(b"k" * 32)
        # Even though hmac_sig is set, canonical_json must exclude it.
        canon = signed.canonical_json()
        assert b"hmac_sig" not in canon


# Sanity that we can import os without it being unused (linter-friendly).
assert os.path is not None
