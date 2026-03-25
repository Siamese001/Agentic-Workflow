"""ADG importability contract for agentic_core/L2_execution/deterministic_providers.py."""
from __future__ import annotations

import agentic_core.L2_execution.deterministic_providers  # noqa: F401


def test_module_importable():
    """Module deterministic_providers must be importable."""
    assert agentic_core.L2_execution.deterministic_providers is not None
