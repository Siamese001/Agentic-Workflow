"""ADG-driven tests for agentic_core/prompt_governance/meta_prompts/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.meta_prompts.__init__ as _mod  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.meta_prompts.__init__ as _mod  # noqa: F401
        """Module meta_prompts must be importable."""
        assert _mod is not None

    assert _mod is not None
