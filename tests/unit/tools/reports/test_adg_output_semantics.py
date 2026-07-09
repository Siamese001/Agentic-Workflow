from __future__ import annotations

from tools.reports.adg_output_semantics import action_semantics, impact_severity_from_band


def test_p0_work_priority_is_only_for_open_blocker_actions() -> None:
    blocker = {"verdict_cluster": "FIX", "sort_band": "P1"}
    candidate = {"verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE", "sort_band": "P0"}

    assert action_semantics(blocker) == {
        "impact_severity": "high",
        "enforcement_effect": "blocker",
        "disposition": "open",
        "work_priority": "P0",
        "queue_section": "open_blockers",
    }
    assert action_semantics(candidate) == {
        "impact_severity": "critical",
        "enforcement_effect": "inventory",
        "disposition": "open",
        "work_priority": "triage",
        "queue_section": "candidate_blockers",
    }


def test_legacy_p_band_maps_to_impact_severity_not_work_priority() -> None:
    assert impact_severity_from_band("P0") == "critical"
    assert impact_severity_from_band("P1") == "high"
