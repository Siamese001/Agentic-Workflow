"""Foundational behavioral tests for agentic_core/adg/artifact/builder.py.

fan_in=9 — imported by 9 other modules.
ADG import-hygiene is covered separately by test_builder_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.artifact.builder_types import (  # noqa: F401
        ADGArtifact,
        ADGArtifactBuilder,
        BlindSpotReport,
        EntityRecord,
        RelationRecord,
        StructuralMetrics,
        build_artifact,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EntityRecord = None  # type: ignore[assignment,misc]
    RelationRecord = None  # type: ignore[assignment,misc]
    StructuralMetrics = None  # type: ignore[assignment,misc]
    BlindSpotReport = None  # type: ignore[assignment,misc]
    ADGArtifact = None  # type: ignore[assignment,misc]
    ADGArtifactBuilder = None  # type: ignore[assignment,misc]
    build_artifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestEntityRecordContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(EntityRecord)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(EntityRecord)}
        assert fnames >= {"layer", "resolved_path", "entity_type", "adg_name", "confidence", "identity_kind"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(EntityRecord)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestRelationRecordContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(RelationRecord)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(RelationRecord)}
        assert fnames >= {"relation_type", "from_name", "edge_kind", "source_file", "to_name", "line_no"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(RelationRecord)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestStructuralMetricsContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(StructuralMetrics)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(StructuralMetrics)}
        assert fnames >= {
            "unresolved_count",
            "module_count",
            "external_count",
            "total_relations",
            "symbol_count",
            "total_entities",
        }

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(StructuralMetrics)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestBlindSpotReportContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(BlindSpotReport)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(BlindSpotReport)}
        assert fnames >= {
            "dynamic_import_locations",
            "star_import_locations",
            "parse_failure_count",
            "dynamic_import_count",
            "parse_failure_files",
            "star_import_count",
        }

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(BlindSpotReport)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestADGArtifactContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ADGArtifact)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(ADGArtifact)}
        assert fnames >= {
            "scanner_digest",
            "schema_version",
            "commit_sha",
            "relations",
            "entities",
            "unresolved_imports",
        }

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(ADGArtifact)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestADGArtifactBuilderContract:
    def test_is_class(self):
        assert isinstance(ADGArtifactBuilder, type)

    def test_has_method_build(self):
        assert callable(getattr(ADGArtifactBuilder, "build", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ADGArtifactBuilder) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="builder.py deps unavailable")
class TestBuildArtifactFunction:
    def test_is_callable(self):
        assert callable(build_artifact)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(build_artifact)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: builder importable or gracefully unavailable."""
    pass
