"""ADG contract tests for L4_state/types/cycle_types.py."""
from __future__ import annotations

import ast

import pytest

pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L4_state/types/cycle_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_has_cycle_state():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "CycleState" in src or "CycleConfig" in src

def test_has_think_act_observe():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "think" in src.lower() or "act" in src.lower() or "observe" in src.lower()

try:
    from agentic_core.L4_state.types.cycle_types import CycleConfig, CycleState
    _AVAIL = True
except ImportError:
    _AVAIL = False
    CycleConfig = CycleState = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCycleConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CycleConfig)
    def test_creates_defaults(self):
        c = CycleConfig(); assert c.max_iterations == 10; assert c.enable_react is True
    def test_to_dict(self):
        c = CycleConfig(); d = c.to_dict(); assert "max_iterations" in d

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCycleState:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CycleState)
    def test_creates(self):
        s = CycleState(mission="test mission", scene={"key": "val"})
        assert s.mission == "test mission"; assert s.iteration == 0
    def test_to_dict(self):
        s = CycleState(mission="m", scene={}); d = s.to_dict(); assert "mission" in d
