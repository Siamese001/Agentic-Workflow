"""Exhaustive contract-validation edge cases for the L1 v6 planning module.

For every ``raise L1ContractViolation`` site in
:mod:`agentic_core.L1_cognition.planning.contracts` this module crafts an
input that triggers exactly that rejection, plus boundary tests on every
numeric range and exhaustive coverage tests on every closed enum.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.planning import (
    ActionExpectation,
    ClarifyAbstainFallbackMarker,
    DependencySketch,
    DownstreamPlanningNotes,
    DraftPlan,
    FinalPlanReadinessReceipt,
    FirstSafetyAuthorityReading,
    InternalPlanState,
    JobClassFrame,
    L1ContractViolation,
    L1HandoffReceipt,
    L1PlanContract,
    L1SelfRepairLedger,
    LowestViableAgencyReceipt,
    NonAuthorityAssertion,
    ParsedRequestInput,
    PlanDigest,
    PlanReplayManifest,
    PlanValidationReport,
    PlanningLoopBudgetReceipt,
    PlanningPriorReadInput,
    PlanningRefinementPass,
    PlanningReasoningInput,
    ProposedRouteHint,
    QuerySpec,
    ReasoningQualitySignals,
    RequestDetailInventory,
    RouteHintSet,
    SupportExpectation,
    TaskSpec,
    WorkUnit,
    WorkUnitSet,
    WorkUnitType,
)
from agentic_core.L1_cognition.planning.contracts import (
    AmbiguitySeverity,
    IntentFrameSnapshot,
    L1PlanContractInput,
    L1TelemetryKeySet,
    PassStatus,
    PlanConsistencyAudit,
    ReferenceClass,
    RepairAction,
    ValidationStatus,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _baseline_intent_snapshot() -> IntentFrameSnapshot:
    return IntentFrameSnapshot(
        request_id="req-ec-1",
        intent_frame_id="if::req-ec-1",
        normalized_goal="Goal under test",
        user_visible_deliverable="answer",
        work_class="summarize",
        audience="user",
        output_target_kind="answer",
        freshness_class="stable",
        action_requirement="none",
        artifact_requirement="inline",
        high_risk=False,
        constraints=(),
        details=(),
        ambiguity={
            "known": [],
            "assumed": [],
            "unresolved": [],
            "resolution_strategy": "assume",
            "mistaken_premise": [],
            "conflicts": [],
            "unstated_likely": [],
        },
        success_condition="ok",
    )


def _baseline_work_unit() -> WorkUnit:
    return WorkUnit(
        work_unit_id="wu::1",
        description="primary",
        work_unit_type=WorkUnitType.SUMMARIZE,
    )


# ---------------------------------------------------------------------------
# ParsedRequestInput
# ---------------------------------------------------------------------------


def test_parsed_request_input_rejects_blank_request_id():
    with pytest.raises(L1ContractViolation):
        ParsedRequestInput(
            request_id="",
            session_id="s",
            trace_root="t",
            caller_scope_baseline="b",
            normalized_user_payload="x",
            validated_request={"k": "v"},
        )


def test_parsed_request_input_rejects_blank_trace_root():
    with pytest.raises(L1ContractViolation):
        ParsedRequestInput(
            request_id="r",
            session_id="s",
            trace_root="",
            caller_scope_baseline="b",
            normalized_user_payload="x",
            validated_request={"k": "v"},
        )


def test_parsed_request_input_accepts_blank_session_id():
    """session_id is allow_empty=True per contract."""
    pi = ParsedRequestInput(
        request_id="r",
        session_id="",
        trace_root="t",
        caller_scope_baseline="b",
        normalized_user_payload="x",
        validated_request={"k": "v"},
    )
    assert pi.session_id == ""


def test_parsed_request_input_rejects_non_str_request_id():
    with pytest.raises(L1ContractViolation):
        ParsedRequestInput(
            request_id=123,  # type: ignore[arg-type]
            session_id="s",
            trace_root="t",
            caller_scope_baseline="b",
            normalized_user_payload="x",
            validated_request={"k": "v"},
        )


def test_parsed_request_input_to_dict_does_not_leak_validated_request_object():
    """The validated_request object itself should not appear in the canonical
    dict — only the boolean flag has_validated_request."""
    pi = ParsedRequestInput(
        request_id="r",
        session_id="s",
        trace_root="t",
        caller_scope_baseline="b",
        normalized_user_payload="x",
        validated_request={"sensitive": "data"},
    )
    d = pi.to_dict()
    assert d["has_validated_request"] is True
    assert "sensitive" not in str(d)


# ---------------------------------------------------------------------------
# RequestDetailInventory
# ---------------------------------------------------------------------------


def test_request_detail_inventory_rejects_non_str_in_files():
    with pytest.raises(L1ContractViolation):
        RequestDetailInventory(files=(123,))  # type: ignore[arg-type]


def test_request_detail_inventory_accepts_all_empty():
    inv = RequestDetailInventory()
    d = inv.to_dict()
    assert d["entities"] == []
    assert d["direct_quote_needed"] is False


# ---------------------------------------------------------------------------
# JobClassFrame
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "work_class",
    [
        "summarize", "compare", "explain", "analyze", "plan", "act",
        "create", "edit", "retrieve", "decide", "escalate",
        "factual", "creative", "mathematical", "code", "unknown",
    ],
)
def test_job_class_frame_accepts_every_doctrine_work_class(work_class):
    """The 11 doctrine classes plus the 5 underlying-WorkClass-enum classes."""
    jcf = JobClassFrame(
        work_class=work_class, is_artifact_or_action=False, is_high_risk=False
    )
    assert jcf.work_class == work_class


def test_job_class_frame_rejects_unknown_work_class():
    with pytest.raises(L1ContractViolation):
        JobClassFrame(
            work_class="not_a_real_class",
            is_artifact_or_action=False,
            is_high_risk=False,
        )


def test_job_class_frame_rejects_blank_work_class():
    with pytest.raises(L1ContractViolation):
        JobClassFrame(work_class="", is_artifact_or_action=False, is_high_risk=False)


# ---------------------------------------------------------------------------
# FirstSafetyAuthorityReading
# ---------------------------------------------------------------------------


def test_first_safety_authority_reading_rejects_blank_request_id():
    with pytest.raises(L1ContractViolation):
        FirstSafetyAuthorityReading(request_id="")


def test_first_safety_authority_reading_rejects_non_str_risk_notes():
    with pytest.raises(L1ContractViolation):
        FirstSafetyAuthorityReading(
            request_id="r",
            risk_notes=(123,),  # type: ignore[arg-type]
        )


def test_first_safety_authority_reading_to_dict_roundtrip():
    fsar = FirstSafetyAuthorityReading(
        request_id="r",
        authority_override_attempt=True,
        risk_notes=("injection:override system",),
    )
    d = fsar.to_dict()
    assert d["authority_override_attempt"] is True
    assert d["risk_notes"] == ["injection:override system"]


# ---------------------------------------------------------------------------
# PlanningPriorReadInput
# ---------------------------------------------------------------------------


def test_planning_prior_read_input_rejects_negative_budget():
    snap = _baseline_intent_snapshot()
    with pytest.raises(L1ContractViolation):
        PlanningPriorReadInput(
            intent_frame=snap,
            ambiguity_register={},
            first_safety_authority_reading=FirstSafetyAuthorityReading(request_id="r"),
            request_id="r",
            trace_root="t",
            caller_scope_baseline="b",
            policy_hash_observed="p",
            instruction_hash_observed="i",
            planning_prior_budget=-1,
        )


def test_planning_prior_read_input_rejects_non_tuple_allowed_classes():
    snap = _baseline_intent_snapshot()
    with pytest.raises(L1ContractViolation):
        PlanningPriorReadInput(
            intent_frame=snap,
            ambiguity_register={},
            first_safety_authority_reading=FirstSafetyAuthorityReading(request_id="r"),
            request_id="r",
            trace_root="t",
            caller_scope_baseline="b",
            policy_hash_observed="p",
            instruction_hash_observed="i",
            allowed_planning_reference_classes=["task_schemas"],  # type: ignore[arg-type]
        )


def test_planning_prior_read_input_serialises_reference_class_enums():
    snap = _baseline_intent_snapshot()
    pi = PlanningPriorReadInput(
        intent_frame=snap,
        ambiguity_register={},
        first_safety_authority_reading=FirstSafetyAuthorityReading(request_id="r"),
        request_id="r",
        trace_root="t",
        caller_scope_baseline="b",
        policy_hash_observed="p",
        instruction_hash_observed="i",
        allowed_planning_reference_classes=(ReferenceClass.TASK_SCHEMAS,),
        blocked_planning_reference_classes=(ReferenceClass.REFUSAL_TAXONOMY,),
    )
    d = pi.to_dict()
    assert d["allowed_planning_reference_classes"] == ["task_schemas"]
    assert d["blocked_planning_reference_classes"] == ["refusal_taxonomy"]


@pytest.mark.parametrize("cls", list(ReferenceClass))
def test_every_reference_class_has_string_value(cls):
    """Each of the 14 doctrine reference classes round-trips to/from str."""
    assert isinstance(cls.value, str)
    assert ReferenceClass(cls.value) is cls


# ---------------------------------------------------------------------------
# PlanningReasoningInput
# ---------------------------------------------------------------------------


def test_planning_reasoning_input_rejects_negative_max_passes():
    snap = _baseline_intent_snapshot()
    from agentic_core.L1_cognition.planning import PlanBundleSnapshot
    bundle = PlanBundleSnapshot(
        bundle_id="pb::test", bundle_hash="hash", schemas=(), route_heuristics=(),
        output_contracts=(), validation_rubric=(), policy_bounds=(),
        escalation_thresholds=(), disallowed_actions=(), hitl_triggers=(),
        exemplars=(), edge_cases=(), approved_templates=(), stopping_rules=(),
        retry_boundaries=(), abstain_patterns=(), max_steps=10, max_wallclock_ms=60000,
        rule_aware_planning_frame={"can_be_proposed": [], "must_be_grounded": [], "must_be_escalated": []},
    )
    with pytest.raises(L1ContractViolation):
        PlanningReasoningInput(
            intent_frame=snap,
            ambiguity_register={},
            request_detail_inventory=RequestDetailInventory(),
            first_safety_authority_reading=FirstSafetyAuthorityReading(request_id="r"),
            plan_bundle=bundle,
            rule_aware_planning_frame={},
            request_id="r",
            trace_root="t",
            policy_hash_observed="p",
            instruction_hash_observed="i",
            max_refinement_passes=-1,
        )


def test_planning_reasoning_input_rejects_negative_budget():
    snap = _baseline_intent_snapshot()
    from agentic_core.L1_cognition.planning import PlanBundleSnapshot
    bundle = PlanBundleSnapshot(
        bundle_id="pb::test", bundle_hash="hash", schemas=(), route_heuristics=(),
        output_contracts=(), validation_rubric=(), policy_bounds=(),
        escalation_thresholds=(), disallowed_actions=(), hitl_triggers=(),
        exemplars=(), edge_cases=(), approved_templates=(), stopping_rules=(),
        retry_boundaries=(), abstain_patterns=(), max_steps=10, max_wallclock_ms=60000,
        rule_aware_planning_frame={"can_be_proposed": [], "must_be_grounded": [], "must_be_escalated": []},
    )
    with pytest.raises(L1ContractViolation):
        PlanningReasoningInput(
            intent_frame=snap,
            ambiguity_register={},
            request_detail_inventory=RequestDetailInventory(),
            first_safety_authority_reading=FirstSafetyAuthorityReading(request_id="r"),
            plan_bundle=bundle,
            rule_aware_planning_frame={},
            request_id="r",
            trace_root="t",
            policy_hash_observed="p",
            instruction_hash_observed="i",
            reasoning_budget=-1,
        )


# ---------------------------------------------------------------------------
# PlanningLoopBudgetReceipt
# ---------------------------------------------------------------------------


def test_planning_loop_budget_receipt_rejects_passes_used_above_max():
    with pytest.raises(L1ContractViolation):
        PlanningLoopBudgetReceipt(
            max_refinement_passes=2,
            passes_used=3,
            reasoning_budget_initial=100,
            reasoning_budget_remaining=50,
            stopped_reason="x",
        )


def test_planning_loop_budget_receipt_rejects_negative_remaining_budget():
    with pytest.raises(L1ContractViolation):
        PlanningLoopBudgetReceipt(
            max_refinement_passes=2,
            passes_used=1,
            reasoning_budget_initial=100,
            reasoning_budget_remaining=-1,
            stopped_reason="x",
        )


def test_planning_loop_budget_receipt_passes_equal_to_max_is_ok():
    r = PlanningLoopBudgetReceipt(
        max_refinement_passes=2,
        passes_used=2,
        reasoning_budget_initial=100,
        reasoning_budget_remaining=0,
        stopped_reason="max_reached",
    )
    assert r.passes_used == 2


# ---------------------------------------------------------------------------
# ReasoningQualitySignals
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("score", [-0.01, 1.01, 1.5, -1.0, 999])
def test_reasoning_quality_signals_rejects_score_out_of_range(score):
    with pytest.raises(L1ContractViolation):
        ReasoningQualitySignals(constraints_preserved_score=score)


@pytest.mark.parametrize("score", [0.0, 0.001, 0.5, 0.999, 1.0])
def test_reasoning_quality_signals_accepts_score_in_range(score):
    rqs = ReasoningQualitySignals(constraints_preserved_score=score)
    assert rqs.constraints_preserved_score == score


@pytest.mark.parametrize("band", ["low", "medium", "high"])
def test_reasoning_quality_signals_accepts_each_band(band):
    rqs = ReasoningQualitySignals(overall_quality_band=band)
    assert rqs.overall_quality_band == band


def test_reasoning_quality_signals_rejects_unknown_band():
    with pytest.raises(L1ContractViolation):
        ReasoningQualitySignals(overall_quality_band="excellent")


def test_reasoning_quality_signals_rejects_non_numeric_score():
    with pytest.raises(L1ContractViolation):
        ReasoningQualitySignals(constraints_preserved_score="high")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# PlanningRefinementPass + PassStatus
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", list(PassStatus))
def test_every_pass_status_value_is_serialisable(status):
    p = PlanningRefinementPass(
        pass_id="p", pass_index=0, input_state_digest="x",
        refinement_focus="f", pass_status=status,
    )
    assert p.to_dict()["pass_status"] == status.value


# ---------------------------------------------------------------------------
# WorkUnit / WorkUnitSet
# ---------------------------------------------------------------------------


def test_work_unit_rejects_blank_id():
    with pytest.raises(L1ContractViolation):
        WorkUnit(work_unit_id="", description="d", work_unit_type=WorkUnitType.INTERPRET)


def test_work_unit_rejects_blank_description():
    with pytest.raises(L1ContractViolation):
        WorkUnit(work_unit_id="u", description="", work_unit_type=WorkUnitType.INTERPRET)


def test_work_unit_rejects_non_enum_type():
    with pytest.raises(L1ContractViolation):
        WorkUnit(
            work_unit_id="u", description="d",
            work_unit_type="interpret",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("kind", list(WorkUnitType))
def test_every_work_unit_type_constructs(kind):
    u = WorkUnit(work_unit_id=f"u::{kind.value}", description="d", work_unit_type=kind)
    assert u.work_unit_type is kind


def test_work_unit_set_rejects_str_units():
    with pytest.raises(L1ContractViolation):
        WorkUnitSet(units="not a tuple")  # type: ignore[arg-type]


def test_work_unit_set_rejects_non_workunit_member():
    with pytest.raises(L1ContractViolation):
        WorkUnitSet(units=(_baseline_work_unit(), {"not": "a workunit"}))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# RouteHintSet — boundaries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("c", [-0.0001, 1.0001, 2.0, -1.0, 1.5])
def test_route_hint_set_rejects_confidence_out_of_range(c):
    with pytest.raises(L1ContractViolation):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
            confidence=c,
        )


@pytest.mark.parametrize("c", [0.0, 0.5, 1.0])
def test_route_hint_set_accepts_confidence_at_boundaries(c):
    r = RouteHintSet(
        route_hint_id="x",
        proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
        confidence=c,
    )
    assert r.confidence == c


def test_route_hint_set_rejects_non_enum_route():
    with pytest.raises(L1ContractViolation):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint="R3",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("hint", list(ProposedRouteHint))
def test_every_proposed_route_hint_value_constructs(hint):
    r = RouteHintSet(
        route_hint_id=f"r::{hint.value}",
        proposed_route_hint=hint,
    )
    assert r.proposed_route_hint is hint


@pytest.mark.parametrize("bad", ["committed", "selected", "decided", "AUTHORITATIVE", ""])
def test_route_hint_set_rejects_any_authority_assertion_other_than_advisory_only(bad):
    with pytest.raises(L1ContractViolation):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
            route_authority_assertion=bad,
        )


# ---------------------------------------------------------------------------
# NonAuthorityAssertion — every flag must be True
# ---------------------------------------------------------------------------


_FLAG_NAMES = (
    "no_evidence_retrieval",
    "no_final_route_commitment",
    "no_tool_execution",
    "no_model_execution_for_work",
    "no_durable_state_mutation",
    "no_external_provider_call_for_work",
    "no_final_egress_approval",
    "no_hitl_approval",
    "no_uwg_commit",
    "no_learning_promotion",
)


@pytest.mark.parametrize("flag", _FLAG_NAMES)
def test_non_authority_assertion_rejects_each_flag_individually(flag):
    """Every one of the 10 NonAuthorityAssertion flags MUST be True for handoff."""
    kwargs = {f: True for f in _FLAG_NAMES}
    kwargs[flag] = False
    with pytest.raises(L1ContractViolation):
        NonAuthorityAssertion(**kwargs)


def test_non_authority_assertion_default_construction_all_true():
    naa = NonAuthorityAssertion()
    d = naa.to_dict()
    assert all(v is True for v in d.values())
    assert len(d) == 10


# ---------------------------------------------------------------------------
# L1HandoffReceipt
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wrong_target",
    ["L1_REASONING", "L0", "L0_ROUTE", "L2_EXECUTION", "C0", "L5", ""],
)
def test_l1_handoff_receipt_rejects_any_target_other_than_l0_route_decision(wrong_target):
    with pytest.raises(L1ContractViolation):
        L1HandoffReceipt(
            handoff_receipt_id="hr",
            l1_plan_id="lp",
            target_layer=wrong_target,
            handoff_time_policy="immediate",
            plan_digest="sha256:0",
            trace_root="t",
            request_id="r",
            readiness_status="ready",
            non_authority_assertion_ref="ref",
        )


# ---------------------------------------------------------------------------
# L1PlanContract — schema invariants
# ---------------------------------------------------------------------------


_VALID_VALIDATION_SUMMARY = {
    "no_retrieval_performed": True,
    "no_execution_performed": True,
    "no_write_performed": True,
}


def _build_l1_contract(**overrides):
    base = dict(
        layer="L1_REASONING_PLAN_GENERATION",
        version="v6",
        authority="advisory_plan_only",
        identity={},
        intent_frame={},
        query_spec=None,
        task_spec={},
        route_hint={
            "proposed_route_hint": "R3_GROUNDED_READ",
            "route_authority_assertion": "advisory_only",
        },
        support_expectation={},
        action_expectation={},
        assumptions_and_gaps={},
        validation_summary=dict(_VALID_VALIDATION_SUMMARY),
        downstream_notes={},
        plan_replay_manifest={},
        plan_digest=PlanDigest(digest="sha256:0"),
        non_authority_assertion=NonAuthorityAssertion(),
    )
    base.update(overrides)
    return base


def test_l1_plan_contract_baseline_constructs():
    L1PlanContract(**_build_l1_contract())


@pytest.mark.parametrize("wrong_layer", ["L0_ROUTING", "L2_EXECUTION", "", "l1"])
def test_l1_plan_contract_rejects_wrong_layer(wrong_layer):
    with pytest.raises(L1ContractViolation):
        L1PlanContract(**_build_l1_contract(layer=wrong_layer))


@pytest.mark.parametrize("wrong_authority", ["committed", "executed", "decided", ""])
def test_l1_plan_contract_rejects_wrong_authority(wrong_authority):
    with pytest.raises(L1ContractViolation):
        L1PlanContract(**_build_l1_contract(authority=wrong_authority))


@pytest.mark.parametrize("forbidden_key", ["route_digest", "hmac_sig"])
def test_l1_plan_contract_rejects_forbidden_route_keys(forbidden_key):
    bad_route = {
        "proposed_route_hint": "R3_GROUNDED_READ",
        "route_authority_assertion": "advisory_only",
        forbidden_key: "naughty",
    }
    with pytest.raises(L1ContractViolation):
        L1PlanContract(**_build_l1_contract(route_hint=bad_route))


@pytest.mark.parametrize(
    "missing_key",
    ["no_retrieval_performed", "no_execution_performed", "no_write_performed"],
)
def test_l1_plan_contract_rejects_validation_summary_with_false_invariant(missing_key):
    vs = dict(_VALID_VALIDATION_SUMMARY)
    vs[missing_key] = False
    with pytest.raises(L1ContractViolation):
        L1PlanContract(**_build_l1_contract(validation_summary=vs))


# ---------------------------------------------------------------------------
# PlanReplayManifest — every excluded_volatile_field is listed
# ---------------------------------------------------------------------------


_EXCLUDED_VOLATILE_FIELDS = (
    "wall_clock_time",
    "nondeterministic_memory_ids",
    "transient_span_ids",
    "provider_latency",
    "local_filesystem_temp_names",
)


@pytest.mark.parametrize("excluded", _EXCLUDED_VOLATILE_FIELDS)
def test_plan_replay_manifest_default_excludes_every_doctrine_volatile_field(excluded):
    manifest = PlanReplayManifest(
        manifest_id="m",
        normalized_request_hash="h",
        visible_context_hash="h",
        intent_frame_hash="h",
        plan_bundle_hash="h",
        internal_plan_state_hash="h",
        draft_plan_hash="h",
        validation_report_hash="h",
        policy_hash="p",
        instruction_hash="i",
        source_envelope_id="e",
    )
    assert excluded in manifest.excluded_volatile_fields


def test_plan_replay_manifest_default_algorithm_is_canonical_json_v1():
    manifest = PlanReplayManifest(
        manifest_id="m",
        normalized_request_hash="h",
        visible_context_hash="h",
        intent_frame_hash="h",
        plan_bundle_hash="h",
        internal_plan_state_hash="h",
        draft_plan_hash="h",
        validation_report_hash="h",
        policy_hash="p",
        instruction_hash="i",
        source_envelope_id="e",
    )
    assert manifest.deterministic_digest_algorithm == "sha256-canonical-json-v1"


# ---------------------------------------------------------------------------
# PlanValidationReport — has_failures / has_warnings / is_pass
# ---------------------------------------------------------------------------


def _empty_report(**overrides) -> PlanValidationReport:
    base = dict(
        report_id="r",
        listened_to_user_status=ValidationStatus.PASS,
        constraints_preserved_status=ValidationStatus.PASS,
        deliverable_fit_status=ValidationStatus.PASS,
        style_format_fit_status=ValidationStatus.PASS,
        safety_checked_status=ValidationStatus.PASS,
        coherent_plan_status=ValidationStatus.PASS,
        route_hint_consistency_status=ValidationStatus.PASS,
        support_expectation_status=ValidationStatus.PASS,
        action_expectation_status=ValidationStatus.PASS,
        lowest_viable_agency_status=ValidationStatus.PASS,
    )
    base.update(overrides)
    return PlanValidationReport(**base)


def test_validation_report_clean_is_pass():
    assert _empty_report().is_pass() is True


def test_validation_report_with_fail_is_not_pass():
    assert _empty_report(safety_checked_status=ValidationStatus.FAIL).is_pass() is False


def test_validation_report_with_not_run_is_not_pass():
    """NOT_RUN must be treated as failure (post-hardening invariant)."""
    assert _empty_report(coherent_plan_status=ValidationStatus.NOT_RUN).is_pass() is False


def test_validation_report_with_warn_is_still_pass():
    assert _empty_report(listened_to_user_status=ValidationStatus.WARN).is_pass() is True


def test_validation_report_has_failures_on_fail_status():
    assert _empty_report(safety_checked_status=ValidationStatus.FAIL).has_failures() is True


def test_validation_report_has_failures_on_not_run():
    assert _empty_report(safety_checked_status=ValidationStatus.NOT_RUN).has_failures() is True


def test_validation_report_has_failures_on_failure_finding():
    assert _empty_report(validation_failures=("some failure",)).has_failures() is True


def test_validation_report_has_warnings_on_warn_status():
    assert _empty_report(listened_to_user_status=ValidationStatus.WARN).has_warnings() is True


def test_validation_report_has_warnings_on_warning_finding():
    assert _empty_report(validation_warnings=("some warning",)).has_warnings() is True


def test_validation_report_clean_has_no_failures_or_warnings():
    r = _empty_report()
    assert r.has_failures() is False
    assert r.has_warnings() is False


# ---------------------------------------------------------------------------
# PlanConsistencyAudit — all_consistent flips False when any flag is False
# ---------------------------------------------------------------------------


_AUDIT_FLAGS = (
    "cache_hint_freshness_consistent",
    "grounded_read_marks_c0",
    "single_action_bounded",
    "managed_workflow_justified",
    "fallback_reason_present",
    "durable_mutation_marks_uwg",
    "high_risk_marks_hitl",
    "confidence_matches_evidence",
    "full_overwrite_preserves_structure",
)


@pytest.mark.parametrize("flag", _AUDIT_FLAGS)
def test_plan_consistency_audit_all_consistent_returns_false_when_any_flag_is_false(flag):
    kwargs = {f: True for f in _AUDIT_FLAGS}
    kwargs[flag] = False
    audit = PlanConsistencyAudit(**kwargs)
    assert audit.all_consistent() is False


def test_plan_consistency_audit_all_true_returns_true():
    audit = PlanConsistencyAudit()  # all defaults are True
    assert audit.all_consistent() is True


# ---------------------------------------------------------------------------
# L1SelfRepairLedger — passes_used <= max_passes invariant
# ---------------------------------------------------------------------------


def test_l1_self_repair_ledger_rejects_passes_used_above_max_passes():
    with pytest.raises(L1ContractViolation):
        L1SelfRepairLedger(
            ledger_id="l", max_passes=2, passes_used=3,
        )


def test_l1_self_repair_ledger_passes_equal_to_max_is_ok():
    ledger = L1SelfRepairLedger(ledger_id="l", max_passes=2, passes_used=2)
    assert ledger.passes_used == 2


# ---------------------------------------------------------------------------
# ClarifyAbstainFallbackMarker — is_active for each combination
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "flag",
    ["clarify_recommended", "abstain_recommended", "fallback_recommended", "policy_review_recommended"],
)
def test_clarify_abstain_fallback_marker_is_active_when_any_flag_set(flag):
    marker = ClarifyAbstainFallbackMarker(marker_id="m", **{flag: True})
    assert marker.is_active() is True


def test_clarify_abstain_fallback_marker_inactive_when_all_flags_false():
    marker = ClarifyAbstainFallbackMarker(marker_id="m")
    assert marker.is_active() is False


# ---------------------------------------------------------------------------
# Enum coverage — every value used somewhere in the module surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", list(ValidationStatus))
def test_every_validation_status_value_round_trips_through_to_dict(status):
    r = _empty_report(safety_checked_status=status)
    assert r.to_dict()["safety_checked_status"] == status.value


@pytest.mark.parametrize("severity", list(AmbiguitySeverity))
def test_every_ambiguity_severity_value_is_serialisable(severity):
    assert isinstance(severity.value, str)
    assert AmbiguitySeverity(severity.value) is severity


@pytest.mark.parametrize("action", list(RepairAction))
def test_every_repair_action_value_is_serialisable(action):
    assert isinstance(action.value, str)
    assert RepairAction(action.value) is action


# ---------------------------------------------------------------------------
# QuerySpec / TaskSpec / DownstreamPlanningNotes — minimal-construction tests
# ---------------------------------------------------------------------------


def test_query_spec_round_trips_through_to_dict():
    qs = QuerySpec(
        normalized_request="x",
        files_or_sources=("a.md", "b.md"),
        currentness_mandatory=True,
    )
    d = qs.to_dict()
    assert d["normalized_request"] == "x"
    assert d["files_or_sources"] == ["a.md", "b.md"]
    assert d["currentness_mandatory"] is True


def test_task_spec_round_trips_through_to_dict():
    ts = TaskSpec(
        work_units=("step1", "step2"),
        output_target="answer",
        output_format="inline",
    )
    d = ts.to_dict()
    assert d["work_units"] == ["step1", "step2"]
    assert d["partial_completion_allowed"] is True


def test_downstream_planning_notes_six_consumer_keys_present():
    notes = DownstreamPlanningNotes()
    d = notes.to_dict()
    for key in ("for_l0", "for_c0", "for_prompt_assembly", "for_l2", "for_exit_control", "for_l6"):
        assert key in d
        assert d[key] == []


# ---------------------------------------------------------------------------
# L1TelemetryKeySet — span coverage
# ---------------------------------------------------------------------------


def test_l1_telemetry_key_set_carries_18_canonical_span_names():
    """Per stage 02.6 doctrine, the telemetry key set carries every L1 stage span."""
    expected_spans = (
        "l1.02.1.input.accepted", "l1.02.1.core.completed", "l1.02.1.output.emitted",
        "l1.02.2.input.accepted", "l1.02.2.core.completed", "l1.02.2.output.emitted",
        "l1.02.3.input.accepted", "l1.02.3.core.completed", "l1.02.3.output.emitted",
        "l1.02.4.input.accepted", "l1.02.4.core.completed", "l1.02.4.output.emitted",
        "l1.02.5.input.accepted", "l1.02.5.core.completed", "l1.02.5.output.emitted",
        "l1.02.6.input.accepted", "l1.02.6.core.completed", "l1.02.6.output.emitted",
    )
    tks = L1TelemetryKeySet(
        request_id="r", trace_root="t", l1_plan_id="lp", plan_digest="sha256:0",
        span_names=expected_spans,
    )
    assert len(tks.span_names) == 18
    assert all(name.startswith("l1.02.") for name in tks.span_names)
