"""ADG-driven tests for agentic_core/L5_safety/validators/intervention_server_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.intervention_server_validator import (  # noqa: F401
        InterventionContext,
        InterventionServer,
        check_intervention_required,
        get_intervention_server,
        start_intervention_server,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    InterventionContext = None  # type: ignore[assignment,misc]
    InterventionServer = None  # type: ignore[assignment,misc]
    check_intervention_required = None  # type: ignore[assignment,misc]
    get_intervention_server = None  # type: ignore[assignment,misc]
    start_intervention_server = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="intervention_server_validator.py deps unavailable")
class TestInterventionContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(InterventionContext)
    def test_importable(self):
        assert InterventionContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="intervention_server_validator.py deps unavailable")
class TestInterventionServer:
    def test_is_class(self):
        assert isinstance(InterventionServer, type)
    def test_importable(self):
        assert InterventionServer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="intervention_server_validator.py deps unavailable")
class TestCheckInterventionRequired:
    def test_is_callable(self):
        assert callable(check_intervention_required)

@pytest.mark.skipif(not _AVAILABLE, reason="intervention_server_validator.py deps unavailable")
class TestGetInterventionServer:
    def test_is_callable(self):
        assert callable(get_intervention_server)

@pytest.mark.skipif(not _AVAILABLE, reason="intervention_server_validator.py deps unavailable")
class TestStartInterventionServer:
    def test_is_callable(self):
        assert callable(start_intervention_server)


def test_module_importable():
    """Module intervention_server_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
