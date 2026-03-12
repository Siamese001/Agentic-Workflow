"""ADG-driven tests for agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py — fan_in=3.

Contract tests: StructureViolationType, StructureViolation, StructureConfig,
StructuralValidatorAgent init, validate_file, validate_structure.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
    StructureConfig,
    StructuralValidatorAgent,
    StructureViolation,
    StructureViolationType,
)


class TestStructureViolationType:
    def test_has_gravity(self):
        assert StructureViolationType.GRAVITY == "GRAVITY"

    def test_has_hierarchy(self):
        assert StructureViolationType.HIERARCHY == "HIERARCHY"

    def test_has_naming(self):
        assert StructureViolationType.NAMING == "NAMING"

    def test_has_documentation(self):
        assert StructureViolationType.DOCUMENTATION == "DOCUMENTATION"

    def test_has_ascii(self):
        assert StructureViolationType.ASCII == "ASCII"


class TestStructureViolation:
    def test_creates_valid(self):
        v = StructureViolation(
            file_path=Path("foo.py"),
            line_number=5,
            violation_type=StructureViolationType.GRAVITY,
            message="upward import",
        )
        assert v.file_path == Path("foo.py")
        assert v.line_number == 5
        assert v.violation_type == "GRAVITY"

    def test_defaults(self):
        v = StructureViolation(
            file_path=Path("x.py"),
            line_number=1,
            violation_type="NAMING",
            message="test",
        )
        assert v.suggested_fix is None
        assert v.auto_fixable is False
        assert v.severity == "ERROR"


class TestStructureConfig:
    def test_defaults(self):
        cfg = StructureConfig()
        assert cfg.enable_gravity is True
        assert cfg.enable_naming is True
        assert cfg.auto_fix is False
        assert cfg.agent_suffix == "Agent"

    def test_layer_constants_accessible(self):
        from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import LAYER_ORDER, GRAVITY_RULES
        assert isinstance(LAYER_ORDER, dict)
        assert isinstance(GRAVITY_RULES, dict)
        assert "L0" in LAYER_ORDER
        assert "L5" in GRAVITY_RULES


class TestStructuralValidatorAgentInit:
    def test_creates_without_args(self):
        agent = StructuralValidatorAgent()
        assert agent is not None

    def test_layer_order_class_attribute(self):
        assert isinstance(StructuralValidatorAgent.LAYER_ORDER, dict)
        assert len(StructuralValidatorAgent.LAYER_ORDER) > 0

    def test_gravity_rules_class_attribute(self):
        assert isinstance(StructuralValidatorAgent.GRAVITY_RULES, dict)
        assert "L0" in StructuralValidatorAgent.GRAVITY_RULES

    def test_config_defaults_applied(self):
        agent = StructuralValidatorAgent()
        assert isinstance(agent.config, StructureConfig)

    def test_violations_start_empty(self):
        agent = StructuralValidatorAgent()
        assert agent.violations == []


class TestStructuralValidatorAgentValidate:
    def setup_method(self):
        self.agent = StructuralValidatorAgent()

    def test_validate_file_nonexistent_returns_empty(self):
        result = self.agent.validate_file(Path("nonexistent_xyz.py"))
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

    def test_validate_structure_returns_self(self):
        with tempfile.TemporaryDirectory() as d:
            tmp_dir = Path(d)
            (tmp_dir / "foo.py").write_text("x = 1\n")
            result = self.agent.validate_structure(tmp_dir)
            assert result is self.agent
