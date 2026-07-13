"""apps-test-model: APP CONTRACT.

apps_research CLI handoff tests for apps_rg targeting briefs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace


@dataclass(frozen=True)
class _FakeRecord:
    run_id: str
    topic: str
    company_brief_text: str
    confidence_score: float = 0.91
    support_coverage: float = 0.88
    hop_terminal_error: str = ""
    fec_run_context: dict | None = None


_VALID_APPS_RG_BRIEF = (
    "Anthropic - Manager Applied AI Architecture Partnerships targeting brief\n"
    "| Manager Applied AI Architecture Partnerships | band | Reports to Partnerships |\n\n"
    "## JD Complement\n"
    "- Company DNA centers on safe frontier AI deployment with partner-led enterprise adoption.\n"
    "- Operating model favors technical architecture depth paired with commercial ecosystem motion.\n\n"
    "## Company DNA & Operating Model\n"
    "- Company DNA emphasizes research-to-product translation for enterprise-grade AI systems.\n"
    "- Operating model blends platform, architecture, and leadership decision rights.\n\n"
    "## Company Strategy & Operating Pressure\n"
    "- Strategy pressure focuses on scaling trusted AI adoption through partner ecosystems.\n"
    "- Recent urgency centers on durable enterprise deployment patterns and platform governance.\n\n"
    "## Leadership & Stakeholder Map\n"
    "- Leadership stakeholders need partner architects who can translate roadmap into technical close.\n"
    "- Stakeholder map spans partnerships, platform, data, and customer architecture teams.\n\n"
    "## AI, Data, Platform, Architecture Signals\n"
    "- AI platform signal favors secure integration, evaluation loops, and data governance.\n"
    "- Architecture signal points to reusable patterns for enterprise deployment readiness.\n\n"
    "## Partnership / Ecosystem Motion\n"
    "- Co-sell motion depends on joint solution design, enablement, and technical close discipline.\n"
    "- Partner ecosystem signal includes GSI and ISV channels supporting adoption motion.\n\n"
    "## Recent Events & Urgency\n"
    "- Recent events create urgency for forward-looking enterprise AI operating models.\n"
    "- Urgency signal supports positioning around safe deployment and measurable partner adoption.\n\n"
    "## apps_rg Positioning Themes\n"
    "- Positioning should connect platform architecture, partner-led delivery, and leadership trust.\n"
    "- Themes should remain targeting context only and not become proof for resume claims.\n\n"
    "## apps_lic Outreach Angles\n"
    "- Outreach angle can emphasize ecosystem revenue, partner enablement, and adoption motion.\n"
    "- Outreach should mirror company strategy without copying job description responsibilities.\n\n"
    "## Do Not Use As Proof\n"
    "- This briefing is targeting context only and must not support candidate achievement claims.\n"
)


def _sidecar_for(brief: str) -> dict:
    normalized = brief.strip()
    x2_receipt = {
        "schema_version": "apps_research.apps_rg_handoff_x2_judge_receipt.v1",
        "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
        "judge_name": "gemini_pro",
        "judge_provider": "gemini_pro",
        "judge_model": "gemini-3.1-pro-preview",
        "threshold": 0.75,
        "model_backed": True,
        "status": "PASS",
        "score": 0.91,
        "verdict": "PASS",
        "provider_status": "MODEL_BACKED_PASS",
    }
    return {
        "brief_text_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "generation_provider": "external_openai",
        "generation_model": "gpt-5.4-mini-2026-03-17",
        "provider_call_attempted": True,
        "handoff_eligible": True,
        "briefing_semantic_score": 0.91,
        "judge_name": "gemini_pro",
        "judge_model": "gemini-3.1-pro-preview",
        "semantic_gate_mode": "model_backed_llm_judge",
        "x2_judge_receipt": x2_receipt,
        "role_archetype": "partnerships",
        "required_sections_present": ["jd complement"],
        "missing_sections": [],
        "source_families_present": ["overview", "partner_ecosystem"],
        "source_families_missing": [],
        "signal_terms_present": ["company dna", "co-sell"],
        "signal_terms_missing": [],
        "source_register": [{"family": "partner_ecosystem", "has_content": True}],
    }


def test_cli_jd_path_writes_fresh_apps_rg_briefing(monkeypatch, tmp_path: Path) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Lead partner solution architecture for Claude.", encoding="utf-8")
    runs_root = tmp_path / "runs"

    captured = {}

    def _fake_run(request):
        captured["request"] = request
        return _FakeRecord(
            run_id="research-run-test",
            topic="Anthropic",
            company_brief_text=_VALID_APPS_RG_BRIEF,
            fec_run_context={
                "company_brief": {
                    "company": "Anthropic",
                    "apps_rg_targeting_brief_sidecar": _sidecar_for(_VALID_APPS_RG_BRIEF),
                }
            },
        )

    monkeypatch.setattr(main_mod, "_run_research_record", _fake_run)
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: runs_root)
    monkeypatch.setattr(main_mod, "_ensure_searxng_runtime_ready", lambda: None)

    code = main_mod._run_profile_spine(
        [
            "--target-company",
            "Anthropic",
            "--target-role",
            "Manager of Applied AI Architecture, Partnerships",
            "--jd",
            str(jd_path),
        ]
    )

    assert code == 0
    request = captured["request"]
    assert request.jd_context["output_format"] == "apps_rg_targeting_brief_v1"
    assert request.jd_context["synthesis_template"] == "apps_rg_targeting_brief_synthesis_v1"
    briefing = runs_root / "research-run-test" / "briefing.md"
    company_json = runs_root / "research-run-test" / "company_brief.json"
    assert briefing.read_text(encoding="utf-8").startswith("Anthropic - Manager")
    assert '"company": "Anthropic"' in company_json.read_text(encoding="utf-8")
    handoff_v2 = json.loads(
        (runs_root / "research-run-test" / "apps_research_apps_rg_handoff_v2.json").read_text(
            encoding="utf-8"
        )
    )
    assert handoff_v2["schema_version"] == "apps_research.apps_rg_handoff.v2"
    assert handoff_v2["identity"]["consumer_app_id"] == "apps_rg"
    assert handoff_v2["identity"]["brief_sha256"] == (
        "sha256:" + hashlib.sha256(briefing.read_bytes()).hexdigest()
    )
    assert handoff_v2["identity"]["jd_sha256"].startswith("sha256:")
    assert set(handoff_v2["mandatory_gate_receipts"]) == {
        "G5",
        "G6",
        "G7",
        "G21",
        "G24",
        "G26",
    }
    assert handoff_v2["exit_authorization"]["x3_code"] == "X3D_ALLOW_FINISH"
    assert not (
        runs_root / "research-run-test" / "apps_research_briefing_envelope.json"
    ).exists()


def test_shared_targeting_writer_persists_producer_owned_bundle(tmp_path: Path) -> None:
    from apps_research.integrations.apps_rg_handoff import (
        persist_apps_rg_targeting_brief_artifacts,
    )

    record = _FakeRecord(
        run_id="research-run-shared-writer",
        topic="Anthropic",
        company_brief_text=_VALID_APPS_RG_BRIEF,
        fec_run_context={
            "company_brief": {
                "apps_rg_targeting_brief_sidecar": _sidecar_for(_VALID_APPS_RG_BRIEF),
            }
        },
    )

    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=record,
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd_text="Run-specific partnerships JD",
        runs_root=tmp_path / "runs",
    )

    assert bundle.briefing_path.is_file()
    assert bundle.company_brief_path.is_file()
    assert bundle.envelope_path.is_file()
    artifacts = {
        row["artifact_id"]: row
        for row in bundle.envelope["artifact_manifest"]["artifacts"]
    }
    assert artifacts["briefing_md"]["artifact_ref"] == str(bundle.briefing_path.resolve())
    assert artifacts["company_brief_json"]["artifact_ref"] == str(
        bundle.company_brief_path.resolve()
    )


def test_generic_writer_preserves_legacy_metadata(monkeypatch, tmp_path: Path) -> None:
    from apps_research import __main__ as main_mod

    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")
    record = _FakeRecord(
        run_id="generic-run",
        topic="AI infrastructure",
        company_brief_text="Generic research briefing",
    )
    request = SimpleNamespace(
        trace_id="generic-trace",
        topic="AI infrastructure",
        mode="brief",
        depth_profile="standard",
        jd_context={},
    )

    artifact_path = main_mod._write_research_artifacts(record, request)

    metadata_path = artifact_path.parent / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert artifact_path.name == "briefing.md"
    assert metadata["run_id"] == "generic-run"
    assert metadata["targeting_format"] == ""
    assert metadata["apps_research_apps_rg_handoff_v2_path"] == ""


def test_cli_jd_path_fails_closed_without_targeting_markdown(
    monkeypatch, tmp_path: Path
) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Partner architecture JD", encoding="utf-8")
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")
    monkeypatch.setattr(main_mod, "_ensure_searxng_runtime_ready", lambda: None)
    monkeypatch.setattr(
        main_mod,
        "_run_research_record",
        lambda _request: _FakeRecord(
            run_id="research-run-empty",
            topic="Anthropic",
            company_brief_text="",
            hop_terminal_error="missing_real_brief",
        ),
    )

    code = main_mod._run_profile_spine(
        ["--target-company", "Anthropic", "--target-role", "Manager", "--jd", str(jd_path)]
    )

    assert code == 1
    assert not (tmp_path / "runs" / "research-run-empty" / "briefing.md").exists()


def test_cli_jd_path_fails_closed_on_stub_targeting_markdown(
    monkeypatch, tmp_path: Path
) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Partner architecture JD", encoding="utf-8")
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")
    monkeypatch.setattr(main_mod, "_ensure_searxng_runtime_ready", lambda: None)
    monkeypatch.setattr(
        main_mod,
        "_run_research_record",
        lambda _request: _FakeRecord(
            run_id="research-run-stub",
            topic="Anthropic",
            company_brief_text=(
                "Stub Company\n\n"
                "Stub executive summary from L2 execution\n"
                "- Finding 1\n"
            ),
            hop_terminal_error="stub_fallback",
        ),
    )

    code = main_mod._run_profile_spine(
        ["--target-company", "Anthropic", "--target-role", "Manager", "--jd", str(jd_path)]
    )

    assert code == 1
    assert not (tmp_path / "runs" / "research-run-stub" / "briefing.md").exists()


def test_cli_dry_run_no_longer_enables_stub(monkeypatch) -> None:
    from apps_research import __main__ as main_mod

    called = False

    def _fake_run(_request):
        nonlocal called
        called = True
        return _FakeRecord(
            run_id="should-not-run",
            topic="Anthropic",
            company_brief_text="brief",
        )

    monkeypatch.setattr(main_mod, "_run_research_record", _fake_run)

    code = main_mod._run_profile_spine(["--target-company", "Anthropic", "--dry-run"])

    assert code == 1
    assert called is False


def test_cli_warms_searxng_before_research(monkeypatch, tmp_path: Path) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Lead partner solution architecture for Claude.", encoding="utf-8")
    calls: list[str] = []

    def _fake_preflight():
        calls.append("preflight")

    def _fake_run(_request):
        calls.append("research")
        return _FakeRecord(
            run_id="research-run-test",
            topic="Anthropic",
            company_brief_text=_VALID_APPS_RG_BRIEF,
            fec_run_context={
                "company_brief": {
                    "company": "Anthropic",
                    "apps_rg_targeting_brief_sidecar": _sidecar_for(_VALID_APPS_RG_BRIEF),
                }
            },
        )

    monkeypatch.setattr(main_mod, "_ensure_searxng_runtime_ready", _fake_preflight)
    monkeypatch.setattr(main_mod, "_run_research_record", _fake_run)
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")

    code = main_mod._run_profile_spine(
        ["--target-company", "Anthropic", "--target-role", "Manager", "--jd", str(jd_path)]
    )

    assert code == 0
    assert calls == ["preflight", "research"]


def test_cli_blocks_before_research_when_searxng_preflight_fails(
    monkeypatch, tmp_path: Path
) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Lead partner solution architecture for Claude.", encoding="utf-8")
    called = False

    def _fake_preflight():
        raise RuntimeError("SearXNG Docker readiness failed")

    def _fake_run(_request):
        nonlocal called
        called = True
        return _FakeRecord(
            run_id="should-not-run",
            topic="Anthropic",
            company_brief_text=_VALID_APPS_RG_BRIEF,
        )

    monkeypatch.setattr(main_mod, "_ensure_searxng_runtime_ready", _fake_preflight)
    monkeypatch.setattr(main_mod, "_run_research_record", _fake_run)
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")

    code = main_mod._run_profile_spine(
        ["--target-company", "Anthropic", "--target-role", "Manager", "--jd", str(jd_path)]
    )

    assert code == 1
    assert called is False
    assert not (tmp_path / "runs").exists()
