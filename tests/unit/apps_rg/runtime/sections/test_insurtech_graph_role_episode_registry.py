from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections import insurtech_graph_role_episode_registry as insurtech


def _insurtech_bundle(**overrides: object) -> dict[str, object]:
    bundle: dict[str, object] = {
        "role_episode_bundle_id": "reb_insurtech_001",
        "employer": insurtech.INSURTECH_EMPLOYER_ID,
        "title": "Director",
        "employer_node_id": insurtech.INSURTECH_EMPLOYER_NODE_ID,
        "bundle_theme": "insurance platform modernization",
        "claim_text": "Modernized insurance platform delivery.",
        "support_level": "graph_backed",
        "executive_scope_signals": ["portfolio_scope"],
        "architecture_scope_signals": ["cloud_modernization"],
        "graph_skill_node_ids": ["skill_cloud"],
        "linked_source_fact_ids": ["fact_insurtech_001"],
        "linked_archive_signal_ids": ["archive_insurtech_001"],
        "linked_metric_outcome_ids": ["metric_insurtech_001"],
        "metric_candidates": [
            {
                "metric_id": "metric_insurtech_held",
                "claim_text_pattern": "availability uplift",
                "proof_shape": "qualitative",
                "approval_status": "HELD",
            }
        ],
        "operating_context": "insurance SaaS",
        "bullet_intent": "prove platform modernization",
        "section_eligibility": ["insurtech_bullets", "executive_summary"],
    }
    bundle.update(overrides)
    return bundle


def _write_doc(path: Path, bundles: list[dict[str, object]]) -> Path:
    path.write_text(json.dumps({"bundles": bundles}), encoding="utf-8")
    return path


def test_insurtech_registry_loads_filters_and_looks_up_bundles(tmp_path: Path) -> None:
    path = _write_doc(
        tmp_path / "insurtech_bundles.json",
        [
            _insurtech_bundle(
                role_episode_bundle_id="reb_insurtech_bullets",
                section_eligibility=["insurtech_bullets"],
            ),
            _insurtech_bundle(
                role_episode_bundle_id="reb_insurtech_narrative",
                section_eligibility=["insurtech_narrative"],
            ),
        ],
    )

    assert [b["role_episode_bundle_id"] for b in insurtech.get_all_bundles(path)] == [
        "reb_insurtech_bullets",
        "reb_insurtech_narrative",
    ]
    assert (
        insurtech.get_bundle_by_id("reb_insurtech_narrative", path)["employer"]
        == insurtech.INSURTECH_EMPLOYER_ID
    )
    assert insurtech.get_bundle_by_id("missing", path) is None
    assert [
        b["role_episode_bundle_id"]
        for b in insurtech.get_bundles_for_section("insurtech_bullets", path)
    ] == ["reb_insurtech_bullets"]


def test_insurtech_validate_bundle_accepts_valid_bundle_and_shared_sections() -> None:
    ok, violations = insurtech.validate_bundle(_insurtech_bundle())

    assert ok is True
    assert violations == []


def test_insurtech_validate_bundle_reports_policy_violations() -> None:
    bad = _insurtech_bundle(
        employer="Wrong Employer",
        employer_node_id="wrong_node",
        graph_skill_node_ids=[],
        linked_metric_outcome_ids=[],
        executive_scope_signals=[],
        section_eligibility=["unknown_section"],
        metric_candidates=[{"metric_id": "bad", "claim_text_pattern": "$10M TCO"}],
    )
    bad.pop("claim_text")

    ok, violations = insurtech.validate_bundle(bad)
    blob = "\n".join(violations)

    assert ok is False
    assert "Missing required fields" in blob
    assert "employer must be one of" in blob
    assert "employer_node_id must be" in blob
    assert "graph_skill_node_ids must not be empty" in blob
    assert "linked_metric_outcome_ids must not be empty" in blob
    assert "executive_scope_signals required" in blob
    assert "Unknown section_eligibility values" in blob
    assert "Generic absolute TCO claim '$10M TCO'" in blob


def test_insurtech_role_episode_bundle_id_gate_blocks_missing_context() -> None:
    insurtech.assert_role_episode_bundle_id_present(
        {"role_episode_bundle_id": "reb_insurtech_001"}
    )

    with pytest.raises(ValueError, match="role_episode_bundle_id"):
        insurtech.assert_role_episode_bundle_id_present(
            {"section": "insurtech_bullets"}
        )

