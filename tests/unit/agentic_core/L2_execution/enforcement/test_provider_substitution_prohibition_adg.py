"""ADG importability contract for agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.provider_substitution_prohibition  # noqa: F401


def test_module_importable():
    """Module provider_substitution_prohibition must be importable."""
    assert agentic_core.L2_execution.enforcement.provider_substitution_prohibition is not None
