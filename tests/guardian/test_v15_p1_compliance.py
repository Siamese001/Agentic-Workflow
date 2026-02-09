"""
V15 P1 Compliance Regression Tests.

Each test maps 1:1 to a P1 backlog item from p0_p1_remediation_backlog.md.
If any test fails, the corresponding P1 item has regressed.

Backlog IDs: P1-F-01, P1-F-02, P1-M-01 through P1-M-22
"""

from __future__ import annotations

from dataclasses import fields

import pytest

from agentic_core.L0_maintenance.types.v15_contracts import (
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
from agentic_core.L0_maintenance.types.v15_types import (
    HEALER_PIPE_ORDER,
    AggregateArtifact,
    CapabilityDepletionTracker,
    IncidentArtifact,
    PermsArtifact,
    ResultArtifact,
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
    SelfHealingTrigger,
    SeverityEnum,
    TokenCapArtifact,
    TokenControlArtifact,
    TokenGateResult,
    VigilanceTier,
)

# =========================================================================
# P1-F-01 (§3.1): RouteDecision typed artifact has all 7 required fields
# =========================================================================


class TestP1F01RouteDecisionArtifact:
    """P1-F-01: RouteDecisionArtifact must have all 7 V15 fields."""

    REQUIRED_FIELDS = {
        "trace_id",
        "timestamp",
        "route_path",
        "risk_score",
        "budget_est",
        "rationale_enum",
        "policy_config_hash",
    }

    def test_all_required_fields_present(self):
        actual = {f.name for f in fields(RouteDecisionArtifact)}
        assert self.REQUIRED_FIELDS == actual

    def test_instantiation(self):
        artifact = RouteDecisionArtifact(
            trace_id="t1",
            timestamp="2026-02-09T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.5,
            budget_est=100.0,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="abc123",
        )
        assert artifact.trace_id == "t1"
        assert artifact.route_path == RoutePath.STANDARD_VALIDATION


# =========================================================================
# P1-F-02 (§3.3): Routing paths strictly defined — 5 paths
# =========================================================================


class TestP1F02RoutingPaths:
    """P1-F-02: RoutePath enum must have exactly 5 members."""

    REQUIRED_PATHS = {
        "LOW_RISK_BYPASS",
        "STANDARD_VALIDATION",
        "HUMAN_ESCALATION",
        "POLICY_CHALLENGE_LOOP",
        "ROUTE_RECOVERY_BUDGET_OVERFLOW",
    }

    def test_exactly_five_paths(self):
        assert len(RoutePath) == 5

    def test_all_required_paths_present(self):
        actual = {member.name for member in RoutePath}
        assert self.REQUIRED_PATHS == actual

    def test_contextual_router_has_six_decisions(self):
        """AST-based verification (§6) — avoids runtime import chain."""
        import ast
        import pathlib

        src = pathlib.Path(__file__).resolve().parents[2] / (
            "agentic_core/runtime/config/contextual_router_config.py"
        )
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=str(src))
        enum_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "RouteDecision":
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                enum_names.add(target.id)
        assert "POLICY_CHALLENGE_LOOP" in enum_names, (
            f"POLICY_CHALLENGE_LOOP missing from RouteDecision: {enum_names}"
        )
        assert "ROUTE_RECOVERY" in enum_names, f"ROUTE_RECOVERY missing from RouteDecision: {enum_names}"
        assert len(enum_names) >= 6, (
            f"RouteDecision has {len(enum_names)} members, expected >=6: {enum_names}"
        )


# =========================================================================
# P1-M-01 (§3.2): Rationale restricted to finite enum
# =========================================================================


class TestP1M01RationaleEnum:
    """P1-M-01: RoutingRationale must be a finite enum (no free-form)."""

    def test_is_enum(self):
        assert issubclass(RoutingRationale, str)
        assert len(RoutingRationale) >= 5

    def test_no_freeform(self):
        with pytest.raises(ValueError):
            RoutingRationale("arbitrary_freeform_text")


# =========================================================================
# P1-M-02 (§3.6): Law Slot Handler / Read-Only Twins / Capability Depletion
# =========================================================================


class TestP1M02LawSlotHandler:
    """P1-M-02: LawSlotHandler enforces tool isolation via read-only twins."""

    def test_register_and_acquire(self):
        handler = LawSlotHandler(trace_id="t1", total_slots=2)
        handler.register_twin("grep", "readonly_grep")
        handler.freeze()
        twin = handler.acquire_slot("grep")
        assert twin == "readonly_grep"

    def test_depletion_fail_closed(self):
        handler = LawSlotHandler(trace_id="t1", total_slots=1)
        handler.register_twin("tool_a", "twin_a")
        handler.freeze()
        handler.acquire_slot("tool_a")
        with pytest.raises(RuntimeError, match="depleted"):
            handler.acquire_slot("tool_a")

    def test_unregistered_tool_rejected(self):
        handler = LawSlotHandler(trace_id="t1", total_slots=5)
        handler.freeze()
        with pytest.raises(KeyError, match="No twin"):
            handler.acquire_slot("unknown")

    def test_register_after_freeze_rejected(self):
        handler = LawSlotHandler(trace_id="t1", total_slots=5)
        handler.freeze()
        with pytest.raises(RuntimeError, match="Cannot register"):
            handler.register_twin("tool", "twin")


# =========================================================================
# P1-M-03 (§4.1): policy_config read-once per healing wave
# P1-M-04 (§4.3): Policy mutation during wave = critical incident
# =========================================================================


class TestP1M03M04PolicyConfigGuard:
    """P1-M-03/M-04: PolicyConfigGuard enforces read-once + mutation detection."""

    def test_read_config_unchanged(self):
        config = {"key": "value", "nested": {"a": 1}}
        guard = PolicyConfigGuard(policy_config=config, wave_id="w1")
        result = guard.read_config(config)
        assert result == config

    def test_mutation_raises_incident(self):
        original = {"key": "value"}
        guard = PolicyConfigGuard(policy_config=original, wave_id="w1")
        mutated = {"key": "changed"}
        with pytest.raises(PolicyMutationIncident, match="mutated"):
            guard.read_config(mutated)

    def test_policy_hash_deterministic(self):
        config = {"b": 2, "a": 1}
        g1 = PolicyConfigGuard(policy_config=config, wave_id="w1")
        g2 = PolicyConfigGuard(policy_config=config, wave_id="w2")
        assert g1.policy_hash == g2.policy_hash


# =========================================================================
# P1-M-05 (§6.3): TokenControl Artifact (≤300 tokens)
# =========================================================================


class TestP1M05TokenControl:
    """P1-M-05: TokenControlArtifact enforces ≤300 token bound."""

    def test_valid_token_control(self):
        artifact = TokenControlArtifact(trace_id="t1", prompt_hash="h1", gold_tokens=200)
        assert artifact.gold_tokens == 200

    def test_exceeds_300_token_bound(self):
        with pytest.raises(ValueError, match="exceeds 300"):
            TokenControlArtifact(trace_id="t1", prompt_hash="h1", gold_tokens=301)


# =========================================================================
# P1-M-06 (§6.4): Static Policy Alignment Check
# =========================================================================


class TestP1M06StaticPolicyAlignment:
    """P1-M-06: static_policy_alignment_check returns PolicyAlignmentResult."""

    def test_aligned(self):
        rules = [{"id": "r1", "check": lambda ctx: True}]
        result = static_policy_alignment_check("t1", "h1", {}, rules)
        assert result.aligned is True
        assert result.violations == []

    def test_violation_detected(self):
        rules = [{"id": "r1", "check": lambda ctx: False}]
        result = static_policy_alignment_check("t1", "h1", {}, rules)
        assert result.aligned is False
        assert len(result.violations) == 1

    def test_missing_check_fn_fail_closed(self):
        rules = [{"id": "r1"}]
        result = static_policy_alignment_check("t1", "h1", {}, rules)
        assert result.aligned is False


# =========================================================================
# P1-M-07 (§7.3): Guardrail Guard (Budget, Payload, Safety, Boundary)
# =========================================================================


class TestP1M07GuardrailGuard:
    """P1-M-07: GuardrailGuard enforces 4 sub-checks, fail-closed."""

    def _make_token_cap(self, result: TokenGateResult) -> TokenCapArtifact:
        return TokenCapArtifact(
            trace_id="t1",
            policy_hash="h1",
            budget_limit=1000,
            tokens_requested=500,
            gate_result=result,
        )

    def test_all_pass(self):
        guard = GuardrailGuard(trace_id="t1")
        assert (
            guard.enforce_all(
                token_cap=self._make_token_cap(TokenGateResult.ALLOW),
                payload_hash="abc",
                expected_hash="abc",
                markers=["trace_id_present", "policy_hash_present", "schema_valid"],
                boundary_token="tok123",
            )
            is True
        )

    def test_budget_deny_blocks(self):
        guard = GuardrailGuard(trace_id="t1")
        assert guard.check_budget(self._make_token_cap(TokenGateResult.DENY)) is False

    def test_payload_mismatch_blocks(self):
        guard = GuardrailGuard(trace_id="t1")
        assert guard.check_payload_integrity("abc", "xyz") is False

    def test_missing_safety_marker_blocks(self):
        guard = GuardrailGuard(trace_id="t1")
        assert guard.check_safety_markers(["trace_id_present"]) is False

    def test_empty_boundary_token_blocks(self):
        guard = GuardrailGuard(trace_id="t1")
        assert guard.check_boundary_tokens("") is False


# =========================================================================
# P1-M-08 (§7.5): Absence of artifact = automatic failure
# =========================================================================


class TestP1M08ArtifactAbsence:
    """P1-M-08: enforce_artifact_presence raises on None."""

    def test_none_raises(self):
        with pytest.raises(ArtifactAbsenceFailure, match="absent"):
            enforce_artifact_presence(None, "RouteDecisionArtifact")

    def test_present_passes(self):
        enforce_artifact_presence("something", "SomeArtifact")


# =========================================================================
# P1-M-09 (§7.6): Meta-Guardian ≥95% invariant coverage
# =========================================================================


class TestP1M09MetaGuardian:
    """P1-M-09: meta_guardian_check enforces ≥95% coverage."""

    def test_above_threshold(self):
        result = meta_guardian_check(total_invariants=100, covered_invariants=96)
        assert result.passing is True
        assert result.coverage_pct >= 0.95

    def test_below_threshold(self):
        result = meta_guardian_check(total_invariants=100, covered_invariants=90)
        assert result.passing is False

    def test_zero_invariants_fails(self):
        result = meta_guardian_check(total_invariants=0, covered_invariants=0)
        assert result.passing is False


# =========================================================================
# P1-M-10 (§7.7): Aggregate Gate Rule
# =========================================================================


class TestP1M10AggregateGate:
    """P1-M-10: aggregate_gate_check rejects None or incomplete AGGREGATE."""

    def test_valid_aggregate(self):
        agg = AggregateArtifact(
            trace_id="t1",
            impact_scope=["file.py"],
            rollback_vector="git_reset",
            risk_delta=0.3,
            pre_heal_assessment="safe",
        )
        assert aggregate_gate_check(agg) is True

    def test_none_rejected(self):
        assert aggregate_gate_check(None) is False

    def test_empty_trace_rejected(self):
        agg = AggregateArtifact(
            trace_id="",
            impact_scope=["f"],
            rollback_vector="r",
            risk_delta=0.1,
            pre_heal_assessment="ok",
        )
        assert aggregate_gate_check(agg) is False

    def test_empty_impact_scope_rejected(self):
        agg = AggregateArtifact(
            trace_id="t1",
            impact_scope=[],
            rollback_vector="r",
            risk_delta=0.1,
            pre_heal_assessment="ok",
        )
        assert aggregate_gate_check(agg) is False


# =========================================================================
# P1-M-11 (§10.1): Healing inside transactional boundary
# =========================================================================


class TestP1M11HealingBoundary:
    """P1-M-11: HealingTransactionBoundary rolls back on error."""

    def test_commit_succeeds(self):
        with HealingTransactionBoundary(trace_id="t1") as txn:
            txn.commit()
        assert txn.committed is True
        assert txn.rolled_back is False

    def test_exception_triggers_rollback(self):
        with pytest.raises(ValueError):
            with HealingTransactionBoundary(trace_id="t1") as txn:
                raise ValueError("heal failed")
        assert txn.rolled_back is True
        assert txn.committed is False

    def test_no_commit_triggers_rollback(self):
        with HealingTransactionBoundary(trace_id="t1") as txn:
            pass
        assert txn.rolled_back is True


# =========================================================================
# P1-M-12 (§10.4): RESULT emission exclusive to L2
# =========================================================================


class TestP1M12ResultEmission:
    """P1-M-12: validate_result_emission rejects non-L2 layers."""

    def test_l2_allowed(self):
        validate_result_emission("L2_execution")

    @pytest.mark.parametrize("layer", ["L0_maintenance", "L5_safety", "L6_observability", "L3_orchestration"])
    def test_non_l2_rejected(self, layer: str):
        with pytest.raises(ResultEmissionViolation):
            validate_result_emission(layer)


# =========================================================================
# P1-M-13 / P1-M-21 (§11.1): TokenCap Enforcement
# =========================================================================


class TestP1M13TokenCap:
    """P1-M-13/M-21: TokenCapArtifact and PermsArtifact exist with required fields."""

    def test_token_cap_fields(self):
        required = {"trace_id", "policy_hash", "budget_limit", "tokens_requested", "gate_result"}
        actual = {f.name for f in fields(TokenCapArtifact)}
        assert required == actual

    def test_perms_fields(self):
        required = {"trace_id", "policy_hash", "budget"}
        actual = {f.name for f in fields(PermsArtifact)}
        assert required == actual

    def test_deny_gate_result(self):
        cap = TokenCapArtifact(
            trace_id="t1",
            policy_hash="h1",
            budget_limit=100,
            tokens_requested=200,
            gate_result=TokenGateResult.DENY,
        )
        assert cap.gate_result == TokenGateResult.DENY


# =========================================================================
# P1-M-14 (§11.2): Route Recovery (TokenOverflow)
# =========================================================================


class TestP1M14RouteRecovery:
    """P1-M-14: RouteRecoveryBox handles overflow without hard crash."""

    def test_retry_on_small_overflow(self):
        box = RouteRecoveryBox(trace_id="t1", max_retries=3)
        assert box.handle_overflow(tokens_requested=150, budget_limit=100) == "retry"

    def test_downgrade_on_large_overflow(self):
        box = RouteRecoveryBox(trace_id="t1", max_retries=3)
        assert box.handle_overflow(tokens_requested=500, budget_limit=100) == "downgrade"

    def test_reject_after_max_retries(self):
        box = RouteRecoveryBox(trace_id="t1", max_retries=1)
        box.handle_overflow(100, 50)
        assert box.handle_overflow(100, 50) == "reject"


# =========================================================================
# P1-M-15 / P1-M-22 (§15.1): Tiered Vigilance + Evacuation
# =========================================================================


class TestP1M15TieredVigilance:
    """P1-M-15/M-22: TieredVigilanceMonitor with Tier III evacuation."""

    def test_tier_i_no_evacuation(self):
        monitor = TieredVigilanceMonitor(trace_id="t1")
        result = monitor.escalate(VigilanceTier.TIER_I, "budget drain")
        assert result is None
        assert monitor.evacuated is False

    def test_tier_iii_triggers_evacuation(self):
        monitor = TieredVigilanceMonitor(trace_id="t1")
        protocol = monitor.escalate(VigilanceTier.TIER_III, "critical breach")
        assert protocol is not None
        assert protocol.freeze_state is True
        assert monitor.evacuated is True

    def test_vigilance_tier_enum_has_three_tiers(self):
        assert len(VigilanceTier) == 3


# =========================================================================
# P1-M-16 (§15.4): Capability Depletion tracking
# =========================================================================


class TestP1M16CapabilityDepletion:
    """P1-M-16: CapabilityDepletionTracker tracks tool slot depletion."""

    def test_consume_slot(self):
        tracker = CapabilityDepletionTracker(trace_id="t1", total_slots=3)
        assert tracker.consume_slot("tool_a") is True
        assert tracker.depletion_rate == pytest.approx(1 / 3)

    def test_depletion_returns_false(self):
        tracker = CapabilityDepletionTracker(trace_id="t1", total_slots=1)
        tracker.consume_slot("tool_a")
        assert tracker.consume_slot("tool_b") is False
        assert tracker.depletion_rate == 1.0


# =========================================================================
# P1-M-17 (§15.6): INCIDENT and RESULT telemetry emission
# =========================================================================


class TestP1M17TelemetryEmission:
    """P1-M-17: TelemetryEmitter emits events for INCIDENT and RESULT."""

    def test_emit_incident(self):
        emitter = TelemetryEmitter()
        incident = IncidentArtifact(
            trace_id="t1",
            incident_id="i1",
            correlation_hash="ch1",
            severity_enum=SeverityEnum.CRITICAL,
            telemetry_events=["e1"],
        )
        emitter.emit_incident(incident)
        assert len(emitter.events) == 1
        assert emitter.events[0]["type"] == "INCIDENT"

    def test_emit_result(self):
        emitter = TelemetryEmitter()
        result = ResultArtifact(
            trace_id="t1",
            execution_outcome="success",
            final_state_hash="h1",
            artifact_class="heal",
        )
        emitter.emit_result(result)
        assert len(emitter.events) == 1
        assert emitter.events[0]["type"] == "RESULT"


# =========================================================================
# P1-M-18 (§2.5): Pipe order enforced (1..10)
# =========================================================================


class TestP1M18PipeOrder:
    """P1-M-18: PipeOrderEnforcer enforces strict 1..10 step order."""

    def test_correct_order_completes(self):
        enforcer = PipeOrderEnforcer()
        for step_name in HEALER_PIPE_ORDER:
            enforcer.advance(step_name)
        assert enforcer.is_complete is True

    def test_wrong_order_raises(self):
        enforcer = PipeOrderEnforcer()
        with pytest.raises(PipeOrderViolation):
            enforcer.advance("commit")

    def test_exactly_ten_steps(self):
        assert len(HEALER_PIPE_ORDER) == 10


# =========================================================================
# P1-M-19 (§2.8): AGGREGATE→Heal boundary typed
# =========================================================================


class TestP1M19AggregateBoundary:
    """P1-M-19: AggregateArtifact has impact_scope, rollback_vector, risk_delta."""

    REQUIRED_FIELDS = {
        "trace_id",
        "impact_scope",
        "rollback_vector",
        "risk_delta",
        "pre_heal_assessment",
    }

    def test_all_required_fields(self):
        actual = {f.name for f in fields(AggregateArtifact)}
        assert self.REQUIRED_FIELDS == actual


# =========================================================================
# P1-M-20 (§5.4): SelfHealingTrigger emission
# =========================================================================


class TestP1M20SelfHealingTrigger:
    """P1-M-20: SelfHealingTrigger has all 5 required fields."""

    REQUIRED_FIELDS = {
        "trace_id",
        "source_layer",
        "target_pipe",
        "signal_hash",
        "severity_enum",
    }

    def test_all_required_fields(self):
        actual = {f.name for f in fields(SelfHealingTrigger)}
        assert self.REQUIRED_FIELDS == actual

    def test_instantiation(self):
        trigger = SelfHealingTrigger(
            trace_id="t1",
            source_layer="L6_observability",
            target_pipe="L2_execution",
            signal_hash="sh1",
            severity_enum=SeverityEnum.ERROR,
        )
        assert trigger.source_layer == "L6_observability"
