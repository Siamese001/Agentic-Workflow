"""ADG importability contract for agentic_core/adg/runtime/policy_state_observer.py."""
from __future__ import annotations

import agentic_core.adg.runtime.policy_state_observer  # noqa: F401


def test_module_importable():
    """Module policy_state_observer must be importable."""
    assert agentic_core.adg.runtime.policy_state_observer is not None
