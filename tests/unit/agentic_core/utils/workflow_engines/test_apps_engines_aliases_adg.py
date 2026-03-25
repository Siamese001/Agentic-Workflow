"""ADG-driven tests for agentic_core/utils/workflow_engines/apps_engines_aliases.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.apps_engines_aliases as _mod  # noqa: F401


def test_module_importable():
    """Module apps_engines_aliases must be importable."""
    assert _mod is not None
