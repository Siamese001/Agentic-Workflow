"""ADG importability contract for agentic_core/L2_execution/scripts/remediation_dispatcher.py."""
from __future__ import annotations

import agentic_core.L2_execution.scripts.remediation_dispatcher  # noqa: F401


def test_module_importable():
    """Module remediation_dispatcher must be importable."""
    assert agentic_core.L2_execution.scripts.remediation_dispatcher is not None
