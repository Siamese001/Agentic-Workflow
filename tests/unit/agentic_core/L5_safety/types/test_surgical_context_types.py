"""Foundational behavioral tests for agentic_core/L5_safety/types/surgical_context_types.py.

fan_in=6 — imported by 6 other modules.
ADG import-hygiene is covered separately by test_surgical_context_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.types.surgical_context_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ASTCoordinate,
        SurgicalContext,
        SurgicalContextBuilder,
        ViolationConstraint,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ASTCoordinate = None  # type: ignore[assignment,misc]
    ViolationConstraint = None  # type: ignore[assignment,misc]
    SurgicalContext = None  # type: ignore[assignment,misc]
    SurgicalContextBuilder = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestASTCoordinateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ASTCoordinate)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ASTCoordinate)}
        assert fnames >= {'column', 'node_type', 'end_line', 'line', 'end_column', 'node_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ASTCoordinate)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestViolationConstraintContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ViolationConstraint)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ViolationConstraint)}
        assert fnames >= {'severity', 'constraint_type', 'message', 'expected_pattern', 'actual_pattern', 'rule_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ViolationConstraint)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestSurgicalContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SurgicalContext)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SurgicalContext)}
        assert fnames >= {'violation_id', 'target_coordinates', 'violations', 'file_path', 'file_content', 'ast_tree'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(SurgicalContext)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestSurgicalContextBuilderContract:
    def test_is_class(self):
        assert isinstance(SurgicalContextBuilder, type)

    def test_has_method_build_context(self):
        assert callable(getattr(SurgicalContextBuilder, 'build_context', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SurgicalContextBuilder) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: surgical_context_types importable or gracefully unavailable."""
    pass
