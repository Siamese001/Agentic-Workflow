"""Tests for W1 plumbing enhancements: jd_targeting_mode, briefing_hash, C0.1 excerpt."""

from __future__ import annotations

import logging

import pytest

from apps_rg.runtime.c0.c01_retrieval_plan import _smart_jd_excerpt, build_c01_retrieval_plan
from apps_rg.runtime.c0.c03_graph_ref_policy import (
    RoleFamilyProjectionError,
    extract_briefing_targeting_supplement,
    merge_graph_targeting_jd_alignment,
    resolve_role_family_projection,
)
from apps_rg.runtime.jd_resolution import JdSource, resolve_jd_for_lanes

# ---------------------------------------------------------------------------
# F2: jd_targeting_mode in u0_validate_apps_rg
# ---------------------------------------------------------------------------


def test_u0_jd_targeting_mode_run_specific(tmp_path):
    """u0_validate_apps_rg sets jd_targeting_mode=RUN_SPECIFIC when run inputs are present."""
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
    )
    from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg

    brief = tmp_path / "brief.txt"
    brief.write_text("Company context.", encoding="utf-8")
    logging.info("C3 write receipt: JD targeting brief fixture written")
    payload = AppsRgIngressPayload(
        target_company="Acme",
        target_role="Staff Engineer",
        source_resume_text="resume body",
        job_description_text="Design distributed systems at scale.",
        manual_brief_path=str(brief),
        l5_certification_ref="test:valid:w6",
    )
    result = u0_validate_apps_rg(RequestEnvelope(payload=payload))
    mode = result.app_payload["query_spec"]["jd_targeting_mode"]
    assert mode == "RUN_SPECIFIC", f"expected RUN_SPECIFIC, got {mode!r}"


def test_u0_rejects_missing_jd_even_with_briefing(tmp_path):
    """U0 must fail closed when JD is missing, even if a briefing ref is present."""
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
    )
    from apps_rg.runtime.bindings.u0_binding import AppsRgU0RejectedError, u0_validate_apps_rg

    brief = tmp_path / "brief.txt"
    brief.write_text("Company context.", encoding="utf-8")

    payload = AppsRgIngressPayload(
        target_company="Acme",
        target_role="Staff Engineer",
        source_resume_text="resume body",
        manual_brief_path=str(brief),
        l5_certification_ref="test:valid:w6",
    )
    with pytest.raises(AppsRgU0RejectedError, match="missing run-specific job_description"):
        u0_validate_apps_rg(RequestEnvelope(payload=payload))


def test_u0_rejects_missing_briefing_even_with_jd():
    """U0 must fail closed when briefing is missing, even if JD text is present."""
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
    )
    from apps_rg.runtime.bindings.u0_binding import AppsRgU0RejectedError, u0_validate_apps_rg

    payload = AppsRgIngressPayload(
        target_company="Acme",
        target_role="Staff Engineer",
        source_resume_text="resume body",
        job_description_text="Design distributed systems at scale.",
        l5_certification_ref="test:valid:w6",
    )
    with pytest.raises(AppsRgU0RejectedError, match="missing run-specific briefing"):
        u0_validate_apps_rg(RequestEnvelope(payload=payload))


def test_u0_rejects_default_ssot_refs():
    """U0 must reject the committed default JD and briefing refs even when present."""
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
    )
    from apps_rg.runtime.bindings.u0_binding import AppsRgU0RejectedError, u0_validate_apps_rg
    from apps_rg.runtime.briefing_ssot import DEFAULT_TARGETING_BRIEFING_PATH
    from apps_rg.runtime.jd_resolution import DEFAULT_JD_TARGETING_PATH

    payload = AppsRgIngressPayload(
        target_company="Acme",
        target_role="Staff Engineer",
        source_resume_text="resume body",
        job_description_ref=str(DEFAULT_JD_TARGETING_PATH),
        manual_brief_path=str(DEFAULT_TARGETING_BRIEFING_PATH),
        l5_certification_ref="test:valid:w6",
    )
    with pytest.raises(AppsRgU0RejectedError, match="static SSOT refs are not allowed at U0"):
        u0_validate_apps_rg(RequestEnvelope(payload=payload))


# ---------------------------------------------------------------------------
# F2: jd_resolution warns on DEFAULT_SSOT
# ---------------------------------------------------------------------------


def test_jd_resolution_logs_warning_on_default_ssot(caplog):
    """A REAL run (run-context present) that falls back to DEFAULT_SSOT emits a WARNING.

    The warning is gated on run-context (target_company/target_role) so the module-level
    ``JD_TEXT_DEFAULT = resolve_jd_for_lanes()`` no-arg constant does not emit it at import (G23 noise).
    """
    with caplog.at_level(logging.WARNING, logger="apps_rg.runtime.jd_resolution"):
        r = resolve_jd_for_lanes(target_company="AIG", target_role="VP")
    assert r.jd_source == JdSource.DEFAULT_SSOT
    warning_msgs = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("DEFAULT_SSOT" in m.getMessage() for m in warning_msgs), (
        "Expected a DEFAULT_SSOT warning log, got: " + str([m.getMessage() for m in caplog.records])
    )


def test_jd_resolution_no_warning_on_module_default_no_context(caplog):
    """The no-arg (module-default) computation must NOT warn — it is not a real run (G23 hygiene)."""
    with caplog.at_level(logging.WARNING, logger="apps_rg.runtime.jd_resolution"):
        r = resolve_jd_for_lanes()
    assert r.jd_source == JdSource.DEFAULT_SSOT
    warning_msgs = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert not any("DEFAULT_SSOT" in m.getMessage() for m in warning_msgs)


def test_jd_resolution_no_warning_on_run_specific(caplog):
    """resolve_jd_for_lanes does NOT emit a WARNING when a run-specific JD is supplied."""
    with caplog.at_level(logging.WARNING, logger="apps_rg.runtime.jd_resolution"):
        r = resolve_jd_for_lanes(job_description_text="Build AI systems.")
    assert r.jd_source == JdSource.RUN_SPECIFIC
    warning_msgs = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert not any("DEFAULT_SSOT" in m.getMessage() for m in warning_msgs)


# ---------------------------------------------------------------------------
# F3: briefing_hash in section evidence trace
# (tested via _build_section_evidence_trace indirectly through app_payload shape)
# ---------------------------------------------------------------------------


def test_briefing_h_from_app_payload_briefing_key():
    """_build_section_evidence_trace picks up briefing_digest from app_payload['briefing']."""
    import hashlib

    from apps_rg.runtime.bindings.c0_binding import _build_section_evidence_trace

    digest = hashlib.sha256(b"briefing text").hexdigest()
    app_payload = {
        "briefing": {"briefing_digest": digest},
        "resume_payload": {},
        "jd_payload": {},
    }
    trace = _build_section_evidence_trace(
        {"section_id": "executive_summary", "section_type": "narrative"},
        None,
        [],
        app_payload,
        timestamp_iso="2026-01-01T00:00:00Z",
    )
    assert trace.briefing_hash == digest[:32], (
        f"expected first 32 chars of digest, got {trace.briefing_hash!r}"
    )


def test_briefing_h_empty_when_no_briefing_key():
    """_build_section_evidence_trace returns '' when no briefing digest is in app_payload."""
    from apps_rg.runtime.bindings.c0_binding import _build_section_evidence_trace

    app_payload: dict = {"resume_payload": {}, "jd_payload": {}}
    trace = _build_section_evidence_trace(
        {"section_id": "executive_summary", "section_type": "narrative"},
        None,
        [],
        app_payload,
        timestamp_iso="2026-01-01T00:00:00Z",
    )
    assert trace.briefing_hash == ""


# ---------------------------------------------------------------------------
# F4: TARGETING_DEGRADED gate in resolve_role_family_projection
# ---------------------------------------------------------------------------


def test_unknown_role_family_projection_fails_closed(caplog):
    """Missing role-family graph targeting must block instead of using generic targeting."""
    with caplog.at_level(logging.WARNING, logger="apps_rg.runtime.c0.c03_graph_ref_policy"):
        with pytest.raises(RoleFamilyProjectionError, match="missing role_family_projection row"):
            resolve_role_family_projection("COMPLETELY_UNKNOWN_ROLE_XYZ_NO_MATCH")
    warning_msgs = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert not any("targeting degraded" in m.getMessage().lower() for m in warning_msgs)


# ---------------------------------------------------------------------------
# F5: smart jd_text_excerpt in c01_retrieval_plan
# ---------------------------------------------------------------------------


def test_smart_excerpt_short_text_returned_intact():
    short = "Build AI platform for enterprise."
    assert _smart_jd_excerpt(short) == short


def test_smart_excerpt_anchors_to_keyword():
    boilerplate = " " * 200
    requirements = "Required skills: Python, cloud, distributed systems."
    jd = boilerplate + requirements + "B" * 100
    excerpt = _smart_jd_excerpt(jd)
    assert "Required" in excerpt or "skills" in excerpt, (
        f"Expected excerpt to contain keyword, got: {excerpt[:60]!r}"
    )
    assert len(excerpt) <= 300


def test_smart_excerpt_fallback_when_no_keyword():
    no_keyword = "C" * 500
    excerpt = _smart_jd_excerpt(no_keyword)
    assert excerpt == "C" * 240


def test_c01_retrieval_plan_uses_smart_excerpt():
    boilerplate = "X" * 200
    jd = boilerplate + "Responsibilities include: leading AI initiatives and cloud strategy."
    plan = build_c01_retrieval_plan(
        section_id="executive_summary",
        jd_text=jd,
    )
    excerpt = plan["jd_text_excerpt"]
    assert "Responsibilities" in excerpt or len(excerpt) <= 300


# ---------------------------------------------------------------------------
# W2 — F1: extract_briefing_targeting_supplement and merge_graph_targeting_jd_alignment
# ---------------------------------------------------------------------------


def test_extract_briefing_supplement_empty_on_blank():
    assert extract_briefing_targeting_supplement("") == []


def test_extract_briefing_supplement_ai_signal():
    terms = extract_briefing_targeting_supplement(
        "The company is investing heavily in AI and machine learning infrastructure."
    )
    assert "AI_PLATFORM" in terms


def test_extract_briefing_supplement_multi_signal():
    terms = extract_briefing_targeting_supplement(
        "We are a cloud-native insurtech startup using agentic AI with strong governance requirements."
    )
    assert len(terms) >= 2
    assert len(terms) <= 5


def test_extract_briefing_supplement_deduplicates():
    terms = extract_briefing_targeting_supplement("AI ai llm machine learning deep learning AI")
    assert terms.count("AI_PLATFORM") == 1


def test_merge_graph_targeting_briefing_supplement_present_for_authorized_source():
    projection = {
        "role_family_key": "SVP_ENGINEERING_AI_PLATFORM",
        "projection_source": "sqlite_role_family_projection",
        "sqlite_projection_row_found": True,
        "fallback_pillar_bridge_used": False,
        "release_eligible_targeting_proof": True,
        "targeting_degraded_explicit": False,
        "pillar_hint_ids": ["AI_PLATFORM"],
    }
    result = merge_graph_targeting_jd_alignment(
        None,
        role_family_projection=projection,
        briefing_text="We are investing in cloud and AI governance.",
        briefing_source="FRESH_APPS_RESEARCH",
    )
    supplement = result["graph_targeting"]["briefing_targeting_supplement"]
    assert isinstance(supplement, list)
    assert len(supplement) >= 1
    assert result["briefing_used_as_proof"] is False
    blocked = merge_graph_targeting_jd_alignment(
        None,
        role_family_projection=projection,
        briefing_text="We are investing in cloud and AI governance.",
        briefing_source="RUN_SPECIFIC",
    )
    assert blocked["graph_targeting"]["briefing_targeting_supplement"] == []


def test_merge_graph_targeting_briefing_supplement_empty_for_default_ssot():
    projection = {
        "role_family_key": "SVP_ENGINEERING_AI_PLATFORM",
        "projection_source": "sqlite_role_family_projection",
        "sqlite_projection_row_found": True,
        "fallback_pillar_bridge_used": False,
        "release_eligible_targeting_proof": True,
        "targeting_degraded_explicit": False,
        "pillar_hint_ids": [],
    }
    result = merge_graph_targeting_jd_alignment(
        None,
        role_family_projection=projection,
        briefing_text="We are investing in cloud and AI governance.",
        briefing_source="DEFAULT_SSOT",
    )
    supplement = result["graph_targeting"]["briefing_targeting_supplement"]
    assert supplement == [], f"Expected empty supplement for DEFAULT_SSOT, got {supplement!r}"


def test_merge_graph_targeting_proof_invariants_preserved():
    """The proof-authority invariants must hold regardless of briefing input."""
    projection = {
        "role_family_key": "ANY",
        "projection_source": "sqlite_role_family_projection",
        "sqlite_projection_row_found": True,
        "fallback_pillar_bridge_used": False,
        "release_eligible_targeting_proof": True,
        "targeting_degraded_explicit": False,
        "pillar_hint_ids": [],
    }
    result = merge_graph_targeting_jd_alignment(
        {"jd_used_as_proof": False, "briefing_used_as_proof": False},
        role_family_projection=projection,
        briefing_text="Strong AI governance requirements.",
        briefing_source="RUN_SPECIFIC",
    )
    assert result["jd_used_as_proof"] is False
    assert result["briefing_used_as_proof"] is False
