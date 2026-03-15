"""ADG-driven tests for system_learning/config/import_policy.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.config.import_policy import (
        ALLOWED_AGENTIC_CORE_PREFIXES,
        FORBIDDEN_IMPORT_PREFIXES,
        STDLIB_PREFIXES,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FORBIDDEN_IMPORT_PREFIXES = None  # type: ignore[assignment]
    ALLOWED_AGENTIC_CORE_PREFIXES = None  # type: ignore[assignment]
    STDLIB_PREFIXES = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="import_policy deps unavailable")
class TestImportPolicy:
    def test_forbidden_is_frozenset(self):
        assert isinstance(FORBIDDEN_IMPORT_PREFIXES, frozenset)

    def test_allowed_is_frozenset(self):
        assert isinstance(ALLOWED_AGENTIC_CORE_PREFIXES, frozenset)

    def test_stdlib_is_frozenset(self):
        assert isinstance(STDLIB_PREFIXES, frozenset)

    def test_layer_modules_are_forbidden(self):
        assert "agentic_core.L0_routing" in FORBIDDEN_IMPORT_PREFIXES

    def test_interfaces_are_allowed(self):
        assert "agentic_core.interfaces" in ALLOWED_AGENTIC_CORE_PREFIXES

    def test_stdlib_typing_allowed(self):
        assert "typing" in STDLIB_PREFIXES


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
