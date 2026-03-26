"""ADG-driven tests for agentic_core/prompt_governance/core/sovereign_prompt_renderer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.core.sovereign_prompt_renderer  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.core.sovereign_prompt_renderer  # noqa: F401
    """Module sovereign_prompt_renderer must be importable."""
    assert agentic_core.prompt_governance.core.sovereign_prompt_renderer is not None
