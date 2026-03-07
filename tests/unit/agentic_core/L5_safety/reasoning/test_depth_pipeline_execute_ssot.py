"""
Stress tests for the execute_ssot depth enforcement pipeline:
  _legacy_archive_depth_violation, _enforce_apps_depth, _enforce_tests_depth,
  _enforce_universal_depth, and their interaction with _heal_depth_violation.

All failure points identified:
  1. _legacy_archive_depth_violation — all 3 branches (success/denied/error) + exception
  2. _enforce_apps_depth — iterates all 3 keys, SOVEREIGN_TERRITORIES missing key, sum
  3. _enforce_tests_depth — delegation to _enforce_depth_for_root
  4. _enforce_universal_depth — non-agentic_core files ignored, wrong extension filtered,
     VDS bypass, depth==expected skipped, depth!=expected healed/detected, dir skipped
  5. Full pipeline: healing_enabled interplay across all three sub-enforcers
  6. Stress: multiple violations, mixed deep/shallow, multiple roots

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent.py | _legacy_archive_depth_violation | gk.safe_archive success | returns 1, logs ARCHIVED | test_legacy_archive_success_returns_one |
| HierarchyAgent.py | _legacy_archive_depth_violation | gk approval_status==DENIED | returns 0, logs SKIPPED | test_legacy_archive_denied_returns_zero |
| HierarchyAgent.py | _legacy_archive_depth_violation | gk success=False, not DENIED | returns 0, logs ERROR | test_legacy_archive_error_returns_zero |
| HierarchyAgent.py | _legacy_archive_depth_violation | exception raised | caught, returns 0 | test_legacy_archive_exception_returns_zero |
| HierarchyAgent.py | _legacy_archive_depth_violation | reason string format | contains label+depth+expected | test_legacy_archive_reason_format |
| HierarchyAgent.py | _legacy_archive_depth_violation | gk.safe_archive called with file_path+agent_name | args correct | test_legacy_archive_gk_args |
| HierarchyAgent.py | _enforce_apps_depth | iterates apps_rg + apps_lic + apps_shared | all 3 called | test_enforce_apps_all_three_keys_iterated |
| HierarchyAgent.py | _enforce_apps_depth | key missing from SOVEREIGN_TERRITORIES | skipped silently | test_enforce_apps_missing_key_skipped |
| HierarchyAgent.py | _enforce_apps_depth | sums counts from all 3 roots | sum correct | test_enforce_apps_sums_all_root_counts |
| HierarchyAgent.py | _enforce_apps_depth | root_check lambda correct per key | only matching root counted | test_enforce_apps_root_check_lambda |
| HierarchyAgent.py | _enforce_tests_depth | delegates to _enforce_depth_for_root with 'tests' | called once | test_enforce_tests_delegates_correctly |
| HierarchyAgent.py | _enforce_universal_depth | non-agentic_core file skipped | not counted | test_universal_non_agentic_core_skipped |
| HierarchyAgent.py | _enforce_universal_depth | wrong extension skipped | not counted | test_universal_wrong_extension_skipped |
| HierarchyAgent.py | _enforce_universal_depth | is_dir skipped | not counted | test_universal_dir_skipped |
| HierarchyAgent.py | _enforce_universal_depth | depth==expected skipped | not counted | test_universal_correct_depth_no_violation |
| HierarchyAgent.py | _enforce_universal_depth | VDS bypass at depth>=2 | skipped | test_universal_vds_bypass_depth2 |
| HierarchyAgent.py | _enforce_universal_depth | VDS bypass NOT at depth==1 | counted | test_universal_vds_no_bypass_depth1 |
| HierarchyAgent.py | _enforce_universal_depth | depth!=expected detection-only | returns violation count | test_universal_detection_only_returns_violations |
| HierarchyAgent.py | _enforce_universal_depth | depth!=expected healing | _heal called, archived incremented | test_universal_healing_calls_heal |
| HierarchyAgent.py | _enforce_universal_depth | healing_enabled=True → returns archived | archived propagated | test_universal_healing_returns_archived_not_violations |
| HierarchyAgent.py | _enforce_universal_depth | DEEP: _heal returns 1 | archived=1 | test_universal_deep_heal_returns_one |
| HierarchyAgent.py | _enforce_universal_depth | DEEP: _heal returns 0 (gk fail) | archived=0, violation still found | test_universal_heal_zero_still_detected |
| HierarchyAgent.py | _enforce_universal_depth | multiple data files, mixed valid/invalid | only violations counted | test_universal_mixed_files_count |
| HierarchyAgent.py | _heal_depth_violation | full collision→legacy→success chain | end-to-end returns 1 | test_full_chain_collision_legacy_success |
| HierarchyAgent.py | _heal_depth_violation | full DEEP→gk→success chain | end-to-end returns 1 | test_full_chain_deep_gk_success |
| HierarchyAgent.py | _heal_depth_violation | full DEEP→gk→fail chain | end-to-end returns 0 | test_full_chain_deep_gk_fail |
| HierarchyAgent.py | enforce_depth_rules | violations_found logged when >0 | Logger.info mentions count | test_pipeline_violations_found_logged |
| HierarchyAgent.py | enforce_depth_rules | archived total logged when healing+violations | info includes all three counts | test_pipeline_archived_total_logged |
| HierarchyAgent.py | enforce_depth_rules | stress: 10 deep violations → archived=10 | sum=10 | test_stress_10_deep_violations_all_archived |
| HierarchyAgent.py | enforce_depth_rules | stress: mixed roots 5+5+5 violations | sum=15 | test_stress_mixed_roots_15_violations |
"""
from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, call, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent(project_root: Path, healing_enabled: bool = True):
    from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

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
    return agent


def _write(tmp_path: Path, rel_str: str, content: str = "") -> Path:
    p = tmp_path / rel_str
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# _legacy_archive_depth_violation
# ---------------------------------------------------------------------------

class TestLegacyArchiveDepthViolation:
    def test_legacy_archive_success_returns_one(self, tmp_path):
        """safe_archive success → returns 1."""
        agent = _make_agent(tmp_path)
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        result = agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        assert result == 1

    def test_legacy_archive_success_logs_archived(self, tmp_path):
        """safe_archive success → Logger.info contains 'ARCHIVED'."""
        agent = _make_agent(tmp_path)
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        info_msgs = [str(c) for c in mock_log.info.call_args_list]
        assert any("ARCHIVED" in m for m in info_msgs)

    def test_legacy_archive_denied_returns_zero(self, tmp_path):
        """safe_archive approval_status==DENIED → returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_archive.return_value = MagicMock(
            success=False, approval_status="DENIED", error=None
        )
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        result = agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        assert result == 0

    def test_legacy_archive_denied_logs_skipped(self, tmp_path):
        """DENIED → Logger.info contains 'SKIPPED'."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_archive.return_value = MagicMock(
            success=False, approval_status="DENIED", error=None
        )
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        info_msgs = [str(c) for c in mock_log.info.call_args_list]
        assert any("SKIPPED" in m for m in info_msgs)

    def test_legacy_archive_error_returns_zero(self, tmp_path):
        """safe_archive fails (not DENIED) → returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_archive.return_value = MagicMock(
            success=False, approval_status="FAILED", error="disk full"
        )
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        result = agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        assert result == 0

    def test_legacy_archive_error_logs_error(self, tmp_path):
        """safe_archive fails (not DENIED) → Logger.error with error message."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_archive.return_value = MagicMock(
            success=False, approval_status="FAILED", error="disk full"
        )
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        error_msgs = [str(c) for c in mock_log.error.call_args_list]
        assert any("Archive failed" in m for m in error_msgs)

    def test_legacy_archive_exception_returns_zero(self, tmp_path):
        """Exception from safe_archive → caught, returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_archive.side_effect = RuntimeError("network failure")
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        result = agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        assert result == 0

    def test_legacy_archive_reason_format(self, tmp_path):
        """Reason string passed to safe_archive includes label, depth, expected."""
        agent = _make_agent(tmp_path)
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        reason_arg = agent.gatekeeper.safe_archive.call_args[0][2]
        assert "COLLISION" in reason_arg
        assert "4" in reason_arg
        assert "3" in reason_arg

    def test_legacy_archive_gk_args(self, tmp_path):
        """safe_archive called with (file_path, agent_name, reason)."""
        agent = _make_agent(tmp_path)
        file_path = _write(tmp_path, "agentic_core/L0_routing/scripts/extra/f.py")
        rel = file_path.relative_to(tmp_path)

        agent._legacy_archive_depth_violation(file_path, rel, 4, 3, "collision", "COLLISION")

        call_args = agent.gatekeeper.safe_archive.call_args[0]
        assert call_args[0] == file_path
        assert call_args[1] == "HierarchyAgent"


# ---------------------------------------------------------------------------
# _enforce_apps_depth
# ---------------------------------------------------------------------------

_FAKE_TERRITORIES = MappingProxyType({
    "apps_rg": {"depth": 2},
    "apps_lic": {"depth": 2},
    "apps_shared": {"depth": 2},
    "tests": {"depth": 2},
    "agentic_core": {"depth": 3},
})


class TestEnforceAppsDepth:
    def test_enforce_apps_all_three_keys_iterated(self, tmp_path):
        """_enforce_depth_for_root is called for each of apps_rg, apps_lic, apps_shared."""
        agent = _make_agent(tmp_path)
        agent._enforce_depth_for_root = MagicMock(return_value=0)

        with patch(
            "agentic_core.L5_safety.reasoning.HierarchyAgent.SOVEREIGN_TERRITORIES",
            _FAKE_TERRITORIES,
        ):
            agent._enforce_apps_depth()

        assert agent._enforce_depth_for_root.call_count == 3
        root_keys = [c[0][0] for c in agent._enforce_depth_for_root.call_args_list]
        assert set(root_keys) == {"apps_rg", "apps_lic", "apps_shared"}

    def test_enforce_apps_missing_key_skipped(self, tmp_path):
        """Key missing from SOVEREIGN_TERRITORIES → _enforce_depth_for_root not called for it."""
        agent = _make_agent(tmp_path)
        agent._enforce_depth_for_root = MagicMock(return_value=0)

        partial = MappingProxyType({"apps_rg": {"depth": 2}, "apps_lic": {"depth": 2}})
        with patch(
            "agentic_core.L5_safety.reasoning.HierarchyAgent.SOVEREIGN_TERRITORIES",
            partial,
        ):
            agent._enforce_apps_depth()

        assert agent._enforce_depth_for_root.call_count == 2
        root_keys = [c[0][0] for c in agent._enforce_depth_for_root.call_args_list]
        assert "apps_shared" not in root_keys

    def test_enforce_apps_sums_all_root_counts(self, tmp_path):
        """Total = sum of violations across all three apps roots."""
        agent = _make_agent(tmp_path)
        agent._enforce_depth_for_root = MagicMock(side_effect=[3, 5, 2])

        with patch(
            "agentic_core.L5_safety.reasoning.HierarchyAgent.SOVEREIGN_TERRITORIES",
            _FAKE_TERRITORIES,
        ):
            total = agent._enforce_apps_depth()

        assert total == 10

    def test_enforce_apps_root_check_lambda_isolates_per_key(self, tmp_path):
        """Lambda passed to _enforce_depth_for_root matches only the correct root key."""
        agent = _make_agent(tmp_path)
        captured_checks = []
        agent._enforce_depth_for_root = MagicMock(
            side_effect=lambda rk, rc, *a, **kw: captured_checks.append(rc) or 0
        )

        with patch(
            "agentic_core.L5_safety.reasoning.HierarchyAgent.SOVEREIGN_TERRITORIES",
            _FAKE_TERRITORIES,
        ):
            agent._enforce_apps_depth()

        assert len(captured_checks) == 3
        # Each check must accept its own key and reject others
        for i, (expected_key, check) in enumerate(
            zip(["apps_rg", "apps_lic", "apps_shared"], captured_checks)
        ):
            assert check(expected_key) is True
            for other_key in {"apps_rg", "apps_lic", "apps_shared"} - {expected_key}:
                assert check(other_key) is False


# ---------------------------------------------------------------------------
# _enforce_tests_depth
# ---------------------------------------------------------------------------

class TestEnforceTestsDepth:
    def test_enforce_tests_delegates_correctly(self, tmp_path):
        """_enforce_tests_depth calls _enforce_depth_for_root with root_key='tests'."""
        agent = _make_agent(tmp_path)
        agent._enforce_depth_for_root = MagicMock(return_value=7)

        result = agent._enforce_tests_depth()

        agent._enforce_depth_for_root.assert_called_once()
        assert agent._enforce_depth_for_root.call_args[0][0] == "tests"
        assert result == 7

    def test_enforce_tests_root_check_accepts_tests_only(self, tmp_path):
        """root_check lambda accepts 'tests' and rejects everything else."""
        agent = _make_agent(tmp_path)
        captured_check = []
        agent._enforce_depth_for_root = MagicMock(
            side_effect=lambda rk, rc, *a: captured_check.append(rc) or 0
        )

        agent._enforce_tests_depth()

        check = captured_check[0]
        assert check("tests") is True
        assert check("agentic_core") is False
        assert check("apps_rg") is False


# ---------------------------------------------------------------------------
# _enforce_universal_depth
# ---------------------------------------------------------------------------

def _run_universal(agent, data_files, vds=None, territories=None):
    """Run _enforce_universal_depth with mocked discovery."""
    vds_patch = vds if vds is not None else frozenset()
    territories_patch = territories or MappingProxyType({"agentic_core": {"depth": 3}})

    def _fake_get_data(root, extensions=None):
        return iter(data_files)

    with patch(
        "agentic_core.L0_routing.utils.ssot_discovery_util.get_data_files",
        _fake_get_data,
    ), patch(
        "agentic_core.L5_safety.reasoning.HierarchyAgent.VARIABLE_DEPTH_SUBFOLDERS",
        vds_patch,
    ), patch(
        "agentic_core.L5_safety.reasoning.HierarchyAgent.SOVEREIGN_TERRITORIES",
        territories_patch,
    ):
        return agent._enforce_universal_depth()


class TestEnforceUniversalDepth:
    def test_universal_non_agentic_core_skipped(self, tmp_path):
        """Files not under agentic_core/ are completely ignored."""
        agent = _make_agent(tmp_path)
        fp = _write(tmp_path, "tests/config/schema.json")
        result = _run_universal(agent, [fp])
        assert result == 0

    def test_universal_wrong_extension_skipped(self, tmp_path):
        """Files with extension not in target_exts are skipped even if under agentic_core/."""
        agent = _make_agent(tmp_path)
        fp = _write(tmp_path, "agentic_core/L0_routing/scripts/agent.py")
        result = _run_universal(agent, [fp])
        assert result == 0

    def test_universal_dir_skipped(self, tmp_path):
        """Directories are skipped."""
        agent = _make_agent(tmp_path)
        d = tmp_path / "agentic_core" / "L0_routing" / "scripts"
        d.mkdir(parents=True)
        result = _run_universal(agent, [d])
        assert result == 0

    def test_universal_correct_depth_no_violation(self, tmp_path):
        """agentic_core/L0_routing/scripts/schema.json at depth=3 → no violation."""
        agent = _make_agent(tmp_path)
        fp = _write(tmp_path, "agentic_core/L0_routing/scripts/schema.json")
        result = _run_universal(agent, [fp])
        assert result == 0

    def test_universal_vds_bypass_depth2(self, tmp_path):
        """VDS subfolder at depth>=2 under agentic_core → skipped."""
        agent = _make_agent(tmp_path)
        fp = _write(tmp_path, "agentic_core/config/settings.json")  # depth=2, config in VDS
        result = _run_universal(agent, [fp], vds=frozenset({"config"}))
        assert result == 0

    def test_universal_vds_no_bypass_depth1(self, tmp_path):
        """VDS subfolder at depth<2 → NOT skipped (depth=1 fails the >=2 check)."""
        agent = _make_agent(tmp_path, healing_enabled=False)
        fp = _write(tmp_path, "agentic_core/config.json")  # depth=1, L1 subfolder is filename itself
        result = _run_universal(agent, [fp], vds=frozenset({"config"}))
        # depth=1 != expected=3 → violation
        assert result == 1

    def test_universal_detection_only_returns_violations(self, tmp_path):
        """healing_enabled=False → returns violation count."""
        agent = _make_agent(tmp_path, healing_enabled=False)
        fp = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")  # depth=4
        result = _run_universal(agent, [fp])
        assert result == 1

    def test_universal_healing_calls_heal(self, tmp_path):
        """healing_enabled=True + violation → _heal_depth_violation called."""
        agent = _make_agent(tmp_path, healing_enabled=True)
        agent._heal_depth_violation = MagicMock(return_value=1)
        fp = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")  # depth=4
        _run_universal(agent, [fp])
        agent._heal_depth_violation.assert_called_once()

    def test_universal_healing_returns_archived_not_violations(self, tmp_path):
        """healing_enabled=True → return value comes from archived count, not violations."""
        agent = _make_agent(tmp_path, healing_enabled=True)
        agent._heal_depth_violation = MagicMock(return_value=1)
        fp = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")  # depth=4
        result = _run_universal(agent, [fp])
        assert result == 1  # archived (from _heal returning 1), not violations

    def test_universal_deep_heal_returns_one(self, tmp_path):
        """DEEP data file → _heal returns 1 → archived=1."""
        agent = _make_agent(tmp_path, healing_enabled=True)
        agent._heal_depth_violation = MagicMock(return_value=1)
        fp = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")  # depth=4, expected=3
        result = _run_universal(agent, [fp])
        assert result == 1

    def test_universal_heal_zero_still_detected(self, tmp_path):
        """Violation detected (violation count=1) but heal returns 0 → archived=0."""
        agent = _make_agent(tmp_path, healing_enabled=True)
        agent._heal_depth_violation = MagicMock(return_value=0)
        fp = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")  # depth=4
        result = _run_universal(agent, [fp])
        assert result == 0  # archived=0 because heal returned 0

    def test_universal_mixed_files_only_violations_counted(self, tmp_path):
        """Mixed: 1 correct-depth + 1 violation → detection-only returns 1."""
        agent = _make_agent(tmp_path, healing_enabled=False)
        good = _write(tmp_path, "agentic_core/L0_routing/scripts/schema.json")  # depth=3
        bad = _write(tmp_path, "agentic_core/L0_routing/extra/sub/schema.json")   # depth=4
        result = _run_universal(agent, [good, bad])
        assert result == 1


# ---------------------------------------------------------------------------
# Full end-to-end chain tests
# ---------------------------------------------------------------------------

class TestFullChain:
    def test_full_chain_collision_legacy_success(self, tmp_path):
        """DEEP + collision → legacy archive → gk.safe_archive → returns 1."""
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, str(rel))
        # Pre-create collision target
        target = tmp_path / "agentic_core" / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent._wg"):
            result = agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        assert result == 1
        agent.gatekeeper.safe_archive.assert_called_once()
        agent.gatekeeper.safe_move.assert_not_called()

    def test_full_chain_deep_gk_success(self, tmp_path):
        """DEEP, no collision → gk.safe_move → returns 1."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, str(rel))

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent._wg"):
            result = agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        assert result == 1
        agent.gatekeeper.safe_move.assert_called_once()

    def test_full_chain_deep_gk_fail(self, tmp_path):
        """DEEP, gk.safe_move fails → returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.return_value = MagicMock(success=False, error="denied")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = _write(tmp_path, str(rel))

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent._wg"):
            result = agent._heal_depth_violation(file_path, rel, depth=4, expected=3)

        assert result == 0


# ---------------------------------------------------------------------------
# enforce_depth_rules pipeline logging + stress
# ---------------------------------------------------------------------------

class TestEnforceRulesPipelineLogging:
    def _make_dispatch_agent(self, project_root: Path, healing: bool = False):
        agent = _make_agent(project_root, healing_enabled=healing)
        agent._enforce_apps_depth = MagicMock(return_value=0)
        agent._enforce_tests_depth = MagicMock(return_value=0)
        agent._enforce_universal_depth = MagicMock(return_value=0)
        return agent

    def test_pipeline_violations_found_logged(self, tmp_path):
        """violations_found > 0 → Logger.info logs the violation count."""
        agent = self._make_dispatch_agent(tmp_path)
        agent._enforce_apps_depth.return_value = 3
        agent._enforce_tests_depth.return_value = 2

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            agent.enforce_depth_rules()

        info_msgs = [str(c) for c in mock_log.info.call_args_list]
        assert any("5" in m and "depth violations" in m for m in info_msgs)

    def test_pipeline_archived_total_logged_when_healing(self, tmp_path):
        """healing_enabled=True + violations → Logger.info logs archived totals."""
        agent = self._make_dispatch_agent(tmp_path, healing=True)
        agent._enforce_apps_depth.return_value = 2
        agent._enforce_tests_depth.return_value = 3
        agent._enforce_universal_depth.return_value = 1

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            agent.enforce_depth_rules()

        info_msgs = [str(c) for c in mock_log.info.call_args_list]
        assert any("Archived" in m and "6" in m for m in info_msgs)

    def test_stress_10_deep_violations_all_archived(self, tmp_path):
        """Stress: 10 violations all healed → archived=10."""
        agent = self._make_dispatch_agent(tmp_path, healing=True)
        agent._enforce_apps_depth.return_value = 10

        result = agent.enforce_depth_rules()

        assert result["apps_archived"] == 10
        assert result["violations_found"] == 10

    def test_stress_mixed_roots_15_violations(self, tmp_path):
        """Stress: 5 apps + 5 tests + 5 universal = 15 violations."""
        agent = self._make_dispatch_agent(tmp_path, healing=False)
        agent._enforce_apps_depth.return_value = 5
        agent._enforce_tests_depth.return_value = 5
        agent._enforce_universal_depth.return_value = 5

        result = agent.enforce_depth_rules()

        assert result["violations_found"] == 15
        # healing disabled → archived keys all 0
        assert result["apps_archived"] == 0
        assert result["tests_archived"] == 0
        assert result["universal_archived"] == 0
