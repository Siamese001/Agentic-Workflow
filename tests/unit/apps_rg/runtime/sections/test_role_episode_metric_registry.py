"""Unit tests for role-episode bundle + metric registry helpers (graph authority W1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.role_episode_bundle_registry import (
    get_role_episode_bundle_by_id,
    get_role_episode_bundles_for_section,
    validate_no_surface_bullet_ids,
    validate_role_episode_bundle_base,
)
from apps_rg.runtime.sections.role_episode_metric_registry import (
    approved_metric_outcome_ids_from_doc,
    approved_metric_outcome_ids_from_path,
    linked_metric_ids_missing_from_metric_nodes,
    linked_metric_outcome_ids_from_doc,
    metric_outcome_nodes_from_doc,
    metric_review_index_ids_from_doc,
    review_index_ids_missing_from_metric_nodes,
)

REPO = Path(__file__).resolve().parents[5]
INSURTECH_GRAPH = REPO / "apps_rg" / "fact_inventory" / "insurtech_role_episode_bundles.json"
EY_GRAPH = REPO / "apps_rg" / "fact_inventory" / "ey_role_episode_bundles.json"


def _minimal_bundle(**overrides) -> dict:
    base = {
        "role_episode_bundle_id": "reb_test_001",
        "employer": "InsurTech Cloud Solutions",
        "title": "Founder",
        "employer_node_id": "employment_exp_insurtech_001",
        "bundle_theme": "theme",
        "graph_skill_node_ids": ["skill_1"],
        "executive_scope_signals": ["scope"],
        "section_eligibility": ["insurtech_bullets", "competencies"],
    }
    base.update(overrides)
    return base


class TestMetricOutcomeNodesFromDoc:
    def test_dict_form(self) -> None:
        doc = {"metric_outcome_nodes": {"m1": {"metric_outcome_id": "m1"}}}
        nodes = metric_outcome_nodes_from_doc(doc)
        assert nodes == {"m1": {"metric_outcome_id": "m1"}}

    def test_list_form(self) -> None:
        doc = {"metric_outcome_nodes": [{"metric_outcome_id": "m2", "metric": "42%"}]}
        nodes = metric_outcome_nodes_from_doc(doc)
        assert "m2" in nodes

    def test_approved_ids_follow_graph_native_nodes_only(self) -> None:
        doc = {
            "metric_outcome_nodes": {"approved": {"metric_outcome_id": "approved"}},
            "approved_metric_outcome_ids": {"stale_review_only": {}},
        }
        assert approved_metric_outcome_ids_from_doc(doc) == ("approved",)

    def test_metric_nodes_are_authority_for_approved_metric_ids(self) -> None:
        doc = {
            "metric_outcome_nodes": {
                "m1": {"label": "Revenue impact"},
                "m2": {"label": "Delivery scale"},
            },
            "approved_metric_outcome_ids": {"m1": True, "stale_review_id": True},
        }

        assert approved_metric_outcome_ids_from_doc(doc) == ("m1", "m2")
        assert metric_review_index_ids_from_doc(doc, "approved_metric_outcome_ids") == (
            "m1",
            "stale_review_id",
        )
        assert review_index_ids_missing_from_metric_nodes(doc) == ("stale_review_id",)


class TestMetricAuthorityGaps:
    def test_linked_metric_missing_from_nodes(self) -> None:
        doc = {
            "metric_outcome_nodes": {"m_ok": {"metric_outcome_id": "m_ok"}},
            "bundles": [
                {"linked_metric_outcome_ids": ["m_ok", "m_orphan"]},
                {"linked_metric_outcome_ids": ["m_orphan"]},
            ],
        }
        assert linked_metric_ids_missing_from_metric_nodes(doc) == ("m_orphan",)

    def test_linked_metric_ids_preserve_order_and_report_missing_nodes(self) -> None:
        doc = {
            "metric_outcome_nodes": [{"metric_outcome_id": "m2", "label": "Scale"}],
            "bundles": [
                {"linked_metric_outcome_ids": ["m1", "m2"]},
                {"linked_metric_outcome_ids": ["m2", "m3", ""]},
            ],
        }

        assert metric_outcome_nodes_from_doc(doc) == {"m2": {"metric_outcome_id": "m2", "label": "Scale"}}
        assert linked_metric_outcome_ids_from_doc(doc) == ("m1", "m2", "m3")
        assert linked_metric_ids_missing_from_metric_nodes(doc) == ("m1", "m3")

    def test_review_index_missing_from_nodes(self) -> None:
        doc = {
            "metric_outcome_nodes": {"m1": {"metric_outcome_id": "m1"}},
            "approved_metric_outcome_ids": {"m1": {}, "ghost": {}},
        }
        assert review_index_ids_missing_from_metric_nodes(doc) == ("ghost",)


class TestRoleEpisodeBundleRegistry:
    def test_section_filter_and_lookup(self, tmp_path: Path) -> None:
        doc = {
            "bundles": [
                {
                    "role_episode_bundle_id": "reb_a",
                    "section_eligibility": ["insurtech_bullets"],
                },
                {
                    "role_episode_bundle_id": "reb_b",
                    "section_eligibility": ["ey_bullets"],
                },
            ]
        }
        path = tmp_path / "bundles.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        assert [b["role_episode_bundle_id"] for b in get_role_episode_bundles_for_section(path, "insurtech_bullets")] == ["reb_a"]
        assert get_role_episode_bundle_by_id(path, "reb_b")["role_episode_bundle_id"] == "reb_b"
        assert get_role_episode_bundle_by_id(path, "missing") is None

    def test_validate_bundle_base_catches_employer_and_section_violations(self) -> None:
        bundle = _minimal_bundle(employer="Wrong Co", section_eligibility=["unknown_lane"])
        violations = validate_role_episode_bundle_base(
            bundle,
            required_fields=("role_episode_bundle_id", "employer", "employer_node_id", "section_eligibility"),
            employer_id="InsurTech Cloud Solutions",
            employer_node_id="employment_exp_insurtech_001",
            valid_sections={"insurtech_bullets", "insurtech_narrative"},
        )
        assert any("employer must be" in v for v in violations)
        assert any("Unknown section_eligibility" in v for v in violations)

    def test_validate_bundle_requires_executive_scope_signals(self) -> None:
        bundle = _minimal_bundle(executive_scope_signals=[])
        violations = validate_role_episode_bundle_base(
            bundle,
            required_fields=("role_episode_bundle_id",),
            employer_id="InsurTech Cloud Solutions",
            employer_node_id="employment_exp_insurtech_001",
            valid_sections={"insurtech_bullets"},
        )
        assert any("executive_scope_signals required" in v for v in violations)

    def test_validate_no_surface_bullet_ids(self) -> None:
        bundle = _minimal_bundle(notes="derived from bul_insurtech_001")
        violations = validate_no_surface_bullet_ids(
            bundle,
            bullet_prefix="bul_insurtech_",
            label="InsurTech",
        )
        assert violations and "forbidden" in violations[0]


def test_metric_registry_path_loader_uses_bundle_doc(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text(
        json.dumps({"metric_outcome_nodes": {"m1": {"label": "Revenue"}}}),
        encoding="utf-8",
    )

    assert approved_metric_outcome_ids_from_path(path) == ("m1",)


@pytest.mark.parametrize("graph_path", [INSURTECH_GRAPH, EY_GRAPH])
def test_live_graph_bundle_linked_metrics_exist_in_metric_nodes(graph_path: Path) -> None:
    """Regression: bundle-linked metric IDs must resolve to graph-native metric nodes."""
    doc = json.loads(graph_path.read_text(encoding="utf-8"))
    missing = linked_metric_ids_missing_from_metric_nodes(doc)
    assert missing == (), f"{graph_path.name} has orphan linked_metric_outcome_ids: {missing}"
