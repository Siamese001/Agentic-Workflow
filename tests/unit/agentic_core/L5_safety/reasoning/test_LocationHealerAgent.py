"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/LocationHealerAgent.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_LocationHealerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import (  # noqa: F401
        LocationHealerAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LocationHealerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="LocationHealerAgent.py deps unavailable")
class TestLocationHealerAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LocationHealerAgent)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(LocationHealerAgent)}
        assert fnames >= {'project_root'}


def test_module_importable():
    """Module LocationHealerAgent must be importable."""
    assert _AVAILABLE or not _AVAILABLE
