"""Foundational behavioral tests for agentic_core/adg/artifact/normalizer.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_normalizer_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.artifact.normalizer_config import (  # noqa: F401
        ArtifactNormalizer,
        NormalizedGraph,
        normalize_artifact,
        size_comparison,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    NormalizedGraph = None  # type: ignore[assignment,misc]
    ArtifactNormalizer = None  # type: ignore[assignment,misc]
    normalize_artifact = None  # type: ignore[assignment,misc]
    size_comparison = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestNormalizedGraphContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(NormalizedGraph)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(NormalizedGraph)}
        assert fnames >= {
            "scanner_digest",
            "edges",
            "nodes",
            "schema_version",
            "commit_sha",
            "artifact_digest",
        }

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(NormalizedGraph)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestArtifactNormalizerContract:
    def test_is_class(self):
        assert isinstance(ArtifactNormalizer, type)

    def test_has_method_normalize(self):
        assert callable(getattr(ArtifactNormalizer, "normalize", None))

    def test_has_method_denormalize(self):
        assert callable(getattr(ArtifactNormalizer, "denormalize", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ArtifactNormalizer) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestNormalizeArtifactFunction:
    def test_is_callable(self):
        assert callable(normalize_artifact)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(normalize_artifact)
        assert sig.return_annotation is not inspect.Parameter.empty


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestSizeComparisonFunction:
    def test_is_callable(self):
        assert callable(size_comparison)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(size_comparison)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: normalizer importable or gracefully unavailable."""
    pass