"""ADG-driven tests for agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py — fan_in=1.

Contract tests: SSOTFolderCleanupAgent init, stats, dry_run default.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_ssot_folder_cleanup_agent_adg")
_emit_applies_guardrail("p0", "test_ssot_folder_cleanup_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_folder_cleanup_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_folder_cleanup_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_ssot_folder_cleanup_agent_adg")
emit_determinism_digest("p0", "test_ssot_folder_cleanup_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent import SSOTFolderCleanupAgent

_REPO_ROOT = Path(__file__).parents[5]


class TestSSOTFolderCleanupAgentInit:
    def test_creates_with_defaults(self):
        agent = SSOTFolderCleanupAgent()
        assert agent is not None

    def test_dry_run_default_true(self):
        agent = SSOTFolderCleanupAgent()
        assert agent.dry_run is True

    def test_project_root_is_path(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.project_root, Path)

    def test_stats_dict_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.stats, dict)
        assert "files_scanned" in agent.stats
        assert "files_moved" in agent.stats
        assert "errors" in agent.stats

    def test_stats_start_zero(self):
        agent = SSOTFolderCleanupAgent()
        assert agent.stats["files_scanned"] == 0
        assert agent.stats["errors"] == 0

    def test_lazy_cognitive_agent_none(self):
        agent = SSOTFolderCleanupAgent()
        assert agent._cognitive_agent is None

    def test_creates_with_custom_root(self):
        agent = SSOTFolderCleanupAgent(project_root=_REPO_ROOT)
        assert agent.project_root == _REPO_ROOT

    def test_dry_run_false(self):
        agent = SSOTFolderCleanupAgent(dry_run=False)
        assert agent.dry_run is False

    def test_sovereign_registry_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.sovereign_registry, dict)
        assert "agentic_core" in agent.sovereign_registry

    def test_core_subfolder_map_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.core_subfolder_map, dict)
        assert "L0_routing" in agent.core_subfolder_map
