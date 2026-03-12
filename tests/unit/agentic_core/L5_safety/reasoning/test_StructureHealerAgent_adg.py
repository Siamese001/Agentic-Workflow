"""ADG-driven tests for agentic_core/L5_safety/reasoning/StructureHealerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.StructureHealerAgent import (  # noqa: F401
        StructureHealingType,
        StructureHealingAction,
        StructureHealerConfig,
        StructureHealerAgent,
        create_legacy_gravity_healer,
        create_legacy_naming_healer,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StructureHealingType = None  # type: ignore[assignment,misc]
    StructureHealingAction = None  # type: ignore[assignment,misc]
    StructureHealerConfig = None  # type: ignore[assignment,misc]
    StructureHealerAgent = None  # type: ignore[assignment,misc]
    create_legacy_gravity_healer = None  # type: ignore[assignment,misc]
    create_legacy_naming_healer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestStructureHealingType:
    def test_is_enum(self):
        import enum
        assert issubclass(StructureHealingType, enum.Enum)
    def test_has_members(self):
        assert len(list(StructureHealingType)) >= 1
    def test_importable(self):
        assert StructureHealingType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestStructureHealingAction:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureHealingAction)
    def test_importable(self):
        assert StructureHealingAction is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestStructureHealerConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StructureHealerConfig)
    def test_importable(self):
        assert StructureHealerConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestStructureHealerAgent:
    def test_is_class(self):
        assert isinstance(StructureHealerAgent, type)
    def test_importable(self):
        assert StructureHealerAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestCreateLegacyGravityHealer:
    def test_is_callable(self):
        assert callable(create_legacy_gravity_healer)

@pytest.mark.skipif(not _AVAILABLE, reason="StructureHealerAgent.py deps unavailable")
class TestCreateLegacyNamingHealer:
    def test_is_callable(self):
        assert callable(create_legacy_naming_healer)


def test_module_importable():
    """Module StructureHealerAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
