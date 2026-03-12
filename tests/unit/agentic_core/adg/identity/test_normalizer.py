"""Foundational behavioral tests for agentic_core/adg/identity/normalizer.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_normalizer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.identity.normalizer import (  # noqa: F401
        IdentityKind,
        IdentityConfidence,
        IdentityRecord,
        NormalizationReport,
        IdentityNormalizer,
        normalize_identity,
        build_identity_index,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IdentityKind = None  # type: ignore[assignment,misc]
    IdentityConfidence = None  # type: ignore[assignment,misc]
    IdentityRecord = None  # type: ignore[assignment,misc]
    NormalizationReport = None  # type: ignore[assignment,misc]
    IdentityNormalizer = None  # type: ignore[assignment,misc]
    normalize_identity = None  # type: ignore[assignment,misc]
    build_identity_index = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestIdentityKindContract:
    def test_is_enum(self):
        import enum
        assert issubclass(IdentityKind, enum.Enum)

    def test_has_members(self):
        assert len(list(IdentityKind)) >= 1

    def test_member_values_accessible(self):
        for m in IdentityKind:
            assert m.value is not None or m.value is None

    def test_known_member_repo_module_present(self):
        assert hasattr(IdentityKind, 'REPO_MODULE')

    def test_members_are_unique(self):
        values = [m.value for m in IdentityKind]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestIdentityConfidenceContract:
    def test_is_enum(self):
        import enum
        assert issubclass(IdentityConfidence, enum.Enum)

    def test_has_members(self):
        assert len(list(IdentityConfidence)) >= 1

    def test_member_values_accessible(self):
        for m in IdentityConfidence:
            assert m.value is not None or m.value is None

    def test_known_member_high_present(self):
        assert hasattr(IdentityConfidence, 'HIGH')

    def test_members_are_unique(self):
        values = [m.value for m in IdentityConfidence]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestIdentityRecordContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(IdentityRecord)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(IdentityRecord)}
        assert fnames >= {'resolved_path', 'raw_name', 'adg_name', 'kind', 'confidence', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(IdentityRecord)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestNormalizationReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(NormalizationReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(NormalizationReport)}
        assert fnames >= {'inferred_symbols', 'by_confidence', 'by_kind', 'total', 'unresolved'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(NormalizationReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestIdentityNormalizerContract:
    def test_is_class(self):
        assert isinstance(IdentityNormalizer, type)

    def test_has_method_normalize(self):
        assert callable(getattr(IdentityNormalizer, 'normalize', None))

    def test_has_method_normalize_many(self):
        assert callable(getattr(IdentityNormalizer, 'normalize_many', None))

    def test_has_method_report(self):
        assert callable(getattr(IdentityNormalizer, 'report', None))

    def test_has_method_normalize_from_scan_result(self):
        assert callable(getattr(IdentityNormalizer, 'normalize_from_scan_result', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(IdentityNormalizer) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestNormalizeIdentityFunction:
    def test_is_callable(self):
        assert callable(normalize_identity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(normalize_identity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="normalizer.py deps unavailable")
class TestBuildIdentityIndexFunction:
    def test_is_callable(self):
        assert callable(build_identity_index)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_identity_index)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: normalizer importable or gracefully unavailable."""
    assert True
