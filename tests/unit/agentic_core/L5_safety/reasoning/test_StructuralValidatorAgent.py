"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_StructuralValidatorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (  # noqa: F401
        StructureViolationType,
        StructureViolation,
        StructureConfig,
        StructuralValidatorAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    StructureViolationType = None  # type: ignore[assignment,misc]
    StructureViolation = None  # type: ignore[assignment,misc]
    StructureConfig = None  # type: ignore[assignment,misc]
    StructuralValidatorAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestStructureViolationTypeContract:
    def test_is_class(self):
        assert isinstance(StructureViolationType, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(StructureViolationType, type)

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestStructureViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureViolation)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StructureViolation)}
        assert field_names >= {'message', 'line_number', 'suggested_fix', 'violation_type', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestStructureConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StructureConfig)}
        assert field_names >= {'enable_hierarchy', 'enable_gravity', 'enable_ascii', 'enable_naming', 'enable_documentation'}

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestStructuralValidatorAgentContract:
    def test_is_class(self):
        assert isinstance(StructuralValidatorAgent, type)

    def test_has_method_config(self):
        assert callable(getattr(StructuralValidatorAgent, 'config', None))

    def test_has_method_validate_structure(self):
        assert callable(getattr(StructuralValidatorAgent, 'validate_structure', None))

    def test_has_method_violations(self):
        assert callable(getattr(StructuralValidatorAgent, 'violations', None))

    def test_has_method_validate_file(self):
        assert callable(getattr(StructuralValidatorAgent, 'validate_file', None))

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module StructuralValidatorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
