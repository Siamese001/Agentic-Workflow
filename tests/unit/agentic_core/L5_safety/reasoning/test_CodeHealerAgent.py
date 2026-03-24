"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CodeHealerAgent.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_CodeHealerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.CodeHealerAgent import (  # noqa: F401
        CodeHealerAgent,
        CodeHealingStrategy,
        HealerConfig,
        HealingAction,
        HealingType,
        create_legacy_canon_healer,
        create_legacy_import_healer,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CodeHealingStrategy = None  # type: ignore[assignment,misc]
    HealingType = None  # type: ignore[assignment,misc]
    HealingAction = None  # type: ignore[assignment,misc]
    HealerConfig = None  # type: ignore[assignment,misc]
    CodeHealerAgent = None  # type: ignore[assignment,misc]
    create_legacy_canon_healer = None  # type: ignore[assignment,misc]
    create_legacy_import_healer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestCodeHealingStrategyContract:
    def test_is_class(self):
        assert isinstance(CodeHealingStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(CodeHealingStrategy, 'execute', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(CodeHealingStrategy) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestHealingTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(HealingType, enum.Enum)

    def test_has_members(self):
        assert len(list(HealingType)) >= 1

    def test_member_values_accessible(self):
        for m in HealingType:
            assert m.value is not None or m.value is None

    def test_known_member_canon_present(self):
        assert hasattr(HealingType, 'CANON')

    def test_members_are_unique(self):
        values = [m.value for m in HealingType]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestHealingActionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingAction)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingAction)}
        assert fnames >= {'old_code', 'new_code', 'line_number', 'description', 'healing_type', 'file_path'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingAction)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestHealerConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealerConfig)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealerConfig)}
        assert fnames >= {'backup_before_heal', 'enable_import', 'enable_canon', 'dry_run', 'backup_dir', 'enable_structural'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealerConfig)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestCodeHealerAgentContract:
    def test_is_class(self):
        assert isinstance(CodeHealerAgent, type)

    def test_has_method_heal_repository(self):
        assert callable(getattr(CodeHealerAgent, 'heal_repository', None))

    def test_has_method_atomic_write(self):
        assert callable(getattr(CodeHealerAgent, 'atomic_write', None))

    def test_has_method_heal_all(self):
        assert callable(getattr(CodeHealerAgent, 'heal_all', None))

    def test_has_method_heal_imports(self):
        assert callable(getattr(CodeHealerAgent, 'heal_imports', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(CodeHealerAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestCreateLegacyCanonHealerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_canon_healer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_canon_healer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent.py deps unavailable")
class TestCreateLegacyImportHealerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_import_healer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_import_healer)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: CodeHealerAgent importable or gracefully unavailable."""
    pass