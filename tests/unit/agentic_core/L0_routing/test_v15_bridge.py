"""Unit tests for the v12 ↔ v15 RouteContract bridge.

Covers:
- Forward translation: every v12 RouteId mapped, fields preserved.
- v15 invariants enforced on output (R5-last, write_authority, etc.).
- Reverse translation: v15 -> v12 round-trip preserves identity.
- Error handling: missing blueprint id when target is managed workflow.
- Lossy fields (R-PAR / R-LOOP / R-CASC -> R3R4_MANAGED_WORKFLOW).
- TIER_HITL handling for R-HITL.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CachePolicy as CachePolicyV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CostTier as CostTierV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    ExecutionForm as ExecutionFormV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    FallbackEntry as FallbackEntryV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    FreshnessClass as FreshnessClassV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    RouteId as RouteIdV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    RouteSLO as RouteSLOV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    TenantScope as TenantScopeV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    V12RouteAnnex,
)
from agentic_core.L0_routing.types.route_contract_v15 import (
    CapabilityClass,
    CostTierV15,
    ExecutionFormV15,
    FreshnessClassV15,
    ReasonCodeV15,
    RouteIdV15,
    SandboxClass,
    SideEffectClass,
    SupportTargetV15,
    V15RouteContractError,
    WriteAuthority,
)
from agentic_core.L0_routing.types.route_contract_v15_bridge import (
    v12_to_v15,
    v15_to_v12,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tenant_v12() -> TenantScopeV12:
    return TenantScopeV12(
        tenant_id="tenant-a",
        region="us-east-1",
        acl_bounds=("read",),
    )


@pytest.fixture
def slo_v12() -> RouteSLOV12:
    return RouteSLOV12(
        latency_budget_ms=15_000,
        token_budget_in=4_000,
        token_budget_out=4_000,
        cost_cap_usd=0.05,
    )


def _v12_annex(
    *,
    route_id: RouteIdV12,
    tenant: TenantScopeV12,
    slo: RouteSLOV12,
    cost_tier: CostTierV12 = CostTierV12.TIER_M,
    cache_policy: CachePolicyV12 = CachePolicyV12.NO_CACHE,
    execution_form: ExecutionFormV12 = ExecutionFormV12.SINGLE_STEP,
    fallback_chain: tuple[FallbackEntryV12, ...] = (),
    reason_codes: tuple[str, ...] = (),
    freshness: FreshnessClassV12 = FreshnessClassV12.STABLE,
) -> V12RouteAnnex:
    return V12RouteAnnex(
        contract_version="1.0.0",
        base_contract_id="c1",
        route_id=route_id,
        confidence=0.85,
        reason_codes=reason_codes,
        freshness_class=freshness,
        cache_policy=cache_policy,
        execution_form=execution_form,
        cost_tier=cost_tier,
        fallback_chain=fallback_chain,
        slo=slo,
        telemetry_keys=(),
        tenant_scope=tenant,
        hmac_sig="",
    )


# ---------------------------------------------------------------------------
# Forward translation: v12 -> v15
# ---------------------------------------------------------------------------


class TestV12ToV15Forward:
    def test_r1a_maps_to_r1a_exact_cache(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R1A,
            tenant=tenant_v12,
            slo=slo_v12,
            cost_tier=CostTierV12.TIER_S,
            cache_policy=CachePolicyV12.EXACT_ONLY,
            execution_form=ExecutionFormV12.TERMINAL_SHORTCIRCUIT,
            reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
        )
        assert v15.route_id == RouteIdV15.R1A_EXACT_CACHE
        assert v15.execution_form == ExecutionFormV15.TERMINAL_SHORTCIRCUIT
        assert v15.fallback_chain == ()
        assert v15.authority.write_authority == WriteAuthority.NONE_UNTIL_UWG
        assert v15.signatures.deterministic_route_digest != ""

    def test_r3_grounded_maps(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R3_GROUNDED,
            tenant=tenant_v12,
            slo=slo_v12,
            cache_policy=CachePolicyV12.CASCADE_CACHE_FIRST,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
            reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
        )
        assert v15.route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ
        assert v15.execution_form == ExecutionFormV15.SINGLE_STEP
        assert v15.fallback_chain[-1].route_id == RouteIdV15.R5_FALLBACK
        assert v15.support_target == SupportTargetV15.SOURCE_BACKED_SUMMARY

    def test_r4_action_maps(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R4_ACTION,
            tenant=tenant_v12,
            slo=slo_v12,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
            reason_codes=(ReasonCodeV15.ACTION_LOW_RISK.value,),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
        )
        assert v15.route_id == RouteIdV15.R4_SINGLE_ACTION

    def test_r_par_collapses_to_managed_workflow(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R_PAR,
            tenant=tenant_v12,
            slo=slo_v12,
            execution_form=ExecutionFormV12.PARALLEL_FANOUT,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
            workflow_blueprint_id="bp-par",
        )
        assert v15.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW
        assert v15.execution_form == ExecutionFormV15.MANAGED_WORKFLOW
        assert ReasonCodeV15.MULTI_STEP_REQUIRED.value in v15.reason_codes
        assert v15.workflow_blueprint_id == "bp-par"

    def test_r_loop_collapses_to_managed_workflow(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R_LOOP,
            tenant=tenant_v12,
            slo=slo_v12,
            execution_form=ExecutionFormV12.ITERATIVE_LOOP,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
            workflow_blueprint_id="bp-loop",
        )
        assert v15.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW

    def test_r_hitl_yields_tier_hitl(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R_HITL,
            tenant=tenant_v12,
            slo=slo_v12,
            execution_form=ExecutionFormV12.HUMAN_GATED,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
            workflow_blueprint_id="bp-hitl",
            side_effect_class=SideEffectClass.IRREVERSIBLE,
            capability_class=CapabilityClass.ACTION,
            sandbox_class=SandboxClass.PROCESS_SANDBOX,
        )
        assert v15.cost_tier == CostTierV15.TIER_HITL
        assert v15.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW
        assert ReasonCodeV15.HITL_REQUIRED.value in v15.reason_codes
        assert "HITL_PRECOMMIT" in v15.hitl_pause_points

    def test_freshness_mapping(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        cases = [
            (FreshnessClassV12.REALTIME, FreshnessClassV15.LIVE),
            (FreshnessClassV12.FRESH, FreshnessClassV15.CURRENT),
            (FreshnessClassV12.STABLE, FreshnessClassV15.SLOW_CHANGING),
            (FreshnessClassV12.ARCHIVAL, FreshnessClassV15.STATIC),
        ]
        for v12_fresh, v15_fresh_expected in cases:
            v12 = _v12_annex(
                route_id=RouteIdV12.R1A,
                tenant=tenant_v12,
                slo=slo_v12,
                cost_tier=CostTierV12.TIER_S,
                cache_policy=CachePolicyV12.EXACT_ONLY,
                execution_form=ExecutionFormV12.TERMINAL_SHORTCIRCUIT,
                reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
                freshness=v12_fresh,
            )
            v15 = v12_to_v15(
                v12,
                blueprint_hash="bp",
                snapshot_id="snap",
                trace_root="trace",
                route_span_id="span",
                replay_key="rk",
                route_telemetry_event_id="evt",
            )
            assert v15.freshness_class == v15_fresh_expected

    def test_managed_route_without_blueprint_raises(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R3R4_WORKFLOW,
            tenant=tenant_v12,
            slo=slo_v12,
            execution_form=ExecutionFormV12.MANAGED_WORKFLOW,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
        )
        with pytest.raises(V15RouteContractError, match="workflow_blueprint_id"):
            v12_to_v15(
                v12,
                blueprint_hash="bp",
                snapshot_id="snap",
                trace_root="trace",
                route_span_id="span",
                replay_key="rk",
                route_telemetry_event_id="evt",
            )

    def test_unknown_v12_reason_codes_dropped(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R1A,
            tenant=tenant_v12,
            slo=slo_v12,
            cost_tier=CostTierV12.TIER_S,
            cache_policy=CachePolicyV12.EXACT_ONLY,
            execution_form=ExecutionFormV12.TERMINAL_SHORTCIRCUIT,
            reason_codes=("not_in_v15_vocab", ReasonCodeV15.EXACT_CACHE_HIT.value),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
        )
        assert "not_in_v15_vocab" not in v15.reason_codes
        assert ReasonCodeV15.EXACT_CACHE_HIT.value in v15.reason_codes

    def test_non_v12annex_input_rejected(self) -> None:
        with pytest.raises(V15RouteContractError, match="V12RouteAnnex"):
            v12_to_v15(
                "not-an-annex",  # type: ignore[arg-type]
                blueprint_hash="bp",
                snapshot_id="snap",
                trace_root="trace",
                route_span_id="span",
                replay_key="rk",
                route_telemetry_event_id="evt",
            )


# ---------------------------------------------------------------------------
# Reverse translation: v15 -> v12
# ---------------------------------------------------------------------------


class TestV15ToV12Reverse:
    def test_r3_round_trip(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R3_GROUNDED,
            tenant=tenant_v12,
            slo=slo_v12,
            cache_policy=CachePolicyV12.CASCADE_CACHE_FIRST,
            fallback_chain=(
                FallbackEntryV12(RouteIdV12.R5_FALLBACK, CostTierV12.TIER_S),
            ),
            reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
        )
        v12_again = v15_to_v12(v15)
        assert v12_again.route_id == RouteIdV12.R3_GROUNDED
        assert v12_again.confidence == v12.confidence
        assert v12_again.tenant_scope == tenant_v12

    def test_v15_to_v12_signs_when_secret_provided(
        self,
        tenant_v12: TenantScopeV12,
        slo_v12: RouteSLOV12,
    ) -> None:
        v12 = _v12_annex(
            route_id=RouteIdV12.R1A,
            tenant=tenant_v12,
            slo=slo_v12,
            cost_tier=CostTierV12.TIER_S,
            cache_policy=CachePolicyV12.EXACT_ONLY,
            execution_form=ExecutionFormV12.TERMINAL_SHORTCIRCUIT,
            reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
        )
        v15 = v12_to_v15(
            v12,
            blueprint_hash="bp",
            snapshot_id="snap",
            trace_root="trace",
            route_span_id="span",
            replay_key="rk",
            route_telemetry_event_id="evt",
        )
        secret = b"k" * 32
        round_tripped = v15_to_v12(v15, secret_key=secret)
        assert round_tripped.hmac_sig != ""
        assert round_tripped.verify(secret) is True

    def test_v15_to_v12_input_validation(self) -> None:
        with pytest.raises(V15RouteContractError, match="V15RouteContract"):
            v15_to_v12("not-a-contract")  # type: ignore[arg-type]
