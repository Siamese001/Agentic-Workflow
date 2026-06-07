"""Narrative role-episode packs must surface bound_skills allowed_phrases (graph vocabulary anchors)."""
from __future__ import annotations

from apps_rg.runtime.sections.ibm_role_episode_evidence import (
    WATSON_STUDIO_SKILL_ID,
    format_ibm_role_episode_evidence_pack,
)
from apps_rg.runtime.sections.unify_role_episode_evidence import (
    format_unify_role_episode_evidence_pack,
)


def test_ibm_narrative_pack_includes_bound_skills_allowed_phrases() -> None:
    payload: dict = {"selected_fact_plan": {"facts": []}, "allowed_fact_ids": []}
    text = format_ibm_role_episode_evidence_pack(payload, section_id="ibm_narrative")
    assert "bound_skills (graph authority — vocabulary anchors only):" in text
    assert "allowed_phrases:" in text
    assert WATSON_STUDIO_SKILL_ID in text
    assert "not metric-bearing authority" in text


def test_unify_narrative_pack_includes_bound_skills_allowed_phrases() -> None:
    payload: dict = {"selected_fact_plan": {"facts": []}, "allowed_fact_ids": []}
    text = format_unify_role_episode_evidence_pack(payload, section_id="unify_narrative")
    assert "bound_skills (graph authority — vocabulary anchors only):" in text
    assert "allowed_phrases:" in text
    assert "Synthesize the Unify role arc" in text
