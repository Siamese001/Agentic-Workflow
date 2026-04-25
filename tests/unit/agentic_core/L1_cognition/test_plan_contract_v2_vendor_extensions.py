"""Vendor-aligned extension tests for L1PlanContractV2 (gap-fixes G1..G12).

Covers:
  G1 PlanPattern taxonomy            G7  IterationCap + stop_conditions
  G2 ReasoningEffort dial            G8  HITLCheckpoint
  G4 PlanStepAnnotation (model_hint) G10 Augmentation per step
  G5 compute_plan_signature          G11 escalation_reason invariant
  G6 PARALLEL_SECTION / PARALLEL_VOTE G12 ReplanPolicy

Invariant under test: existing L1PlanContractV2 callers that do NOT supply
any of the new fields must continue to validate cleanly (back-compat).
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    Augmentation,
    ExpectedGroundTruth,
    HITLCheckpoint,
    HITLCheckpointTrigger,
    IterationCap,
    L1PlanContractV2,
    PlanContractViolation,
    PlanPattern,
    PlanStepAnnotation,
    PlanTaskStep,
    PlannerTelemetry,
    ProposedRoute,
    QuerySpec,
    ReasoningEffort,
    ReasoningMode,
    ReplanAction,
    ReplanPolicy,
    Reversibility,
    RiskBand,
    RouteRisk,
)


def _base_step(step_id: str = "s1") -> PlanTaskStep:
    return PlanTaskStep(
        step_id=step_id,
        description="do the thing",
        expected_ground_truth=ExpectedGroundTruth(
            signal_kind="tool_result",
            shape_hint="dict[str,Any]",
            success_predicate="result.status == 'ok'",
        ),
    )


def _base_telemetry() -> PlannerTelemetry:
    return PlannerTelemetry(refinements_used=0, wall_clock_ms=10, token_usage=100, critic_iterations=0)


def _base_route_risk() -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=Reversibility.READ,
    )


def _minimal_contract(**overrides) -> L1PlanContractV2:
    """Build a minimal valid V2 contract; tests override specific fields."""
    defaults: dict[str, Any] = dict(
        plan_id="p1",
        request_id="r1",
        policy_hash="h1",
        proposed_route=ProposedRoute.R1A,
        reasoning_mode=ReasoningMode.DIRECT,
        query_spec=None,
        task_spec=(_base_step("s1"),),
        route_risk=_base_route_risk(),
        confidence_score=0.9,
        grounding_required=False,
        declared_assumptions=(Assumption("x", AssumptionGrade.DIRECTLY_OBSERVED),),
        unresolved_gaps=(),
        published_rationale="rationale",
        planner_telemetry=_base_telemetry(),
    )
    defaults.update(overrides)
    return L1PlanContractV2(**defaults)


class TestBackCompat:
    def test_minimal_v2_no_new_fields_validates(self):
        """Existing callers that don't set any v3.1 field still pass validate()."""
        _minimal_contract().validate()  # must not raise

    def test_to_dict_includes_new_keys_with_safe_defaults(self):
        d = _minimal_contract().to_dict()
        assert d["pattern"] is None
        assert d["reasoning_effort"] is None
        assert d["iteration_cap"] is None
        assert d["stop_conditions"] == []
        assert d["hitl_checkpoints"] == []
        assert d["replan_policy"] is None
        assert d["plan_signature"] is None
        assert d["escalation_reason"] is None
        assert d["step_annotations"] == []


class TestPlanPattern:
    def test_augmented_call_no_escalation_reason_required(self):
        _minimal_contract(pattern=PlanPattern.AUGMENTED_CALL).validate()

    @pytest.mark.parametrize(
        "pattern",
        [
            PlanPattern.CHAIN,
            PlanPattern.ROUTE,
            PlanPattern.PARALLEL_SECTION,
            PlanPattern.PARALLEL_VOTE,
            PlanPattern.ORCHESTRATOR_WORKERS,
        ],
    )
    def test_escalated_pattern_requires_escalation_reason(self, pattern):
        with pytest.raises(PlanContractViolation, match="escalation_reason"):
            _minimal_contract(pattern=pattern).validate()

    def test_escalated_pattern_with_reason_validates(self):
        _minimal_contract(
            pattern=PlanPattern.CHAIN,
            escalation_reason="V3 failed: multi-step decomposition needed",
        ).validate()

    def test_evaluator_optimizer_requires_iteration_cap(self):
        with pytest.raises(PlanContractViolation, match="iteration_cap"):
            _minimal_contract(
                pattern=PlanPattern.EVALUATOR_OPTIMIZER,
                escalation_reason="critic loop needed",
            ).validate()

    def test_agent_requires_iteration_cap(self):
        with pytest.raises(PlanContractViolation, match="iteration_cap"):
            _minimal_contract(pattern=PlanPattern.AGENT, escalation_reason="tool loop needed").validate()

    def test_agent_with_iteration_cap_validates(self):
        _minimal_contract(
            pattern=PlanPattern.AGENT,
            escalation_reason="tool loop needed",
            iteration_cap=IterationCap(max_steps=5, max_retries=1, max_critic_rounds=1),
        ).validate()

    def test_pattern_wrong_type_rejected(self):
        with pytest.raises(PlanContractViolation, match="PlanPattern"):
            _minimal_contract(pattern="CHAIN").validate()  # raw string


class TestReasoningEffort:
    @pytest.mark.parametrize("effort", [ReasoningEffort.LOW, ReasoningEffort.MEDIUM, ReasoningEffort.HIGH])
    def test_valid_effort_levels(self, effort):
        _minimal_contract(reasoning_effort=effort).validate()

    def test_wrong_type_rejected(self):
        with pytest.raises(PlanContractViolation, match="ReasoningEffort"):
            _minimal_contract(reasoning_effort="HIGH").validate()


class TestIterationCap:
    def test_defaults(self):
        c = IterationCap()
        assert c.max_steps == 10
        assert c.max_retries == 2
        assert c.max_critic_rounds == 2

    def test_to_dict(self):
        assert IterationCap(max_steps=3, max_retries=1, max_critic_rounds=0).to_dict() == {
            "max_steps": 3,
            "max_retries": 1,
            "max_critic_rounds": 0,
        }

    def test_wrong_type_on_contract_rejected(self):
        with pytest.raises(PlanContractViolation, match="IterationCap"):
            _minimal_contract(iteration_cap={"max_steps": 5}).validate()


class TestStopConditions:
    def test_empty_default(self):
        _minimal_contract().validate()

    def test_list_of_strings_ok(self):
        _minimal_contract(stop_conditions=("schema_valid", "citations_matched")).validate()

    def test_non_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="stop_conditions"):
            _minimal_contract(stop_conditions=(1, 2, 3)).validate()

    def test_bare_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="stop_conditions"):
            _minimal_contract(stop_conditions="schema_valid").validate()


class TestHITLCheckpoints:
    def test_checkpoint_must_reference_existing_step(self):
        cp = HITLCheckpoint(after_step_id="missing", trigger=HITLCheckpointTrigger.ALWAYS)
        with pytest.raises(PlanContractViolation, match="hitl_checkpoints"):
            _minimal_contract(hitl_checkpoints=(cp,)).validate()

    def test_checkpoint_referencing_real_step_ok(self):
        cp = HITLCheckpoint(after_step_id="s1", trigger=HITLCheckpointTrigger.ON_LOW_CONFIDENCE)
        _minimal_contract(hitl_checkpoints=(cp,)).validate()

    def test_wrong_element_type_rejected(self):
        with pytest.raises(PlanContractViolation, match="HITLCheckpoint"):
            _minimal_contract(hitl_checkpoints=({"after_step_id": "s1"},)).validate()


class TestReplanPolicy:
    def test_defaults(self):
        p = ReplanPolicy()
        assert p.on_ground_truth_mismatch == ReplanAction.REPLAN
        assert p.on_tool_failure == ReplanAction.REPLAN
        assert p.on_policy_block == ReplanAction.ESCALATE_HITL
        assert p.budget == 2

    def test_contract_accepts_policy(self):
        _minimal_contract(replan_policy=ReplanPolicy(budget=3)).validate()

    def test_to_dict(self):
        d = ReplanPolicy().to_dict()
        assert d["on_policy_block"] == "ESCALATE_HITL"
        assert d["budget"] == 2


class TestStepAnnotations:
    def test_annotation_must_reference_existing_step(self):
        ann = PlanStepAnnotation(step_id="missing", model_hint="fast")
        with pytest.raises(PlanContractViolation, match="step_annotations"):
            _minimal_contract(step_annotations=(ann,)).validate()

    def test_annotation_with_augmentations_ok(self):
        ann = PlanStepAnnotation(
            step_id="s1",
            model_hint="reasoning",
            augmentations=(Augmentation.RETRIEVAL, Augmentation.TOOLS),
        )
        _minimal_contract(step_annotations=(ann,)).validate()

    def test_non_enum_augmentation_rejected(self):
        ann = PlanStepAnnotation(step_id="s1", augmentations=("RETRIEVAL",))  # str, not enum
        with pytest.raises(PlanContractViolation, match="Augmentation"):
            _minimal_contract(step_annotations=(ann,)).validate()

    def test_annotation_to_dict(self):
        ann = PlanStepAnnotation(step_id="s1", model_hint="fast", augmentations=(Augmentation.MEMORY,))
        assert ann.to_dict() == {
            "step_id": "s1",
            "model_hint": "fast",
            "augmentations": ["MEMORY"],
        }


class TestPlanSignature:
    def test_signature_deterministic(self):
        c1 = _minimal_contract(pattern=PlanPattern.AUGMENTED_CALL)
        c2 = _minimal_contract(pattern=PlanPattern.AUGMENTED_CALL)
        assert c1.compute_plan_signature() == c2.compute_plan_signature()

    def test_signature_changes_with_body(self):
        c1 = _minimal_contract(pattern=PlanPattern.AUGMENTED_CALL)
        c2 = _minimal_contract(pattern=PlanPattern.CHAIN, escalation_reason="V2 failed: ordering needed")
        assert c1.compute_plan_signature() != c2.compute_plan_signature()

    def test_signature_excludes_telemetry(self):
        """Telemetry drift must not rotate the signature — G5 invariant."""
        c1 = _minimal_contract()
        c2 = _minimal_contract(
            planner_telemetry=PlannerTelemetry(
                refinements_used=99, wall_clock_ms=9999, token_usage=9999, critic_iterations=9
            )
        )
        assert c1.compute_plan_signature() == c2.compute_plan_signature()

    def test_signature_excludes_published_rationale(self):
        """Rationale rewording must not rotate the signature."""
        c1 = _minimal_contract(published_rationale="v1 text")
        c2 = _minimal_contract(published_rationale="v2 rewording")
        assert c1.compute_plan_signature() == c2.compute_plan_signature()

    def test_signature_sha256_hex(self):
        sig = _minimal_contract().compute_plan_signature()
        assert len(sig) == 64
        int(sig, 16)  # must be valid hex


class TestImmutability:
    """Frozen dataclass invariants — mutation attempts must fail."""

    def test_contract_is_frozen(self):
        c = _minimal_contract()
        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
            c.pattern = PlanPattern.CHAIN  # type: ignore[misc]

    def test_iteration_cap_is_frozen(self):
        cap = IterationCap()
        with pytest.raises((AttributeError, Exception)):
            cap.max_steps = 99  # type: ignore[misc]

    def test_replan_policy_is_frozen(self):
        p = ReplanPolicy()
        with pytest.raises((AttributeError, Exception)):
            p.budget = 99  # type: ignore[misc]

    def test_hitl_checkpoint_is_frozen(self):
        cp = HITLCheckpoint(after_step_id="s1", trigger=HITLCheckpointTrigger.ALWAYS)
        with pytest.raises((AttributeError, Exception)):
            cp.after_step_id = "s2"  # type: ignore[misc]

    def test_step_annotation_is_frozen(self):
        ann = PlanStepAnnotation(step_id="s1")
        with pytest.raises((AttributeError, Exception)):
            ann.model_hint = "fast"  # type: ignore[misc]


class TestPickleAndDeepcopy:
    """Frozen dataclasses must round-trip through pickle and deepcopy."""

    def test_contract_pickles(self):
        import pickle

        c = _minimal_contract(
            pattern=PlanPattern.CHAIN,
            escalation_reason="ordering needed",
            reasoning_effort=ReasoningEffort.MEDIUM,
        )
        restored = pickle.loads(pickle.dumps(c))
        assert restored == c
        assert restored.compute_plan_signature() == c.compute_plan_signature()

    def test_contract_deepcopies(self):
        import copy

        c = _minimal_contract(
            replan_policy=ReplanPolicy(budget=5),
            iteration_cap=IterationCap(max_steps=3),
            pattern=PlanPattern.AGENT,
            escalation_reason="tool loop",
        )
        d = copy.deepcopy(c)
        assert d == c
        assert d is not c

    def test_new_enums_pickle(self):
        import pickle

        for enum in (PlanPattern, ReasoningEffort, Augmentation, HITLCheckpointTrigger, ReplanAction):
            for member in enum:
                restored = pickle.loads(pickle.dumps(member))
                assert restored is member


class TestSignatureDeterminism:
    """Signature must be stable across process restarts (simulated)."""

    def test_signature_stable_under_equal_bodies(self):
        c = _minimal_contract(
            pattern=PlanPattern.CHAIN,
            escalation_reason="multi-step",
            stop_conditions=("a", "b"),
            iteration_cap=IterationCap(max_steps=5),
        )
        # Build an equivalent contract separately.
        c2 = _minimal_contract(
            pattern=PlanPattern.CHAIN,
            escalation_reason="multi-step",
            stop_conditions=("a", "b"),
            iteration_cap=IterationCap(max_steps=5),
        )
        assert c.compute_plan_signature() == c2.compute_plan_signature()

    def test_signature_stop_condition_order_sensitive(self):
        """Ordered sequences must matter — ('a','b') != ('b','a')."""
        c1 = _minimal_contract(stop_conditions=("a", "b"))
        c2 = _minimal_contract(stop_conditions=("b", "a"))
        assert c1.compute_plan_signature() != c2.compute_plan_signature()

    def test_signature_plan_id_participates(self):
        c1 = _minimal_contract(plan_id="p1")
        c2 = _minimal_contract(plan_id="p2")
        assert c1.compute_plan_signature() != c2.compute_plan_signature()

    def test_signature_iteration_cap_participates(self):
        c1 = _minimal_contract(iteration_cap=IterationCap(max_steps=5))
        c2 = _minimal_contract(iteration_cap=IterationCap(max_steps=6))
        assert c1.compute_plan_signature() != c2.compute_plan_signature()

    def test_signature_replan_policy_participates(self):
        c1 = _minimal_contract(replan_policy=ReplanPolicy(budget=1))
        c2 = _minimal_contract(replan_policy=ReplanPolicy(budget=2))
        assert c1.compute_plan_signature() != c2.compute_plan_signature()


class TestSignatureHelpers:
    """with_signature / verify_signature / require_signed_for_dispatch."""

    def test_with_signature_binds_digest(self):
        c = _minimal_contract()
        signed = c.with_signature()
        assert signed.plan_signature == c.compute_plan_signature()

    def test_with_signature_idempotent(self):
        c = _minimal_contract().with_signature()
        again = c.with_signature()
        assert again is c  # same instance returned when already current

    def test_with_signature_preserves_all_fields(self):
        c = _minimal_contract(
            pattern=PlanPattern.EVALUATOR_OPTIMIZER,
            escalation_reason="critic loop",
            iteration_cap=IterationCap(max_critic_rounds=3),
            reasoning_effort=ReasoningEffort.HIGH,
        )
        signed = c.with_signature()
        # semantic body unchanged
        assert signed.pattern == c.pattern
        assert signed.escalation_reason == c.escalation_reason
        assert signed.iteration_cap == c.iteration_cap
        assert signed.reasoning_effort == c.reasoning_effort
        # still validates
        signed.validate()

    def test_verify_signature_true(self):
        c = _minimal_contract().with_signature()
        assert c.verify_signature(c.plan_signature) is True

    def test_verify_signature_false_on_mismatch(self):
        c = _minimal_contract()
        assert c.verify_signature("0" * 64) is False

    def test_verify_signature_constant_time(self):
        """hmac.compare_digest — sanity: rejects length mismatch without raising."""
        c = _minimal_contract()
        assert c.verify_signature("") is False
        assert c.verify_signature("short") is False

    def test_require_signed_for_dispatch_agent_unsigned_raises(self):
        c = _minimal_contract(
            pattern=PlanPattern.AGENT,
            escalation_reason="tool loop",
            iteration_cap=IterationCap(),
        )
        with pytest.raises(PlanContractViolation, match="plan_signature is required"):
            c.require_signed_for_dispatch()

    def test_require_signed_for_dispatch_agent_signed_ok(self):
        c = _minimal_contract(
            pattern=PlanPattern.AGENT,
            escalation_reason="tool loop",
            iteration_cap=IterationCap(),
        ).with_signature()
        c.require_signed_for_dispatch()  # must not raise

    def test_require_signed_for_dispatch_write_unsigned_raises(self):
        c = _minimal_contract(
            route_risk=RouteRisk(
                cost_band=RiskBand.LOW,
                latency_band=RiskBand.LOW,
                safety_band=RiskBand.LOW,
                reversibility=Reversibility.WRITE,
            )
        )
        with pytest.raises(PlanContractViolation, match="plan_signature is required"):
            c.require_signed_for_dispatch()

    def test_require_signed_for_dispatch_high_safety_unsigned_raises(self):
        c = _minimal_contract(
            route_risk=RouteRisk(
                cost_band=RiskBand.LOW,
                latency_band=RiskBand.LOW,
                safety_band=RiskBand.HIGH,
                reversibility=Reversibility.READ,
            )
        )
        with pytest.raises(PlanContractViolation, match="plan_signature is required"):
            c.require_signed_for_dispatch()

    def test_require_signed_for_dispatch_low_risk_unsigned_ok(self):
        """Default low-risk READ plans don't require a signature."""
        _minimal_contract().require_signed_for_dispatch()  # must not raise

    def test_require_signed_for_dispatch_rejects_stale_signature(self):
        """Signature computed over old body is stale when body has been perturbed."""
        c = _minimal_contract(pattern=PlanPattern.AUGMENTED_CALL)
        # Bind a deliberately wrong signature (64 hex chars that is valid hex
        # but does not match the body).
        bad = L1PlanContractV2(
            plan_id=c.plan_id,
            request_id=c.request_id,
            policy_hash=c.policy_hash,
            proposed_route=c.proposed_route,
            reasoning_mode=c.reasoning_mode,
            query_spec=c.query_spec,
            task_spec=c.task_spec,
            route_risk=c.route_risk,
            confidence_score=c.confidence_score,
            grounding_required=c.grounding_required,
            declared_assumptions=c.declared_assumptions,
            unresolved_gaps=c.unresolved_gaps,
            published_rationale=c.published_rationale,
            planner_telemetry=c.planner_telemetry,
            pattern=c.pattern,
            plan_signature="a" * 64,  # stale / wrong
        )
        with pytest.raises(PlanContractViolation, match="stale"):
            bad.require_signed_for_dispatch()


class TestFromV1ForwardMigration:
    """from_v1 must populate v3.1 fields with safe defaults (back-compat)."""

    def test_from_v1_has_empty_extensions(self):
        from agentic_core.L1_cognition.types.plan_contract_types import L1PlanContract

        v1 = L1PlanContract(
            plan_id="p",
            request_id="r",
            policy_hash="h",
            reasoning_mode=ReasoningMode.DIRECT,
            grounding_required=False,
            confidence_score=0.8,
            steps=({"step_id": "s1", "desc": "x"},),
        )
        v2 = L1PlanContractV2.from_v1(
            v1,
            proposed_route=ProposedRoute.R1A,
            route_risk=_base_route_risk(),
            task_spec=(_base_step("s1"),),
        )
        # extensions at safe defaults
        assert v2.pattern is None
        assert v2.reasoning_effort is None
        assert v2.iteration_cap is None
        assert v2.stop_conditions == ()
        assert v2.hitl_checkpoints == ()
        assert v2.replan_policy is None
        assert v2.plan_signature is None
        assert v2.escalation_reason is None
        assert v2.step_annotations == ()
        v2.validate()  # must still validate


class TestIntegrationComposition:
    """Real-world composite cases — all features combined."""

    def test_full_agent_plan_end_to_end(self):
        cp = HITLCheckpoint(after_step_id="s1", trigger=HITLCheckpointTrigger.ON_POLICY_BOUND)
        ann = PlanStepAnnotation(
            step_id="s1",
            model_hint="reasoning",
            augmentations=(Augmentation.RETRIEVAL, Augmentation.TOOLS, Augmentation.MEMORY),
        )
        c = _minimal_contract(
            pattern=PlanPattern.AGENT,
            escalation_reason="open-ended tool loop required",
            reasoning_effort=ReasoningEffort.HIGH,
            iteration_cap=IterationCap(max_steps=20, max_retries=3, max_critic_rounds=2),
            stop_conditions=("schema_valid", "budget_not_exceeded"),
            hitl_checkpoints=(cp,),
            replan_policy=ReplanPolicy(
                on_ground_truth_mismatch=ReplanAction.REPLAN,
                on_tool_failure=ReplanAction.ESCALATE_HITL,
                on_policy_block=ReplanAction.ABSTAIN,
                budget=3,
            ),
            step_annotations=(ann,),
        ).with_signature()
        c.validate()
        c.require_signed_for_dispatch()
        d = c.to_dict()
        # all extension keys present in serialization
        assert d["pattern"] == "PTN_7_AGENT"
        assert d["reasoning_effort"] == "HIGH"
        assert d["iteration_cap"]["max_steps"] == 20
        assert d["stop_conditions"] == ["schema_valid", "budget_not_exceeded"]
        assert d["hitl_checkpoints"][0]["trigger"] == "ON_POLICY_BOUND"
        assert d["replan_policy"]["budget"] == 3
        assert d["step_annotations"][0]["augmentations"] == ["RETRIEVAL", "TOOLS", "MEMORY"]
        assert d["plan_signature"] is not None
        assert c.to_v1().plan_id == c.plan_id  # v1 projection still works

    def test_large_task_spec_with_annotations(self):
        """50-step plan with per-step annotations — validate() scales."""
        steps = tuple(_base_step(f"s{i}") for i in range(50))
        anns = tuple(
            PlanStepAnnotation(
                step_id=f"s{i}",
                model_hint="fast" if i % 2 else "reasoning",
                augmentations=(Augmentation.RETRIEVAL,) if i % 3 == 0 else (),
            )
            for i in range(50)
        )
        c = _minimal_contract(
            task_spec=steps,
            step_annotations=anns,
            pattern=PlanPattern.ORCHESTRATOR_WORKERS,
            escalation_reason="dynamic decomposition",
        )
        c.validate()  # must not raise
        assert len(c.step_annotations) == 50


class TestEnumCoverage:
    """Every enum member must be constructible, valuable, and round-trip."""

    @pytest.mark.parametrize("member", list(PlanPattern))
    def test_plan_pattern_every_member(self, member):
        assert isinstance(member.value, str)
        assert member.value.startswith("PTN_")

    @pytest.mark.parametrize("member", list(ReasoningEffort))
    def test_reasoning_effort_every_member(self, member):
        assert member.value in {"LOW", "MEDIUM", "HIGH"}

    @pytest.mark.parametrize("member", list(Augmentation))
    def test_augmentation_every_member(self, member):
        assert member.value == member.name

    @pytest.mark.parametrize("member", list(HITLCheckpointTrigger))
    def test_hitl_trigger_every_member(self, member):
        cp = HITLCheckpoint(after_step_id="s1", trigger=member)
        _minimal_contract(hitl_checkpoints=(cp,)).validate()

    @pytest.mark.parametrize("member", list(ReplanAction))
    def test_replan_action_every_member(self, member):
        ReplanPolicy(on_ground_truth_mismatch=member).to_dict()


class TestBaselineV2StillWorks:
    """Regression fence: the pre-extension v2 tests should still apply."""

    def test_grounding_requires_query_spec(self):
        with pytest.raises(PlanContractViolation, match="query_spec"):
            _minimal_contract(grounding_required=True, query_spec=None).validate()

    def test_grounding_with_query_spec_ok(self):
        _minimal_contract(
            grounding_required=True,
            query_spec=QuerySpec(query_text="q", freshness_window_s=60, max_results=10),
            proposed_route=ProposedRoute.R3,
        ).validate()

    def test_clarify_cannot_require_grounding(self):
        with pytest.raises(PlanContractViolation, match="CLARIFY"):
            _minimal_contract(
                proposed_route=ProposedRoute.CLARIFY,
                grounding_required=True,
                query_spec=QuerySpec(query_text="q", freshness_window_s=60, max_results=10),
            ).validate()
