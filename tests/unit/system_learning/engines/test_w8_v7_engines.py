"""W8 tests — v7 spec gap closures.

Covers: RuntimeExhaustCollector (S1A), IncidentRCAEngine (S3B),
V7RuleDrafter (S3D), PromotionPacket schema, FailureMode taxonomy.
"""

from __future__ import annotations

import pytest

from system_learning.engines.incident_rca_engine import (
    IncidentEvidence,
    IncidentRCAEngine,
    RootCauseClass,
    classify_defects,
    localize_first_bad_span,
)
from system_learning.engines.runtime_exhaust_collector import (
    REQUIRED_LINEAGE_FIELDS,
    ExhaustDefect,
    RuntimeExhaustCollector,
)
from system_learning.engines.v6_kpi_board import V6KPIName
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard
from system_learning.engines.v7_promotion_schemas import (
    CONTAINMENT_TABLE,
    ActivationPolicySpec,
    EvidenceLink,
    FailureMode,
    PromotionPacket,
    validate_promotion_packet,
)
from system_learning.engines.v7_rule_drafter import (
    REQUIRED_DRAFT_FIELDS,
    DraftType,
    IncompleteDraftError,
    V7RuleDrafter,
)


# ---- RuntimeExhaustCollector (S1A) ---------------------------------------


def test_collector_required_lineage_fields_count():
    """Spec lines 158-178 enumerate exactly 21 fields."""
    assert len(REQUIRED_LINEAGE_FIELDS) == 21


def test_collector_detects_all_11_defect_classes():
    """Spec lines 180-191 enumerate exactly 11 detections."""
    assert len(list(ExhaustDefect)) == 11


def test_collector_clean_record_has_no_gaps():
    c = RuntimeExhaustCollector()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["span_sealed"] = True
    rec["span_end_epoch"] = 1000.0
    rec["record_id"] = "r1"
    bundle = c.collect([rec], now_epoch=1100.0)
    assert bundle.gap_report == ()
    assert bundle.ingest_quality_score == 1.0
    assert bundle.newest_span_age_seconds == 100.0


def test_collector_flags_missing_trace_link():
    c = RuntimeExhaustCollector()
    rec = {"record_id": "r1", "run_id": "run-1"}
    bundle = c.collect([rec], now_epoch=1000.0)
    assert len(bundle.gap_report) == 1
    assert ExhaustDefect.MISSING_TRACE_LINK in bundle.gap_report[0].detected_defects


def test_collector_flags_orphan_artifact():
    c = RuntimeExhaustCollector()
    rec = {"record_id": "r1", "artifact_digest": "ad-1"}
    bundle = c.collect([rec], now_epoch=1000.0)
    defects = bundle.gap_report[0].detected_defects
    assert ExhaustDefect.ORPHAN_ARTIFACT in defects


def test_collector_flags_unsealed_span():
    c = RuntimeExhaustCollector()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["record_id"] = "r1"
    rec["span_sealed"] = False
    bundle = c.collect([rec], now_epoch=1000.0)
    assert ExhaustDefect.UNSEALED_SPAN in bundle.gap_report[0].detected_defects


def test_collector_flags_impossible_stage_order():
    c = RuntimeExhaustCollector()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["record_id"] = "r1"
    rec["step_id"] = 1
    rec["prior_step_id"] = 5
    bundle = c.collect([rec], now_epoch=1000.0)
    assert ExhaustDefect.IMPOSSIBLE_STAGE_ORDER in bundle.gap_report[0].detected_defects


def test_collector_flags_policy_hash_mismatch():
    c = RuntimeExhaustCollector()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["record_id"] = "r1"
    rec["policy_hash"] = "ph_NOW"
    rec["policy_hash_at_planning"] = "ph_PLANNING"
    bundle = c.collect([rec], now_epoch=1000.0)
    assert ExhaustDefect.POLICY_HASH_MISMATCH in bundle.gap_report[0].detected_defects


def test_collector_flags_duplicate_run_identity():
    c = RuntimeExhaustCollector()
    base = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    base["span_sealed"] = True
    rec1 = dict(base, record_id="r1")
    rec2 = dict(base, record_id="r2")
    bundle = c.collect([rec1, rec2], now_epoch=1000.0)
    second = next(g for g in bundle.gap_report if g.record_id == "r2")
    assert ExhaustDefect.DUPLICATE_RUN_IDENTITY in second.detected_defects


def test_collector_flags_unknown_provider_fallback():
    c = RuntimeExhaustCollector()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["record_id"] = "r1"
    rec["provider_lane"] = "unknown_fallback"
    bundle = c.collect([rec], now_epoch=1000.0)
    assert ExhaustDefect.UNKNOWN_PROVIDER_FALLBACK in bundle.gap_report[0].detected_defects


def test_collector_publishes_trace_ingest_freshness():
    c = RuntimeExhaustCollector()
    board = UnifiedKPIBoard()
    rec = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    rec["span_sealed"] = True
    rec["span_end_epoch"] = 950.0
    rec["record_id"] = "r1"
    bundle = c.collect([rec], now_epoch=1000.0)
    c.publish_kpi_sample(board, bundle)
    sample = board.latest(V6KPIName.TRACE_INGEST_FRESHNESS)
    assert sample.value == 50.0


def test_collector_quality_score_partial():
    c = RuntimeExhaustCollector()
    base = {f: f"v_{f}" for f in REQUIRED_LINEAGE_FIELDS}
    base["span_sealed"] = True
    base["span_end_epoch"] = 1000.0
    good = dict(base, record_id="ok", run_id="run-good")
    bad = {"record_id": "bad"}  # missing everything
    bundle = c.collect([good, bad], now_epoch=1100.0)
    assert bundle.ingest_quality_score == 0.5


# ---- IncidentRCAEngine (S3B) ---------------------------------------------


def test_root_cause_class_count_is_16():
    """Spec lines 711-726 enumerate exactly 16 classes."""
    assert len(list(RootCauseClass)) == 16


def test_localize_first_bad_span_returns_first_failure():
    spans = [
        {"span_id": "s1", "status": "OK"},
        {"span_id": "s2", "status": "OK"},
        {"span_id": "s3", "status": "FAIL"},
        {"span_id": "s4", "status": "ERROR"},
    ]
    assert localize_first_bad_span(spans) == "s3"


def test_localize_first_bad_span_none_when_all_ok():
    spans = [{"span_id": "s1", "status": "OK"}]
    assert localize_first_bad_span(spans) is None


def test_classify_defects_route_miss():
    assert classify_defects(["route_thrash"]) is RootCauseClass.ROUTE_MISS


def test_classify_defects_unknown_when_no_match():
    assert classify_defects(["frobnicate_failure"]) is RootCauseClass.UNKNOWN_ROOT_CAUSE


def test_rca_engine_localizes_and_classifies():
    e = IncidentRCAEngine()
    ev = IncidentEvidence(
        incident_id="inc-1",
        spans=[
            {"span_id": "s1", "status": "OK", "surface": "L0"},
            {"span_id": "s2", "status": "FAIL", "surface": "L1"},
        ],
        eval_record_id="eval-1",
        drift_flags=["retrieval_recall_gap"],
        evidence_links=("trace-1",),
    )
    rca = e.investigate(ev)
    assert rca.first_bad_span == "s2"
    assert rca.root_cause_class is RootCauseClass.RETRIEVAL_RECALL_GAP
    assert rca.confidence == 0.85
    assert rca.failure_chain == ("s1", "s2")


def test_rca_engine_unknown_with_low_confidence():
    e = IncidentRCAEngine()
    ev = IncidentEvidence(
        incident_id="inc-2",
        spans=[{"span_id": "s1", "status": "OK"}],
        eval_record_id="eval-2",
        drift_flags=[],
    )
    rca = e.investigate(ev)
    assert rca.first_bad_span is None
    assert rca.root_cause_class is RootCauseClass.UNKNOWN_ROOT_CAUSE
    assert rca.confidence == 0.20
    assert "first_bad_span_unresolved" in rca.uncertainty_markers
    assert "root_cause_unresolved" in rca.uncertainty_markers


def test_rca_engine_respects_suspected_class():
    e = IncidentRCAEngine()
    ev = IncidentEvidence(
        incident_id="inc-3",
        spans=[{"span_id": "s1", "status": "FAIL"}],
        eval_record_id="eval-3",
        drift_flags=["irrelevant"],
        suspected_class=RootCauseClass.HITL_GATE_ERROR,
        evidence_links=("e1",),
    )
    rca = e.investigate(ev)
    assert rca.root_cause_class is RootCauseClass.HITL_GATE_ERROR


# ---- V7RuleDrafter (S3D) -------------------------------------------------


def test_required_draft_fields_count_is_12():
    """Spec lines 806-818 enumerate exactly 12 mandatory fields."""
    assert len(REQUIRED_DRAFT_FIELDS) == 12


def test_draft_type_count_is_10():
    """Spec lines 820-830 enumerate exactly 10 draft types."""
    assert len(list(DraftType)) == 10


def test_drafter_rejects_incomplete():
    d = V7RuleDrafter()
    with pytest.raises(IncompleteDraftError):
        d.draft(
            draft_id="d1",
            draft_type=DraftType.PROMPT_UPDATE,
            fields_payload={"target_surface": "prompt.X"},  # missing 11 others
        )


def _full_payload() -> dict:
    return {
        "target_surface": "prompt.X",
        "problem_statement": "X is wrong",
        "evidence_link": "trace-1",
        "completed_eval_record_id": "eval-1",
        "rca_packet_id": "rca-1",
        "expected_effect": "fix wrongness",
        "rollback_plan": "revert to v1",
        "blast_radius_statement": "single prompt template",
        "affected_tests": ["test_a", "test_b"],
        "migration_notes": "no schema change",
        "owner_signer_identity": "alice@org",
        "expiration_review_ttl": 9999.0,
    }


def test_drafter_accepts_complete_payload():
    d = V7RuleDrafter()
    pkt = d.draft(
        draft_id="d1",
        draft_type=DraftType.PROMPT_UPDATE,
        fields_payload=_full_payload(),
    )
    assert pkt.draft_id == "d1"
    assert pkt.draft_type is DraftType.PROMPT_UPDATE
    assert pkt.affected_tests == ("test_a", "test_b")


def test_drafter_handles_string_affected_tests():
    d = V7RuleDrafter()
    payload = _full_payload()
    payload["affected_tests"] = "single_test"
    pkt = d.draft(draft_id="d2", draft_type=DraftType.RUBRIC_UPDATE,
                  fields_payload=payload)
    assert pkt.affected_tests == ("single_test",)


def test_drafter_counters_track_built_and_rejected():
    d = V7RuleDrafter()
    d.draft(draft_id="d1", draft_type=DraftType.PROMPT_UPDATE,
            fields_payload=_full_payload())
    with pytest.raises(IncompleteDraftError):
        d.draft(draft_id="d2", draft_type=DraftType.PROMPT_UPDATE,
                fields_payload={})
    assert d.counters == (1, 1)


# ---- PromotionPacket schema ----------------------------------------------


def _make_valid_packet(**overrides) -> PromotionPacket:
    base = {
        "proposal_id": "p1",
        "proposal_type": "PROMPT_UPDATE",
        "target_surface": "prompt.X",
        "target_version_current": "v1",
        "target_version_proposed": "v2",
        "proposed_diff": "+...",
        "content_hash": "ch",
        "signer_identity": "alice",
        "owner": "team-llm",
        "policy_hash": "ph",
        "eval_record_id": "er1",
        "outcome_eval_ref": "oe1",
        "trajectory_eval_ref": "te1",
        "governance_eval_ref": "ge1",
        "calibration_ref": None,
        "rca_packet_id": "rca1",
        "incident_ids": ("inc-1",),
        "pattern_ids": (),
        "evidence_links": (
            EvidenceLink("t1", "s1", "r1", "rk1", "ah1", "src1", None),
        ),
        "root_cause_class": "ROUTE_MISS",
        "first_bad_span": "s1",
        "expected_effect": "fix",
        "affected_surfaces": ("prompt.X",),
        "blast_radius": "single prompt",
        "regression_pack_ids": (),
        "golden_set_ids": (),
        "gauntlet_receipt": "gr1",
        "rollout_plan": "dark_launch",
        "rollback_plan": "revert to v1",
        "activation_policy": ActivationPolicySpec(
            future_run_only=True,
            activate_at="next_run_start",
            canary_scope=None,
            ttl_review_date_epoch=99999.0,
        ),
        "approval_decision_id": "ad1",
        "uwg_receipt_id": "ur1",
        "l4_version_digest": "vd1",
        "bus_u_activation_receipt": "ar1",
    }
    base.update(overrides)
    return PromotionPacket(**base)


def test_valid_packet_passes_validation():
    pkt = _make_valid_packet()
    assert validate_promotion_packet(pkt) == ()


def test_packet_violates_invariant_9_when_future_run_only_false():
    pkt = _make_valid_packet(activation_policy=ActivationPolicySpec(
        future_run_only=False, activate_at="next_run_start",
        canary_scope=None, ttl_review_date_epoch=99999.0,
    ))
    errors = validate_promotion_packet(pkt)
    assert any("INV9_FUTURE_RUN_ONLY" in e for e in errors)


def test_packet_violates_invariant_9_when_activate_at_wrong():
    pkt = _make_valid_packet(activation_policy=ActivationPolicySpec(
        future_run_only=True, activate_at="immediate",
        canary_scope=None, ttl_review_date_epoch=99999.0,
    ))
    errors = validate_promotion_packet(pkt)
    assert any("INV9_ACTIVATE_AT" in e for e in errors)


def test_packet_violates_invariant_6_when_signer_empty():
    pkt = _make_valid_packet(signer_identity="")
    errors = validate_promotion_packet(pkt)
    assert any("INV6_NO_SILENT_PROMOTE" in e and "signer" in e for e in errors)


def test_packet_violates_invariant_12_when_rollback_empty():
    pkt = _make_valid_packet(rollback_plan="")
    errors = validate_promotion_packet(pkt)
    assert any("INV12_ROLLBACK_REQUIRED" in e for e in errors)


def test_packet_violates_invariant_5_when_rca_empty():
    pkt = _make_valid_packet(rca_packet_id="")
    errors = validate_promotion_packet(pkt)
    assert any("INV5_RCA_REQUIRED" in e for e in errors)


def test_packet_violates_invariant_2_when_eval_empty():
    pkt = _make_valid_packet(eval_record_id="")
    errors = validate_promotion_packet(pkt)
    assert any("INV2_EVAL_BEFORE_LEARNING" in e for e in errors)


def test_packet_violates_invariant_11_when_evidence_empty():
    pkt = _make_valid_packet(evidence_links=())
    errors = validate_promotion_packet(pkt)
    assert any("INV11_LINEAGE_REQUIRED" in e for e in errors)


def test_packet_aggregates_multiple_violations():
    pkt = _make_valid_packet(
        signer_identity="", rollback_plan="", policy_hash="",
        rca_packet_id="", eval_record_id="", evidence_links=(),
    )
    errors = validate_promotion_packet(pkt)
    assert len(errors) >= 6


# ---- FailureMode taxonomy -------------------------------------------------


def test_failure_mode_count_is_15():
    """Spec lines 1344-1362 enumerate exactly 15 failure modes."""
    assert len(list(FailureMode)) == 15


def test_containment_table_covers_every_mode():
    for mode in FailureMode:
        assert mode in CONTAINMENT_TABLE
        action = CONTAINMENT_TABLE[mode]
        assert action.mode is mode
        assert action.containment  # non-empty
        assert action.looks_like  # non-empty


def test_containment_for_shadow_writer_is_freeze():
    action = CONTAINMENT_TABLE[FailureMode.SHADOW_WRITER]
    assert "freeze" in action.containment.lower()
    assert "sovereignty" in action.containment.lower()


def test_containment_for_current_run_mutation_is_fatal():
    action = CONTAINMENT_TABLE[FailureMode.CURRENT_RUN_MUTATION]
    assert "fatal" in action.containment.lower()
