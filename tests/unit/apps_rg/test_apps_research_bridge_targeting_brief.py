"""Unit tests for apps_rg AppsResearchBridge targeting-brief delegation seam."""

from __future__ import annotations

from typing import Any

import pytest

from apps_rg.integrations.apps_research_bridge import (
    AppsResearchBridge,
    EvidenceItem,
    MockAppsResearchBridge,
    ResearchResult,
)


def _fetch_kwargs(**overrides: Any) -> dict[str, Any]:
    base = {
        "company_name": "AIG",
        "job_title": "VP Global Head Agentic AI",
        "capability_ref": "apps_research.v1",
        "request_id": "req-targeting-001",
        "run_id": "run-targeting-001",
        "trace_id": "trace-targeting-001",
    }
    base.update(overrides)
    return base


def test_bridge_blocks_unsupported_capability_ref() -> None:
    bridge = AppsResearchBridge()
    result = bridge.fetch(**_fetch_kwargs(capability_ref="unsupported.v9"))
    assert isinstance(result, ResearchResult)
    assert result.is_blocked is True
    assert "Unsupported capability_ref" in result.block_reason
    assert result.company_brief_text == ""


def test_bridge_wraps_invoke_exception_as_blocked_result() -> None:
    bridge = AppsResearchBridge()

    def _boom(**_kwargs: Any) -> None:
        raise RuntimeError("governed runner unavailable")

    bridge._invoke_apps_research = _boom  # type: ignore[method-assign]
    result = bridge.fetch(**_fetch_kwargs())
    assert result.is_blocked is True
    assert "RuntimeError" in result.block_reason
    assert "governed runner unavailable" in result.block_reason


def test_bridge_translate_preserves_company_brief_text_from_raw() -> None:
    bridge = AppsResearchBridge()

    class _Raw:
        run_id = "run-abc"
        is_blocked = False
        block_reason = ""
        is_stale = False
        age_days = 0.0
        evidence_items = ()
        confidence_score = 0.9
        company_brief_text = "=== STRATEGIC MANDATE ===\nBuild agentic AI platform."

    result = bridge._translate(
        raw=_Raw(),
        run_id="run-abc",
        trace_id="bridge:rg:test:trace-abc",
        request_id="req-abc",
        t_start=0.0,
    )
    assert result.company_brief_text.startswith("=== STRATEGIC MANDATE ===")
    assert result.is_blocked is False
    assert result.confidence_score == pytest.approx(0.9)


def test_bridge_translate_falls_back_to_evidence_labels_when_brief_missing() -> None:
    bridge = AppsResearchBridge()

    class _Raw:
        run_id = "run-fallback"
        is_blocked = False
        block_reason = ""
        is_stale = False
        age_days = 0.0
        confidence_score = 0.75
        company_brief_text = ""
        evidence_items = [
            EvidenceItem(
                source_id="ev-1",
                label="Q1 NPW grew 8% YoY",
                uri="sha256:ev1",
                source_type="company_brief",
                field_ref="company_brief",
                confidence=0.75,
            )
        ]

    result = bridge._translate(
        raw=_Raw(),
        run_id="run-fallback",
        trace_id="bridge:rg:test:trace-fallback",
        request_id="req-fallback",
        t_start=0.0,
    )
    assert "Delegated company research briefing" in result.company_brief_text
    assert "Q1 NPW grew 8% YoY" in result.company_brief_text


def test_bridge_invoke_wires_apps_rg_targeting_brief_jd_context(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class _FakeRunner:
        def run_governed_e2e(self, *, request: Any) -> Any:
            captured["request"] = request
            raw = type("_Raw", (), {})()
            raw.run_id = "run-capture"
            raw.is_blocked = False
            raw.block_reason = ""
            raw.is_stale = False
            raw.age_days = 0.0
            raw.evidence_items = ()
            raw.confidence_score = 0.8
            raw.company_brief_text = "Captured brief"
            raw.support_coverage = 0.8
            return raw

    monkeypatch.setattr(
        "apps_research.integrations.governed_research_run.GovernedResearchRun",
        _FakeRunner,
    )

    bridge = AppsResearchBridge()
    result = bridge.fetch(**_fetch_kwargs(company_name="Anthropic", job_title="Partner ADE"))

    assert result.is_blocked is False
    assert result.company_brief_text == "Captured brief"
    req = captured["request"]
    jd = req.jd_context
    assert jd["output_format"] == "apps_rg_targeting_brief_v1"
    assert jd["synthesis_template"] == "apps_rg_targeting_brief_synthesis_v1"
    assert "Anthropic" in jd["content"]
    assert "Partner ADE" in jd["content"]
    assert req.mode == "brief"
    assert req.depth_profile == "COMPANY_BRIEF_STANDARD"


def test_mock_bridge_returns_configured_brief_without_live_research() -> None:
    bridge = MockAppsResearchBridge(
        company_brief_text="Mock SSOT targeting brief for resume lanes.",
        confidence_score=0.92,
    )
    result = bridge.fetch(**_fetch_kwargs())
    assert result.is_blocked is False
    assert result.company_brief_text == "Mock SSOT targeting brief for resume lanes."
    assert result.confidence_score == pytest.approx(0.92)
    assert len(result.evidence_items) >= 1
