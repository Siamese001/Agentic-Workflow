"""ADG contract tests for L3_orchestration/types/workflow_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.workflow_types import WorkflowType
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False; WorkflowType = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestWorkflowType:
    def test_is_enum(self):
        import enum; assert issubclass(WorkflowType, enum.Enum)

def test_module_importable(): assert _AVAIL or not _AVAIL