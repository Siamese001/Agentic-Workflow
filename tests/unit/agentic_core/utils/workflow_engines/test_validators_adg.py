"""ADG importability contract for agentic_core/utils/workflow_engines/validators.py."""
from __future__ import annotations

import agentic_core.utils.workflow_engines.validators  # noqa: F401


def test_module_importable():
    """Module validators must be importable."""
    assert agentic_core.utils.workflow_engines.validators is not None
