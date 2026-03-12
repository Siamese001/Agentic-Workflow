"""ADG-driven tests for agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py — fan_in=5.

Contract tests: GravityRepairProhibitedError, GravityFix, GravityLeakRepairAgent init and analyze.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
    GravityFix,
    GravityLeakRepairAgent,
    GravityRepairProhibitedError,
)


class TestGravityRepairProhibitedError:
    def test_is_exception(self):
        assert issubclass(GravityRepairProhibitedError, Exception)

    def test_attributes_stored(self):
        err = GravityRepairProhibitedError(
            file_path=Path("agentic_core/L2/foo.py"),
            layer="L2",
            op="write_text",
        )
        assert err.file_path == Path("agentic_core/L2/foo.py")
        assert err.layer == "L2"
        assert err.op == "write_text"

    def test_message_contains_layer(self):
        err = GravityRepairProhibitedError(Path("x.py"), "L3", "copy")
        assert "L3" in str(err)

    def test_can_be_raised(self):
        with pytest.raises(GravityRepairProhibitedError):
            raise GravityRepairProhibitedError(Path("x.py"), "L2", "op")


class TestGravityFix:
    def test_valid_creation(self):
        fix = GravityFix(
            file_path=Path("agentic_core/L2/foo.py"),
            line_number=42,
            old_import="from agentic_core.L5_safety.x import y",
            new_import="from agentic_core.utils.x import y",
            fix_type="RELOCATE",
            rationale="gravity violation",
        )
        assert fix.file_path == Path("agentic_core/L2/foo.py")
        assert fix.line_number == 42
        assert fix.fix_type == "RELOCATE"

    def test_is_dataclass(self):
        from dataclasses import fields
        field_names = {f.name for f in fields(GravityFix)}
        assert {"file_path", "line_number", "old_import", "new_import", "fix_type", "rationale"} == field_names


class TestGravityLeakRepairAgentInit:
    def test_creates_without_args(self):
        agent = GravityLeakRepairAgent()
        assert agent is not None

    def test_creates_with_path(self):
        agent = GravityLeakRepairAgent(project_root=Path("."))
        assert agent.project_root == Path(".")

    def test_layer_order_present(self):
        assert hasattr(GravityLeakRepairAgent, "LAYER_ORDER")
        assert isinstance(GravityLeakRepairAgent.LAYER_ORDER, dict)

    def test_prohibition_hits_starts_empty(self):
        agent = GravityLeakRepairAgent()
        assert agent._prohibition_hits == {}


class TestGravityLeakRepairAgentAnalyze:
    def setup_method(self):
        self.agent = GravityLeakRepairAgent()

    def test_analyze_violation_returns_gravity_fix(self):
        fix = self.agent.analyze_violation(
            file_path=Path("agentic_core/L2_execution/foo.py"),
            import_statement="from agentic_core.L5_safety.x import y",
            file_layer="L2",
            import_layer="L5",
        )
        assert isinstance(fix, GravityFix)

    def test_analyze_violation_fix_type_nonempty(self):
        fix = self.agent.analyze_violation(
            file_path=Path("agentic_core/L2_execution/foo.py"),
            import_statement="from agentic_core.L5_safety.x import y",
            file_layer="L2",
            import_layer="L5",
        )
        assert fix.fix_type in {"RELOCATE", "ABSTRACT", "INJECT", "REMOVE", "DEFERRED"}

    def test_analyze_violation_records_file_path(self):
        p = Path("agentic_core/L2_execution/bar.py")
        fix = self.agent.analyze_violation(
            file_path=p,
            import_statement="from agentic_core.L5_safety.y import z",
            file_layer="L2",
            import_layer="L5",
        )
        assert fix.file_path == p
