"""
Exhaustive tests for HierarchyAgent._heal_depth_violation,
_enforce_depth_for_root, and enforce_depth_rules target-territory dispatch.

Covers every branch, boundary, and side-effect surface per §1 Constitutional Rules.

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent.py | _heal_depth_violation | DEEP: _legacy returns 1 (collision+archive ok) | propagates 1 | test_deep_collision_legacy_returns_one_propagated |
| HierarchyAgent.py | _heal_depth_violation | DEEP: _legacy returns 0 (collision+archive denied) | propagates 0 | test_deep_collision_legacy_returns_zero_propagated |
| HierarchyAgent.py | _heal_depth_violation | DEEP: _wg.ensure_dir called with target.parent | ensure_dir arg correct | test_deep_ensure_dir_called_with_correct_parent |
| HierarchyAgent.py | _heal_depth_violation | DEEP: expected=1, single-level target | parts[:1]+(name,) | test_deep_expected_one_flattens_to_root_level |
| HierarchyAgent.py | _heal_depth_violation | DEEP: expected=2, depth=4 | parts[:2]+(name,) | test_deep_expected_two_drops_two_levels |
| HierarchyAgent.py | _heal_depth_violation | DEEP: expected=4, depth=5 | parts[:4]+(name,) | test_deep_expected_four_drops_one_level |
| HierarchyAgent.py | _heal_depth_violation | DEEP: gk.safe_move receives (file_path, target, agent_name, reason) | args correct | test_deep_gk_called_with_correct_args |
| HierarchyAgent.py | _heal_depth_violation | DEEP: source file content preserved (gk mock does not move) | content unchanged | test_deep_source_content_unchanged_after_gk_call |
| HierarchyAgent.py | _heal_depth_violation | DEEP: success logs HEALED with rel and target | Logger.info called | test_deep_success_logs_healed |
| HierarchyAgent.py | _heal_depth_violation | DEEP: gk failure → source file not mutated | file still exists | test_deep_gk_failure_source_still_exists |
| HierarchyAgent.py | _heal_depth_violation | DEEP: gk failure → _legacy NOT called | _legacy not called | test_deep_gk_failure_does_not_call_legacy |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW: depth==expected-1 boundary | 0, no gk | test_shallow_boundary_minus_one |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW: depth==0 | 0, no gk | test_shallow_depth_zero |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW: depth==1, expected==10 | 0, no gk | test_shallow_large_deficit |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW: logs 'Manual intervention' | Logger.error | test_shallow_logs_manual_intervention |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW: _legacy never called | no _legacy | test_shallow_never_calls_legacy |
| HierarchyAgent.py | _heal_depth_violation | depth==expected → else branch, 0 | 0, no gk | test_depth_equal_hits_else_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | TypeError in gk.safe_move | caught, returns 0 | test_type_error_in_gk_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | PermissionError from ensure_dir | caught, returns 0 | test_permission_error_from_ensure_dir |
| HierarchyAgent.py | _heal_depth_violation | exception path: _legacy NOT called | no _legacy | test_exception_does_not_call_legacy |
| HierarchyAgent.py | _enforce_depth_for_root | VARIABLE_DEPTH_SUBFOLDERS subfolder at depth>=2 skipped | not counted | test_variable_depth_subfolder_at_depth2_skipped |
| HierarchyAgent.py | _enforce_depth_for_root | VARIABLE_DEPTH_SUBFOLDERS subfolder at depth==1 NOT skipped | counted | test_variable_depth_subfolder_at_depth1_counted |
| HierarchyAgent.py | _enforce_depth_for_root | healing_enabled=False → returns violation count | violations not archived | test_enforce_depth_healing_disabled_returns_violations |
| HierarchyAgent.py | _enforce_depth_for_root | healing_enabled=True → returns archived count | archived propagated | test_enforce_depth_healing_enabled_returns_archived |
| HierarchyAgent.py | _enforce_depth_for_root | file with is_dir()==True skipped | not counted | test_enforce_depth_dirs_skipped |
| HierarchyAgent.py | _enforce_depth_for_root | root_check filters out wrong-root files | other roots not counted | test_enforce_depth_root_check_filters |
| HierarchyAgent.py | _enforce_depth_for_root | correct-depth file → no violation | not counted | test_enforce_depth_correct_depth_no_violation |
| HierarchyAgent.py | enforce_depth_rules | target_territory=None → all three run | apps+tests+universal | test_enforce_rules_no_territory_all_run |
| HierarchyAgent.py | enforce_depth_rules | target_territory='apps_rg' → apps only | tests/universal skipped | test_enforce_rules_apps_territory_skips_tests_universal |
| HierarchyAgent.py | enforce_depth_rules | target_territory='tests' → tests only | apps/universal skipped | test_enforce_rules_tests_territory_skips_apps_universal |
| HierarchyAgent.py | enforce_depth_rules | target_territory='agentic_core' → universal only | apps/tests skipped | test_enforce_rules_core_territory_skips_apps_tests |
| HierarchyAgent.py | enforce_depth_rules | violations_found accumulates across sub-counts | sum correct | test_enforce_rules_violations_accumulated |
| HierarchyAgent.py | enforce_depth_rules | healing_enabled=False → archived keys stay 0 | no mutation | test_enforce_rules_detection_only_archived_zero |
| HierarchyAgent.py | enforce_depth_rules | violations_found==0 → no summary log | Logger.info count | test_enforce_rules_no_log_when_no_violations |
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, patch

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_agent(project_root: Path, healing_enabled: bool = True):
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = project_root
    agent.agent_name = "HierarchyAgent"
    agent.healing_enabled = healing_enabled
    gk = MagicMock()
    gk.safe_move.return_value = MagicMock(success=True, error=None)
    gk.safe_archive.return_value = MagicMock(
        success=True, destination_path="archive/x.py", approval_status="APPROVED"
    )
    agent.gatekeeper = gk
    agent._legacy_archive_depth_violation = MagicMock(return_value=0)
    return agent


def _call(agent, file_path, rel, depth, expected):
    with patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg:
        mock_wg.ensure_dir = MagicMock()
        return agent._heal_depth_violation(file_path, rel, depth, expected), mock_wg


def _call_clean(agent, file_path, rel, depth, expected):
    result, _ = _call(agent, file_path, rel, depth, expected)
    return result


def _write(tmp_path, rel_str, content=""):
    p = tmp_path / rel_str
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# _heal_depth_violation — DEEP: collision delegation
# ---------------------------------------------------------------------------


class TestDeepCollisionDelegation:
    def test_deep_collision_legacy_returns_one_propagated(self, tmp_path):
        """Collision + legacy archive succeeds → _heal_depth_violation returns 1."""
        agent = _make_agent(tmp_path)
        agent._legacy_archive_depth_violation.return_value = 1
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)
        # Pre-create collision target
        target = tmp_path / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        result = _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert result == 1
        agent._legacy_archive_depth_violation.assert_called_once()

    def test_deep_collision_legacy_returns_zero_propagated(self, tmp_path):
        """Collision + legacy archive denied → _heal_depth_violation returns 0."""
        agent = _make_agent(tmp_path)
        agent._legacy_archive_depth_violation.return_value = 0
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)
        target = tmp_path / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        result = _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert result == 0

    def test_deep_collision_gk_not_called(self, tmp_path):
        """Collision → gatekeeper.safe_move is NEVER called (legacy handles it)."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)
        target = tmp_path / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        agent.gatekeeper.safe_move.assert_not_called()

    def test_deep_collision_legacy_called_with_collision_args(self, tmp_path):
        """Collision → _legacy_archive called with 'collision' subdir and 'COLLISION' label."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)
        target = tmp_path / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        args = agent._legacy_archive_depth_violation.call_args[0]
        assert "collision" in args
        assert "COLLISION" in args


# ---------------------------------------------------------------------------
# _heal_depth_violation — DEEP: gk arguments + ensure_dir
# ---------------------------------------------------------------------------


class TestDeepGkArgs:
    def test_deep_ensure_dir_called_with_correct_parent(self, tmp_path):
        """_wg.ensure_dir must receive target_path.parent (not source parent)."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        _, mock_wg = _call(agent, file_path, rel, depth=4, expected=3)

        expected_parent = tmp_path / AGENTIC_CORE_DIR / "L0_routing" / "scripts"
        mock_wg.ensure_dir.assert_called_once_with(expected_parent)

    def test_deep_gk_called_with_correct_args(self, tmp_path):
        """gk.safe_move called with (file_path, target_path, agent_name, reason_str)."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        call_args = agent.gatekeeper.safe_move.call_args[0]
        assert call_args[0] == file_path
        assert call_args[2] == "HierarchyAgent"
        assert "FLATTENED" in call_args[3] or "Depth healing" in call_args[3]

    def test_deep_expected_one_flattens_to_root_level(self, tmp_path):
        """expected=1, depth=3 → target is root/agent.py (parts[:1]+(name,))."""
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/sub/agent.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=2, expected=1)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert target_rel == Path("apps_rg/agent.py")

    def test_deep_expected_two_drops_two_levels(self, tmp_path):
        """expected=2, depth=4 → parts[:2]+(name,) drops two intermediate dirs."""
        agent = _make_agent(tmp_path)
        rel = Path("apps_rg/engines/sub1/sub2/my_engine.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=4, expected=2)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert target_rel == Path("apps_rg/engines/my_engine.py")

    def test_deep_expected_four_drops_one_level(self, tmp_path):
        """expected=4, depth=5 → parts[:4]+(name,) drops exactly one level."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/utils/extra/agent.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=5, expected=4)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        target_rel = target.relative_to(tmp_path)
        assert target_rel == Path("agentic_core/L0_routing/scripts/utils/agent.py")

    def test_deep_source_content_unchanged_after_gk_call(self, tmp_path):
        """gk mock doesn't move file → source still has original content."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel, content="# original")

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert file_path.read_text() == "# original"

    def test_deep_success_logs_healed(self, tmp_path):
        """DEEP success → Logger.info called with 'HEALED' and 'FLATTENED'."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        with (
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log,
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg"),
        ):
            agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        info_calls = [str(c) for c in mock_log.info.call_args_list]
        assert any("HEALED" in c and "FLATTENED" in c for c in info_calls)


# ---------------------------------------------------------------------------
# _heal_depth_violation — DEEP: gk failure side-effects
# ---------------------------------------------------------------------------


class TestDeepGkFailure:
    def test_deep_gk_failure_source_still_exists(self, tmp_path):
        """gk failure → source file not deleted."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.return_value = MagicMock(success=False, error="denied")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel, content="# src")

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert file_path.exists()

    def test_deep_gk_failure_does_not_call_legacy(self, tmp_path):
        """gk failure path does NOT fall through to _legacy_archive."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.return_value = MagicMock(success=False, error="denied")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        agent._legacy_archive_depth_violation.assert_not_called()

    def test_deep_gk_failure_returns_zero(self, tmp_path):
        """gk failure → returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.return_value = MagicMock(success=False, error="nope")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert result == 0


# ---------------------------------------------------------------------------
# _heal_depth_violation — SHALLOW boundaries
# ---------------------------------------------------------------------------


class TestShallowBoundaries:
    def test_shallow_boundary_minus_one(self, tmp_path):
        """depth == expected-1 → SHALLOW, returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=2, expected=3)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_shallow_depth_zero(self, tmp_path):
        """depth=0, expected=3 → SHALLOW, returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("agent.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=0, expected=3)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_shallow_large_deficit(self, tmp_path):
        """depth=1, expected=10 → SHALLOW, always returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=1, expected=10)

        assert result == 0

    def test_shallow_logs_manual_intervention(self, tmp_path):
        """SHALLOW → Logger.error contains 'Manual intervention'."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = _write(tmp_path, rel)

        with (
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log,
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg"),
        ):
            agent._heal_depth_violation(file_path, rel, depth=1, expected=3)

        error_msgs = [str(c) for c in mock_log.error.call_args_list]
        assert any("Manual intervention" in m for m in error_msgs)

    def test_shallow_never_calls_legacy(self, tmp_path):
        """SHALLOW → _legacy_archive_depth_violation never called."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=1, expected=3)

        agent._legacy_archive_depth_violation.assert_not_called()


# ---------------------------------------------------------------------------
# _heal_depth_violation — depth==expected edge + exception variants
# ---------------------------------------------------------------------------


class TestEdgeAndExceptions:
    def test_depth_equal_hits_else_returns_zero(self, tmp_path):
        """depth==expected → hits else branch (SHALLOW), returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=3, expected=3)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_type_error_in_gk_returns_zero(self, tmp_path):
        """TypeError in gk.safe_move → caught, returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = TypeError("bad type")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        result = _call_clean(agent, file_path, rel, depth=4, expected=3)

        assert result == 0

    def test_permission_error_from_ensure_dir(self, tmp_path):
        """PermissionError from _wg.ensure_dir → caught, returns 0."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        with patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg:
            mock_wg.ensure_dir.side_effect = PermissionError("no access")
            result = agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        assert result == 0

    def test_exception_does_not_call_legacy(self, tmp_path):
        """Exception during DEEP heal → _legacy never called."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = OSError("disk full")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        _call_clean(agent, file_path, rel, depth=4, expected=3)

        agent._legacy_archive_depth_violation.assert_not_called()

    def test_exception_logs_error_with_rel(self, tmp_path):
        """Exception → Logger.error mentions the file rel path."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = RuntimeError("boom")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, rel)

        with (
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log,
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg"),
        ):
            agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        error_msgs = [str(c) for c in mock_log.error.call_args_list]
        assert any("agent.py" in m or "extra" in m for m in error_msgs)


# ---------------------------------------------------------------------------
# _enforce_depth_for_root — VARIABLE_DEPTH_SUBFOLDERS bypass
# ---------------------------------------------------------------------------

_FAKE_VDS = frozenset({"engines", "utils", "config"})


def _make_enforce_agent(project_root: Path, healing_enabled: bool = True):
    agent = _make_agent(project_root, healing_enabled)
    return agent


def _make_py_file(project_root: Path, rel_str: str) -> Path:
    p = project_root / rel_str
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("")
    return p


class TestEnforceDepthForRoot:
    """Tests for _enforce_depth_for_root using mocked ssot_discovery."""

    def _patch_discovery(self, py_files, data_files=None):
        """Context manager: patch get_python_files and get_data_files."""
        data_files = data_files or []
        return patch.multiple(
            "agentic_core.L5_safety.reasoning.hierarchy_healer",
            **{},
        )

    def _run(self, agent, root_key, root_check, py_files, data_files=None, vds=None):
        """Run _enforce_depth_for_root with mocked discovery."""
        data_files = data_files or []
        vds_patch = vds if vds is not None else _FAKE_VDS

        def _fake_get_python(root):
            return iter(py_files)

        def _fake_get_data(root, extensions=None):
            return iter(data_files)

        with (
            patch(
                "agentic_core.L0_routing.utils.ssot_discovery_util.get_python_files",
                _fake_get_python,
            ),
            patch(
                "agentic_core.L0_routing.utils.ssot_discovery_util.get_data_files",
                _fake_get_data,
            ),
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.VARIABLE_DEPTH_SUBFOLDERS",
                vds_patch,
            ),
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.SOVEREIGN_TERRITORIES",
                MappingProxyType(
                    {APPS_RG_DIR: {"depth": 2}, TESTS_DIR: {"depth": 2}, AGENTIC_CORE_DIR: {"depth": 3}}
                ),
            ),
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg"),
        ):
            return agent._enforce_depth_for_root(root_key, root_check, "subdir", "LABEL")

    def test_variable_depth_subfolder_at_depth2_skipped(self, tmp_path):
        """
        File in VARIABLE_DEPTH_SUBFOLDERS at depth>=2 → skipped, not counted.
        apps_rg/engines/my_engine.py: depth=2, subfolder='engines' in VDS, depth>=2 → skip.
        """
        agent = _make_enforce_agent(tmp_path)
        fp = _make_py_file(tmp_path, "apps_rg/engines/my_engine.py")

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fp],
            vds=frozenset({"engines"}),
        )

        assert count == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_variable_depth_subfolder_at_depth1_counted(self, tmp_path):
        """
        File in VARIABLE_DEPTH_SUBFOLDERS at depth==1 → NOT skipped (depth<2 check fails).
        apps_rg/engines.py: depth=1, subfolder='engines' in VDS but depth<2 → violation counted.
        Use healing_enabled=False so the return value is the violation count (not archived count).
        SHALLOW heal returns 0, so detection-only mode is required to observe the count.
        """
        agent = _make_enforce_agent(tmp_path, healing_enabled=False)
        fp = _make_py_file(tmp_path, "apps_rg/engines.py")

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fp],
            vds=frozenset({"engines"}),
        )

        assert count >= 1

    def test_enforce_depth_healing_disabled_returns_violations(self, tmp_path):
        """
        healing_enabled=False → returns violation count (not archived).
        """
        agent = _make_enforce_agent(tmp_path, healing_enabled=False)
        fp = _make_py_file(tmp_path, "apps_rg/extra/sub/agent.py")  # depth=3, expected=2

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fp],
            vds=frozenset(),
        )

        assert count == 1
        agent.gatekeeper.safe_move.assert_not_called()

    def test_enforce_depth_healing_enabled_returns_archived(self, tmp_path):
        """
        healing_enabled=True + _heal returns 1 → _enforce_depth_for_root returns 1.
        """
        agent = _make_enforce_agent(tmp_path, healing_enabled=True)
        fp = _make_py_file(tmp_path, "apps_rg/extra/sub/agent.py")  # depth=3, expected=2
        agent._heal_depth_violation = MagicMock(return_value=1)

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fp],
            vds=frozenset(),
        )

        assert count == 1
        agent._heal_depth_violation.assert_called_once()

    def test_enforce_depth_dirs_skipped(self, tmp_path):
        """Directories (is_dir()==True) are skipped, not counted as violations."""
        agent = _make_enforce_agent(tmp_path)
        # Create a directory, not a file
        fake_dir = tmp_path / APPS_RG_DIR / "sub"
        fake_dir.mkdir(parents=True)

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fake_dir],
            vds=frozenset(),
        )

        assert count == 0

    def test_enforce_depth_root_check_filters_wrong_root(self, tmp_path):
        """Files whose root doesn't match root_check are silently filtered."""
        agent = _make_enforce_agent(tmp_path)
        fp = _make_py_file(tmp_path, "tests/unit/test_something.py")  # wrong root

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,  # tests != apps_rg
            py_files=[fp],
            vds=frozenset(),
        )

        assert count == 0

    def test_enforce_depth_correct_depth_no_violation(self, tmp_path):
        """File at exactly expected depth → no violation."""
        agent = _make_enforce_agent(tmp_path)
        fp = _make_py_file(tmp_path, "apps_rg/engines/my_engine.py")  # depth=2, expected=2

        count = self._run(
            agent,
            root_key=APPS_RG_DIR,
            root_check=lambda r: r == APPS_RG_DIR,
            py_files=[fp],
            vds=frozenset(),  # no VDS bypass
        )

        assert count == 0


# ---------------------------------------------------------------------------
# enforce_depth_rules — target_territory dispatch
# ---------------------------------------------------------------------------


class TestEnforceDepthRulesDispatch:
    """Tests for enforce_depth_rules target_territory scoping."""

    def _make_dispatch_agent(self, project_root: Path, healing: bool = False):
        agent = _make_enforce_agent(project_root, healing_enabled=healing)
        agent._enforce_apps_depth = MagicMock(return_value=0)
        agent._enforce_tests_depth = MagicMock(return_value=0)
        agent._enforce_universal_depth = MagicMock(return_value=0)
        return agent

    def test_enforce_rules_no_territory_all_three_run(self, tmp_path):
        """target_territory=None → all three sub-enforcers called."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=None)
        agent._enforce_apps_depth.assert_called_once()
        agent._enforce_tests_depth.assert_called_once()
        agent._enforce_universal_depth.assert_called_once()

    def test_enforce_rules_apps_territory_skips_tests_universal(self, tmp_path):
        """target_territory='apps_rg' → apps runs; tests and universal skipped."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=APPS_RG_DIR)
        agent._enforce_apps_depth.assert_called_once()
        agent._enforce_tests_depth.assert_not_called()
        agent._enforce_universal_depth.assert_not_called()

    def test_enforce_rules_tests_territory_skips_apps_universal(self, tmp_path):
        """target_territory='tests' → tests runs; apps and universal skipped."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=TESTS_DIR)
        agent._enforce_apps_depth.assert_not_called()
        agent._enforce_tests_depth.assert_called_once()
        agent._enforce_universal_depth.assert_not_called()

    def test_enforce_rules_core_territory_skips_apps_tests(self, tmp_path):
        """target_territory='agentic_core' → universal runs; apps and tests skipped."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=AGENTIC_CORE_DIR)
        agent._enforce_apps_depth.assert_not_called()
        agent._enforce_tests_depth.assert_not_called()
        agent._enforce_universal_depth.assert_called_once()

    def test_enforce_rules_violations_accumulated(self, tmp_path):
        """violations_found sums all three sub-counts."""
        agent = self._make_dispatch_agent(tmp_path)
        agent._enforce_apps_depth.return_value = 3
        agent._enforce_tests_depth.return_value = 5
        agent._enforce_universal_depth.return_value = 2

        result = agent.enforce_depth_rules(target_territory=None)

        assert result["violations_found"] == 10

    def test_enforce_rules_detection_only_archived_keys_stay_zero(self, tmp_path):
        """healing_enabled=False → archived keys remain 0 even with violations."""
        agent = self._make_dispatch_agent(tmp_path, healing=False)
        agent._enforce_apps_depth.return_value = 2
        agent._enforce_tests_depth.return_value = 3
        agent._enforce_universal_depth.return_value = 1

        result = agent.enforce_depth_rules(target_territory=None)

        assert result["apps_archived"] == 0
        assert result["tests_archived"] == 0
        assert result["universal_archived"] == 0
        assert result["violations_found"] == 6

    def test_enforce_rules_healing_enabled_archived_set(self, tmp_path):
        """healing_enabled=True → archived keys reflect sub-counts."""
        agent = self._make_dispatch_agent(tmp_path, healing=True)
        agent._enforce_apps_depth.return_value = 2
        agent._enforce_tests_depth.return_value = 3
        agent._enforce_universal_depth.return_value = 1

        result = agent.enforce_depth_rules(target_territory=None)

        assert result["apps_archived"] == 2
        assert result["tests_archived"] == 3
        assert result["universal_archived"] == 1

    def test_enforce_rules_result_dict_has_all_keys(self, tmp_path):
        """Return dict always has all 5 expected keys."""
        agent = self._make_dispatch_agent(tmp_path)
        result = agent.enforce_depth_rules()

        assert "apps_archived" in result
        assert "tests_archived" in result
        assert "universal_archived" in result
        assert "violations_found" in result
        assert "errors" in result

    def test_enforce_rules_no_log_when_no_violations(self, tmp_path):
        """violations_found==0 → no summary info log about depth violations."""
        agent = self._make_dispatch_agent(tmp_path)
        with patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log:
            agent.enforce_depth_rules()

        info_msgs = [str(c) for c in mock_log.info.call_args_list]
        assert not any("Found" in m and "depth violations" in m for m in info_msgs)

    def test_enforce_rules_apps_lic_prefix_runs_apps(self, tmp_path):
        """target_territory='apps_lic' starts with 'apps_' → apps enforced."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=APPS_LIC_DIR)
        agent._enforce_apps_depth.assert_called_once()
        agent._enforce_tests_depth.assert_not_called()
        agent._enforce_universal_depth.assert_not_called()
        assert True  # no-exception contract

    def test_enforce_rules_apps_shared_prefix_runs_apps(self, tmp_path):
        """target_territory='apps_shared' starts with 'apps_' → apps enforced."""
        agent = self._make_dispatch_agent(tmp_path)
        agent.enforce_depth_rules(target_territory=APPS_SHARED_DIR)
        agent._enforce_apps_depth.assert_called_once()
        agent._enforce_universal_depth.assert_not_called()
        assert True  # no-exception contract
