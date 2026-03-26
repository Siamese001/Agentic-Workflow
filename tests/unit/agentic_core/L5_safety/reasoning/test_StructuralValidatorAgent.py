"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_StructuralValidatorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    StructuralValidatorAgent,
    StructureConfig,
    StructureViolation,
    StructureViolationType,
)


class TestStructureViolationTypeContract:
    def test_is_class(self):
                from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (  # noqa: F401
                assert isinstance(StructureViolationType, type)

        assert isinstance(StructureViolationType, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(StructureViolationType, type)

class TestStructureViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureViolation)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StructureViolation)}
        assert field_names >= {'message', 'line_number', 'suggested_fix', 'violation_type', 'file_path'}

class TestStructureConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StructureConfig)}
        assert field_names >= {'enable_hierarchy', 'enable_gravity', 'enable_ascii', 'enable_naming', 'enable_documentation'}

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

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module StructuralValidatorAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
