"""W2: SelectedRoleFactSet path threaded through canonical CLI dispatch (all generated lanes).

Structural / plumbing contract — SRFS file authority is contract-fixture only; product path uses graph proof pool.
"""

from __future__ import annotations

from typing import Any

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES


def _stub_spine_return() -> dict[str, Any]:
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
def test_run_canonical_passes_section_to_spine(monkeypatch, lane: str) -> None:
    from apps_rg.runtime.spine import apps_rg_spine_run as spine

    captured: dict[str, Any] = {}

    def capture_spine(**kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return _stub_spine_return()

    monkeypatch.setattr(spine, "run_apps_rg_spine", capture_spine)

    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Acme Labs",
        target_role="VP Engineering",
        section=lane,
    )

    assert captured.get("section_id") == lane
    assert captured.get("scope") == "section"


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
