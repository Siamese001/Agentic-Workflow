"""ADG importability contract for agentic_core/utils/workflow_engines/policies.py."""
from __future__ import annotations

import agentic_core.utils.workflow_engines.policies  # noqa: F401


def test_module_importable():
    """Module policies must be importable."""
    assert agentic_core.utils.workflow_engines.policies is not None
