"""ADG importability contract for agentic_core/L3_orchestration/engines/autonomous_workflow_engine.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.engines.autonomous_workflow_engine  # noqa: F401


def test_module_importable():
    """Module autonomous_workflow_engine must be importable."""
    assert agentic_core.L3_orchestration.engines.autonomous_workflow_engine is not None
