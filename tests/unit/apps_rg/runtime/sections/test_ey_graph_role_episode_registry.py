from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections import ey_graph_role_episode_registry as ey


def _ey_bundle(**overrides: object) -> dict[str, object]:
    bundle: dict[str, object] = {
        "role_episode_bundle_id": "reb_ey_001",
        "employer": ey.EY_EMPLOYER_ID,
        "title": "Senior Manager",
        "employer_node_id": ey.EY_EMPLOYER_NODE_ID,
        "bundle_theme": "regulated transformation",
        "claim_text": "Led regulated transformation programs.",
        "support_level": "graph_backed",
        "executive_scope_signals": ["portfolio_scope"],
        "architecture_scope_signals": ["platform_modernization"],
        "graph_skill_node_ids": ["skill_architecture"],
        "linked_source_fact_ids": ["fact_ey_001"],
        "linked_archive_signal_ids": ["archive_ey_001"],
        "linked_metric_outcome_ids": ["metric_ey_001"],
        "metric_candidates": [
            {
                "metric_id": "metric_ey_held",
                "claim_text_pattern": "capital efficiency",
                "proof_shape": "qualitative",
                "approval_status": "HELD",
            }
        ],
        "operating_context": "insurance advisory",
        "bullet_intent": "prove regulated delivery",
        "section_eligibility": ["ey_bullets", "executive_summary"],
    }
    bundle.update(overrides)
    return bundle


def _write_doc(path: Path, bundles: list[dict[str, object]]) -> Path:
    path.write_text(json.dumps({"bundles": bundles}), encoding="utf-8")
    return path


def test_ey_registry_loads_filters_and_looks_up_bundles(tmp_path: Path) -> None:
    path = _write_doc(
        tmp_path / "ey_bundles.json",
        [
            _ey_bundle(role_episode_bundle_id="reb_ey_bullets", section_eligibility=["ey_bullets"]),
            _ey_bundle(role_episode_bundle_id="reb_ey_narrative", section_eligibility=["ey_narrative"]),
        ],
    )

    assert [b["role_episode_bundle_id"] for b in ey.get_all_bundles(path)] == [
        "reb_ey_bullets",
        "reb_ey_narrative",
    ]
    assert ey.get_bundle_by_id("reb_ey_narrative", path)["employer"] == ey.EY_EMPLOYER_ID
    assert ey.get_bundle_by_id("missing", path) is None
    assert [b["role_episode_bundle_id"] for b in ey.get_bundles_for_section("ey_bullets", path)] == [
        "reb_ey_bullets",
    ]


def test_ey_validate_bundle_accepts_valid_bundle_and_shared_sections() -> None:
    ok, violations = ey.validate_bundle(_ey_bundle())

    assert ok is True
    assert violations == []


def test_ey_validate_bundle_reports_policy_violations() -> None:
    bad = _ey_bundle(
        employer="Wrong Employer",
        employer_node_id="wrong_node",
        graph_skill_node_ids=[],
        linked_metric_outcome_ids=[],
        executive_scope_signals=[],
        section_eligibility=["unknown_section"],
        typed_edges=["forbidden"],
        source="bul_ey_001",
        metric_candidates=[
            {"metric_id": "metric_bad", "approval_status": "PROMOTABLE"}
        ],
    )
    bad.pop("claim_text")

    ok, violations = ey.validate_bundle(bad)
    blob = "\n".join(violations)

    assert ok is False
    assert "Missing required fields" in blob
    assert "employer must be one of" in blob
    assert "employer_node_id must be" in blob
    assert "graph_skill_node_ids must not be empty" in blob
    assert "linked_metric_outcome_ids must not be empty" in blob
    assert "executive_scope_signals required" in blob
    assert "Unknown section_eligibility values" in blob
    assert "base-resume bullet ids are forbidden as EY graph proof" in blob
    assert "typed-edge fields are excluded by EY edge policy" in blob
    assert "metric candidate missing claim_text_pattern" in blob
    assert "metric candidate cannot be PROMOTABLE" in blob


def test_ey_role_episode_bundle_id_gate_blocks_missing_context() -> None:
    ey.assert_role_episode_bundle_id_present({"role_episode_bundle_id": "reb_ey_001"})

    with pytest.raises(ValueError, match="role_episode_bundle_id"):
        ey.assert_role_episode_bundle_id_present({"section": "ey_bullets"})

