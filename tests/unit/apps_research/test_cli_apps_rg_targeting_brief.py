"""apps-test-model: APP CONTRACT.

apps_research CLI handoff tests for apps_rg targeting briefs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class _FakeRecord:
    run_id: str
    topic: str
    company_brief_text: str
    confidence_score: float = 0.91
    support_coverage: float = 0.88
    hop_terminal_error: str = ""
    fec_run_context: dict | None = None


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
            company_brief_text=(
                "Anthropic - Manager targeting brief\n"
                "| Manager | band | Reports to Partnerships |\n\n"
                "=== STRATEGIC MANDATE ===\n"
                "- Partner-led enterprise AI deployment at scale\n"
            ),
            fec_run_context={"company_brief": {"company": "Anthropic"}},
        )

    monkeypatch.setattr(main_mod, "_run_research_record", _fake_run)
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: runs_root)

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


def test_cli_jd_path_fails_closed_without_targeting_markdown(
    monkeypatch, tmp_path: Path
) -> None:
    from apps_research import __main__ as main_mod

    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("Partner architecture JD", encoding="utf-8")
    monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path / "runs")
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
