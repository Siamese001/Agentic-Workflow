"""ADG-driven tests for agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py — fan_in=3.

Contract tests: StructureViolationType, StructureViolation, NamingRule, StructureConfig,
StructureEnforcerAgent init, validate_file, heal_repository.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import (
    NamingRule,
    StructureConfig,
    StructureEnforcerAgent,
    StructureViolation,
    StructureViolationType,
)


class TestStructureViolationTypeEnforcer:
    def test_has_gravity(self):
        assert StructureViolationType.GRAVITY == "GRAVITY"

    def test_has_naming(self):
        assert StructureViolationType.NAMING == "NAMING"

    def test_has_documentation(self):
        assert StructureViolationType.DOCUMENTATION == "DOCUMENTATION"


class TestStructureViolationEnforcer:
    def test_creates_valid(self):
        v = StructureViolation(
            file_path=Path("foo.py"),
            line_number=3,
            violation_type="GRAVITY",
            message="upward import",
        )
        assert v.message == "upward import"
        assert v.severity == "ERROR"

    def test_auto_fixable_default(self):
        v = StructureViolation(
            file_path=Path("x.py"), line_number=1, violation_type="NAMING", message="test"
        )
        assert v.auto_fixable is False


class TestNamingRule:
    def test_creates_valid(self):
        rule = NamingRule(
            pattern=".*Agent",
            suffix="Agent",
            description="All agent classes must end with Agent",
        )
        assert rule.pattern == ".*Agent"
        assert rule.auto_rename is True

    def test_auto_rename_can_be_disabled(self):
        rule = NamingRule(
            pattern=".*Util",
            suffix="Util",
            description="Utility pattern",
            auto_rename=False,
        )
        assert rule.auto_rename is False


class TestStructureConfigEnforcer:
    def test_defaults(self):
        cfg = StructureConfig()
        assert cfg.enable_gravity is True
        assert cfg.auto_fix is False
        assert cfg.agent_suffix == "Agent"
        assert cfg.min_docstring_length == 10


class TestStructureEnforcerAgentInit:
    def test_creates_without_args(self):
        agent = StructureEnforcerAgent()
        assert agent is not None

    def test_layer_order_class_attribute(self):
        assert isinstance(StructureEnforcerAgent.LAYER_ORDER, dict)
        assert "L0" in StructureEnforcerAgent.LAYER_ORDER

    def test_gravity_rules_class_attribute(self):
        assert isinstance(StructureEnforcerAgent.GRAVITY_RULES, dict)
        assert len(StructureEnforcerAgent.GRAVITY_RULES) > 0

    def test_l0_only_imports_l0(self):
        assert StructureEnforcerAgent.GRAVITY_RULES["L0"] == {"L0"}

    def test_l5_can_import_l0_through_l5(self):
        allowed = StructureEnforcerAgent.GRAVITY_RULES["L5"]
        for layer in ("L0", "L1", "L2", "L3", "L4", "L5"):
            assert layer in allowed


class TestStructureEnforcerAgentAPI:
    def setup_method(self):
        self.agent = StructureEnforcerAgent()

    def test_validate_file_nonexistent_returns_empty(self):
        result = self.agent.validate_file(Path("nonexistent_xyz_abc.py"))
        assert result == []

    def test_validate_file_clean_returns_list(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = 1\n")
            tmp = Path(f.name)
        try:
            result = self.agent.validate_file(tmp)
            assert isinstance(result, list)
        finally:
            tmp.unlink(missing_ok=True)

    def test_heal_repository_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
        assert "violations" in result

    def test_check_gravity_import_method_exists(self):
        assert callable(self.agent.check_gravity_import)
