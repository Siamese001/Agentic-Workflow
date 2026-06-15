from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.role_episode_bundle_registry import (
    COMMON_ROLE_EPISODE_BUNDLE_FIELDS,
    DEFAULT_SHARED_SECTIONS,
    get_all_role_episode_bundles,
    get_role_episode_bundle_by_id,
    get_role_episode_bundles_for_section,
    validate_no_surface_bullet_ids,
    validate_role_episode_bundle_base,
)


def _bundle(**overrides: object) -> dict[str, object]:
    base = {field: f"value_{field}" for field in COMMON_ROLE_EPISODE_BUNDLE_FIELDS}
    base.update(
        {
            "role_episode_bundle_id": "reb_001",
            "employer": "IBM",
            "employer_node_id": "employer_ibm",
            "graph_skill_node_ids": ["skill_cloud"],
            "linked_metric_outcome_ids": ["metric_growth"],
            "executive_scope_signals": ["enterprise_scope"],
            "section_eligibility": ["ibm_narrative", "headline"],
        }
    )
    base.update(overrides)
    return base


def _write_doc(path: Path, bundles: list[dict[str, object]]) -> None:
    path.write_text(json.dumps({"bundles": bundles}), encoding="utf-8")


def test_role_episode_bundle_lookup_and_section_filter(tmp_path: Path) -> None:
    path = tmp_path / "bundles.json"
    _write_doc(
        path,
        [
            _bundle(role_episode_bundle_id="reb_ibm", section_eligibility=["ibm_narrative"]),
            _bundle(role_episode_bundle_id="reb_headline", section_eligibility=["headline"]),
        ],
    )

    assert [b["role_episode_bundle_id"] for b in get_all_role_episode_bundles(path)] == [
        "reb_ibm",
        "reb_headline",
    ]
    assert get_role_episode_bundle_by_id(path, "reb_ibm")["employer"] == "IBM"
    assert get_role_episode_bundle_by_id(path, "missing") is None
    assert [b["role_episode_bundle_id"] for b in get_role_episode_bundles_for_section(path, "headline")] == [
        "reb_headline",
    ]


def test_validate_role_episode_bundle_base_accepts_valid_bundle_with_shared_sections() -> None:
    violations = validate_role_episode_bundle_base(
        _bundle(section_eligibility=["headline"]),
        required_fields=COMMON_ROLE_EPISODE_BUNDLE_FIELDS,
        employer_id="IBM",
        employer_node_id="employer_ibm",
        valid_sections=["ibm_narrative"],
        valid_employer_labels=["IBM", "International Business Machines"],
    )

    assert violations == []
    assert "headline" in DEFAULT_SHARED_SECTIONS


def test_validate_role_episode_bundle_base_reports_authority_and_shape_errors() -> None:
    bad = _bundle(
        employer="Wrong Co",
        employer_node_id="wrong_node",
        graph_skill_node_ids=[],
        linked_metric_outcome_ids=[],
        executive_scope_signals=[],
        section_eligibility=["unknown_lane"],
    )
    bad.pop("claim_text")

    violations = validate_role_episode_bundle_base(
        bad,
        required_fields=COMMON_ROLE_EPISODE_BUNDLE_FIELDS,
        employer_id="IBM",
        employer_node_id="employer_ibm",
        valid_sections=["ibm_narrative"],
        require_linked_metric_outcome_ids=True,
    )
    blob = "\n".join(violations)

    assert "Missing required fields" in blob
    assert "claim_text" in blob
    assert "employer must be one of" in blob
    assert "employer_node_id must be" in blob
    assert "graph_skill_node_ids must not be empty" in blob
    assert "linked_metric_outcome_ids must not be empty" in blob
    assert "executive_scope_signals required" in blob
    assert "Unknown section_eligibility values" in blob


def test_validate_no_surface_bullet_ids_blocks_base_resume_ids() -> None:
    violations = validate_no_surface_bullet_ids(
        {"role_episode_bundle_id": "reb_001", "source": "bul_ibm_001"},
        bullet_prefix="bul_ibm_",
        label="IBM",
    )

    assert violations == [
        "base-resume bullet ids are forbidden as IBM graph proof; use role_episode_bundle_id"
    ]
    assert validate_no_surface_bullet_ids(
        {"role_episode_bundle_id": "reb_001"},
        bullet_prefix="bul_ibm_",
        label="IBM",
    ) == []
