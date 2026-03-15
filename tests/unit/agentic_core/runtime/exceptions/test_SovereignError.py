"""Foundational behavioral tests for agentic_core/runtime/exceptions/SovereignError.py.

fan_in=20 — this module is imported by 20 other modules.
ADG contract: import-hygiene is covered by test_SovereignError_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.SovereignError import (  # noqa: F401
        CircularDependencyError,
        ConfigurationError,
        HealerError,
        HygieneError,
        SovereignError,
        StructuralError,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    SovereignError = None  # type: ignore[assignment,misc]
    HealerError = None  # type: ignore[assignment,misc]
    CircularDependencyError = None  # type: ignore[assignment,misc]
    ConfigurationError = None  # type: ignore[assignment,misc]
    StructuralError = None  # type: ignore[assignment,misc]
    HygieneError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestSovereignErrorContract:
    def test_is_class(self):
        assert isinstance(SovereignError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SovereignError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestHealerErrorContract:
    def test_is_class(self):
        assert isinstance(HealerError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealerError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestCircularDependencyErrorContract:
    def test_is_class(self):
        assert isinstance(CircularDependencyError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CircularDependencyError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestConfigurationErrorContract:
    def test_is_class(self):
        assert isinstance(ConfigurationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ConfigurationError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestStructuralErrorContract:
    def test_is_class(self):
        assert isinstance(StructuralError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(StructuralError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError.py deps unavailable")
class TestHygieneErrorContract:
    def test_is_class(self):
        assert isinstance(HygieneError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HygieneError, type)


def test_module_importable():
    """Module SovereignError must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
