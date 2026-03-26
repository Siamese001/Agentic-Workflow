"""ADG-driven tests for agentic_core/prompt_governance/core/governance_hub.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.core.governance_hub  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.core.governance_hub  # noqa: F401
    """Module governance_hub must be importable."""
    assert agentic_core.prompt_governance.core.governance_hub is not None
