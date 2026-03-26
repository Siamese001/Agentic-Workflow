"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/registry_verification_enforcer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.registry_verification_enforcer  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.registry_verification_enforcer  # noqa: F401
    """Module registry_verification_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.registry_verification_enforcer is not None
