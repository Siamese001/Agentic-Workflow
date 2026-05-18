"""W2: SelectedRoleFactSet path threaded through canonical CLI dispatch (all generated lanes).

Structural / plumbing contract only — SRFS consumption per lane is W3+.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES


def _stub_lane_return() -> dict[str, Any]:
    return {
        "exit_status": "success",
        "execution_status": "completed",
        "outcome_authorized": False,
        "x3_disposition": "",
        "fault": "",
        "artifact_dir": "",
        "run_id": "",
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
        "competencies_cli_output_text": "",
    }


_RUNNER_BY_LANE: dict[str, str] = {
    "headline": "_run_headline_lane_from_cli",
    "executive_summary": "_run_executive_summary_lane_from_cli",
    "unify_bullets": "_run_unify_bullets_lane_from_cli",
    "unify_narrative": "_run_unify_narrative_lane_from_cli",
    "ibm_bullets": "_run_ibm_bullets_lane_from_cli",
    "ibm_narrative": "_run_ibm_narrative_lane_from_cli",
    "competencies": "_run_competencies_lane_from_cli",
}


def test_cli_help_selected_role_fact_set_not_executive_only() -> None:
    from apps_rg.__main__ import _build_parser

    parser = _build_parser()
    action = next(
        a
        for a in parser._actions
        if getattr(a, "dest", None) == "selected_role_fact_set"
    )
    help_text = str(action.help or "")
    lower = help_text.lower()
    assert "ignored unless" not in lower
    assert "executive_summary-only" not in lower
    assert "generated apps_rg" in lower
    assert "section-specific" in lower


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_run_canonical_passes_selected_role_fact_set_to_lane_runner(monkeypatch, lane: str) -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    srfs_path = "artifacts/apps_rg/fact_inventory/example_srfs.json"
    captured: dict[str, Any] = {}

    def capture_runner(**kwargs: Any) -> dict[str, Any]:  # type: ignore[no-untyped-def]
        captured.update(kwargs)
        return _stub_lane_return()

    runner_attr = _RUNNER_BY_LANE[lane]
    monkeypatch.setattr(cd, runner_attr, capture_runner)

    cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Acme Labs",
        target_role="VP Engineering",
        section=lane,
        selected_role_fact_set=srfs_path,
    )

    assert captured.get("selected_role_fact_set") == srfs_path


def test_headline_and_competencies_lane_args_carry_selected_role_fact_set() -> None:
    from apps_rg.runtime.sections import competencies_lane, headline_lane

    p = "fixtures/srfs_demo.json"
    h = headline_lane.build_headline_lane_args(
        provider="mock",
        temperature=0.45,
        x1d_judges="gemini_pro",
        mock_judges=True,
        target_title="T",
        target_company="C",
        jd_text="J",
        briefing="B",
        selected_role_fact_set=p,
    )
    assert getattr(h, "selected_role_fact_set", "") == p

    c = competencies_lane.build_competencies_lane_args(
        provider="mock",
        temperature=0.45,
        x1d_judges="gemini_pro",
        mock_judges=True,
        target_title="T",
        target_company="C",
        jd_text="J",
        briefing="B",
        selected_role_fact_set=p,
    )
    assert getattr(c, "selected_role_fact_set", "") == p


def test_section_cli_still_dispatches_via_canonical_primitives_only() -> None:
    """Guard: section lane path should not add a parallel dispatcher module."""
    repo = Path(__file__).resolve().parents[2]
    main_src = (repo / "apps_rg" / "__main__.py").read_text(encoding="utf-8")
    assert "run_canonical_apps_rg_from_cli_primitives" in main_src
    # Obvious anti-patterns for a splinter entry surface (none expected).
    assert "run_srfs_section_dispatch" not in main_src


def test_canonical_dispatch_exposes_all_generated_lane_runners() -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    for lane in GENERATED_LANES:
        name = _RUNNER_BY_LANE[lane]
        assert callable(getattr(cd, name))

