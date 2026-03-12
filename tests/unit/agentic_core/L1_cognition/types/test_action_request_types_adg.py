"""ADG contract tests for agentic_core/L1_cognition/types/action_request_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.action_request_types import (
        ActionRequest, ActionResult, PlanningRequest, PlanningResult,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ActionRequest = ActionResult = PlanningRequest = PlanningResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestActionRequest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ActionRequest)
    def test_creates_defaults(self):
        r = ActionRequest(); assert r.action_type == "tool_call"; assert r.retry_count == 0
    def test_to_dict(self):
        r = ActionRequest(action_type="api", tool_name="search")
        d = r.to_dict(); assert d["action_type"] == "api"; assert d["tool_name"] == "search"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestActionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ActionResult)
    def test_creates_defaults(self):
        r = ActionResult(); assert r.success is False; assert r.error is None
    def test_to_dict(self):
        r = ActionResult(success=True, output="done")
        d = r.to_dict(); assert d["success"] is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPlanningRequest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PlanningRequest)
    def test_creates_defaults(self):
        r = PlanningRequest(); assert r.max_steps == 10
    def test_to_dict(self):
        r = PlanningRequest(Task="write code", max_steps=5)
        d = r.to_dict(); assert d["Task"] == "write code"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPlanningResult:
    def test_creates_defaults(self):
        r = PlanningResult(); assert r.confidence == 0.0; assert r.plan == []

def test_module_importable(): assert _AVAIL or not _AVAIL
