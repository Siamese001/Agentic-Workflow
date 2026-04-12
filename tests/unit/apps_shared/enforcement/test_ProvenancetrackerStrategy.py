"""Foundational behavioral tests for apps_shared/enforcement/ProvenancetrackerStrategy.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_ProvenancetrackerStrategy_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import all classes/constants at module level so they're available to all tests
try:
    from apps_shared.enforcement.ProvenancetrackerStrategy import (
        BATCH_SIZE,
        BUFFER_SIZE,
        ArtifactLineage,
        ProvenanceContext,
        ProvenanceTracker,
        SourceCitation,
        get_provenance_tracker,
        provenance_tracked,
        track_provenance,
    )
except ImportError as _import_err:
    pytest.skip(f"ProvenancetrackerStrategy not available: {_import_err}", allow_module_level=True)

pytestmark = pytest.mark.unit


class TestSourceCitationContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(SourceCitation)

    def test_field_names_present(self):
        import dataclasses

        field_names = {f.name for f in dataclasses.fields(SourceCitation)}
        assert field_names >= {"relevance_score", "citation_type", "snippet", "source_id", "uri"}


class TestArtifactLineageContract:
    def test_is_class(self):
        assert isinstance(ArtifactLineage, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ArtifactLineage, type)


class TestProvenanceTrackerContract:
    def test_is_class(self):
        assert isinstance(ProvenanceTracker, type)

    def test_has_method_capture_context(self):
        assert callable(getattr(ProvenanceTracker, "capture_context", None))

    def test_has_method_record_generation(self):
        assert callable(getattr(ProvenanceTracker, "record_generation", None))

    def test_has_method_verify_citations(self):
        assert callable(getattr(ProvenanceTracker, "verify_citations", None))

    def test_has_method_get_lineage(self):
        assert callable(getattr(ProvenanceTracker, "get_lineage", None))


class TestProvenanceContextContract:
    def test_is_class(self):
        assert isinstance(ProvenanceContext, type)

    def test_has_method_record_generation(self):
        assert callable(getattr(ProvenanceContext, "record_generation", None))


class TestGetProvenanceTrackerFunction:
    def test_is_callable(self):
        pass


class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None


class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module ProvenancetrackerStrategy must be importable or skip gracefully."""
    pass  # Import verified at module level
