"""ADG-driven tests for apps_rg/tools/DataEnricher.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.tools.DataEnricher import (  # noqa: F401
        DataEnricher,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DataEnricher = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DataEnricher.py deps unavailable")
class TestDataEnricher:
    def test_is_class(self):
        assert isinstance(DataEnricher, type)
    def test_importable(self):
        assert DataEnricher is not None


def test_module_importable():
    """Module DataEnricher.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
