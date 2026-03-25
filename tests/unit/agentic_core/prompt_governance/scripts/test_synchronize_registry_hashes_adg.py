"""ADG-driven tests for agentic_core/prompt_governance/scripts/synchronize_registry_hashes.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.prompt_governance.scripts.synchronize_registry_hashes  # noqa: F401


def test_module_importable():
    """Module synchronize_registry_hashes must be importable."""
    assert agentic_core.prompt_governance.scripts.synchronize_registry_hashes is not None
