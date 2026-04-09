"""Tests for the evidence shaping pipeline."""

from __future__ import annotations

import pytest

from tools.adg.prompt_assembly.contracts import ContradictionFlag, EvidenceBundle, EvidenceItem
from tools.adg.prompt_assembly.shaping.evidence_shaper import (
    _compute_coverage,
    _dedupe_items,
    _identify_gaps,
    _normalize_fields,
    _reconcile_counts,
    shape_evidence,
)


# ---------------------------------------------------------------------------
# Normalize
# ---------------------------------------------------------------------------


class TestNormalizeFields:
    def test_alias_mapping(self) -> None:
        data = {"file_path": "/a/b.py", "lineno": 42, "type": "imports"}
        result = _normalize_fields(data)
        assert result["source_file"] == "/a/b.py"
        assert result["line_no"] == 42
        assert result["relation_type"] == "imports"

    def test_nested_normalization(self) -> None:
        data = {"inner": {"filepath": "/x.py"}, "items": [{"kind": "module"}]}
        result = _normalize_fields(data)
        assert result["inner"]["source_file"] == "/x.py"
        assert result["items"][0]["identity_kind"] == "module"

    def test_unknown_keys_pass_through(self) -> None:
        data = {"custom_field": "value"}
        result = _normalize_fields(data)
        assert result["custom_field"] == "value"


# ---------------------------------------------------------------------------
# Dedupe
# ---------------------------------------------------------------------------


class TestDedupeItems:
    def test_removes_duplicates(self) -> None:
        item = EvidenceItem(
            source_artifact="test.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            row_references=["row:1"],
            data={"x": 1},
        )
        result = _dedupe_items([item, item])
        assert len(result) == 1

    def test_dedupes_empty_row_refs(self) -> None:
        """Two items with same source_artifact, source_type, and empty row_references dedupe to 1."""
        item1 = EvidenceItem(
            source_artifact="db.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            data={"x": 1},
        )
        item2 = EvidenceItem(
            source_artifact="db.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            data={"x": 2},
        )
        result = _dedupe_items([item1, item2])
        assert len(result) == 1
        assert result[0].data == {"x": 1}  # first one kept

    def test_keeps_different_items(self) -> None:
        item1 = EvidenceItem(
            source_artifact="a.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            row_references=["row:1"],
        )
        item2 = EvidenceItem(
            source_artifact="b.json",
            source_type="json_report",
            snapshot_id="ts",
            row_references=["row:2"],
        )
        result = _dedupe_items([item1, item2])
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Reconcile
# ---------------------------------------------------------------------------


class TestReconcileCounts:
    def test_detects_node_count_mismatch_minor(self) -> None:
        db_item = EvidenceItem(
            source_artifact="db.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            data={"db_node_count": 65708},
        )
        report_item = EvidenceItem(
            source_artifact="snapshot.json",
            source_type="json_report",
            snapshot_id="ts",
            data={"modules_total": 65682},
        )
        contradictions = _reconcile_counts([db_item, report_item])
        assert len(contradictions) == 1
        assert contradictions[0].field_name == "node_count"
        assert contradictions[0].severity == "minor"  # diff=26, < 100 threshold

    def test_detects_node_count_mismatch_major(self) -> None:
        db_item = EvidenceItem(
            source_artifact="db.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            data={"db_node_count": 70000},
        )
        report_item = EvidenceItem(
            source_artifact="snapshot.json",
            source_type="json_report",
            snapshot_id="ts",
            data={"modules_total": 69800},
        )
        contradictions = _reconcile_counts([db_item, report_item])
        assert len(contradictions) == 1
        assert contradictions[0].severity == "major"  # diff=200, > 100 threshold

    def test_no_contradiction_when_matching(self) -> None:
        db_item = EvidenceItem(
            source_artifact="db.sqlite",
            source_type="sqlite",
            snapshot_id="ts",
            data={"db_node_count": 100},
        )
        report_item = EvidenceItem(
            source_artifact="snapshot.json",
            source_type="json_report",
            snapshot_id="ts",
            data={"modules_total": 100},
        )
        contradictions = _reconcile_counts([db_item, report_item])
        assert len(contradictions) == 0

    def test_detects_provenance_edges_mismatch(self) -> None:
        item = EvidenceItem(
            source_artifact="provenance.json",
            source_type="json_report",
            snapshot_id="ts",
            data={
                "reconciliation": {
                    "nodes_match": True,
                    "edges_match": False,
                    "db_edges": 12000,
                    "report_edges": 11500,
                }
            },
        )
        contradictions = _reconcile_counts([item])
        assert len(contradictions) == 1
        assert contradictions[0].field_name == "provenance_edges_match"
        assert contradictions[0].severity == "major"
        assert contradictions[0].value_a == 12000
        assert contradictions[0].value_b == 11500

    def test_detects_provenance_nodes_mismatch(self) -> None:
        item = EvidenceItem(
            source_artifact="provenance.json",
            source_type="json_report",
            snapshot_id="ts",
            data={
                "reconciliation": {
                    "nodes_match": False,
                    "db_nodes": 65708,
                    "report_nodes": 65682,
                    "edges_match": True,
                }
            },
        )
        contradictions = _reconcile_counts([item])
        assert len(contradictions) == 1
        assert contradictions[0].field_name == "provenance_nodes_match"


# ---------------------------------------------------------------------------
# Coverage and Gaps
# ---------------------------------------------------------------------------


class TestCoverageAndGaps:
    def test_full_coverage(self) -> None:
        items = [
            EvidenceItem(
                source_artifact="provenance_report_ts.json", source_type="json_report", snapshot_id="ts"
            ),
            EvidenceItem(
                source_artifact="closure_validation_report_ts.json",
                source_type="json_report",
                snapshot_id="ts",
            ),
            EvidenceItem(source_artifact="db.sqlite", source_type="sqlite", snapshot_id="ts"),
        ]
        score = _compute_coverage(items, ["provenance_report", "closure_report", "sqlite"])
        assert score == 1.0

    def test_partial_coverage(self) -> None:
        items = [
            EvidenceItem(source_artifact="db.sqlite", source_type="sqlite", snapshot_id="ts"),
        ]
        score = _compute_coverage(items, ["provenance_report", "sqlite"])
        assert 0.0 < score < 1.0

    def test_gaps_identified(self) -> None:
        items = [
            EvidenceItem(source_artifact="db.sqlite", source_type="sqlite", snapshot_id="ts"),
        ]
        gaps = _identify_gaps(items, ["provenance_report", "closure_report", "sqlite"])
        assert "missing_must_use_source:provenance_report" in gaps
        assert "missing_must_use_source:closure_report" in gaps

    def test_error_items_not_counted(self) -> None:
        items = [
            EvidenceItem(
                source_artifact="db.sqlite", source_type="sqlite", snapshot_id="ts", data={"error": "missing"}
            ),
        ]
        score = _compute_coverage(items, ["sqlite"])
        assert score == 0.0


# ---------------------------------------------------------------------------
# Full shape_evidence pipeline
# ---------------------------------------------------------------------------


class TestShapeEvidence:
    def test_basic_shaping(self) -> None:
        items = [
            EvidenceItem(
                source_artifact="provenance_report_ts.json",
                source_type="json_report",
                snapshot_id="ts",
                freshness="2026-04-08T23:00:00Z",
                data={"reconciliation": {"nodes_match": True, "edges_match": True}},
            ),
        ]
        bundle = shape_evidence(items, must_use_sources=["provenance_report"])
        assert isinstance(bundle, EvidenceBundle)
        assert bundle.coverage_score == 1.0
        assert bundle.contradiction_status == "none"
        assert bundle.gaps == []

    def test_contradiction_preserved(self) -> None:
        items = [
            EvidenceItem(
                source_artifact="provenance_report_ts.json",
                source_type="json_report",
                snapshot_id="ts",
                data={
                    "reconciliation": {
                        "nodes_match": False,
                        "db_nodes": 100,
                        "report_nodes": 90,
                        "edges_match": True,
                    }
                },
            ),
        ]
        bundle = shape_evidence(items)
        assert bundle.contradiction_status == "major"
        assert len(bundle.contradictions) >= 1

    def test_empty_items_no_must_use(self) -> None:
        """Empty items with no must_use_sources → coverage 1.0, no gaps."""
        bundle = shape_evidence([], must_use_sources=[])
        assert bundle.coverage_score == 1.0
        assert bundle.gaps == []
        assert bundle.items == []
        assert bundle.contradiction_status == "none"

    def test_empty_items_with_must_use(self) -> None:
        """Empty items with must_use_sources → coverage 0.0, gaps listed, weak_support."""
        bundle = shape_evidence([], must_use_sources=["sqlite", "ratchet"])
        assert bundle.coverage_score == 0.0
        assert len(bundle.gaps) == 2
        assert bundle.weak_support is True

    def test_weak_support_flagged(self) -> None:
        items = [
            EvidenceItem(
                source_artifact="db.sqlite",
                source_type="sqlite",
                snapshot_id="ts",
                data={"something": True},
            ),
        ]
        bundle = shape_evidence(
            items,
            must_use_sources=[
                "provenance_report",
                "closure_report",
                "sqlite",
                "ratchet",
            ],
        )
        assert bundle.coverage_score < 0.5
        assert bundle.weak_support is True
