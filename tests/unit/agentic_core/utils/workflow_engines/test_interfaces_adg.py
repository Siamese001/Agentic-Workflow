"""ADG importability contract for agentic_core/utils/workflow_engines/interfaces.py."""
from __future__ import annotations

import agentic_core.utils.workflow_engines.interfaces  # noqa: F401


def test_module_importable():
    """Module interfaces must be importable."""
    assert agentic_core.utils.workflow_engines.interfaces is not None
