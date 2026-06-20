"""Unit tests for the shared graph-evidence contract helpers."""

from __future__ import annotations

from apps_rg.runtime.sections.graph_evidence_contract import (
    build_graph_evidence_runtime_payload,
    build_selected_graph_evidence_plan,
)


def test_build_selected_graph_evidence_plan_preserves_section_metadata() -> None:
    plan = build_selected_graph_evidence_plan(
        section_id="headline",
        selection_method="canonical_headline",
        facts=[{"fact_id": "fact_a"}],
        required_fact_ids=["fact_a"],
        facts_semantics="candidate_fact_pool_full_records",
    )

    assert plan == {
        "section_id": "headline",
        "selection_method": "canonical_headline",
        "facts": [{"fact_id": "fact_a"}],
        "required_fact_ids": ["fact_a"],
        "facts_semantics": "candidate_fact_pool_full_records",
    }


def test_build_graph_evidence_runtime_payload_emits_both_era_keys(tmp_path) -> None:
    repo_root = tmp_path
    base_json_path = repo_root / "base.json"
    payload = build_graph_evidence_runtime_payload(
        run_id_prefix="headline",
        section_id="headline",
        prompt_id="headline_prompt_v1",
        repo_root=repo_root,
        base_json_path=base_json_path,
        base_hash="abc123",
        selected_graph_evidence_plan={"section_id": "headline", "facts": []},
        allowed_graph_evidence_ids=["fact_a", "fact_b"],
        target_title="SVP Engineering",
        target_company="Example Corp",
        jd_text="JD",
        briefing="Briefing",
        writable_context_scope="headline_only",
        extra_fields={"custom_flag": True},
    )

    assert payload["selected_graph_evidence_plan"] == {"section_id": "headline", "facts": []}
    assert payload["selected_fact_plan"] == {"section_id": "headline", "facts": []}
    assert payload["allowed_graph_evidence_ids"] == ["fact_a", "fact_b"]
    assert payload["allowed_fact_ids"] == ["fact_a", "fact_b"]
    assert payload["base_resume_json_ref"] == "base.json"
    assert payload["custom_flag"] is True
