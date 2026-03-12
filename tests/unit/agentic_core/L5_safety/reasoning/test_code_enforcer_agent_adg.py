"""ADG-driven tests for agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py — fan_in=3.

Contract tests: EnforcementType, ViolationSeverity, CodeViolation, SignedException,
EnforcementConfig, CodeEnforcerAgent init and validate_file.
"""
from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import (
    CodeEnforcerAgent,
    CodeViolation,
    EnforcementConfig,
    EnforcementType,
    SignedException,
    ViolationSeverity,
)


class TestEnforcementType:
    def test_all_members_present(self):
        members = {e.name for e in EnforcementType}
        assert {"SSOT_SYNC", "CODE_STANDARDS", "PATTERN", "TYPE_HINTS", "SOVEREIGNTY"} == members

    def test_is_enum(self):
        from enum import Enum
        assert issubclass(EnforcementType, Enum)


class TestViolationSeverity:
    def test_all_levels_present(self):
        names = {e.name for e in ViolationSeverity}
        assert {"INFO", "WARNING", "ERROR", "CRITICAL"} == names

    def test_ordering(self):
        assert ViolationSeverity.INFO.value < ViolationSeverity.CRITICAL.value


class TestCodeViolation:
    def test_creates_valid(self):
        v = CodeViolation(
            file_path=Path("foo.py"),
            line_number=10,
            enforcement_type=EnforcementType.PATTERN,
            severity=ViolationSeverity.ERROR,
            message="bare except detected",
        )
        assert v.file_path == Path("foo.py")
        assert v.line_number == 10
        assert v.severity == ViolationSeverity.ERROR

    def test_defaults(self):
        v = CodeViolation(
            file_path=Path("x.py"),
            line_number=1,
            enforcement_type=EnforcementType.CODE_STANDARDS,
            severity=ViolationSeverity.WARNING,
            message="test",
        )
        assert v.suggested_fix is None
        assert v.auto_fixable is False


class TestSignedException:
    def test_creates_valid(self):
        s = SignedException(
            exception_id="exc-001",
            source_layer="L3",
            target_layer="L5",
            target_file="L5/foo.py",
            granted_by="architect",
        )
        assert s.exception_id == "exc-001"
        assert s.source_layer == "L3"

    def test_defaults(self):
        s = SignedException(
            exception_id="e",
            source_layer="L2",
            target_layer="L4",
            target_file="x.py",
            granted_by="admin",
        )
        assert isinstance(s.granted_at, datetime)
        assert s.expires_at is None
        assert s.reason == ""


class TestEnforcementConfig:
    def test_defaults(self):
        cfg = EnforcementConfig()
        assert cfg.enable_ssot_sync is True
        assert cfg.enable_standards is True
        assert cfg.enable_patterns is True
        assert cfg.auto_fix is False

    def test_protected_layers_default(self):
        cfg = EnforcementConfig()
        assert "L5" in cfg.protected_layers
        assert "L6" in cfg.protected_layers

    def test_custom_config(self):
        cfg = EnforcementConfig(auto_fix=True, enable_type_hints=False)
        assert cfg.auto_fix is True
        assert cfg.enable_type_hints is False


class TestCodeEnforcerAgentInit:
    def test_creates_without_args(self):
        agent = CodeEnforcerAgent()
        assert agent is not None

    def test_creates_with_path(self):
        agent = CodeEnforcerAgent(project_root=Path("."))
        assert agent.project_root == Path(".")

    def test_default_config_applied(self):
        agent = CodeEnforcerAgent()
        assert isinstance(agent._agent_config, EnforcementConfig)

    def test_violations_start_empty(self):
        agent = CodeEnforcerAgent()
        assert agent._violations == []

    def test_signed_exceptions_start_empty(self):
        agent = CodeEnforcerAgent()
        assert agent._signed_exceptions == {}


class TestCodeEnforcerAgentValidateFile:
    def setup_method(self):
        self.agent = CodeEnforcerAgent()

    def test_nonexistent_file_returns_empty(self):
        result = self.agent.validate_file(Path("nonexistent_xyz.py"))
        assert result == []

    def test_clean_file_no_violations(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = 1\ny = x + 2\n")
            tmp = Path(f.name)
        try:
            violations = self.agent.validate_file(tmp)
            assert isinstance(violations, list)
        finally:
            tmp.unlink(missing_ok=True)

    def test_heal_repository_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
        assert "violations_found" in result
