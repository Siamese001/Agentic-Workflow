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


# ---------------------------------------------------------------------------
# G3: _normalize_top_k boundary cases (phase-added to embeddings.py)
# ---------------------------------------------------------------------------


def test_normalize_top_k_zero_clamps_to_one():
    """_normalize_top_k(0) must return 1 — no zero-sized result set."""
    from agentic_core.interfaces.embeddings import _normalize_top_k

    assert _normalize_top_k(0) == 1


def test_normalize_top_k_negative_clamps_to_one():
    """_normalize_top_k(-n) must return 1."""
    from agentic_core.interfaces.embeddings import _normalize_top_k

    assert _normalize_top_k(-10) == 1


def test_normalize_top_k_above_max_clamps_to_max():
    """_normalize_top_k(n > _MAX_TOP_K) must return _MAX_TOP_K."""
    from agentic_core.interfaces.embeddings import _MAX_TOP_K, _normalize_top_k

    assert _normalize_top_k(_MAX_TOP_K + 5) == _MAX_TOP_K


def test_normalize_top_k_valid_value_unchanged():
    """_normalize_top_k(n) where 1 <= n <= _MAX_TOP_K must return n unchanged."""
    from agentic_core.interfaces.embeddings import _normalize_top_k

    assert _normalize_top_k(10) == 10


# ---------------------------------------------------------------------------
# G4: _MissingOptionalDependency fail-fast proxy (safety.py)
# ---------------------------------------------------------------------------


def test_missing_optional_dependency_raises_on_getattr():
    """_MissingOptionalDependency.__getattr__ must raise ModuleNotFoundError."""
    from agentic_core.interfaces.safety import _MissingOptionalDependency

    proxy = _MissingOptionalDependency("FakeClass", "test reason")
    with pytest.raises(ModuleNotFoundError, match="FakeClass is unavailable"):
        _ = proxy.some_attribute


def test_missing_optional_dependency_raises_on_call():
    """_MissingOptionalDependency.__call__ must raise ModuleNotFoundError."""
    from agentic_core.interfaces.safety import _MissingOptionalDependency

    proxy = _MissingOptionalDependency("FakeClass", "test reason")
    with pytest.raises(ModuleNotFoundError, match="FakeClass is unavailable"):
        proxy()


# ---------------------------------------------------------------------------
# G5: _missing_rule_failure fail-fast stub (validators.py)
# ---------------------------------------------------------------------------


def test_missing_rule_failure_raises_on_instantiation():
    """Stub class produced by _missing_rule_failure must raise ModuleNotFoundError on __init__."""
    from agentic_core.interfaces.validators import _missing_rule_failure

    StubClass = _missing_rule_failure("test reason")
    with pytest.raises(ModuleNotFoundError, match="RuleFailure is unavailable"):
        StubClass()


# ---------------------------------------------------------------------------
# G6: query_similarity ImportError / empty-query fallback paths (embeddings.py)
# ---------------------------------------------------------------------------


def test_query_similarity_returns_empty_for_empty_string():
    """query_similarity('') must return [] without touching the cache."""
    from agentic_core.interfaces.embeddings import query_similarity

    assert query_similarity("") == []


def test_query_similarity_returns_empty_for_whitespace():
    """query_similarity with all-whitespace must return [] (stripped → empty)."""
    from agentic_core.interfaces.embeddings import query_similarity

    assert query_similarity("   ") == []


def test_query_similarity_handles_cache_import_error():
    """query_similarity must return [] when SovereignSemanticCache is unavailable."""
    import sys

    from agentic_core.interfaces.embeddings import query_similarity

    cache_key = "agentic_core.L4_state.utils.memory.sovereign_semantic_cache"
    orig = sys.modules.pop(cache_key, None)
    try:
        sys.modules[cache_key] = None  # None entry forces ImportError on next import
        result = query_similarity("test query text")
        assert result == []
    finally:
        if orig is not None:
            sys.modules[cache_key] = orig
        else:
            sys.modules.pop(cache_key, None)
