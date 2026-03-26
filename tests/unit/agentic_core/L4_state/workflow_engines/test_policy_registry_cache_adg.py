"""ADG-driven tests for agentic_core/L4_state/workflow_engines/policy_registry_cache.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.workflow_engines.policy_registry_cache  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.workflow_engines.policy_registry_cache  # noqa: F401
    """Module policy_registry_cache must be importable."""
    assert agentic_core.L4_state.workflow_engines.policy_registry_cache is not None
