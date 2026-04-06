"""Tests for protocol validation and invariants."""
from __future__ import annotations

import pytest

from agentic_core.interfaces.IMemoryStoreProtocol import StoredArtifact, StoredArtifactRef
from agentic_core.interfaces.IValidatorProtocol import ValidationReport


def test_stored_artifact_ref_validates_non_empty_kind():
    """StoredArtifactRef raises ValueError for empty kind."""
    with pytest.raises(ValueError, match="kind cannot be empty"):
        StoredArtifactRef(kind="", logical_id="test", version=1, path="/test", size_bytes=100)


def test_stored_artifact_ref_validates_non_empty_logical_id():
    """StoredArtifactRef raises ValueError for empty logical_id."""
    with pytest.raises(ValueError, match="logical_id cannot be empty"):
        StoredArtifactRef(kind="test", logical_id="", version=1, path="/test", size_bytes=100)


def test_stored_artifact_ref_validates_version_ge_zero():
    """StoredArtifactRef raises ValueError for negative version."""
    with pytest.raises(ValueError, match="version must be >= 0"):
        StoredArtifactRef(kind="test", logical_id="test", version=-1, path="/test", size_bytes=100)


def test_stored_artifact_ref_validates_size_bytes_ge_zero():
    """StoredArtifactRef raises ValueError for negative size_bytes."""
    with pytest.raises(ValueError, match="size_bytes must be >= 0"):
        StoredArtifactRef(kind="test", logical_id="test", version=1, path="/test", size_bytes=-1)


def test_stored_artifact_ref_accepts_valid_values():
    """StoredArtifactRef accepts valid values."""
    ref = StoredArtifactRef(kind="test", logical_id="test", version=1, path="/test", size_bytes=100)
    assert ref.kind == "test"
    assert ref.logical_id == "test"
    assert ref.version == 1
    assert ref.path == "/test"
    assert ref.size_bytes == 100


def test_stored_artifact_validates_non_empty_kind():
    """StoredArtifact raises ValueError for empty kind."""
    with pytest.raises(ValueError, match="kind cannot be empty"):
        StoredArtifact(
            kind="",
            logical_id="test",
            payload={},
            content_type="application/json",
            created_utc="2024-01-01",
            hashes={},
            metadata={},
        )


def test_stored_artifact_validates_non_empty_logical_id():
    """StoredArtifact raises ValueError for empty logical_id."""
    with pytest.raises(ValueError, match="logical_id cannot be empty"):
        StoredArtifact(
            kind="test",
            logical_id="",
            payload={},
            content_type="application/json",
            created_utc="2024-01-01",
            hashes={},
            metadata={},
        )


def test_stored_artifact_validates_non_empty_content_type():
    """StoredArtifact raises ValueError for empty content_type."""
    with pytest.raises(ValueError, match="content_type cannot be empty"):
        StoredArtifact(
            kind="test",
            logical_id="test",
            payload={},
            content_type="",
            created_utc="2024-01-01",
            hashes={},
            metadata={},
        )


def test_stored_artifact_validates_non_empty_created_utc():
    """StoredArtifact raises ValueError for empty created_utc."""
    with pytest.raises(ValueError, match="created_utc cannot be empty"):
        StoredArtifact(
            kind="test",
            logical_id="test",
            payload={},
            content_type="application/json",
            created_utc="",
            hashes={},
            metadata={},
        )


def test_stored_artifact_accepts_valid_values():
    """StoredArtifact accepts valid values."""
    artifact = StoredArtifact(
        kind="test",
        logical_id="test",
        payload={"key": "value"},
        content_type="application/json",
        created_utc="2024-01-01",
        hashes={"sha256": "abc123"},
        metadata={"meta": "data"},
    )
    assert artifact.kind == "test"
    assert artifact.logical_id == "test"
    assert artifact.content_type == "application/json"
    assert artifact.created_utc == "2024-01-01"


def test_validation_report_to_markdown_compliant():
    """ValidationReport.to_markdown() generates correct output for compliant report."""
    report = ValidationReport(
        total_violations=0,
        compliance_score=100.0,
        violations=[],
        scan_duration=1.5,
        is_compliant=True,
    )
    markdown = report.to_markdown()
    assert "# Validation Report" in markdown
    assert "100.0%" in markdown
    assert "COMPLIANT" in markdown
    assert "0 violations" not in markdown


def test_validation_report_to_markdown_non_compliant():
    """ValidationReport.to_markdown() generates correct output for non-compliant report."""
    report = ValidationReport(
        total_violations=5,
        compliance_score=75.0,
        violations=[{"type": "error", "message": "test"}],
        scan_duration=2.5,
        is_compliant=False,
    )
    markdown = report.to_markdown()
    assert "# Validation Report" in markdown
    assert "75.0%" in markdown
    assert "NON-COMPLIANT" in markdown
    assert "1 violations" in markdown  # Shows len(violations), not total_violations
