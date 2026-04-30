"""Tests — W1 phase 3 calibration dataset (user §C class coverage)."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = REPO_ROOT / "data" / "certification" / "calibration_pairs.json"


def _read() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


class TestDatasetExists:
    def test_file_present(self):
        assert DATASET.exists(), f"Calibration dataset missing at {DATASET}"

    def test_valid_json(self):
        _read()  # will raise if invalid

    def test_schema_version(self):
        d = _read()
        # v2 supersedes v1; both contract-equivalent at the floor level.
        assert d["schema_version"] in (1, 2)
        assert d["dataset_id"] in (
            "rtc-req-055-calibration-v1",
            "rtc-req-055-calibration-v2",
        )


class TestClassCoverage:
    """User §C — at least 4 classes, each represented."""

    def test_all_required_classes_declared(self):
        d = _read()
        classes = set(d["classes"].keys())
        # v1 names OR v2 renamed names (both are contract-equivalent)
        v1_classes = {
            "paraphrase_positive",
            "near_miss_negative",
            "lexical_overlap_negative",
            "reference_contract_negative",
        }
        v2_classes_floor = {
            "paraphrase_positive",
            "near_miss_negative",
            "lexical_overlap_different_meaning_negative",
            "policy_tenant_freshness_reuse_negative",
        }
        # v1 exact OR v2 superset
        assert classes == v1_classes or v2_classes_floor.issubset(classes)

    def test_paraphrase_positives_floor(self):
        d = _read()
        count = sum(1 for p in d["pairs"] if p["class"] == "paraphrase_positive")
        assert count >= 8, f"Need >=8 paraphrase positives, got {count}"

    def test_near_miss_negatives_floor(self):
        d = _read()
        count = sum(1 for p in d["pairs"] if p["class"] == "near_miss_negative")
        assert count >= 6

    def test_lexical_overlap_negatives_floor(self):
        d = _read()
        # v1 name OR v2 renamed name
        count = sum(
            1 for p in d["pairs"]
            if p["class"] in (
                "lexical_overlap_negative",
                "lexical_overlap_different_meaning_negative",
            )
        )
        assert count >= 6

    def test_reference_contract_negatives_floor(self):
        d = _read()
        # v1 name OR v2 renamed name
        count = sum(
            1 for p in d["pairs"]
            if p["class"] in (
                "reference_contract_negative",
                "policy_tenant_freshness_reuse_negative",
            )
        )
        assert count >= 4


class TestSizeFloor:
    """User §C — 'more than two happy examples'."""

    def test_total_pair_count(self):
        d = _read()
        assert len(d["pairs"]) >= 20, (
            f"Dataset must have >=20 pairs to be meaningful; got {len(d['pairs'])}"
        )

    def test_measurable_pair_count(self):
        """Non-reference pairs (those the probe actually measures)."""
        d = _read()
        NON_MEASURABLE = {
            "reference_contract_negative",
            "policy_tenant_freshness_reuse_negative",
        }
        measurable = [p for p in d["pairs"]
                      if p["class"] not in NON_MEASURABLE]
        assert len(measurable) >= 16


class TestDatasetIntegrity:
    def test_no_duplicate_ids(self):
        d = _read()
        ids = [p["id"] for p in d["pairs"]]
        assert len(ids) == len(set(ids)), "Duplicate pair ids present"

    def test_no_empty_texts(self):
        d = _read()
        for p in d["pairs"]:
            assert p.get("text_a"), f"Pair {p.get('id')} has empty text_a"
            assert p.get("text_b"), f"Pair {p.get('id')} has empty text_b"

    def test_positives_distinct_text_a_text_b(self):
        d = _read()
        for p in d["pairs"]:
            if p["class"] == "paraphrase_positive":
                assert p["text_a"] != p["text_b"], (
                    f"Positive pair {p['id']} has identical text_a == text_b; "
                    f"that does not test paraphrase capability."
                )

    def test_each_pair_has_id_and_class_and_notes(self):
        d = _read()
        for p in d["pairs"]:
            assert "id" in p
            assert "class" in p
            assert "notes" in p
            assert p["class"] in d["classes"]


class TestProductionThresholdReference:
    def test_dataset_declares_production_threshold(self):
        d = _read()
        assert d["production_threshold_target"] == 0.95, (
            "Dataset must reference the production threshold (0.95 dynamic tier)"
        )

    def test_dataset_declares_expected_model(self):
        d = _read()
        assert d["embedding_model_required"] == "BAAI/bge-m3"
