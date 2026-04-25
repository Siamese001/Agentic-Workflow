"""W4 tests for v7 6C engines: signal_fusion_engine, pattern_synthesizer,
proposal_admission_gate."""

from __future__ import annotations

import pytest

from system_learning.engines.pattern_synthesizer import (
    FirstBadSpanLocalizer,
    IncidentRCA,
    PatternSynthesizer,
    RootCauseClass,
    TraceSpan,
)
from system_learning.engines.proposal_admission_gate import (
    AdmissionVerdict,
    ProposalAdmissionGate,
    ProposalDraft,
)
from system_learning.engines.signal_fusion_engine import (
    Signal,
    SignalFusionEngine,
    SignalSource,
)
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard, V7KPIName


# ---- signal_fusion_engine -------------------------------------------------


def _sig(source, severity, confidence, **kw):
    return Signal(
        source=source, severity=severity, confidence=confidence,
        sample_size=kw.get("n", 5),
        recency_seconds=kw.get("recency", 0.0),
        reproducibility=kw.get("repro", 0.5),
        user_impact=kw.get("impact", 0.5),
        policy_criticality=kw.get("policy", 0.5),
        affected_surface=kw.get("surface", "L2:tool.search"),
    )


def test_fuse_no_signals_returns_zero():
    eng = SignalFusionEngine()
    out = eng.fuse([])
    assert out.fused_severity == 0.0
    assert out.severity_class == "low"
    assert out.recommended_investigation == "no_signals"


def test_fuse_high_sev_high_conf_recommends_immediate_rca():
    eng = SignalFusionEngine()
    sigs = [
        _sig(SignalSource.RED_TEAM, 0.95, 0.9),
        _sig(SignalSource.INCIDENT_REPORT, 0.9, 0.85),
    ]
    out = eng.fuse(sigs)
    assert out.severity_class in {"critical", "high"}
    assert out.confidence_band in {"high", "medium"}
    assert out.recommended_investigation == "open_incident_rca_immediately"


def test_fuse_low_severity_recommends_monitor():
    eng = SignalFusionEngine()
    sigs = [_sig(SignalSource.BUS_T_TELEMETRY, 0.1, 0.8)]
    out = eng.fuse(sigs)
    assert out.severity_class == "low"
    assert out.recommended_investigation == "monitor_only"


def test_fuse_human_calibration_outweighs_equal_volume_bus_p():
    """At equal sample volume, a HUMAN_CALIBRATION signal carries more
    weight than a BUS_P_PREFERENCE signal (per-source reliability prior)."""
    eng = SignalFusionEngine()
    sigs = [
        _sig(SignalSource.HUMAN_CALIBRATION, 1.0, 1.0, repro=1.0),
        _sig(SignalSource.BUS_P_PREFERENCE, 0.0, 1.0, repro=1.0),
    ]
    out = eng.fuse(sigs)
    # human_calibration weight should exceed bus_p_preference weight in
    # the weighted_sources ranking (regardless of fused severity class).
    by_source = dict(out.weighted_sources)
    assert by_source["human_calibration"] > by_source["bus_p_preference"]


def test_fuse_surfaces_ranked_by_weight():
    eng = SignalFusionEngine()
    sigs = [
        _sig(SignalSource.HUMAN_CALIBRATION, 0.9, 1.0, surface="L2:write"),
        _sig(SignalSource.BUS_P_PREFERENCE, 0.5, 0.5, surface="L0:route"),
    ]
    out = eng.fuse(sigs)
    assert out.affected_surface_candidates[0] == "L2:write"


# ---- first_bad_span_localizer + pattern_synthesizer -----------------------


def test_first_bad_span_returns_none_when_all_ok():
    loc = FirstBadSpanLocalizer()
    spans = [
        TraceSpan(span_id="s1", parent_span_id=None, surface="L0", status="ok", started_at=1.0),
        TraceSpan(span_id="s2", parent_span_id="s1", surface="L2", status="ok", started_at=2.0),
    ]
    assert loc.localize(spans) is None


def test_first_bad_span_picks_earliest_non_ok():
    loc = FirstBadSpanLocalizer()
    spans = [
        TraceSpan(span_id="s1", parent_span_id=None, surface="L0", status="ok", started_at=1.0),
        TraceSpan(span_id="s2", parent_span_id="s1", surface="L2", status="error", started_at=2.0),
        TraceSpan(span_id="s3", parent_span_id="s1", surface="L3", status="error", started_at=3.0),
    ]
    bad = loc.localize(spans)
    assert bad is not None
    assert bad.span_id == "s2"


def test_pattern_synthesizer_groups_by_class_and_surface():
    syn = PatternSynthesizer()
    incs = [
        IncidentRCA(incident_id=f"i{i}", first_bad_span_id=f"s{i}",
                    root_cause_class=RootCauseClass.RETRIEVAL_RECALL_GAP,
                    failure_chain=("L2:search",), affected_surfaces=("L2:search",),
                    confidence=0.8)
        for i in range(5)
    ]
    incs.append(IncidentRCA(incident_id="iX", first_bad_span_id="sX",
                            root_cause_class=RootCauseClass.PROVIDER_DRIFT,
                            failure_chain=(), affected_surfaces=("L5:gateway",),
                            confidence=0.7))
    records = syn.synthesize(incs)
    assert len(records) == 2
    by_id = {r.pattern_id: r for r in records}
    assert by_id["RETRIEVAL_RECALL_GAP::L2:search"].incident_count == 5
    assert by_id["PROVIDER_DRIFT::L5:gateway"].incident_count == 1


def test_pattern_synthesizer_action_class_mapping():
    syn = PatternSynthesizer()
    inc_retrieval = IncidentRCA(
        incident_id="i1", first_bad_span_id="s1",
        root_cause_class=RootCauseClass.RETRIEVAL_RECALL_GAP,
        failure_chain=(), affected_surfaces=("L2:search",), confidence=0.8,
    )
    # 5 incidents => not LOCAL_PATCH, not THRESHOLD_CHANGE
    records = syn.synthesize([inc_retrieval] * 5)
    assert records[0].proposed_action_class == "RETRIEVAL_PROFILE_UPDATE"


def test_pattern_synthesizer_publishes_localization_kpi():
    syn = PatternSynthesizer()
    board = UnifiedKPIBoard()
    incs = [
        IncidentRCA(incident_id=f"i{i}", first_bad_span_id=f"s{i}",
                    root_cause_class=RootCauseClass.ROUTE_MISS,
                    failure_chain=(), affected_surfaces=("L0",), confidence=0.7)
        for i in range(9)
    ]
    incs.append(IncidentRCA(incident_id="iX", first_bad_span_id=None,
                            root_cause_class=RootCauseClass.UNKNOWN_ROOT_CAUSE,
                            failure_chain=(), affected_surfaces=(), confidence=0.3))
    syn.synthesize(incs)
    syn.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.ROOT_CAUSE_LOCALIZATION_RATE)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(0.9)


# ---- proposal_admission_gate ---------------------------------------------


def _draft(**overrides):
    base = dict(
        proposal_id="p1", eval_record_id="e1", rca_packet_id="r1",
        target_surface="L2:tool", proposed_diff="+x -y",
        blast_radius="local", rollback_plan="revert commit",
        test_plan="run regression", owner="alice@example",
        freshness_age_seconds=3600.0, has_open_blocker=False,
        confidence_band="high", requires_sme_review=False,
    )
    base.update(overrides)
    return ProposalDraft(**base)


def test_admit_complete_proposal():
    g = ProposalAdmissionGate()
    d = g.decide(_draft())
    assert d.verdict is AdmissionVerdict.ADMIT_TO_GAUNTLET


def test_hold_when_field_missing():
    g = ProposalAdmissionGate()
    d = g.decide(_draft(rollback_plan=""))
    assert d.verdict is AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE
    assert "rollback_plan" in d.missing_fields


def test_hold_when_blocker_open():
    g = ProposalAdmissionGate()
    d = g.decide(_draft(has_open_blocker=True))
    assert d.verdict is AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE
    assert "blocker" in d.notes.lower()


def test_hold_when_evidence_stale():
    g = ProposalAdmissionGate()
    d = g.decide(_draft(freshness_age_seconds=10 * 86400.0))
    assert d.verdict is AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE


def test_reject_when_low_confidence():
    g = ProposalAdmissionGate()
    d = g.decide(_draft(confidence_band="low"))
    assert d.verdict is AdmissionVerdict.REJECT_WEAK_PROPOSAL


def test_require_sme_review():
    g = ProposalAdmissionGate()
    d = g.decide(_draft(requires_sme_review=True))
    assert d.verdict is AdmissionVerdict.REQUIRE_SME_REVIEW


def test_admission_publishes_evidence_completeness_kpi():
    g = ProposalAdmissionGate()
    board = UnifiedKPIBoard()
    g.decide(_draft())  # complete
    g.decide(_draft())  # complete
    g.decide(_draft(rollback_plan=""))  # incomplete
    g.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.PROPOSAL_EVIDENCE_COMPLETENESS)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(2 / 3)
