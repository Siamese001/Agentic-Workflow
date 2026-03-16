#!/usr/bin/env python3
"""
Tests for HierarchyAgent (previously HierarchyAgent.py, renamed to hierarchy_healer.py
in commit 2f0dc584d — refactor(phase5): rename HierarchyAgent.py -> hierarchy_healer.py).
"""
from __future__ import annotations

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
from agentic_core.L5_safety.reasoning.hierarchy_validator import HierarchyValidatorAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_HierarchyAgent")
_emit_applies_guardrail("p0", "test_HierarchyAgent", "p0_governance")
_emit_reads_policy_state("p0", "test_HierarchyAgent", "policy_binding")
_emit_snapshots_state("p0", "test_HierarchyAgent", "state_snapshot")
emit_replay_key("p0", "test_HierarchyAgent")
emit_determinism_digest("p0", "test_HierarchyAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestHierarchyAgentSmoke:
    def test_instantiates_with_project_root(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent is not None

    def test_project_root_stored(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent.project_root == tmp_path.resolve()

    def test_healing_disabled_flag(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent.healing_enabled is False

    def test_healing_enabled_flag(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=True)
        assert agent.healing_enabled is True

    def test_has_heal_method(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert callable(getattr(agent, "heal", None))

    def test_heal_returns_non_error_when_disabled(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "STRUCTURE", "file": str(tmp_path / "foo.py")})
        assert result["status"] in ("skipped", "manual_required", "success", "partial_success")

    def test_heal_missing_file_path_returns_error_or_skipped(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "MISPLACED"})
        assert result["status"] in ("failed", "skipped", "manual_required")


class TestHierarchyValidatorAgentSmoke:
    def test_instantiates_with_project_root(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        assert validator is not None

    def test_project_root_stored(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        assert validator.project_root == tmp_path.resolve()

    def test_scan_root_violations_returns_dict(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        result = validator.scan_root_violations()
        assert isinstance(result, dict)
