"""ADG-driven tests for agentic_core/prompt_governance/core/prompt_loader.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.core.prompt_loader  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.core.prompt_loader  # noqa: F401
        """Module prompt_loader must be importable."""
        assert agentic_core.prompt_governance.core.prompt_loader is not None

    assert agentic_core.prompt_governance.core.prompt_loader is not None
