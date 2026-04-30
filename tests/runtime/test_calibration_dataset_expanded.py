"""W1 phase 4 — expanded calibration dataset coverage.

Tests the v2 schema + new class counts + stability of v1 pair IDs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = REPO_ROOT / "data" / "certification" / "calibration_pairs.json"


@pytest.fixture(scope="module")
def dataset() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


class TestSchemaV2:
    def test_schema_version_is_2(self, dataset):
        assert dataset["schema_version"] == 2

    def test_dataset_id_is_v2(self, dataset):
        assert dataset["dataset_id"] == "rtc-req-055-calibration-v2"

    def test_supersedes_v1(self, dataset):
        assert dataset.get("supersedes") == "rtc-req-055-calibration-v1"


class TestSixClassesDeclared:
    def test_classes_block_has_six(self, dataset):
        assert len(dataset["classes"]) == 6

    def test_all_user_approved_classes_present(self, dataset):
        required = {
            "paraphrase_positive",
            "abbreviation_definition_positive",
            "short_form_reminder_positive",
            "near_miss_negative",
            "lexical_overlap_different_meaning_negative",
            "policy_tenant_freshness_reuse_negative",
        }
        assert set(dataset["classes"].keys()) == required

    def test_each_class_declares_safety_tier(self, dataset):
        for cls_name, cls_block in dataset["classes"].items():
            assert "safety_tier" in cls_block, f"class {cls_name} missing safety_tier"

    def test_policy_class_is_safety_critical(self, dataset):
        assert (
            dataset["classes"]["policy_tenant_freshness_reuse_negative"]["safety_tier"]
            == "safety_critical"
        )

    def test_near_miss_class_is_safety_critical(self, dataset):
        assert (
            dataset["classes"]["near_miss_negative"]["safety_tier"] == "safety_critical"
        )


class TestClassCountFloors:
    def test_paraphrase_positive_floor_20(self, dataset):
        n = sum(1 for p in dataset["pairs"] if p["class"] == "paraphrase_positive")
        assert n >= 20, f"expected >=20 paraphrase_positive, got {n}"

    def test_abbreviation_definition_positive_floor_12(self, dataset):
        n = sum(1 for p in dataset["pairs"] if p["class"] == "abbreviation_definition_positive")
        assert n >= 12

    def test_short_form_reminder_positive_floor_8(self, dataset):
        n = sum(1 for p in dataset["pairs"] if p["class"] == "short_form_reminder_positive")
        assert n >= 8

    def test_near_miss_negative_floor_15(self, dataset):
        n = sum(1 for p in dataset["pairs"] if p["class"] == "near_miss_negative")
        assert n >= 15

    def test_lexical_overlap_negative_floor_15(self, dataset):
        n = sum(
            1
            for p in dataset["pairs"]
            if p["class"] == "lexical_overlap_different_meaning_negative"
        )
        assert n >= 15

    def test_policy_contract_negative_floor_6(self, dataset):
        n = sum(
            1
            for p in dataset["pairs"]
            if p["class"] == "policy_tenant_freshness_reuse_negative"
        )
        assert n >= 6


class TestSizeAndStatistics:
    def test_total_pairs_at_least_100(self, dataset):
        assert dataset["statistics"]["total_pairs"] >= 100
        assert len(dataset["pairs"]) >= 100

    def test_balanced_positives_negatives(self, dataset):
        stats = dataset["statistics"]
        assert stats["total_positives"] == 50
        assert stats["total_negatives"] == 50

    def test_measurable_pair_count_at_least_90(self, dataset):
        NON_MEASURABLE = {"policy_tenant_freshness_reuse_negative", "reference_contract_negative"}
        measurable = [p for p in dataset["pairs"] if p["class"] not in NON_MEASURABLE]
        assert len(measurable) >= 90


class TestBackwardCompat:
    def test_v1_ids_preserved(self, dataset):
        """User-required: existing v1 pair IDs must still be present in v2."""
        v1_ids = {
            "PP-01", "PP-02", "PP-03", "PP-04", "PP-05", "PP-06", "PP-07", "PP-08",
            "NM-01", "NM-02", "NM-03", "NM-04", "NM-05", "NM-06",
            "LO-01", "LO-02", "LO-03", "LO-04", "LO-05", "LO-06",
            "RC-01", "RC-02", "RC-03", "RC-04",
        }
        all_ids = {p["id"] for p in dataset["pairs"]}
        missing = v1_ids - all_ids
        assert not missing, f"v1 pair IDs disappeared in v2: {missing}"

    def test_backward_compatibility_block_declared(self, dataset):
        assert "backward_compatibility" in dataset
        renames = dataset["backward_compatibility"]["v1_class_renames"]
        assert renames["lexical_overlap_negative"] == "lexical_overlap_different_meaning_negative"
        assert renames["reference_contract_negative"] == "policy_tenant_freshness_reuse_negative"


class TestDatasetIntegrity:
    def test_all_ids_unique(self, dataset):
        ids = [p["id"] for p in dataset["pairs"]]
        assert len(ids) == len(set(ids))

    def test_no_empty_texts(self, dataset):
        for p in dataset["pairs"]:
            assert p["text_a"], f"pair {p['id']} has empty text_a"
            assert p["text_b"], f"pair {p['id']} has empty text_b"

    def test_every_pair_has_declared_class(self, dataset):
        declared_classes = set(dataset["classes"].keys())
        for p in dataset["pairs"]:
            assert p["class"] in declared_classes, (
                f"pair {p['id']} has undeclared class {p['class']}"
            )

    def test_distinct_text_a_text_b_for_all_measurable_positives(self, dataset):
        POSITIVE_CLASSES = {
            "paraphrase_positive",
            "abbreviation_definition_positive",
            "short_form_reminder_positive",
        }
        for p in dataset["pairs"]:
            if p["class"] in POSITIVE_CLASSES:
                assert p["text_a"] != p["text_b"], (
                    f"positive pair {p['id']} has identical text_a == text_b"
                )


class TestCalibrationMetadata:
    def test_sweep_candidates_declared(self, dataset):
        assert "threshold_sweep_candidates" in dataset
        assert dataset["threshold_sweep_candidates"] == [0.95, 0.92, 0.90, 0.88, 0.85, 0.80]

    def test_production_threshold_target_unchanged(self, dataset):
        assert dataset["production_threshold_target"] == 0.95

    def test_embedding_model_required_is_bge_m3(self, dataset):
        assert dataset["embedding_model_required"] == "BAAI/bge-m3"
