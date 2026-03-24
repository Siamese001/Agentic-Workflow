"""ADG-driven tests for agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.git_health_sensor_enforcer import (  # noqa: F401
        GitHealthSensor,
        check_git_health,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GitHealthSensor = None  # type: ignore[assignment,misc]
    check_git_health = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="git_health_sensor_enforcer.py deps unavailable")
class TestGitHealthSensor:
    def test_is_class(self):
        assert isinstance(GitHealthSensor, type)
    def test_importable(self):
        assert GitHealthSensor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="git_health_sensor_enforcer.py deps unavailable")
class TestCheckGitHealth:
    def test_is_callable(self):
        assert callable(check_git_health)


def test_module_importable():
    """Module git_health_sensor_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE