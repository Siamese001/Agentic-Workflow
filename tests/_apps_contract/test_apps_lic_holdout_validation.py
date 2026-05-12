#!/usr/bin/env python3
"""Unit tests for apps_lic holdout corpus validation scripts.

Tests:
- Corpus validation success and failure cases
- Human label validation including invalid scores
- Adjudication flag when labelers differ by >= 2
- Calibration report generation with unavailable judge imports
"""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import pytest

# Import validation scripts
from apps_lic.evals.scripts.validate_holdout_corpus import validate_corpus
from apps_lic.evals.scripts.validate_human_labels import validate_labels, parse_boolean, parse_int_range
from apps_lic.evals.scripts.adjudicate_human_labels import adjudicate, load_labels, parse_boolean as adj_parse_boolean
from apps_lic.evals.scripts.score_judges_against_holdout import try_import_judges, compute_spearman, compute_mae


class TestValidateHoldoutCorpus:
    """Tests for validate_holdout_corpus.py"""

    def test_corpus_validation_success(self, tmp_path: Path) -> None:
        """Valid corpus passes validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        
        # Generate 52 valid items to meet minimum of 50
        with corpus_file.open("w", encoding="utf-8") as f:
            for i in range(52):
                item = {
                    "holdout_id": f"lic_holdout_{i:04d}",
                    "scenario_id": f"test_{i}",
                    "channel": "email" if i % 2 == 0 else "linkedin_inmail",
                    "recipient_class": "recruiter" if i % 3 == 0 else "hiring_manager",
                    "outreach_mode": "cold" if i % 2 == 0 else "warm",
                    "evidence_posture": "fully_grounded" if i % 2 == 0 else "partially_grounded",
                    "source_items": [f"item{i}"],
                    "composed_message": f"This is a valid test message with sufficient length for item {i}.",
                    "expected_guardrail_flags": [] if i % 5 != 0 else ["spammy_or_hype_language_flag"],
                    "notes": f"Test item {i}",
                    "frozen": True,
                    "split": "holdout",
                    "created_by": "synthetic_seed",
                    "schema_version": "outreach_holdout_corpus.v1",
                }
                f.write(json.dumps(item) + "\n")

        report = validate_corpus(corpus_file)

        assert report["valid"] is True
        assert report["total_rows"] == 52
        assert report["unique_holdout_ids"] == 52
        assert len(report["errors"]) == 0

    def test_corpus_validation_fails_duplicate_holdout_id(self, tmp_path: Path) -> None:
        """Corpus with duplicate holdout_id fails validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        
        # Generate 52 items with one duplicate
        with corpus_file.open("w", encoding="utf-8") as f:
            for i in range(52):
                holdout_id = f"lic_holdout_{i:04d}" if i < 51 else "lic_holdout_0001"  # Duplicate on last item
                item = {
                    "holdout_id": holdout_id,
                    "scenario_id": f"test_{i}",
                    "channel": "email",
                    "recipient_class": "recruiter",
                    "outreach_mode": "cold",
                    "evidence_posture": "fully_grounded",
                    "source_items": [f"item{i}"],
                    "composed_message": f"Test message with sufficient length for item {i} here.",
                    "expected_guardrail_flags": [],
                    "notes": f"Test item {i}",
                    "frozen": True,
                    "split": "holdout",
                    "created_by": "synthetic_seed",
                    "schema_version": "outreach_holdout_corpus.v1",
                }
                f.write(json.dumps(item) + "\n")

        report = validate_corpus(corpus_file)

        assert report["valid"] is False
        assert any("Duplicate holdout_id" in e for e in report["errors"])

    def test_corpus_validation_fails_missing_field(self, tmp_path: Path) -> None:
        """Corpus with missing required field fails validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        corpus_data = [
            {
                "holdout_id": "lic_holdout_0001",
                # Missing many required fields
                "composed_message": "Message without other fields.",
                "expected_guardrail_flags": [],
                "frozen": True,
                "split": "holdout",
                "created_by": "synthetic_seed",
                "schema_version": "outreach_holdout_corpus.v1",
            },
        ]
        with corpus_file.open("w", encoding="utf-8") as f:
            for item in corpus_data:
                f.write(json.dumps(item) + "\n")

        report = validate_corpus(corpus_file)

        assert report["valid"] is False
        assert any("Missing required field" in e for e in report["errors"])

    def test_corpus_validation_fails_invalid_guardrail_flag(self, tmp_path: Path) -> None:
        """Corpus with invalid guardrail flag fails validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        
        # Generate 52 items with invalid flag on first item
        with corpus_file.open("w", encoding="utf-8") as f:
            for i in range(52):
                item = {
                    "holdout_id": f"lic_holdout_{i:04d}",
                    "scenario_id": f"test_{i}",
                    "channel": "email",
                    "recipient_class": "recruiter",
                    "outreach_mode": "cold",
                    "evidence_posture": "fully_grounded",
                    "source_items": [f"item{i}"],
                    "composed_message": f"Test message with sufficient length for item {i} here.",
                    "expected_guardrail_flags": ["invalid_flag_name"] if i == 0 else [],  # Invalid on first
                    "notes": f"Test item {i}",
                    "frozen": True,
                    "split": "holdout",
                    "created_by": "synthetic_seed",
                    "schema_version": "outreach_holdout_corpus.v1",
                }
                f.write(json.dumps(item) + "\n")

        report = validate_corpus(corpus_file)

        assert report["valid"] is False
        assert any("Invalid guardrail flags" in e for e in report["errors"])


class TestValidateHumanLabels:
    """Tests for validate_human_labels.py"""

    def test_label_validation_success(self, tmp_path: Path) -> None:
        """Valid labels pass validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        corpus_data = {
            "holdout_id": "lic_holdout_0001",
            "scenario_id": "test",
            "channel": "email",
            "recipient_class": "recruiter",
            "outreach_mode": "cold",
            "evidence_posture": "fully_grounded",
            "source_items": ["item1"],
            "composed_message": "Test message content here.",
            "expected_guardrail_flags": [],
            "notes": "Test",
            "frozen": True,
            "split": "holdout",
            "created_by": "synthetic_seed",
            "schema_version": "outreach_holdout_corpus.v1",
        }
        with corpus_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps(corpus_data) + "\n")

        labels_file = tmp_path / "labels.csv"
        with labels_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "holdout_id", "labeler_id_hash", "label_batch_id", "labeled_at",
                "response_likelihood_1_5", "brand_voice_1_5", "personalization_quality_1_5",
                "ask_clarity_low_friction_1_5", "fake_personalization_flag",
                "fabricated_relationship_flag", "unsupported_company_fact_flag",
                "unsupported_recipient_fact_flag", "confidential_leakage_flag",
                "sensitive_targeting_flag", "spammy_or_hype_language_flag",
                "channel_length_violation_flag", "labeler_confidence_1_3", "comments"
            ])
            writer.writerow([
                "lic_holdout_0001",
                "a" * 64,  # Valid hash length
                "batch_001",
                "2026-05-11T10:00:00Z",
                "4", "4", "3", "4",  # Valid 1-5 scores
                "false", "false", "false", "false", "false", "false", "false", "false",  # Valid booleans
                "2",  # Valid confidence
                "Good message overall"
            ])

        report = validate_labels(labels_file, corpus_file)

        assert report["valid"] is True
        assert report["total_labels"] == 1

    def test_label_validation_fails_invalid_score(self, tmp_path: Path) -> None:
        """Labels with invalid score values fail validation."""
        corpus_file = tmp_path / "corpus.jsonl"
        corpus_data = {
            "holdout_id": "lic_holdout_0001",
            "scenario_id": "test",
            "channel": "email",
            "recipient_class": "recruiter",
            "outreach_mode": "cold",
            "evidence_posture": "fully_grounded",
            "source_items": ["item1"],
            "composed_message": "Test message.",
            "expected_guardrail_flags": [],
            "notes": "Test",
            "frozen": True,
            "split": "holdout",
            "created_by": "synthetic_seed",
            "schema_version": "outreach_holdout_corpus.v1",
        }
        with corpus_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps(corpus_data) + "\n")

        labels_file = tmp_path / "labels.csv"
        with labels_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "holdout_id", "labeler_id_hash", "label_batch_id", "labeled_at",
                "response_likelihood_1_5", "brand_voice_1_5", "personalization_quality_1_5",
                "ask_clarity_low_friction_1_5", "fake_personalization_flag",
                "fabricated_relationship_flag", "unsupported_company_fact_flag",
                "unsupported_recipient_fact_flag", "confidential_leakage_flag",
                "sensitive_targeting_flag", "spammy_or_hype_language_flag",
                "channel_length_violation_flag", "labeler_confidence_1_3", "comments"
            ])
            writer.writerow([
                "lic_holdout_0001",
                "a" * 64,
                "batch_001",
                "2026-05-11T10:00:00Z",
                "7",  # Invalid: > 5
                "4",
                "3",
                "4",
                "false", "false", "false", "false", "false", "false", "false", "false",
                "2",
                ""
            ])

        report = validate_labels(labels_file, corpus_file)

        assert report["valid"] is False
        assert any("out of range" in e for e in report["errors"])

    def test_parse_boolean(self) -> None:
        """Boolean parsing works correctly."""
        # parse_boolean returns (success, value) tuple
        assert parse_boolean("true") == (True, True)
        assert parse_boolean("True") == (True, True)
        assert parse_boolean("1") == (True, True)
        assert parse_boolean("yes") == (True, True)
        assert parse_boolean("false") == (True, False)
        assert parse_boolean("False") == (True, False)
        assert parse_boolean("0") == (True, False)
        assert parse_boolean("no") == (True, False)
        # Invalid values return (False, False)
        assert parse_boolean("") == (False, False)
        assert parse_boolean("maybe") == (False, False)

    def test_parse_int_range(self) -> None:
        """Integer range parsing works correctly."""
        assert parse_int_range("3", 1, 5) == (True, 3)
        assert parse_int_range("1", 1, 5) == (True, 1)
        assert parse_int_range("5", 1, 5) == (True, 5)
        assert parse_int_range("0", 1, 5) == (False, 0)  # Out of range
        assert parse_int_range("6", 1, 5) == (False, 6)  # Out of range
        assert parse_int_range("abc", 1, 5) == (False, None)  # Not an integer


class TestAdjudicateHumanLabels:
    """Tests for adjudicate_human_labels.py"""

    def test_adjudication_computes_median(self, tmp_path: Path) -> None:
        """Adjudication computes median scores correctly."""
        labels_file = tmp_path / "labels.csv"
        with labels_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "holdout_id", "labeler_id_hash", "label_batch_id", "labeled_at",
                "response_likelihood_1_5", "brand_voice_1_5", "personalization_quality_1_5",
                "ask_clarity_low_friction_1_5", "fake_personalization_flag",
                "fabricated_relationship_flag", "unsupported_company_fact_flag",
                "unsupported_recipient_fact_flag", "confidential_leakage_flag",
                "sensitive_targeting_flag", "spammy_or_hype_language_flag",
                "channel_length_violation_flag", "labeler_confidence_1_3", "comments"
            ])
            # Two labels for same holdout
            writer.writerow([
                "lic_holdout_0001", "a" * 64, "batch_001", "2026-05-11T10:00:00Z",
                "3", "4", "3", "4",
                "false", "false", "false", "false", "false", "false", "false", "false",
                "2", ""
            ])
            writer.writerow([
                "lic_holdout_0001", "b" * 64, "batch_001", "2026-05-11T11:00:00Z",
                "5", "4", "5", "4",
                "false", "false", "false", "false", "false", "false", "false", "false",
                "3", ""
            ])

        labels_by_holdout = load_labels(labels_file)
        results = adjudicate(labels_by_holdout)

        assert len(results) == 1
        result = results[0]
        assert result["holdout_id"] == "lic_holdout_0001"
        # Median of [3, 5] using median_high = 5 (rounds up for even counts)
        assert result["median_response_likelihood_1_5"] == 5
        # Median of [4, 4] = 4
        assert result["median_brand_voice_1_5"] == 4

    def test_adjudication_flags_disagreement_ge_2(self, tmp_path: Path) -> None:
        """Adjudication flags when labelers differ by >= 2 on any dimension."""
        labels_file = tmp_path / "labels.csv"
        with labels_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "holdout_id", "labeler_id_hash", "label_batch_id", "labeled_at",
                "response_likelihood_1_5", "brand_voice_1_5", "personalization_quality_1_5",
                "ask_clarity_low_friction_1_5", "fake_personalization_flag",
                "fabricated_relationship_flag", "unsupported_company_fact_flag",
                "unsupported_recipient_fact_flag", "confidential_leakage_flag",
                "sensitive_targeting_flag", "spammy_or_hype_language_flag",
                "channel_length_violation_flag", "labeler_confidence_1_3", "comments"
            ])
            # Two labels with disagreement of 2 on response_likelihood
            writer.writerow([
                "lic_holdout_0001", "a" * 64, "batch_001", "2026-05-11T10:00:00Z",
                "2", "4", "3", "4",  # 2
                "false", "false", "false", "false", "false", "false", "false", "false",
                "2", "Low response likelihood"
            ])
            writer.writerow([
                "lic_holdout_0001", "b" * 64, "batch_001", "2026-05-11T11:00:00Z",
                "4", "4", "5", "4",  # 4 (diff = 2)
                "false", "false", "false", "false", "false", "false", "false", "false",
                "3", "High response likelihood"
            ])

        labels_by_holdout = load_labels(labels_file)
        results = adjudicate(labels_by_holdout)

        assert len(results) == 1
        result = results[0]
        assert result["adjudication_required"] is True
        assert result["disagreement_max"] == 2
        assert "disagreement >= 2" in result["reason_for_review"]


class TestScoreJudgesAgainstHoldout:
    """Tests for score_judges_against_holdout.py"""

    def test_try_import_judges_returns_dict(self) -> None:
        """Judge import function returns dict with availability info."""
        judges = try_import_judges()

        # Should return dict of judge names
        assert isinstance(judges, dict)

        # Each judge should have 'available' key
        for name, info in judges.items():
            assert "available" in info

    def test_compute_spearman_with_valid_data(self) -> None:
        """Spearman correlation computes correctly with valid data."""
        x = [1, 2, 3, 4, 5]
        y = [1, 2, 3, 4, 5]  # Perfect positive correlation

        corr = compute_spearman(x, y)

        # Should be close to 1.0 for perfect correlation
        assert corr is not None
        assert corr > 0.99

    def test_compute_spearman_with_inverse_data(self) -> None:
        """Spearman correlation with inverse relationship."""
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]  # Perfect negative correlation

        corr = compute_spearman(x, y)

        # Should be close to -1.0
        assert corr is not None
        assert corr < -0.99

    def test_compute_spearman_insufficient_data(self) -> None:
        """Spearman returns None with insufficient data."""
        x = [1, 2]
        y = [1, 2]

        corr = compute_spearman(x, y)

        # Need at least 3 points
        assert corr is None

    def test_compute_mae(self) -> None:
        """Mean absolute error computes correctly."""
        predicted = [0.5, 0.6, 0.7]
        actual = [0.5, 0.5, 0.5]

        mae = compute_mae(predicted, actual)

        assert mae is not None
        assert abs(mae - 0.1) < 0.001  # (0 + 0.1 + 0.2) / 3 = 0.1


class TestRealCorpus:
    """Integration tests with the real corpus file."""

    def test_real_corpus_validates(self) -> None:
        """The real corpus file passes validation."""
        corpus_path = Path("apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl")

        if not corpus_path.exists():
            pytest.skip("Corpus file not found")

        report = validate_corpus(corpus_path)

        assert report["valid"] is True, f"Corpus validation failed: {report['errors']}"
        assert report["total_rows"] == 80
        assert report["unique_holdout_ids"] == 80

    def test_real_corpus_size_in_range(self) -> None:
        """Real corpus size is within 50-100 range."""
        corpus_path = Path("apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl")

        if not corpus_path.exists():
            pytest.skip("Corpus file not found")

        report = validate_corpus(corpus_path)

        assert 50 <= report["total_rows"] <= 100

    def test_real_corpus_all_frozen(self) -> None:
        """All items in real corpus have frozen=true."""
        corpus_path = Path("apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl")

        if not corpus_path.exists():
            pytest.skip("Corpus file not found")

        report = validate_corpus(corpus_path)

        frozen_errors = [e for e in report["errors"] if "frozen" in e]
        assert len(frozen_errors) == 0, "Some items not frozen"
