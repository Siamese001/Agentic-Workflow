"""ADG-driven tests for system_learning/ports/__init__.py — fan_in=2.

Contract tests: namespace importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestSystemLearningPortsInit:
    def test_namespace_importable(self):
                import system_learning.ports
                assert system_learning.ports is not None

        assert system_learning.ports is not None
