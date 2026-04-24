"""Unit tests for v12 L0 Routing extensions.

Covers:
- route_contract_v12_extensions: enums, V12RouteAnnex validity, HMAC sign/verify
- fallback_chains_loader: chain lookup, SLO defaults, hardcoded fallback
- cold_start_safeguard: override / no-override / terminal / already-conservative
- loop_guard: suspected / insufficient spans / healthy / invalid input
- v12_route_selector: §13 decision-order first-match-wins
- routing_calibration.get_v12_threshold / get_v12_int
"""

from __future__ import annotations

import os

import pytest

from agentic_core.L0_routing.config import routing_calibration
from agentic_core.L0_routing.config.fallback_chains_loader import (
    get_fallback_chain,
    get_slo_default,
    reset_cache as reset_fallback_cache,
)
from agentic_core.L0_routing.reasoning.cold_start_safeguard import (
    ColdStartDecision,
    maybe_override_for_cold_start,
)
from agentic_core.L0_routing.reasoning.v12_route_selector import (
    RouteSignals,
    select_route,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CachePolicy,
    CostTier,
    ExecutionForm,
    FallbackEntry,
    FreshnessClass,
    RouteId,
    RouteSLO,
    TenantScope,
    V12RouteAnnex,
    V12RouteContractError,
    load_secret_key_from_env,
)
from agentic_core.L0_routing.utils.loop_guard import evaluate_loop_guard


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tenant() -> TenantScope:
    return TenantScope(tenant_id="t1", region="us-east-1", acl_bounds=("read",))


@pytest.fixture
def minimal_slo() -> RouteSLO:
    return RouteSLO(
        latency_budget_ms=1000,
        token_budget_in=0,
        token_budget_out=0,
        cost_cap_usd=0.0,
    )


# ---------------------------------------------------------------------------
# V12RouteAnnex validity
# ---------------------------------------------------------------------------


class TestV12RouteAnnexValidity:
    def test_terminal_shortcut_requires_cache_route(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        with pytest.raises(V12RouteContractError, match="TERMINAL_SHORTCIRCUIT"):
            V12RouteAnnex(
                contract_version="1.0.0",
                base_contract_id="c1",
                route_id=RouteId.R3_GROUNDED,
                confidence=0.9,
                reason_codes=(),
                freshness_class=FreshnessClass.STABLE,
                cache_policy=CachePolicy.SEMANTIC_OK,
                execution_form=ExecutionForm.TERMINAL_SHORTCIRCUIT,
                cost_tier=CostTier.TIER_M,
                fallback_chain=(),
                slo=minimal_slo,
                telemetry_keys=(),
                tenant_scope=tenant,
            )

    def test_human_gated_requires_hitl(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        with pytest.raises(V12RouteContractError, match="HUMAN_GATED"):
            V12RouteAnnex(
                contract_version="1.0.0",
                base_contract_id="c1",
                route_id=RouteId.R4_ACTION,
                confidence=0.9,
                reason_codes=(),
                freshness_class=FreshnessClass.STABLE,
                cache_policy=CachePolicy.NO_CACHE,
                execution_form=ExecutionForm.HUMAN_GATED,
                cost_tier=CostTier.TIER_M,
                fallback_chain=(FallbackEntry(RouteId.R5_FALLBACK, CostTier.TIER_S),),
                slo=minimal_slo,
                telemetry_keys=(),
                tenant_scope=tenant,
            )

    def test_non_terminal_requires_non_empty_chain(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        with pytest.raises(V12RouteContractError, match="non-empty fallback_chain"):
            V12RouteAnnex(
                contract_version="1.0.0",
                base_contract_id="c1",
                route_id=RouteId.R3_GROUNDED,
                confidence=0.9,
                reason_codes=(),
                freshness_class=FreshnessClass.STABLE,
                cache_policy=CachePolicy.SEMANTIC_OK,
                execution_form=ExecutionForm.SINGLE_STEP,
                cost_tier=CostTier.TIER_M,
                fallback_chain=(),
                slo=minimal_slo,
                telemetry_keys=(),
                tenant_scope=tenant,
            )

    def test_r5_must_be_last_in_chain(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        with pytest.raises(V12RouteContractError, match="R5_FALLBACK must be the last"):
            V12RouteAnnex(
                contract_version="1.0.0",
                base_contract_id="c1",
                route_id=RouteId.R3_GROUNDED,
                confidence=0.9,
                reason_codes=(),
                freshness_class=FreshnessClass.STABLE,
                cache_policy=CachePolicy.SEMANTIC_OK,
                execution_form=ExecutionForm.SINGLE_STEP,
                cost_tier=CostTier.TIER_M,
                fallback_chain=(
                    FallbackEntry(RouteId.R5_FALLBACK, CostTier.TIER_S),
                    FallbackEntry(RouteId.R3R4_WORKFLOW, CostTier.TIER_L),
                ),
                slo=minimal_slo,
                telemetry_keys=(),
                tenant_scope=tenant,
            )

    def test_confidence_range(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        with pytest.raises(V12RouteContractError, match="confidence out of range"):
            V12RouteAnnex(
                contract_version="1.0.0",
                base_contract_id="c1",
                route_id=RouteId.R1A,
                confidence=1.5,
                reason_codes=(),
                freshness_class=FreshnessClass.STABLE,
                cache_policy=CachePolicy.EXACT_ONLY,
                execution_form=ExecutionForm.TERMINAL_SHORTCIRCUIT,
                cost_tier=CostTier.TIER_S,
                fallback_chain=(),
                slo=minimal_slo,
                telemetry_keys=(),
                tenant_scope=tenant,
            )

    def test_hmac_sign_verify_roundtrip(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        annex = V12RouteAnnex(
            contract_version="1.0.0",
            base_contract_id="c1",
            route_id=RouteId.R1A,
            confidence=0.99,
            reason_codes=("exact_cache_hit",),
            freshness_class=FreshnessClass.FRESH,
            cache_policy=CachePolicy.EXACT_ONLY,
            execution_form=ExecutionForm.TERMINAL_SHORTCIRCUIT,
            cost_tier=CostTier.TIER_S,
            fallback_chain=(),
            slo=minimal_slo,
            telemetry_keys=("intent_class",),
            tenant_scope=tenant,
        )
        signed = annex.sign(b"test-key")
        assert signed.hmac_sig != ""
        assert signed.verify(b"test-key") is True
        assert signed.verify(b"wrong-key") is False

    def test_unsigned_verify_returns_false(self, tenant: TenantScope, minimal_slo: RouteSLO) -> None:
        annex = V12RouteAnnex(
            contract_version="1.0.0",
            base_contract_id="c1",
            route_id=RouteId.R1A,
            confidence=0.99,
            reason_codes=(),
            freshness_class=FreshnessClass.FRESH,
            cache_policy=CachePolicy.EXACT_ONLY,
            execution_form=ExecutionForm.TERMINAL_SHORTCIRCUIT,
            cost_tier=CostTier.TIER_S,
            fallback_chain=(),
            slo=minimal_slo,
            telemetry_keys=(),
            tenant_scope=tenant,
        )
        assert annex.verify(b"anything") is False

    def test_load_secret_key_from_env_missing(self) -> None:
        os.environ.pop("AGENTIC_V12_ROUTE_HMAC_KEY", None)
        with pytest.raises(V12RouteContractError, match="unset or empty"):
            load_secret_key_from_env()

    def test_load_secret_key_from_env_present(self) -> None:
        os.environ["AGENTIC_V12_ROUTE_HMAC_KEY"] = "abc123"
        try:
            assert load_secret_key_from_env() == b"abc123"
        finally:
            os.environ.pop("AGENTIC_V12_ROUTE_HMAC_KEY", None)


# ---------------------------------------------------------------------------
# Fallback chains
# ---------------------------------------------------------------------------


class TestFallbackChains:
    def setup_method(self) -> None:
        reset_fallback_cache()

    def test_r1a_empty_chain(self) -> None:
        assert get_fallback_chain(RouteId.R1A) == ()

    def test_r5_empty_chain(self) -> None:
        assert get_fallback_chain(RouteId.R5_FALLBACK) == ()

    def test_r3_grounded_chain_ends_with_r5(self) -> None:
        chain = get_fallback_chain(RouteId.R3_GROUNDED)
        assert len(chain) >= 1
        assert chain[-1].route_id == RouteId.R5_FALLBACK

    def test_hitl_chain_is_r5_only(self) -> None:
        chain = get_fallback_chain(RouteId.R_HITL)
        assert len(chain) == 1
        assert chain[0].route_id == RouteId.R5_FALLBACK

    def test_slo_default_r1a(self) -> None:
        slo = get_slo_default(RouteId.R1A)
        assert slo.latency_budget_ms == 50
        assert slo.cost_cap_usd == 0.0

    def test_slo_default_r3_grounded_tier_m(self) -> None:
        slo = get_slo_default(RouteId.R3_GROUNDED, CostTier.TIER_M)
        assert slo.latency_budget_ms == 6000
        assert slo.token_budget_in == 12000

    def test_slo_default_r3_grounded_tier_l(self) -> None:
        slo = get_slo_default(RouteId.R3_GROUNDED, CostTier.TIER_L)
        assert slo.latency_budget_ms == 20000

    def test_slo_default_unknown_raises(self) -> None:
        with pytest.raises(V12RouteContractError, match="no SLO default"):
            get_slo_default("UNKNOWN_ROUTE")


# ---------------------------------------------------------------------------
# Cold-start safeguard
# ---------------------------------------------------------------------------


class TestColdStartSafeguard:
    def test_high_confidence_no_override(self) -> None:
        d = maybe_override_for_cold_start(
            top_pick=RouteId.R3_GROUNDED,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.9,
            cold_start_threshold=0.5,
        )
        assert d.overridden is False
        assert d.route_id == RouteId.R3_GROUNDED
        assert d.cost_tier == CostTier.TIER_S

    def test_low_confidence_forces_override(self) -> None:
        d = maybe_override_for_cold_start(
            top_pick=RouteId.R_CASC,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.3,
            cold_start_threshold=0.5,
        )
        assert d.overridden is True
        assert d.route_id == RouteId.R3_GROUNDED
        assert d.cost_tier == CostTier.TIER_M
        assert "cold_start_override" in d.reason_codes
        assert len(d.fallback_chain_prefix) == 1
        assert d.fallback_chain_prefix[0].route_id == RouteId.R_CASC

    def test_terminal_route_never_overridden(self) -> None:
        for terminal in (RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK):
            d = maybe_override_for_cold_start(
                top_pick=terminal,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.1,
                cold_start_threshold=0.5,
            )
            assert d.overridden is False
            assert d.route_id == terminal

    def test_already_conservative_idempotent(self) -> None:
        d = maybe_override_for_cold_start(
            top_pick=RouteId.R3_GROUNDED,
            top_pick_tier=CostTier.TIER_M,
            classifier_confidence=0.1,
            cold_start_threshold=0.5,
        )
        assert d.overridden is False
        assert "cold_start_already_conservative" in d.reason_codes

    def test_confidence_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="out of range"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R3_GROUNDED,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=1.5,
                cold_start_threshold=0.5,
            )


# ---------------------------------------------------------------------------
# Loop guard
# ---------------------------------------------------------------------------


class TestLoopGuard:
    def test_empty_trace(self) -> None:
        v = evaluate_loop_guard([], set(), efficiency_threshold=0.4, min_spans=5)
        assert v.suspected is False
        assert v.reason == "empty_trace"

    def test_insufficient_spans(self) -> None:
        v = evaluate_loop_guard(["s1", "s2"], {"s1"}, efficiency_threshold=0.4, min_spans=5)
        assert v.suspected is False
        assert "insufficient_spans" in v.reason

    def test_healthy_trace(self) -> None:
        spans = [f"s{i}" for i in range(10)]
        productive = set(spans[:9])  # 90% productive
        v = evaluate_loop_guard(spans, productive, efficiency_threshold=0.4, min_spans=5)
        assert v.suspected is False
        assert v.efficiency_score == pytest.approx(0.9)

    def test_loop_suspected(self) -> None:
        spans = [f"s{i}" for i in range(10)]
        productive = set(spans[:2])  # 20% productive — below 0.4 threshold
        v = evaluate_loop_guard(spans, productive, efficiency_threshold=0.4, min_spans=5)
        assert v.suspected is True
        assert v.efficiency_score == pytest.approx(0.2)

    def test_invalid_productive_ids(self) -> None:
        with pytest.raises(ValueError, match="not in span_ids"):
            evaluate_loop_guard(
                ["s1", "s2"],
                {"s3"},
                efficiency_threshold=0.4,
                min_spans=1,
            )


# ---------------------------------------------------------------------------
# Calibration loader v12 getters
# ---------------------------------------------------------------------------


class TestV12Calibration:
    def setup_method(self) -> None:
        routing_calibration.reset_cache()

    def test_known_threshold(self) -> None:
        v = routing_calibration.get_v12_threshold("classifier_surface_threshold")
        assert 0.0 <= v <= 1.0
        assert v == pytest.approx(0.72)

    def test_unknown_threshold_raises(self) -> None:
        with pytest.raises(KeyError):
            routing_calibration.get_v12_threshold("nonexistent")

    def test_known_int(self) -> None:
        assert routing_calibration.get_v12_int("r_casc_max_depth") == 3

    def test_env_override_threshold(self) -> None:
        os.environ["AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD"] = "0.80"
        try:
            assert routing_calibration.get_v12_threshold("classifier_surface_threshold") == pytest.approx(
                0.80
            )
        finally:
            os.environ.pop("AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD", None)

    def test_env_override_int(self) -> None:
        os.environ["AGENTIC_V12_R_CASC_MAX_DEPTH"] = "5"
        try:
            assert routing_calibration.get_v12_int("r_casc_max_depth") == 5
        finally:
            os.environ.pop("AGENTIC_V12_R_CASC_MAX_DEPTH", None)

    def test_malformed_env_falls_back(self) -> None:
        os.environ["AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD"] = "not_a_number"
        try:
            assert routing_calibration.get_v12_threshold("classifier_surface_threshold") == pytest.approx(
                0.72
            )
        finally:
            os.environ.pop("AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD", None)


# ---------------------------------------------------------------------------
# §13 Route selector — first-match-wins decision order
# ---------------------------------------------------------------------------


def _base_signals(tenant: TenantScope, **overrides: object) -> RouteSignals:
    defaults: dict[str, object] = {
        "ingress_ok": True,
        "tenant_scope": tenant,
        "classifier_confidence": 0.9,
        "top_pick_route": RouteId.R3_GROUNDED,
        "top_pick_tier": CostTier.TIER_M,
        "base_contract_id": "base-1",
    }
    defaults.update(overrides)
    return RouteSignals(**defaults)  # type: ignore[arg-type]


class TestRouteSelectorDecisionOrder:
    def test_step1_ingress_reject(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, ingress_ok=False))
        assert annex.route_id == RouteId.R5_FALLBACK
        assert "ingress_reject" in annex.reason_codes

    def test_step3_exact_cache_wins(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                exact_cache_hit=True,
                semantic_cache_hit=True,  # exact must still win
                single_step_grounded_sufficient=True,
            )
        )
        assert annex.route_id == RouteId.R1A

    def test_step4_semantic_cache_when_no_exact(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                exact_cache_hit=False,
                semantic_cache_hit=True,
                single_step_grounded_sufficient=True,
            )
        )
        assert annex.route_id == RouteId.R1B

    def test_step5_high_stakes_beats_r4(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                high_stakes_action=True,
                bounded_reversible_action=True,
            )
        )
        assert annex.route_id == RouteId.R_HITL
        assert annex.cost_tier == CostTier.TIER_M
        assert annex.execution_form == ExecutionForm.HUMAN_GATED

    def test_step6_r4_action(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, bounded_reversible_action=True))
        assert annex.route_id == RouteId.R4_ACTION

    def test_step7_parallel_fanout(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, independent_subtasks_ge_2=True))
        assert annex.route_id == RouteId.R_PAR
        assert annex.execution_form == ExecutionForm.PARALLEL_FANOUT

    def test_step8_r_loop(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, generator_critic_refiner_applicable=True))
        assert annex.route_id == RouteId.R_LOOP
        assert annex.execution_form == ExecutionForm.ITERATIVE_LOOP

    def test_step9_single_step_grounded(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, single_step_grounded_sufficient=True))
        assert annex.route_id == RouteId.R3_GROUNDED

    def test_step10_tier_varying_to_cascade(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, tier_varying_difficulty=True))
        assert annex.route_id == RouteId.R_CASC
        assert annex.cost_tier == CostTier.TIER_S  # cascade always starts at S

    def test_step11_managed_workflow(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, cross_step_contract_change=True))
        assert annex.route_id == RouteId.R3R4_WORKFLOW
        assert annex.cost_tier == CostTier.TIER_L

    def test_step12_no_viable_route_falls_back(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant))
        assert annex.route_id == RouteId.R5_FALLBACK

    def test_cold_start_override_applied_to_ambiguous(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                classifier_confidence=0.2,
                tier_varying_difficulty=True,
            )
        )
        # §7 cold-start override replaces R-CASC with R3_GROUNDED TIER_M.
        assert annex.route_id == RouteId.R3_GROUNDED
        assert annex.cost_tier == CostTier.TIER_M
        assert "cold_start_override" in annex.reason_codes

    def test_cold_start_does_not_override_cache_hits(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                classifier_confidence=0.1,
                exact_cache_hit=True,
            )
        )
        assert annex.route_id == RouteId.R1A

    def test_assembled_chain_ends_with_r5(self, tenant: TenantScope) -> None:
        annex = select_route(_base_signals(tenant, single_step_grounded_sufficient=True))
        assert annex.fallback_chain[-1].route_id == RouteId.R5_FALLBACK

    def test_assembled_chain_deduped(self, tenant: TenantScope) -> None:
        annex = select_route(
            _base_signals(
                tenant,
                classifier_confidence=0.1,
                tier_varying_difficulty=True,
            )
        )
        seen = set()
        for entry in annex.fallback_chain:
            key = (entry.route_id.value, entry.cost_tier.value)
            assert key not in seen, f"duplicate entry: {key}"
            seen.add(key)
