"""apps-test-model: APP CONTRACT.

Regression tests for competencies JSON salvage after provider truncation.
"""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_lane_runtime import parse_model_json


def test_parse_model_json_salvages_truncated_categories_before_claim_ledger() -> None:
    raw = (
        '{"categories":[{"category_id":"ccb_partner","category_label":"Strategic Partnerships",'
        '"terms":[{"text":"cloud partner ecosystem GTM"}]}],'
        '"selected_fact_plan":{"section_id":"competencies"},'
        '"claim_ledger":[{"claim_text":"unterminated'
    )

    parsed, err = parse_model_json(raw)

    assert err == ""
    assert parsed is not None
    assert parsed["categories"][0]["category_id"] == "ccb_partner"
    assert parsed["claim_ledger"] == []
    assert parsed["change_log"][0]["operation"] == "salvage_truncated_competencies_json"


def test_parse_model_json_preserves_complete_categories_output() -> None:
    raw = (
        '{"categories":[{"category_id":"ccb_partner","category_label":"Strategic Partnerships",'
        '"terms":[{"text":"cloud partner ecosystem GTM"}]}],'
        '"claim_ledger":[{"claim_text":"cloud partner ecosystem GTM","source_fact_ids":["reb_1"]}]}'
    )

    parsed, err = parse_model_json(raw)

    assert err == ""
    assert parsed is not None
    assert parsed["categories"][0]["category_label"] == "Strategic Partnerships"
    assert parsed["claim_ledger"][0]["source_fact_ids"] == ["reb_1"]
