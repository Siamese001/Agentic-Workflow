"""ADG importability contract for agentic_core/utils/workflow_engines/completeness.py."""
from __future__ import annotations

import agentic_core.utils.workflow_engines.completeness  # noqa: F401


def test_module_importable():
    """Module completeness must be importable."""
    assert agentic_core.utils.workflow_engines.completeness is not None
