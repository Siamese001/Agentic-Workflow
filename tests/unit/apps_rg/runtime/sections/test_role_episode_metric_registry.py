from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.role_episode_metric_registry import (
    approved_metric_outcome_ids_from_doc,
    approved_metric_outcome_ids_from_path,
    linked_metric_ids_missing_from_metric_nodes,
    linked_metric_outcome_ids_from_doc,
    metric_outcome_nodes_from_doc,
    metric_review_index_ids_from_doc,
    review_index_ids_missing_from_metric_nodes,
)


def test_metric_nodes_are_authority_for_approved_metric_ids() -> None:
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


def test_linked_metric_ids_preserve_order_and_report_missing_nodes() -> None:
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


def test_metric_registry_path_loader_uses_bundle_doc(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text(
        json.dumps({"metric_outcome_nodes": {"m1": {"label": "Revenue"}}}),
        encoding="utf-8",
    )

    assert approved_metric_outcome_ids_from_path(path) == ("m1",)
