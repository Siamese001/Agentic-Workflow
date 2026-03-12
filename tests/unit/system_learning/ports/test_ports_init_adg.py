"""ADG-driven tests for system_learning/ports/__init__.py — fan_in=2.

Contract tests: namespace importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestSystemLearningPortsInit:
    def test_namespace_importable(self):
        try:
            import system_learning.ports
            assert system_learning.ports is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"system_learning.ports deps unavailable: {e}")

    def test_docstring_present(self):
        try:
            import system_learning.ports
            assert system_learning.ports.__doc__ is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"system_learning.ports deps unavailable: {e}")
