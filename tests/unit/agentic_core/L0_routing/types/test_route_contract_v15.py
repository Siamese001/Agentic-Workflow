"""Unit tests for agentic_core.L0_routing.types.route_contract_v15.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 L0 v15 route contract.
``route_contract_v15`` (fan_in=11, L0_routing) defines the deterministic
RouteContract emitted by L0: the closed-vocabulary enums, the substructures
(FallbackEntryV15, RouteSLOV15, AuthorityScope, TelemetryKeysV15, SignaturesV15),
the V15RouteContract with its rich __post_init__ invariants, plus the digest /
manifest / confidence-classification helpers.
"""

from __future__ import annotations

import dataclasses

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
)


def _slo() -> RouteSLOV15:
    return RouteSLOV15(
        max_latency_ms=1000,
        max_cost=1.0,
        max_tokens=1000,
        max_retrieval_passes=2,
        max_graph_hops=2,
        max_tool_calls=2,
        max_iterations=2,
        reserve_for_exit_eval=100,
    )


def _authority() -> AuthorityScope:
    return AuthorityScope(
        tenant_scope="tenant-a",
        acl_scope=("acl-1",),
        region_scope="us",
        capability_class=CapabilityClass.READ_ONLY,
        side_effect_class=SideEffectClass.PURE,
        sandbox_class=SandboxClass.NO_SANDBOX,
    )


def _telemetry() -> TelemetryKeysV15:
    return TelemetryKeysV15(
        trace_root="tr",
        route_span_id="rs",
        route_digest="rd",
        policy_hash="ph",
        blueprint_hash="bh",
        snapshot_id="sn",
        replay_key="rk",
        route_telemetry_event_id="ev",
    )


def _signatures() -> SignaturesV15:
    return SignaturesV15(manifest_hash="mh", deterministic_route_digest="drd")


def _r5_fallback_entry() -> FallbackEntryV15:
    return FallbackEntryV15(route_id=RouteIdV15.R5_FALLBACK, cost_tier=CostTierV15.TIER_S)


def _r3_contract(**overrides: object) -> V15RouteContract:
    """A valid non-terminal R3 contract (SINGLE_STEP, READ_THROUGH cache)."""
    base: dict[str, object] = {
        "contract_version": "v15.0",
        "route_id": RouteIdV15.R3_SIMPLE_GROUNDED_READ,
        "execution_form": ExecutionFormV15.SINGLE_STEP,
        "confidence_score": 0.9,
        "confidence_class": ConfidenceClass.HIGH,
        "reason_codes": (ReasonCodeV15.GROUNDING_REQUIRED.value,),
        "freshness_class": FreshnessClassV15.CURRENT,
        "cache_policy": CachePolicyV15.READ_THROUGH,
        "support_target": SupportTargetV15.SOURCE_BACKED_SUMMARY,
        "cost_tier": CostTierV15.TIER_M,
        "fallback_chain": (_r5_fallback_entry(),),
        "slo": _slo(),
        "authority": _authority(),
        "telemetry_keys": _telemetry(),
        "signatures": _signatures(),
    }
    base.update(overrides)
    return V15RouteContract(**base)  # type: ignore[arg-type]


def _r5_contract(**overrides: object) -> V15RouteContract:
    """A valid terminal R5 contract (TERMINAL_SHORTCIRCUIT, empty chain)."""
    base: dict[str, object] = {
        "contract_version": "v15.0",
        "route_id": RouteIdV15.R5_FALLBACK,
        "execution_form": ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
        "confidence_score": 0.3,
        "confidence_class": ConfidenceClass.INSUFFICIENT_SUPPORT,
        "reason_codes": (ReasonCodeV15.FALLBACK_SELECTED.value,),
        "freshness_class": FreshnessClassV15.STATIC,
        "cache_policy": CachePolicyV15.NO_CACHE,
        "support_target": SupportTargetV15.NONE,
        "cost_tier": CostTierV15.TIER_S,
        "fallback_chain": (),
        "slo": _slo(),
        "authority": _authority(),
        "telemetry_keys": _telemetry(),
        "signatures": _signatures(),
        "safe_response_type": SafeResponseType.ABSTAIN,
    }
    base.update(overrides)
    return V15RouteContract(**base)  # type: ignore[arg-type]


class TestEnums:
    def test_route_id_members(self) -> None:
        assert {r.value for r in RouteIdV15} == {
            "R1A_EXACT_CACHE",
            "R1B_SEMANTIC_CACHE",
            "R3_SIMPLE_GROUNDED_READ",
            "R4_SINGLE_ACTION",
            "R3R4_MANAGED_WORKFLOW",
            "R5_FALLBACK",
        }

    def test_execution_form_members(self) -> None:
        assert {e.value for e in ExecutionFormV15} == {
            "TERMINAL_SHORTCIRCUIT",
            "SINGLE_STEP",
            "MANAGED_WORKFLOW",
        }

    def test_cost_tier_has_hitl(self) -> None:
        assert CostTierV15.TIER_HITL.value == "TIER_HITL"

    def test_write_authority_members(self) -> None:
        assert {w.value for w in WriteAuthority} == {"NONE_UNTIL_UWG", "UWG_CLEARED"}


class TestClassifyConfidence:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (1.0, ConfidenceClass.EXACT),
            (0.9, ConfidenceClass.HIGH),
            (0.7, ConfidenceClass.MEDIUM),
            (0.5, ConfidenceClass.LOW),
            (0.1, ConfidenceClass.INSUFFICIENT_SUPPORT),
        ],
    )
    def test_boundaries(self, score: float, expected: ConfidenceClass) -> None:
        assert _classify_confidence(score) is expected

    def test_out_of_range_is_insufficient(self) -> None:
        assert _classify_confidence(2.0) is ConfidenceClass.INSUFFICIENT_SUPPORT
        assert _classify_confidence(float("nan")) is ConfidenceClass.INSUFFICIENT_SUPPORT


class TestSubstructures:
    def test_fallback_entry_defaults(self) -> None:
        e = _r5_fallback_entry()
        assert e.provider is None

    def test_fallback_entry_bad_route_id_type_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="route_id must be RouteIdV15"):
            FallbackEntryV15(route_id="R5", cost_tier=CostTierV15.TIER_S)  # type: ignore[arg-type]

    def test_slo_negative_field_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="must be >= 0"):
            RouteSLOV15(
                max_latency_ms=-1,
                max_cost=1.0,
                max_tokens=1,
                max_retrieval_passes=1,
                max_graph_hops=1,
                max_tool_calls=1,
                max_iterations=1,
                reserve_for_exit_eval=1,
            )

    def test_slo_nan_cost_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="max_cost must be finite"):
            RouteSLOV15(
                max_latency_ms=1,
                max_cost=float("inf"),
                max_tokens=1,
                max_retrieval_passes=1,
                max_graph_hops=1,
                max_tool_calls=1,
                max_iterations=1,
                reserve_for_exit_eval=1,
            )

    def test_authority_blank_tenant_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="tenant_scope must be non-empty"):
            AuthorityScope(
                tenant_scope="",
                acl_scope=(),
                region_scope="us",
                capability_class=CapabilityClass.READ_ONLY,
                side_effect_class=SideEffectClass.PURE,
                sandbox_class=SandboxClass.NO_SANDBOX,
            )

    def test_authority_default_write_authority(self) -> None:
        assert _authority().write_authority is WriteAuthority.NONE_UNTIL_UWG

    def test_telemetry_blank_field_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="TelemetryKeysV15.trace_root"):
            TelemetryKeysV15(
                trace_root="",
                route_span_id="rs",
                route_digest="rd",
                policy_hash="ph",
                blueprint_hash="bh",
                snapshot_id="sn",
                replay_key="rk",
                route_telemetry_event_id="ev",
            )

    def test_signatures_blank_manifest_hash_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="manifest_hash"):
            SignaturesV15(manifest_hash="", deterministic_route_digest="drd")


class TestContractConstruction:
    def test_valid_r3_contract(self) -> None:
        c = _r3_contract()
        assert c.route_id is RouteIdV15.R3_SIMPLE_GROUNDED_READ
        assert c.safe_response_type is None

    def test_valid_r5_contract(self) -> None:
        c = _r5_contract()
        assert c.route_id is RouteIdV15.R5_FALLBACK
        assert c.safe_response_type is SafeResponseType.ABSTAIN

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _r3_contract().confidence_score = 0.1  # type: ignore[misc]


class TestContractInvariants:
    def test_confidence_score_out_of_range_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="out of range"):
            _r3_contract(confidence_score=1.5, confidence_class=ConfidenceClass.HIGH)

    def test_unknown_reason_code_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="not in ReasonCodeV15 vocabulary"):
            _r3_contract(reason_codes=("NOT_A_REAL_CODE",))

    def test_execution_form_route_mismatch_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="incompatible with"):
            _r3_contract(execution_form=ExecutionFormV15.TERMINAL_SHORTCIRCUIT)

    def test_cache_policy_not_allowed_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="not allowed for"):
            _r3_contract(cache_policy=CachePolicyV15.EXACT_ONLY)

    def test_non_terminal_empty_chain_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="requires non-empty fallback_chain"):
            _r3_contract(fallback_chain=())

    def test_non_terminal_chain_not_ending_r5_raises(self) -> None:
        entry = FallbackEntryV15(route_id=RouteIdV15.R4_SINGLE_ACTION, cost_tier=CostTierV15.TIER_S)
        with pytest.raises(V15RouteContractError, match="last entry must be R5_FALLBACK"):
            _r3_contract(fallback_chain=(entry,))

    def test_r5_with_nonempty_chain_raises(self) -> None:
        # Use a distinct cost_tier so the self-reference guard does not fire first.
        entry = FallbackEntryV15(route_id=RouteIdV15.R5_FALLBACK, cost_tier=CostTierV15.TIER_M)
        with pytest.raises(V15RouteContractError, match="empty fallback_chain"):
            _r5_contract(fallback_chain=(entry,))

    def test_r5_missing_safe_response_type_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="requires safe_response_type"):
            _r5_contract(safe_response_type=None)

    def test_non_r5_with_safe_response_type_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="meaningful only on R5_FALLBACK"):
            _r3_contract(safe_response_type=SafeResponseType.ABSTAIN)

    def test_confidence_class_score_disagreement_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="disagrees with derived"):
            _r3_contract(confidence_score=0.5, confidence_class=ConfidenceClass.HIGH)

    def test_unsafe_class_bypasses_derivation(self) -> None:
        c = _r3_contract(confidence_score=0.5, confidence_class=ConfidenceClass.UNSAFE)
        assert c.confidence_class is ConfidenceClass.UNSAFE

    def test_self_referential_fallback_raises(self) -> None:
        self_entry = FallbackEntryV15(
            route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ, cost_tier=CostTierV15.TIER_M
        )
        with pytest.raises(V15RouteContractError, match="self-referential"):
            _r3_contract(fallback_chain=(self_entry, _r5_fallback_entry()))

    def test_write_authority_must_be_none_until_uwg(self) -> None:
        bad_authority = AuthorityScope(
            tenant_scope="t",
            acl_scope=(),
            region_scope="us",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
            write_authority=WriteAuthority.UWG_CLEARED,
        )
        with pytest.raises(V15RouteContractError, match="NONE_UNTIL_UWG"):
            _r3_contract(authority=bad_authority)


class TestSignAndVerify:
    def test_sign_then_verify_roundtrip(self) -> None:
        c = _r3_contract()
        signed = c.sign(b"secret-key-bytes")
        assert signed.signatures.hmac_sig != ""
        assert signed.verify(b"secret-key-bytes") is True

    def test_verify_fails_wrong_key(self) -> None:
        signed = _r3_contract().sign(b"secret-key-bytes")
        assert signed.verify(b"other-key") is False

    def test_verify_false_when_unsigned(self) -> None:
        assert _r3_contract().verify(b"k") is False

    def test_sign_rejects_empty_key(self) -> None:
        with pytest.raises(V15RouteContractError, match="non-empty"):
            _r3_contract().sign(b"")


class TestDigestAndManifest:
    def _digest(self) -> str:
        return compute_deterministic_route_digest(
            route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
            execution_form=ExecutionFormV15.SINGLE_STEP,
            cache_policy=CachePolicyV15.READ_THROUGH,
            freshness_class=FreshnessClassV15.CURRENT,
            support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
            cost_tier=CostTierV15.TIER_M,
            reason_codes=(ReasonCodeV15.GROUNDING_REQUIRED.value,),
            fallback_chain=(_r5_fallback_entry(),),
            authority=_authority(),
            policy_hash="ph",
            blueprint_hash="bh",
            snapshot_id="sn",
        )

    def test_digest_deterministic_64_hex(self) -> None:
        d1 = self._digest()
        d2 = self._digest()
        assert d1 == d2
        assert len(d1) == 64

    def test_digest_blank_policy_hash_raises(self) -> None:
        with pytest.raises(V15RouteContractError, match="policy_hash"):
            compute_deterministic_route_digest(
                route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
                execution_form=ExecutionFormV15.SINGLE_STEP,
                cache_policy=CachePolicyV15.READ_THROUGH,
                freshness_class=FreshnessClassV15.CURRENT,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                cost_tier=CostTierV15.TIER_M,
                reason_codes=(),
                fallback_chain=(),
                authority=_authority(),
                policy_hash="",
                blueprint_hash="bh",
                snapshot_id="sn",
            )

    def test_manifest_hash_deterministic_64_hex(self) -> None:
        h = compute_manifest_hash(
            contract_version="v15.0",
            route_digest="rd",
            policy_hash="ph",
            blueprint_hash="bh",
            snapshot_id="sn",
        )
        assert len(h) == 64
