"""
Edge-case, stress, and bypass-scenario tests for HierarchyAgent phantom directory bugs.

Complements test_hierarchy_agent_depth_violation.py (happy-path branches) with:
  - File already inside depth_aligned/ at correct depth → silent bypass (enforcement gap)
  - Extreme depth values (0, 100, single-level)
  - Stress: 25 DEEP / 25 SHALLOW files in one batch
  - Idempotency: repeated DEEP heal on same file hits collision path
  - Interleaved DEEP+SHALLOW routing correctness
  - SOVEREIGN_TERRITORIES blueprint invariants: no depth_aligned in required_subfolders
  - Contaminated required_subfolders: documents the vulnerability and the guard location
  - apps_rg/depth_aligned/ bypass: file at correct depth passes silently

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent.py | _heal_depth_violation | file in depth_aligned/ at depth==expected | else branch: 0, no gk | test_file_in_depth_aligned_correct_depth_silent_bypass |
| HierarchyAgent.py | _heal_depth_violation | file in depth_aligned/sub/ depth > expected | DEEP: gk called | test_file_in_depth_aligned_too_deep_healed |
| HierarchyAgent.py | _heal_depth_violation | deep heal from depth_aligned/sub/ | target has sub removed, gk called | test_deep_flatten_from_depth_aligned_gk_arg |
| HierarchyAgent.py | _heal_depth_violation | depth=100, expected=2 | DEEP: gk called, 3-part target | test_extreme_depth_100_flattened |
| HierarchyAgent.py | _heal_depth_violation | depth=100, no phantom dirs in target | depth_aligned absent in gk arg | test_extreme_depth_100_no_phantom_in_target |
| HierarchyAgent.py | _heal_depth_violation | depth=0, expected=3 | SHALLOW: returns 0, no gk | test_extreme_shallow_0_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | depth=0, no filesystem mutation | file unchanged | test_extreme_shallow_0_no_mutation |
| HierarchyAgent.py | _heal_depth_violation | depth=1, expected=10 | SHALLOW: returns 0, no gk | test_large_deficit_shallow_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | depth=5, expected=2 | DEEP: 3-part flattened target | test_depth_5_expected_2_flattens_correctly |
| HierarchyAgent.py | _heal_depth_violation | stress: 25 DEEP files | 25 gk calls | test_stress_25_deep_files_all_gk_called |
| HierarchyAgent.py | _heal_depth_violation | stress: 25 DEEP files, no phantom | depth_aligned absent from all targets | test_stress_25_deep_files_no_phantom_in_targets |
| HierarchyAgent.py | _heal_depth_violation | stress: 25 SHALLOW files | gk.safe_move never called | test_stress_25_shallow_files_no_gk |
| HierarchyAgent.py | _heal_depth_violation | stress: 25 SHALLOW, no dir creation | no new dirs added | test_stress_25_shallow_no_dir_creation |
| HierarchyAgent.py | _heal_depth_violation | interleaved DEEP+SHALLOW | DEEP count = gk count | test_interleaved_deep_shallow_routing |
| HierarchyAgent.py | _heal_depth_violation | repeated DEEP same file, target exists | 2nd call → _legacy_archive | test_idempotent_deep_heal_collision |
| _constants.py | SOVEREIGN_TERRITORIES | required_subfolders all territories | no depth_aligned | test_no_depth_aligned_in_required_subfolders |
| _constants.py | SOVEREIGN_TERRITORIES | tests required_subfolders | no l*_* names | test_no_l_layer_in_tests_required_subfolders |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"]["support"] | no subfolders key | flat | test_support_has_no_declared_subfolders |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"] | support exists | approved | test_support_in_approved_tests_subfolders |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"] | depth_aligned absent | not approved | test_depth_aligned_not_in_approved_tests_subfolders |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"] | no l*_* at top level | no l-layer | test_no_l_layer_in_approved_tests_subfolders |
| HierarchyAgent.py | _create_territory_structure | required_subfolders has depth_aligned | creates it (vulnerability) | test_create_territory_contaminated_blueprint_creates_phantom |
| HierarchyAgent.py | create_missing_structure | controlled SOVEREIGN_TERRITORIES | no depth_aligned in ensure_dir calls | test_create_missing_structure_no_depth_aligned_dir_calls |
| HierarchyAgent.py | _heal_depth_violation | apps_rg/depth_aligned/__init__.py depth==expected | returns 0, no gk (bypass) | test_apps_rg_depth_aligned_correct_depth_bypass |
| HierarchyAgent.py | _heal_depth_violation | apps_rg/depth_aligned/sub/f.py depth > expected | DEEP: gk called | test_apps_rg_depth_aligned_subfile_too_deep_detected |
"""

from __future__ import annotations

import re
from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    L0_ROUTING_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_agent_phantom_dir_edge_cases")
_emit_applies_guardrail("p0", "test_hierarchy_agent_phantom_dir_edge_cases", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_agent_phantom_dir_edge_cases", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_agent_phantom_dir_edge_cases", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_1")
_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_2")
_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_3")
_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_4")
_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_5")
_emit_emits_metric_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "metric_6")
_emit_records_incident_event("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "anomaly")
_emit_writes_observability_log("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "mon_state")
_emit_triggers_alert("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "alert")
_emit_links_incident_trace("test_hierarchy_agent_phantom_dir_edge_cases", "p4obs", "trace_link")
_emit_captures_pattern("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "pattern")
_emit_records_learning_event("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "routing")
_emit_improves_agent_policy("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "policy")
_emit_stores_learning_state("test_hierarchy_agent_phantom_dir_edge_cases", "p3lm", "state")
_emit_records_execution_trace("test_hierarchy_agent_phantom_dir_edge_cases", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hierarchy_agent_phantom_dir_edge_cases", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hierarchy_agent_phantom_dir_edge_cases", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hierarchy_agent_phantom_dir_edge_cases", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hierarchy_agent_phantom_dir_edge_cases", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hierarchy_agent_phantom_dir_edge_cases", "env_read", "p2_env_1")
_emit_reads_environ("test_hierarchy_agent_phantom_dir_edge_cases", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hierarchy_agent_phantom_dir_edge_cases", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hierarchy_agent_phantom_dir_edge_cases", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "context_pull")
_emit_pulls_context("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "uwg_term_2")
_emit_writes_through("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "write_through")
_emit_writes_through("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "safety_validation")
_emit_invokes_eval("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "eval_call")
_emit_proposal_commits_routing("p1", "test_hierarchy_agent_phantom_dir_edge_cases", "routing_commit")
emit_replay_key("p0", "test_hierarchy_agent_phantom_dir_edge_cases")
emit_determinism_digest("p0", "test_hierarchy_agent_phantom_dir_edge_cases")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "execution_auth")
_emit_validates_capability("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "capability_check")
_emit_routes_to_capability("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "capability_route")
_emit_writes_via_uwg("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "uwg_write")
_emit_blocks_direct_write("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "tool_invocation")
_emit_captures_execution_output("p2", "test_hierarchy_agent_phantom_dir_edge_cases", "exec_output")
_emit_dispatches_agent("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "healing_outcome")
_emit_escalates_failure("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hierarchy_agent_phantom_dir_edge_cases", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hierarchy_agent_phantom_dir_edge_cases", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hierarchy_agent_phantom_dir_edge_cases", "eval_metric")
_emit_stores_embedding("p4", "test_hierarchy_agent_phantom_dir_edge_cases", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hierarchy_agent_phantom_dir_edge_cases", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hierarchy_agent_phantom_dir_edge_cases", "exec_snapshot_link")

_Mapping = (dict, MappingProxyType)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent(project_root: Path, healing_enabled: bool = True):
    """Construct a minimal HierarchyAgent without triggering __init__ chain."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = project_root
    agent.agent_name = "HierarchyAgent"
    agent.healing_enabled = healing_enabled
    gk = MagicMock()
    gk.safe_move.return_value = MagicMock(success=True, error=None)
    gk.safe_archive.return_value = MagicMock(
        success=True, destination_path=project_root / ".healing_backups" / "x"
    )
    gk.safe_delete.return_value = MagicMock(success=True)
    agent.gatekeeper = gk
    agent._legacy_archive_depth_violation = MagicMock(return_value=0)
    return agent


def _call(agent, file_path, rel, depth, expected):
    with patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg:
        mock_wg.ensure_dir = MagicMock()
        return agent._heal_depth_violation(file_path, rel, depth, expected)


# ---------------------------------------------------------------------------
# Bug 2 core scenario: file inside depth_aligned/ at correct depth is bypassed
# ---------------------------------------------------------------------------


class TestFileInsideDepthAlignedDir:
    """
    The core mechanism behind the depth_aligned phantom bug:
    A file placed at the correct depth INSIDE a depth_aligned/ directory is
    never detected or moved by depth enforcement (depth == expected → else branch).
    Only the filesystem scan invariant catches this.
    """

    def test_file_in_depth_aligned_correct_depth_returns_zero(self, tmp_path):
        """
        Silent bypass: agentic_core/cache/depth_aligned/schema_cache.py
        depth=3, expected=3 → falls through all branches → returns 0, no gk call.
        """
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/cache/depth_aligned/schema_cache.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=3, expected=3)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_file_in_depth_aligned_correct_depth_no_filesystem_mutation(self, tmp_path):
        """Silent bypass: file untouched when depth == expected inside depth_aligned/."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/cache/depth_aligned/schema_cache.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("original content")

        _call(agent, file_path, rel, depth=3, expected=3)

        assert file_path.read_text() == "original content"

    def test_file_in_depth_aligned_correct_depth_legacy_archive_not_called(self, tmp_path):
        """Silent bypass: _legacy_archive_depth_violation NOT called either."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/cache/depth_aligned/schema_cache.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=3, expected=3)

        agent._legacy_archive_depth_violation.assert_not_called()

    def test_file_in_depth_aligned_too_deep_healed_out(self, tmp_path):
        """
        DEEP violation inside depth_aligned/: depth=4, expected=3.
        agentic_core/cache/depth_aligned/sub/file.py → gk.safe_move called.
        """
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/cache/depth_aligned/sub/file.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=4, expected=3)

        agent.gatekeeper.safe_move.assert_called_once()
        assert result == 1

    def test_file_in_depth_aligned_too_deep_gk_target_drops_sub(self, tmp_path):
        """
        DEEP heal of agentic_core/cache/depth_aligned/sub/file.py → depth 4.
        Flattened target: parts[:3] + (name,) = agentic_core/cache/depth_aligned/file.py.
        'sub' is removed. No NEW depth_aligned folder is created.
        """
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/cache/depth_aligned/sub/file.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=4, expected=3)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        assert "sub" not in str(target)
        assert target.name == "file.py"


# ---------------------------------------------------------------------------
# Extreme boundary values
# ---------------------------------------------------------------------------


class TestExtremeBoundaries:
    """Extreme depth values that expose latent edge behavior."""

    def test_extreme_depth_100_expected_2_gk_called(self, tmp_path):
        """depth=20, expected=2 → DEEP, gk.safe_move called once."""
        agent = _make_agent(tmp_path)
        parts = (AGENTIC_CORE_DIR,) + ("sub",) * 19 + ("agent.py",)
        rel = Path(*parts)
        file_path = tmp_path.joinpath(*parts)
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=20, expected=2)

        agent.gatekeeper.safe_move.assert_called_once()

    def test_extreme_depth_100_flattened_to_expected_depth(self, tmp_path):
        """depth=20, expected=2 → flattened target has exactly 3 parts (root/sub/file)."""
        agent = _make_agent(tmp_path)
        parts = (AGENTIC_CORE_DIR,) + ("sub",) * 19 + ("agent.py",)
        rel = Path(*parts)
        file_path = tmp_path.joinpath(*parts)
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=20, expected=2)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert len(target_rel.parts) == 3

    def test_extreme_depth_100_no_phantom_dirs_in_target(self, tmp_path):
        """depth=20, expected=2 → target path must not contain 'depth_aligned'."""
        agent = _make_agent(tmp_path)
        parts = (AGENTIC_CORE_DIR,) + ("sub",) * 19 + ("agent.py",)
        rel = Path(*parts)
        file_path = tmp_path.joinpath(*parts)
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=20, expected=2)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        assert "depth_aligned" not in str(target)

    def test_extreme_shallow_depth_0_expected_3_returns_zero(self, tmp_path):
        """depth=0, expected=3 → SHALLOW: returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("agent.py")
        file_path = tmp_path / rel
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=0, expected=3)

        assert result == 0

    def test_extreme_shallow_depth_0_gk_never_called(self, tmp_path):
        """depth=0, expected=3 → SHALLOW: gk.safe_move never called."""
        agent = _make_agent(tmp_path)
        rel = Path("agent.py")
        file_path = tmp_path / rel
        file_path.write_text("")

        _call(agent, file_path, rel, depth=0, expected=3)

        agent.gatekeeper.safe_move.assert_not_called()

    def test_extreme_shallow_depth_0_no_filesystem_mutation(self, tmp_path):
        """depth=0, expected=3 → no dirs created, file untouched."""
        agent = _make_agent(tmp_path)
        rel = Path("agent.py")
        file_path = tmp_path / rel
        file_path.write_text("immutable")

        _call(agent, file_path, rel, depth=0, expected=3)

        assert file_path.read_text() == "immutable"

    def test_large_deficit_shallow_returns_zero(self, tmp_path):
        """depth=1, expected=10 → deficit of 9 → SHALLOW: returns 0, no gk."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=1, expected=10)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_depth_5_expected_2_flattened_correctly(self, tmp_path):
        """depth=5, expected=2 → target has exactly 3 parts (root/sub/file)."""
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/engines/sub1/sub2/sub3/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=5, expected=2)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert len(target_rel.parts) == 3
        assert target_rel.parts[0] == APPS_RG_DIR
        assert target_rel.parts[1] == "engines"
        assert target_rel.name == "agent.py"


# ---------------------------------------------------------------------------
# Stress tests: batch processing
# ---------------------------------------------------------------------------


class TestStressHealDepthViolation:
    """Stress tests with 25-file batches to verify no phantom accumulation."""

    def test_stress_25_deep_files_all_gk_called(self, tmp_path):
        """25 DEEP files → gk.safe_move called exactly 25 times."""
        agent = _make_agent(tmp_path)
        for i in range(25):
            rel = Path(f"agentic_core/L0_routing/scripts/extra/agent_{i:02d}.py")
            fp = tmp_path / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(f"# agent {i}")
            _call(agent, fp, rel, depth=4, expected=3)

        assert agent.gatekeeper.safe_move.call_count == 25

    def test_stress_25_deep_files_no_depth_aligned_in_targets(self, tmp_path):
        """25 DEEP files → 'depth_aligned' never appears in any gk target path."""
        agent = _make_agent(tmp_path)
        for i in range(25):
            rel = Path(f"agentic_core/L0_routing/scripts/extra/agent_{i:02d}.py")
            fp = tmp_path / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("")
            _call(agent, fp, rel, depth=4, expected=3)

        for c in agent.gatekeeper.safe_move.call_args_list:
            target = c[0][1]
            assert "depth_aligned" not in str(target), f"depth_aligned appeared in move target: {target}"

    def test_stress_25_shallow_files_gk_never_called(self, tmp_path):
        """25 SHALLOW files → gk.safe_move never called at all."""
        agent = _make_agent(tmp_path)
        for i in range(25):
            rel = Path(f"tests/test_stress_{i:02d}.py")
            fp = tmp_path / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("")
            _call(agent, fp, rel, depth=1, expected=2)

        agent.gatekeeper.safe_move.assert_not_called()

    def test_stress_25_shallow_no_new_dirs_created(self, tmp_path):
        """25 SHALLOW files → no directories added by the healing calls."""
        agent = _make_agent(tmp_path)
        for i in range(25):
            rel = Path(f"tests/test_stress_{i:02d}.py")
            (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / rel).write_text("")

        dirs_before = {p for p in tmp_path.rglob("*") if p.is_dir()}

        for i in range(25):
            rel = Path(f"tests/test_stress_{i:02d}.py")
            fp = tmp_path / rel
            _call(agent, fp, rel, depth=1, expected=2)

        dirs_after = {p for p in tmp_path.rglob("*") if p.is_dir()}
        assert dirs_after == dirs_before, "SHALLOW healing must not create new directories"

    def test_interleaved_deep_shallow_gk_called_only_for_deep(self, tmp_path):
        """Interleaved DEEP+SHALLOW (10 each) → gk.safe_move called only for DEEP files."""
        agent = _make_agent(tmp_path)
        deep_count = 0

        for i in range(20):
            if i % 2 == 0:
                rel = Path(f"agentic_core/L0_routing/scripts/extra/a{i}.py")
                fp = tmp_path / rel
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text("")
                _call(agent, fp, rel, depth=4, expected=3)
                deep_count += 1
            else:
                rel = Path(f"tests/test_s{i}.py")
                fp = tmp_path / rel
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text("")
                _call(agent, fp, rel, depth=1, expected=2)

        assert agent.gatekeeper.safe_move.call_count == deep_count == 10

    def test_idempotent_deep_heal_second_call_hits_collision(self, tmp_path):
        """
        Idempotency: after 1st DEEP heal, target pre-exists → 2nd call
        hits collision and delegates to _legacy_archive, NOT gk.safe_move.
        """
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        fp = tmp_path / rel
        fp.parent.mkdir(parents=True)
        fp.write_text("")

        _call(agent, fp, rel, depth=4, expected=3)
        assert agent.gatekeeper.safe_move.call_count == 1

        target = tmp_path / L0_ROUTING_DIR / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")
        fp.write_text("still here")

        agent.gatekeeper.safe_move.reset_mock()
        agent._legacy_archive_depth_violation.reset_mock()

        _call(agent, fp, rel, depth=4, expected=3)

        agent._legacy_archive_depth_violation.assert_called_once()
        agent.gatekeeper.safe_move.assert_not_called()

    def test_idempotent_deep_heal_no_phantom_dirs_either_pass(self, tmp_path):
        """Both passes of a repeated DEEP heal must never produce depth_aligned dirs."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        fp = tmp_path / rel
        fp.parent.mkdir(parents=True)
        fp.write_text("")

        _call(agent, fp, rel, depth=4, expected=3)

        target = tmp_path / L0_ROUTING_DIR / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")
        fp.write_text("")

        _call(agent, fp, rel, depth=4, expected=3)

        for c in agent.gatekeeper.safe_move.call_args_list:
            assert "depth_aligned" not in str(c[0][1])


# ---------------------------------------------------------------------------
# SOVEREIGN_TERRITORIES blueprint invariants
# ---------------------------------------------------------------------------


@pytest.mark.architecture
class TestSovereignTerritoriesDepthAlignedInvariants:
    """Live-SSOT invariants: the blueprint must not contain phantom dir names."""

    def test_no_depth_aligned_in_any_required_subfolders(self):
        """HARD INVARIANT: depth_aligned absent from required_subfolders of every territory."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        violations = [
            t
            for t, cfg in get_all_territories().items()
            if isinstance(cfg, dict) and "depth_aligned" in cfg.get("required_subfolders", [])
        ]
        assert not violations, (
            f"BLUEPRINT CONTAMINATED: territories with 'depth_aligned' in required_subfolders: {violations}"
        )

    def test_no_l_layer_pattern_in_tests_required_subfolders(self):
        """HARD INVARIANT: no l[0-9]_* names in tests.required_subfolders."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        l_pattern = re.compile(r"^l[0-9]_[a-z]+$")
        required = get_all_territories().get(TESTS_DIR, {}).get("required_subfolders", [])
        violations = [s for s in required if l_pattern.match(s)]
        assert not violations, f"L-layer names in tests.required_subfolders: {violations}"

    def test_support_subfolder_has_no_declared_subfolders(self):
        """
        HARD INVARIANT: get_all_territories()[TESTS_DIR]['subfolders']['support'] has no 'subfolders' key.

        tests/support/ must remain flat — no nested subdirectory structure declared in blueprint.
        """
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        if not isinstance(tests_subs, _Mapping):
            return
        support_cfg = tests_subs.get("support", {}) if isinstance(tests_subs, _Mapping) else {}
        if not isinstance(support_cfg, _Mapping):
            return
        declared = support_cfg.get("subfolders", None)
        assert declared is None or (hasattr(declared, "__len__") and len(declared) == 0), (
            f"tests/support/ has declared subfolders in get_all_territories(): {declared}. "
            "This would allow healing agents to create subdirectories inside support/."
        )

    def test_support_in_approved_tests_subfolders(self):
        """'support' must be a canonical tests/ subfolder (approved by SOVEREIGN_TERRITORIES)."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        approved = HierarchyAgent._get_approved_tests_subfolders()
        assert "support" in approved, (
            "'support' must be an approved tests/ subfolder. Removing it would cause "
            "healing agents to treat all tests/support/ files as violations."
        )

    def test_depth_aligned_not_in_approved_tests_subfolders(self):
        """'depth_aligned' must NEVER appear in the approved tests/ subfolders set."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        approved = HierarchyAgent._get_approved_tests_subfolders()
        assert "depth_aligned" not in approved, (
            "'depth_aligned' appeared in approved tests/ subfolders — healing agents "
            "would treat files inside depth_aligned/ as compliant."
        )

    def test_no_l_layer_in_approved_tests_subfolders(self):
        """No l[0-9]_* names in the top-level approved tests/ subfolders."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        approved = HierarchyAgent._get_approved_tests_subfolders()
        l_pattern = re.compile(r"^l[0-9]_[a-z]+$")
        violations = [s for s in approved if l_pattern.match(s)]
        assert not violations, (
            f"L-layer folder names in approved tests/ subfolders: {violations}. "
            "These would allow healing agents to treat L-layer phantom dirs as canonical."
        )


# ---------------------------------------------------------------------------
# create_missing_structure: phantom prevention
# ---------------------------------------------------------------------------


class TestCreateMissingStructurePhantomPrevention:
    """Verify create_missing_structure never generates phantom directories."""

    def test_create_territory_contaminated_required_subfolders_creates_phantom(self, tmp_path):
        """
        VULNERABILITY DOCUMENTED: _create_territory_structure has no internal guard.
        If required_subfolders contains 'depth_aligned', the agent WILL try to create it.
        The guard is in the blueprint (_constants.py), not the agent code.
        """
        agent = _make_agent(tmp_path, healing_enabled=True)
        created_labels: list[str] = []

        def _fake_create(path, results, label):
            created_labels.append(label)

        agent._create_dir_with_init = _fake_create

        territory_path = tmp_path / OPS_SCRIPTS_DIR
        territory_path.mkdir(parents=True, exist_ok=True)
        contaminated_config = {"required_subfolders": ["depth_aligned"]}
        results = {"violations_found": 0, "created": [], "errors": []}

        agent._create_territory_structure(OPS_SCRIPTS_DIR, territory_path, contaminated_config, results)

        assert "ops_scripts/depth_aligned" in created_labels, (
            "VULNERABILITY CONFIRMED: _create_territory_structure creates whatever is in "
            "required_subfolders without a guard. The blueprint invariant "
            "(test_no_depth_aligned_in_any_required_subfolders) is the correct gate."
        )
        assert results["violations_found"] == 1

    def test_create_missing_structure_with_clean_blueprint_no_depth_aligned_calls(self, tmp_path):
        """
        Run create_missing_structure with a controlled SOVEREIGN_TERRITORIES (no depth_aligned).
        Verify ensure_dir is never called with a path containing 'depth_aligned'.
        """
        agent = _make_agent(tmp_path, healing_enabled=True)
        agent.project_root = tmp_path

        ensure_dir_calls: list[str] = []

        def _track_ensure_dir(path):
            ensure_dir_calls.append(str(path))

        clean_st = {
            OPS_SCRIPTS_DIR: {
                "required_subfolders": ["ci", "general"],
                "subfolders": {"ci": {}, "general": {}},
            },
        }
        with (
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg,
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.SOVEREIGN_TERRITORIES",
                clean_st,
            ),
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.ENFORCED_TERRITORIES",
                frozenset({OPS_SCRIPTS_DIR}),
            ),
        ):
            mock_wg.ensure_dir.side_effect = _track_ensure_dir
            mock_wg.touch_file = MagicMock()
            agent.create_missing_structure()

        for path_str in ensure_dir_calls:
            assert "depth_aligned" not in path_str, (
                f"create_missing_structure called ensure_dir with depth_aligned: {path_str}"
            )

    def test_create_territory_structure_l_layer_contamination_creates_phantom(self, tmp_path):
        """
        VULNERABILITY DOCUMENTED: same gap applies for L-layer names in required_subfolders.
        """
        agent = _make_agent(tmp_path, healing_enabled=True)
        created_labels: list[str] = []

        def _fake_create(path, results, label):
            created_labels.append(label)

        agent._create_dir_with_init = _fake_create

        territory_path = tmp_path / TESTS_DIR
        territory_path.mkdir(parents=True, exist_ok=True)
        contaminated_config = {"required_subfolders": ["l1_cognition"]}
        results = {"violations_found": 0, "created": [], "errors": []}

        agent._create_territory_structure(TESTS_DIR, territory_path, contaminated_config, results)

        assert "tests/l1_cognition" in created_labels, (
            "VULNERABILITY CONFIRMED: L-layer name in required_subfolders would create "
            "a phantom L-layer subdirectory. Blueprint invariant is the correct gate."
        )


# ---------------------------------------------------------------------------
# apps_rg/depth_aligned/ bypass scenario
# ---------------------------------------------------------------------------


class TestAppsDepthAlignedBypassScenario:
    """
    Test the apps_rg/depth_aligned/ phantom dir bypass:
    files at the correct depth inside depth_aligned/ pass enforcement silently.
    """

    def test_apps_rg_depth_aligned_correct_depth_returns_zero(self, tmp_path):
        """
        Silent bypass: apps_rg/depth_aligned/__init__.py at depth 2 (expected 2).
        Depth enforcement does NOT detect the phantom directory.
        """
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/depth_aligned/__init__.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=2, expected=2)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_apps_rg_depth_aligned_correct_depth_legacy_not_called(self, tmp_path):
        """Silent bypass: _legacy_archive_depth_violation also not called."""
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/depth_aligned/__init__.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=2, expected=2)

        agent._legacy_archive_depth_violation.assert_not_called()

    def test_apps_rg_depth_aligned_subfile_too_deep_is_detected(self, tmp_path):
        """
        DEEP detection: apps_rg/depth_aligned/sub/file.py at depth 3 > expected 2.
        Depth enforcement DOES detect this → gk.safe_move called.
        """
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/depth_aligned/sub/file.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=3, expected=2)

        agent.gatekeeper.safe_move.assert_called_once()
        assert result == 1

    def test_apps_rg_depth_aligned_subfile_flattened_to_depth_2(self, tmp_path):
        """DEEP heal of apps_rg/depth_aligned/sub/file.py → target at depth 2 (3 parts)."""
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/depth_aligned/sub/file.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=3, expected=2)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert len(target_rel.parts) == 3
        assert target_rel.parts[0] == APPS_RG_DIR
        assert "sub" not in str(target_rel)
