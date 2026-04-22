"""Behavioral tests for GravityLeakRepairAgent + FilesystemSSOTReconcilerAgent."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
    GravityFix,
    GravityLeakRepairAgent,
    GravityRepairProhibitedError,
)
from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
    FilesystemSSOTReconcilerAgent,
    ReconciliationViolation,
)


# ============================================================================
# GravityLeakRepairAgent
# ============================================================================


class TestGravityRepairProhibitedError:
    def test_attributes(self, tmp_path: Path) -> None:
        f = tmp_path / "x.py"
        exc = GravityRepairProhibitedError(f, "L3", "relocate")
        assert exc.file_path == f
        assert exc.layer == "L3"
        assert exc.op == "relocate"

    def test_message_contains_fields(self, tmp_path: Path) -> None:
        exc = GravityRepairProhibitedError(tmp_path / "y.py", "L5", "abstract")
        msg = str(exc)
        assert "GRAVITY_REPAIR_PROHIBITED" in msg
        assert "L5" in msg
        assert "abstract" in msg

    def test_is_exception(self) -> None:
        assert issubclass(GravityRepairProhibitedError, Exception)


class TestGravityFix:
    def test_required_fields(self, tmp_path: Path) -> None:
        fix = GravityFix(
            file_path=tmp_path / "a.py",
            line_number=10,
            old_import="from L5 import X",
            new_import="from utils import X",
            fix_type="RELOCATE",
            rationale="upward import — move to utils",
        )
        assert fix.fix_type == "RELOCATE"
        assert fix.line_number == 10


class TestGravityLeakRepairAgent:
    def test_project_root_default_cwd(self) -> None:
        agent = GravityLeakRepairAgent()
        assert agent.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path) -> None:
        agent = GravityLeakRepairAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path

    def test_string_root_coerced(self, tmp_path: Path) -> None:
        agent = GravityLeakRepairAgent(project_root=str(tmp_path))
        assert isinstance(agent.project_root, Path)

    def test_prohibition_hits_empty(self, tmp_path: Path) -> None:
        agent = GravityLeakRepairAgent(project_root=tmp_path)
        assert agent._prohibition_hits == {}

    def test_context_wired(self, tmp_path: Path) -> None:
        agent = GravityLeakRepairAgent(project_root=tmp_path)
        assert agent.context is not None

    def test_layer_order_is_class_attr(self) -> None:
        assert hasattr(GravityLeakRepairAgent, "LAYER_ORDER")
        assert GravityLeakRepairAgent.LAYER_ORDER is not None


# ============================================================================
# FilesystemSSOTReconcilerAgent
# ============================================================================


class TestReconciliationViolation:
    def test_defaults(self) -> None:
        v = ReconciliationViolation(is_valid=True, message="ok")
        assert v.is_valid is True
        assert v.message == "ok"
        assert v.drift_type is None
        assert v.file_path is None
        assert v.suggested_action is None
        assert v.severity == 5

    def test_all_fields(self, tmp_path: Path) -> None:
        v = ReconciliationViolation(
            is_valid=False,
            message="drift found",
            drift_type="unmapped",
            file_path=tmp_path / "x.py",
            suggested_action="archive",
            severity=8,
        )
        assert v.is_valid is False
        assert v.severity == 8
        assert v.drift_type == "unmapped"


class TestFilesystemSSOTReconcilerAgent:
    def test_project_root_resolved(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()

    def test_enforcement_mode_default_true(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        assert agent.enforcement_mode is True

    def test_enforcement_mode_override(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(
            project_root=tmp_path, enforcement_mode=False,
        )
        assert agent.enforcement_mode is False

    def test_blueprint_file_path(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        assert agent.blueprint_file == (
            tmp_path / "agentic_core" / "L5_safety" / "config" / "structure_blueprint_config.py"
        ).resolve() or agent.blueprint_file.parent.parent.parent.parent == tmp_path.resolve()

    def test_class_attrs_present(self) -> None:
        assert hasattr(FilesystemSSOTReconcilerAgent, "BLUEPRINT_PATH")
        assert hasattr(FilesystemSSOTReconcilerAgent, "ARCHIVE_ROOT")


class TestFilesystemSSOTReconcilerHeal:
    def test_heal_empty_violation_skipped(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal({})
        assert result["status"] == "skipped"

    def test_heal_with_target(self, tmp_path: Path) -> None:
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal({"file": "x.py", "type": "drift"})
        assert result["status"] == "manual_required"
        assert "blueprint alignment" in result["details"]
