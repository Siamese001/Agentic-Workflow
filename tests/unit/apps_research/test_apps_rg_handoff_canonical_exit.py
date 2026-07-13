"""Canonical apps_research GateMesh/Exit authorization for apps_rg handoff."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from apps_research.integrations.apps_rg_handoff import (
    persist_apps_rg_targeting_brief_artifacts,
)
from apps_rg.prerequisites.briefing_validator import (
    validate_apps_research_handoff,
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
    assert bundle.handoff_v2_path and bundle.handoff_v2_path.is_file()
    assert bundle.commit_manifest_path and bundle.commit_manifest_path.is_file()
    assert bundle.u0_receipt_path and bundle.u0_receipt_path.is_file()
    assert bundle.brief_sha256.startswith("sha256:")
    assert bundle.result_metadata_digest.startswith("sha256:")
    assert bundle.bundle_manifest_digest.startswith("sha256:")

    handoff = bundle.envelope
    assert handoff["schema_version"] == "apps_research.apps_rg_handoff.v2"
    assert handoff["exit_authorization"]["x3_code"] == "X3D_ALLOW_FINISH"
    assert handoff["identity"]["brief_sha256"] == bundle.brief_sha256
    assert set(handoff["mandatory_gate_receipts"]) == {
        "G5",
        "G6",
        "G7",
        "G21",
        "G24",
        "G26",
    }
    assert all(
        row["status"] == "PASS"
        for row in handoff["mandatory_gate_receipts"].values()
    )
    assert not (bundle.run_dir / "apps_research_briefing_envelope.json").exists()
    consumer_validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    assert consumer_validation.valid, consumer_validation.reason
    persisted_consumer_receipt = (
        bundle.run_dir / "apps_research_handoff_validation_receipt.json"
    )
    assert persisted_consumer_receipt.is_file()
    assert json.loads(persisted_consumer_receipt.read_text())["status"] == "PASS"


def test_consumer_treats_long_inline_json_jd_as_text(tmp_path: Path) -> None:
    jd = json.dumps({"description": "architecture " * 450}, sort_keys=True)
    assert len(jd) > 4096
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("long-inline-jd"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )

    assert validation.valid, validation.reason


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


def test_consumer_rejects_tampered_exit_receipt(tmp_path: Path) -> None:
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("tamper"),
        target_company="Anthropic",
        target_role="Manager",
        jd_text="JD",
        runs_root=tmp_path / "runs",
    )
    receipt = json.loads(bundle.exit_disposition_path.read_text(encoding="utf-8"))
    receipt["unknown_count"] = 1
    bundle.exit_disposition_path.write_text(
        json.dumps(receipt, sort_keys=True),
        encoding="utf-8",
    )

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref="JD",
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    assert not validation.valid
    assert "exit_authorization_receipt_sha256_mismatch" in validation.reason
    assert "persisted_exit_unknown_count_nonzero" in validation.reason


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


def test_v2_consumer_rejects_tampered_committed_brief_bytes(tmp_path: Path) -> None:
    jd = "Lead partner solution architecture for Claude."
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("v2-byte-tamper"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )
    bundle.briefing_path.write_bytes(bundle.briefing_path.read_bytes() + b"tamper")

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_canonical_exit=True,
    )

    assert not validation.valid
    assert "artifact_byte_length_mismatch:briefing.md" in validation.reason
    assert "brief_sha256_mismatch" in validation.reason


def test_v2_consumer_rejects_missing_commit_marker(tmp_path: Path) -> None:
    jd = "Lead partner solution architecture for Claude."
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("v2-marker-missing"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )
    assert bundle.commit_manifest_path is not None
    bundle.commit_manifest_path.unlink()

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_canonical_exit=True,
    )

    assert not validation.valid
    assert "missing_commit_marker" in validation.reason


def test_v2_consumer_rejects_target_identity_mismatch(tmp_path: Path) -> None:
    jd = "Lead partner solution architecture for Claude."
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("v2-target-mismatch"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=jd,
        runs_root=tmp_path / "runs",
    )

    validation = validate_apps_research_handoff(
        brief_ref=str(bundle.briefing_path),
        jd_ref=jd,
        require_observed=True,
        require_canonical_exit=True,
        expected_target_company="Different Company",
        expected_target_role="Manager Applied AI Architecture Partnerships",
    )

    assert not validation.valid
    assert "identity_target_company_context_mismatch" in validation.reason


def test_consumer_rejects_legacy_only_product_handoff(tmp_path: Path) -> None:
    brief = tmp_path / "briefing.md"
    brief.write_text(_VALID_BRIEF, encoding="utf-8")
    (tmp_path / "apps_research_briefing_envelope.json").write_text(
        json.dumps(
            {
                "schema_version": "apps_research.apps_rg_briefing_envelope.v1",
                "producer_app": "apps_research",
                "consumer_app": "apps_rg",
            }
        ),
        encoding="utf-8",
    )

    validation = validate_apps_research_handoff(
        brief_ref=str(brief),
        require_observed=True,
        require_canonical_exit=True,
    )

    assert not validation.valid
    assert validation.reason == "legacy_only_handoff_rejected"


def test_atomic_publisher_never_exposes_final_directory_before_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import apps_research.integrations.apps_rg_handoff as handoff

    original = handoff._write_fsync

    def fail_on_marker(path: Path, payload: bytes) -> None:
        if path.name == "bundle_commit_manifest.json":
            raise OSError("simulated marker write failure")
        original(path, payload)

    monkeypatch.setattr(handoff, "_write_fsync", fail_on_marker)
    runs_root = tmp_path / "runs"
    with pytest.raises(OSError, match="simulated marker write failure"):
        persist_apps_rg_targeting_brief_artifacts(
            record=_record("atomic-marker-failure"),
            target_company="Anthropic",
            target_role="Manager Applied AI Architecture Partnerships",
            jd_text="Lead partner solution architecture for Claude.",
            runs_root=runs_root,
        )

    assert not (runs_root / "atomic-marker-failure").exists()
    assert not list(runs_root.glob(".atomic-marker-failure.staging-*"))
