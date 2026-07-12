"""Canonical apps_research GateMesh/Exit authorization for apps_rg handoff."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pytest

from apps_research.integrations.apps_rg_handoff import (
    persist_apps_rg_targeting_brief_artifacts,
)
from apps_rg.prerequisites.briefing_validator import (
    validate_apps_research_handoff,
    validate_canonical_apps_research_exit,
)
from apps_rg.runtime.bindings.briefing_u0_signals import (
    briefing_supplied_at_u0,
)


_VALID_BRIEF = (
    "Anthropic - Manager Applied AI Architecture Partnerships targeting brief\n"
    "| Manager Applied AI Architecture Partnerships | band | Reports to Partnerships |\n\n"
    "## JD Complement\n"
    "- Company DNA centers on safe frontier AI deployment with partner-led enterprise adoption.\n"
    "- Operating model favors technical architecture depth paired with ecosystem motion.\n\n"
    "## Company DNA & Operating Model\n"
    "- Company DNA emphasizes research-to-product translation for enterprise AI systems.\n"
    "- Operating model blends platform architecture and leadership decision rights.\n\n"
    "## Company Strategy & Operating Pressure\n"
    "- Strategy pressure focuses on scaling trusted AI adoption through partner ecosystems.\n"
    "- Recent urgency centers on durable enterprise deployment and platform governance.\n\n"
    "## Leadership & Stakeholder Map\n"
    "- Leadership stakeholders need architects who translate roadmap into technical close.\n"
    "- Stakeholder map spans partnerships, platform, data, and customer architecture teams.\n\n"
    "## AI, Data, Platform, Architecture Signals\n"
    "- AI platform signal favors secure integration, evaluation loops, and data governance.\n"
    "- Architecture signal points to reusable enterprise deployment patterns.\n\n"
    "## Partnership / Ecosystem Motion\n"
    "- Co-sell motion depends on joint solution design, enablement, and technical close.\n"
    "- Partner ecosystem signal includes GSI and ISV channels supporting adoption.\n\n"
    "## Recent Events & Urgency\n"
    "- Recent events create urgency for forward-looking enterprise AI operating models.\n"
    "- Urgency supports positioning around safe deployment and measurable adoption.\n\n"
    "## apps_rg Positioning Themes\n"
    "- Positioning should connect platform architecture, partner delivery, and trust.\n"
    "- Themes remain targeting context and never become proof for resume claims.\n\n"
    "## apps_lic Outreach Angles\n"
    "- Outreach can emphasize ecosystem revenue, enablement, and adoption motion.\n"
    "- Outreach mirrors company strategy without copying JD responsibilities.\n\n"
    "## Do Not Use As Proof\n"
    "- This briefing is targeting context only and cannot support candidate claims.\n"
)


@dataclass(frozen=True)
class _Record:
    run_id: str
    topic: str
    company_brief_text: str
    fec_run_context: dict
    confidence_score: float = 0.91
    support_coverage: float = 0.88
    hop_terminal_error: str = ""
    trace_id: str = ""


def _sidecar(brief: str, *, x2_status: str = "PASS") -> dict:
    score = 0.91 if x2_status == "PASS" else 0.0
    return {
        "brief_text_sha256": hashlib.sha256(brief.strip().encode("utf-8")).hexdigest(),
        "generation_provider": "external_openai",
        "generation_model": "gpt-5.4-mini-2026-03-17",
        "provider_call_attempted": True,
        "handoff_eligible": True,
        "reason": "ok",
        "x2_judge_receipt": {
            "schema_version": "apps_research.apps_rg_handoff_x2_judge_receipt.v1",
            "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
            "judge_name": "gemini_pro",
            "judge_provider": "gemini_pro",
            "judge_model": "gemini-3.1-pro-preview",
            "threshold": 0.75,
            "model_backed": True,
            "status": x2_status,
            "score": score,
            "verdict": x2_status,
            "provider_status": f"MODEL_BACKED_{x2_status}",
        },
        "role_archetype": "partnerships",
        "required_sections_present": ["jd complement"],
        "missing_sections": [],
        "source_families_present": ["overview", "partner_ecosystem"],
        "source_families_missing": [],
        "signal_terms_present": ["company dna", "co-sell"],
        "signal_terms_missing": [],
        "source_register": [
            {"family": "overview", "has_content": True, "char_count": 500},
            {"family": "partner_ecosystem", "has_content": True, "char_count": 500},
        ],
    }


def _record(run_id: str, *, x2_status: str = "PASS") -> _Record:
    return _Record(
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        topic="Anthropic",
        company_brief_text=_VALID_BRIEF,
        fec_run_context={
            "company_brief": {
                "apps_rg_targeting_brief_sidecar": _sidecar(
                    _VALID_BRIEF,
                    x2_status=x2_status,
                )
            }
        },
    )


def test_publisher_writes_brief_only_after_canonical_x3d(tmp_path: Path) -> None:
    jd = "Lead partner solution architecture for Claude."
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("canonical-allow"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )

    assert bundle.briefing_path.is_file()
    assert bundle.gate_mesh_path and bundle.gate_mesh_path.is_file()
    assert bundle.exit_review_path and bundle.exit_review_path.is_file()
    assert bundle.exit_disposition_path and bundle.exit_disposition_path.is_file()
    assert bundle.runtime_exhaust_path and bundle.runtime_exhaust_path.is_file()

    envelope = bundle.envelope
    assert envelope["canonical_exit_authorized"] is True
    assert envelope["x3_code"] == "X3D_ALLOW_FINISH"
    receipt = envelope["apps_research_exit_disposition_receipt"]
    assert receipt["required_gates_passed"] is True
    assert receipt["hard_fail_count"] == 0
    assert receipt["unknown_count"] == 0
    assert receipt["missing_gate_count"] == 0
    assert receipt["output_artifact_digest"] == envelope["brief_sha256"]
    assert (
        envelope["apps_research_runtime_exhaust_bundle"]["exit_disposition_ref"]
        == envelope["exit_disposition_receipt_digest"]
    )

    valid, failures = validate_canonical_apps_research_exit(envelope)
    assert valid, failures
    consumer_validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    assert consumer_validation.valid, consumer_validation.reason


def test_unknown_x2_never_publishes_briefing(tmp_path: Path) -> None:
    runs_root = tmp_path / "runs"
    with pytest.raises(RuntimeError, match="canonical Exit"):
        persist_apps_rg_targeting_brief_artifacts(
            record=_record("canonical-unknown", x2_status="UNKNOWN"),
            target_company="Anthropic",
            target_role="Manager Applied AI Architecture Partnerships",
            jd_text="Lead partner solution architecture for Claude.",
            runs_root=runs_root,
        )

    assert not (runs_root / "canonical-unknown").exists()
    assert not (runs_root / "canonical-unknown" / "briefing.md").exists()


def test_consumer_rejects_tampered_exit_receipt() -> None:
    record = _record("tamper")
    sidecar = record.fec_run_context["company_brief"][
        "apps_rg_targeting_brief_sidecar"
    ]
    from apps_research.integrations.apps_rg_handoff import (
        build_apps_rg_handoff_envelope,
        run_apps_rg_handoff_exit_authorization,
    )

    authorization = run_apps_rg_handoff_exit_authorization(
        run_id=record.run_id,
        trace_root=record.trace_id,
        briefing_text=record.company_brief_text,
        jd_text="JD",
        sidecar=sidecar,
    )
    envelope = build_apps_rg_handoff_envelope(
        sidecar=sidecar,
        run_id=record.run_id,
        target_company="Anthropic",
        target_role="Manager",
        briefing_text=record.company_brief_text,
        jd_text="JD",
        generated_at_utc="2026-07-12T12:00:00+00:00",
        exit_authorization=authorization,
    )
    envelope["apps_research_exit_disposition_receipt"]["unknown_count"] = 1

    valid, failures = validate_canonical_apps_research_exit(envelope)
    assert not valid
    assert "canonical_unknown_count_nonzero" in failures
    assert "exit_disposition_receipt_digest_mismatch" in failures


def test_u0_signal_requires_canonical_exit_for_auto_research(tmp_path: Path) -> None:
    manual = tmp_path / "manual.md"
    manual.write_text(_VALID_BRIEF, encoding="utf-8")
    assert briefing_supplied_at_u0(
        {
            "briefing_artifact_ref": str(manual),
            "auto_research_internal": False,
        }
    )
    assert not briefing_supplied_at_u0(
        {
            "briefing_artifact_ref": str(manual),
            "auto_research_internal": True,
            "job_description_text": "JD",
        }
    )

    jd = "Lead partner solution architecture for Claude."
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("u0-accepted"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )
    assert briefing_supplied_at_u0(
        {
            "briefing_artifact_ref": str(bundle.briefing_path),
            "manual_brief_path": str(bundle.briefing_path),
            "auto_research_internal": True,
            "research_via": "apps_research",
            "job_description_text": jd,
        }
    )


def test_u0_binding_reaches_authorized_briefing_signal() -> None:
    source = Path("apps_rg/runtime/bindings/u0_binding.py").read_text(
        encoding="utf-8"
    )
    assert "briefing_supplied_at_u0(app_payload)" in source
