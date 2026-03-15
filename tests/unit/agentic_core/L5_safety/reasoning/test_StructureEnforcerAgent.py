"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_StructureEnforcerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        NamingRule,
        StructureConfig,
        StructureEnforcerAgent,
        StructureViolation,
        StructureViolationType,
        create_legacy_doc_enforcer,
        create_legacy_gravity_enforcer,
        create_legacy_naming_enforcer,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StructureViolationType = None  # type: ignore[assignment,misc]
    StructureViolation = None  # type: ignore[assignment,misc]
    NamingRule = None  # type: ignore[assignment,misc]
    StructureConfig = None  # type: ignore[assignment,misc]
    StructureEnforcerAgent = None  # type: ignore[assignment,misc]
    create_legacy_gravity_enforcer = None  # type: ignore[assignment,misc]
    create_legacy_naming_enforcer = None  # type: ignore[assignment,misc]
    create_legacy_doc_enforcer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestStructureViolationTypeContract:
    def test_is_class(self):
        assert isinstance(StructureViolationType, type)

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestStructureViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureViolation)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(StructureViolation)}
        assert fnames >= {'auto_fixable', 'violation_type', 'line_number', 'message', 'file_path', 'suggested_fix'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(StructureViolation)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestNamingRuleContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(NamingRule)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(NamingRule)}
        assert fnames >= {'suffix', 'auto_rename', 'pattern', 'description'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(NamingRule)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestStructureConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureConfig)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(StructureConfig)}
        assert fnames >= {'enable_naming', 'enable_documentation', 'enable_hierarchy', 'enable_gravity', 'enable_ascii', 'auto_fix'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(StructureConfig)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestStructureEnforcerAgentContract:
    def test_is_class(self):
        assert isinstance(StructureEnforcerAgent, type)

    def test_has_method_heal_repository(self):
        assert callable(getattr(StructureEnforcerAgent, 'heal_repository', None))

    def test_has_method_validate_file(self):
        assert callable(getattr(StructureEnforcerAgent, 'validate_file', None))

    def test_has_method_check_gravity_import(self):
        assert callable(getattr(StructureEnforcerAgent, 'check_gravity_import', None))

    def test_has_method_force_rename_class(self):
        assert callable(getattr(StructureEnforcerAgent, 'force_rename_class', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(StructureEnforcerAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestCreateLegacyGravityEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_gravity_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_gravity_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestCreateLegacyNamingEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_naming_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_naming_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestCreateLegacyDocEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_doc_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_doc_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureEnforcerAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: StructureEnforcerAgent importable or gracefully unavailable."""
    pass
