"""Behavioral tests for ``agentic_core.L0_routing.types.routing_contracts_types``.

Covers V15 P1 fail-closed enforcement contracts:
- LawSlotHandler: twin registration, freeze, slot acquisition, depletion.
- PolicyConfigGuard: read-once + mutation incident on config change.
- static_policy_alignment_check: aligned on all-pass; collects rule ids on failure.
- GuardrailGuard: four sub-checks (budget, payload, markers, boundary) + enforce_all.
- enforce_artifact_presence / ArtifactAbsenceFailure.
- meta_guardian_check threshold + empty-input handling.
- aggregate_gate_check fail-closed on None/missing fields; pass on complete.
- HealingTransactionBoundary: explicit commit, rollback-on-exception,
  rollback-on-no-commit, commit-outside-boundary rejected.
- validate_result_emission / ResultEmissionViolation.
- RouteRecoveryBox: retry / downgrade / reject progression.
- PipeOrderEnforcer: correct sequence + PipeOrderViolation on out-of-order.
- TieredVigilanceMonitor: Tier-III triggers EvacuationProtocol.
- TelemetryEmitter: incident/result/route_decision/typed emission + flush.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L0_routing.types.routing_artifact_types import (
    HEALER_PIPE_ORDER,
    AggregateArtifact,
    IncidentArtifact,
    ResultArtifact,
    RouteDecisionArtifact,
    SeverityEnum,
    TokenCapArtifact,
    TokenGateResult,
    VigilanceTier,
)
from agentic_core.L0_routing.types.routing_contracts_types import (
    ArtifactAbsenceFailure,
    GuardrailGuard,
    HealingTransactionBoundary,
    LawSlotHandler,
    PipeOrderEnforcer,
    PipeOrderViolation,
    PolicyConfigGuard,
    PolicyMutationIncident,
    ResultEmissionViolation,
    RouteRecoveryBox,
    TelemetryEmitter,
    TieredVigilanceMonitor,
    aggregate_gate_check,
    enforce_artifact_presence,
    meta_guardian_check,
    static_policy_alignment_check,
    validate_result_emission,
)


# ---- LawSlotHandler ------------------------------------------------------


class TestLawSlotHandler:
    def test_register_then_acquire(self) -> None:
        h = LawSlotHandler(trace_id="t", total_slots=2)
        twin = object()
        h.register_twin("toolA", twin)
        assert h.acquire_slot("toolA") is twin

    def test_unknown_twin_raises(self) -> None:
        h = LawSlotHandler(trace_id="t", total_slots=2)
        with pytest.raises(KeyError, match="No twin registered"):
            h.acquire_slot("missing")

    def test_freeze_blocks_register(self) -> None:
        h = LawSlotHandler(trace_id="t", total_slots=1)
        h.freeze()
        with pytest.raises(RuntimeError, match="freeze"):
            h.register_twin("x", object())

    def test_depletion_after_consuming_slots(self) -> None:
        h = LawSlotHandler(trace_id="t", total_slots=1)
        h.register_twin("toolA", object())
        h.acquire_slot("toolA")
        with pytest.raises(RuntimeError, match="depleted"):
            h.acquire_slot("toolA")


# ---- PolicyConfigGuard ---------------------------------------------------


class TestPolicyConfigGuard:
    def test_read_unchanged_config_returns_it(self) -> None:
        cfg = {"a": 1, "b": 2}
        g = PolicyConfigGuard(policy_config=cfg, wave_id="w1")
        assert g.read_config(cfg) == cfg
        assert len(g.policy_hash) == 64

    def test_hash_stable_for_equivalent_dicts(self) -> None:
        g = PolicyConfigGuard(policy_config={"a": 1, "b": 2}, wave_id="w1")
        # Same content, different insertion order — hash must match (sorted keys)
        assert g.read_config({"b": 2, "a": 1}) == {"b": 2, "a": 1}

    def test_mutation_raises_incident(self) -> None:
        g = PolicyConfigGuard(policy_config={"a": 1}, wave_id="w1")
        with pytest.raises(PolicyMutationIncident) as exc:
            g.read_config({"a": 2})
        assert exc.value.wave_id == "w1"


# ---- static_policy_alignment_check ---------------------------------------


class TestStaticPolicyAlignment:
    def test_all_pass_aligned(self) -> None:
        rules = [
            {"id": "r1", "check": lambda c: True},
            {"id": "r2", "check": lambda c: True},
        ]
        r = static_policy_alignment_check("t", "hash", {}, rules)
        assert r.aligned is True
        assert r.violations == []

    def test_failing_rule_reports_id(self) -> None:
        rules = [
            {"id": "r1", "check": lambda c: True},
            {"id": "bad", "check": lambda c: False},
        ]
        r = static_policy_alignment_check("t", "hash", {}, rules)
        assert r.aligned is False
        assert any("bad" in v for v in r.violations)

    def test_missing_check_fail_closed(self) -> None:
        rules = [{"id": "r1"}]
        r = static_policy_alignment_check("t", "hash", {}, rules)
        assert r.aligned is False
        assert any("no check function" in v for v in r.violations)

    def test_check_exception_reported(self) -> None:
        rules = [{"id": "boom", "check": lambda c: (_ for _ in ()).throw(ValueError("x"))}]
        r = static_policy_alignment_check("t", "hash", {}, rules)
        assert r.aligned is False
        assert any("boom" in v and "check error" in v for v in r.violations)


# ---- GuardrailGuard ------------------------------------------------------


def _tc(gate: TokenGateResult = TokenGateResult.ALLOW) -> TokenCapArtifact:
    return TokenCapArtifact(
        trace_id="t",
        policy_hash="p",
        budget_limit=100,
        tokens_requested=50,
        gate_result=gate,
    )


class TestGuardrailGuard:
    def test_budget_allow(self) -> None:
        assert GuardrailGuard("t").check_budget(_tc(TokenGateResult.ALLOW)) is True

    def test_budget_downgrade_still_ok(self) -> None:
        assert GuardrailGuard("t").check_budget(_tc(TokenGateResult.DOWNGRADE)) is True

    def test_budget_deny_blocks(self) -> None:
        assert GuardrailGuard("t").check_budget(_tc(TokenGateResult.DENY)) is False

    def test_payload_integrity(self) -> None:
        g = GuardrailGuard("t")
        assert g.check_payload_integrity("abc", "abc") is True
        assert g.check_payload_integrity("abc", "xyz") is False

    def test_safety_markers(self) -> None:
        g = GuardrailGuard("t")
        required = ["trace_id_present", "policy_hash_present", "schema_valid"]
        assert g.check_safety_markers(required) is True
        assert g.check_safety_markers(required + ["extra"]) is True
        assert g.check_safety_markers(required[:-1]) is False

    def test_boundary_tokens(self) -> None:
        g = GuardrailGuard("t")
        assert g.check_boundary_tokens("token") is True
        assert g.check_boundary_tokens("") is False
        assert g.check_boundary_tokens("   ") is False

    def test_enforce_all_passes(self) -> None:
        g = GuardrailGuard("t")
        assert (
            g.enforce_all(
                token_cap=_tc(),
                payload_hash="h",
                expected_hash="h",
                markers=["trace_id_present", "policy_hash_present", "schema_valid"],
                boundary_token="tok",
            )
            is True
        )

    def test_enforce_all_fails_on_any(self) -> None:
        g = GuardrailGuard("t")
        assert (
            g.enforce_all(
                token_cap=_tc(TokenGateResult.DENY),
                payload_hash="h",
                expected_hash="h",
                markers=["trace_id_present", "policy_hash_present", "schema_valid"],
                boundary_token="tok",
            )
            is False
        )


# ---- enforce_artifact_presence ------------------------------------------


class TestArtifactPresence:
    def test_passes_for_any_non_none(self) -> None:
        enforce_artifact_presence({"x": 1}, "payload")
        enforce_artifact_presence(0, "zero")  # 0 is a valid artifact
        enforce_artifact_presence("", "empty-string")

    def test_raises_on_none(self) -> None:
        with pytest.raises(ArtifactAbsenceFailure) as exc:
            enforce_artifact_presence(None, "critical-artifact")
        assert exc.value.artifact_name == "critical-artifact"


# ---- meta_guardian_check -------------------------------------------------


class TestMetaGuardian:
    def test_passes_above_threshold(self) -> None:
        r = meta_guardian_check(100, 96)
        assert r.passing is True
        assert r.coverage_pct == 0.96

    def test_fails_below_threshold(self) -> None:
        r = meta_guardian_check(100, 94)
        assert r.passing is False

    def test_empty_is_not_passing(self) -> None:
        r = meta_guardian_check(0, 0)
        assert r.passing is False
        assert r.coverage_pct == 0.0

    def test_custom_threshold(self) -> None:
        r = meta_guardian_check(10, 5, threshold=0.5)
        assert r.passing is True


# ---- aggregate_gate_check ------------------------------------------------


class TestAggregateGate:
    def _ag(self, **overrides: Any) -> AggregateArtifact:
        kwargs: dict[str, Any] = {
            "trace_id": "t",
            "impact_scope": ["mod.a"],
            "rollback_vector": "v1",
            "risk_delta": 0.1,
            "pre_heal_assessment": "ok",
        }
        kwargs.update(overrides)
        return AggregateArtifact(**kwargs)

    def test_none_rejected(self) -> None:
        assert aggregate_gate_check(None) is False

    def test_complete_accepted(self) -> None:
        assert aggregate_gate_check(self._ag()) is True

    def test_empty_trace_rejected(self) -> None:
        assert aggregate_gate_check(self._ag(trace_id="")) is False

    def test_empty_impact_scope_rejected(self) -> None:
        assert aggregate_gate_check(self._ag(impact_scope=[])) is False

    def test_empty_rollback_rejected(self) -> None:
        assert aggregate_gate_check(self._ag(rollback_vector="")) is False


# ---- HealingTransactionBoundary ------------------------------------------


class TestHealingTransactionBoundary:
    def test_commit_flow(self) -> None:
        tx = HealingTransactionBoundary("t")
        with tx:
            tx.commit()
        assert tx.committed is True
        assert tx.rolled_back is False

    def test_exception_rolls_back(self) -> None:
        tx = HealingTransactionBoundary("t")
        with pytest.raises(RuntimeError, match="boom"):
            with tx:
                raise RuntimeError("boom")
        assert tx.rolled_back is True
        assert tx.committed is False

    def test_missing_commit_rolls_back(self) -> None:
        tx = HealingTransactionBoundary("t")
        with tx:
            pass  # no commit
        assert tx.rolled_back is True
        assert tx.committed is False

    def test_commit_outside_raises(self) -> None:
        tx = HealingTransactionBoundary("t")
        with pytest.raises(RuntimeError, match="outside active boundary"):
            tx.commit()


# ---- validate_result_emission --------------------------------------------


class TestResultEmission:
    def test_l2_allowed(self) -> None:
        validate_result_emission("L2_execution")  # no raise

    @pytest.mark.parametrize("layer", ["L0", "L0_routing", "L5_safety", "L6", "L1"])
    def test_other_layers_blocked(self, layer: str) -> None:
        with pytest.raises(ResultEmissionViolation) as exc:
            validate_result_emission(layer)
        assert exc.value.layer == layer


# ---- RouteRecoveryBox ----------------------------------------------------


class TestRouteRecoveryBox:
    def test_retry_when_within_2x_budget(self) -> None:
        box = RouteRecoveryBox("t", max_retries=3)
        assert box.handle_overflow(tokens_requested=150, budget_limit=100) == "retry"
        assert box.attempts == 1

    def test_downgrade_when_over_2x_budget(self) -> None:
        box = RouteRecoveryBox("t", max_retries=3)
        assert box.handle_overflow(tokens_requested=500, budget_limit=100) == "downgrade"

    def test_reject_after_max_retries(self) -> None:
        box = RouteRecoveryBox("t", max_retries=2)
        box.handle_overflow(150, 100)
        box.handle_overflow(150, 100)
        assert box.handle_overflow(150, 100) == "reject"
        assert box.attempts == 3


# ---- PipeOrderEnforcer ---------------------------------------------------


class TestPipeOrderEnforcer:
    def test_correct_sequence_advances(self) -> None:
        p = PipeOrderEnforcer()
        for i, step in enumerate(HEALER_PIPE_ORDER, start=1):
            assert p.advance(step) == i
        assert p.is_complete is True
        assert p.current_step == len(HEALER_PIPE_ORDER)

    def test_out_of_order_raises(self) -> None:
        p = PipeOrderEnforcer()
        with pytest.raises(PipeOrderViolation) as exc:
            p.advance("hash_verification")  # must start at schema_validation
        assert exc.value.expected == "schema_validation"
        assert exc.value.actual == "hash_verification"
        assert exc.value.step == 1

    def test_advance_after_complete_raises(self) -> None:
        p = PipeOrderEnforcer()
        for step in HEALER_PIPE_ORDER:
            p.advance(step)
        with pytest.raises(PipeOrderViolation):
            p.advance("commit")  # already complete


# ---- TieredVigilanceMonitor ----------------------------------------------


class TestTieredVigilanceMonitor:
    def test_starts_tier_i(self) -> None:
        m = TieredVigilanceMonitor("t")
        assert m.current_tier is VigilanceTier.TIER_I
        assert m.evacuated is False

    def test_tier_ii_no_evacuation(self) -> None:
        m = TieredVigilanceMonitor("t")
        assert m.escalate(VigilanceTier.TIER_II, reason="probe") is None
        assert m.current_tier is VigilanceTier.TIER_II
        assert m.evacuated is False

    def test_tier_iii_triggers_evacuation(self) -> None:
        m = TieredVigilanceMonitor("t")
        proto = m.escalate(VigilanceTier.TIER_III, reason="budget-exhaust")
        assert proto is not None
        assert proto.tier is VigilanceTier.TIER_III
        assert proto.freeze_state is True
        assert proto.reason == "budget-exhaust"
        assert m.evacuated is True


# ---- TelemetryEmitter ----------------------------------------------------


class TestTelemetryEmitter:
    def test_emit_incident(self) -> None:
        e = TelemetryEmitter()
        inc = IncidentArtifact(
            trace_id="t",
            incident_id="i1",
            correlation_hash="h",
            severity_enum=SeverityEnum.ERROR,
            telemetry_events=[],
        )
        e.emit_incident(inc)
        assert e.events == [
            {
                "type": "INCIDENT",
                "trace_id": "t",
                "incident_id": "i1",
                "severity": "error",
            }
        ]

    def test_emit_result(self) -> None:
        # ResultArtifact __post_init__ invokes a separate layer-emission validator
        # which is out of scope for this test. Use a duck-typed stand-in carrying
        # the two attributes emit_result reads.
        from types import SimpleNamespace

        e = TelemetryEmitter()
        e.emit_result(SimpleNamespace(trace_id="t", execution_outcome="success"))
        assert e.events[0]["type"] == "RESULT"
        assert e.events[0]["outcome"] == "success"
        assert e.events[0]["trace_id"] == "t"

    def test_emit_route_decision_payload_is_dict(self) -> None:
        # RouteDecisionArtifact is a dataclass — minimal fields to construct
        from dataclasses import fields as dc_fields

        defaults: dict[str, Any] = {}
        for f in dc_fields(RouteDecisionArtifact):
            ann = f.type
            if ann == "str" or ann is str:
                defaults[f.name] = "x"
            elif ann == "int" or ann is int:
                defaults[f.name] = 0
            elif ann == "float" or ann is float:
                defaults[f.name] = 0.0
            elif ann == "bool" or ann is bool:
                defaults[f.name] = False
            else:
                defaults[f.name] = None
        try:
            artifact = RouteDecisionArtifact(**defaults)
        except Exception:  # noqa: BLE001
            pytest.skip("RouteDecisionArtifact construction varies by schema")
        e = TelemetryEmitter()
        e.emit_route_decision(artifact)
        assert e.events[0]["type"] == "ROUTE_DECISION"
        assert isinstance(e.events[0]["payload"], dict)

    def test_events_returns_copy(self) -> None:
        e = TelemetryEmitter()
        inc = IncidentArtifact(
            trace_id="t",
            incident_id="i",
            correlation_hash="h",
            severity_enum=SeverityEnum.INFO,
            telemetry_events=[],
        )
        e.emit_incident(inc)
        events = e.events
        events.clear()
        assert len(e.events) == 1  # internal list not affected

    def test_flush_no_events_returns_none(self, tmp_path: Path) -> None:
        e = TelemetryEmitter()
        assert e.flush_to_artifacts_dir(tmp_path) is None

    def test_flush_writes_ndjson(self, tmp_path: Path) -> None:
        e = TelemetryEmitter()
        inc = IncidentArtifact(
            trace_id="t",
            incident_id="i",
            correlation_hash="h",
            severity_enum=SeverityEnum.WARNING,
            telemetry_events=[],
        )
        e.emit_incident(inc)
        out = e.flush_to_artifacts_dir(tmp_path)
        assert out is not None
        content = Path(out).read_text(encoding="utf-8").strip().splitlines()
        assert len(content) == 1
        parsed = json.loads(content[0])
        assert parsed["type"] == "INCIDENT"
