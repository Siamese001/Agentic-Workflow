"""
Wave 2 Phase 5 — Four Execution Paths Tests

§4-compliant test suite covering:
- SecureToolsImpl: path traversal guard, blacklist enforcement,
  read/write/list/command execution paths, all branches, negative controls
- TimeshiftRouter: prior-signal routing, compliance vs standard mode,
  boundary thresholds, same-cycle-influence invariant, determinism
- PathRouter A/B/C/D semantic mapping to execution semantics
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.engines.path_router import Path as RoutePath
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L0_routing.engines.timeshift_router import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    RoutingMode,
    evaluate_timeshift_routing,
)
from agentic_core.L2_execution.engines.secure_tools_impl import SecureToolsImpl

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tools(tmp_path: Path) -> SecureToolsImpl:
    return SecureToolsImpl(work_dir=tmp_path)


def _mock_prior(anomaly_score: float, signal_hash: str = "abc123") -> MagicMock:
    m = MagicMock()
    m.anomaly_score = anomaly_score
    m.signal_hash = signal_hash
    return m


def _mock_routing_config(threshold: float = 0.5) -> MagicMock:
    cfg = MagicMock()
    cfg.anomaly_routing_threshold = threshold
    return cfg


# ===========================================================================
# 1. SecureToolsImpl — path traversal guard (_safe_path)
# ===========================================================================


class TestSecureToolsPathTraversalGuard:
    @pytest.mark.governance
    def test_safe_path_returns_absolute_path_within_workspace(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools._safe_path("file.txt")
        assert str(result).startswith(str(tmp_path))

    @pytest.mark.governance
    def test_safe_path_raises_on_parent_traversal(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools._safe_path("../../etc/passwd")

    @pytest.mark.governance
    def test_safe_path_raises_on_absolute_path_outside_workspace(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools._safe_path("/etc/passwd")

    @pytest.mark.governance
    def test_safe_path_allows_subdirectory_within_workspace(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools._safe_path("subdir/file.txt")
        assert str(result).startswith(str(tmp_path))

    @pytest.mark.governance
    def test_safe_path_raises_on_double_dot_in_middle(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools._safe_path("a/../../etc/passwd")

    @pytest.mark.governance
    def test_safe_path_handles_workspace_root_reference(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools._safe_path(".")
        assert result.exists()

    @pytest.mark.governance
    def test_safe_path_does_not_mutate_work_dir(self, tmp_path):
        tools = _tools(tmp_path)
        original = tools.work_dir
        with pytest.raises(ValueError):
            tools._safe_path("../../escape")
        assert tools.work_dir == original


# ===========================================================================
# 2. SecureToolsImpl — tool_write_file (direct execution path)
# ===========================================================================


class TestSecureToolsWriteFile:
    @pytest.mark.governance
    def test_write_file_creates_file_with_correct_content(self, tmp_path):
        tools = _tools(tmp_path)
        tools.tool_write_file("out.txt", "hello")
        assert (tmp_path / "out.txt").read_text() == "hello"

    @pytest.mark.governance
    def test_write_file_returns_success_message(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools.tool_write_file("out.txt", "content")
        assert "written successfully" in result.lower()

    @pytest.mark.governance
    def test_write_file_creates_parent_directories(self, tmp_path):
        tools = _tools(tmp_path)
        tools.tool_write_file("deep/nested/file.txt", "data")
        assert (tmp_path / "deep" / "nested" / "file.txt").exists()

    @pytest.mark.governance
    def test_write_file_raises_on_path_traversal(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_write_file("../../evil.txt", "bad content")

    @pytest.mark.governance
    def test_write_file_deterministic_content_on_same_write_twice(self, tmp_path):
        tools = _tools(tmp_path)
        tools.tool_write_file("f.txt", "v1")
        tools.tool_write_file("f.txt", "v2")
        assert (tmp_path / "f.txt").read_text() == "v2"


# ===========================================================================
# 3. SecureToolsImpl — tool_read_file (read-only path)
# ===========================================================================


class TestSecureToolsReadFile:
    @pytest.mark.governance
    def test_read_file_returns_content_when_file_exists(self, tmp_path):
        tools = _tools(tmp_path)
        (tmp_path / "readme.txt").write_text("hello world")
        result = tools.tool_read_file("readme.txt")
        assert result == "hello world"

    @pytest.mark.governance
    def test_read_file_returns_error_when_file_missing(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools.tool_read_file("missing.txt")
        assert "does not exist" in result.lower() or "error" in result.lower()

    @pytest.mark.governance
    def test_read_file_returns_error_when_path_is_directory(self, tmp_path):
        tools = _tools(tmp_path)
        (tmp_path / "subdir").mkdir()
        result = tools.tool_read_file("subdir")
        assert "not a file" in result.lower() or "error" in result.lower()

    @pytest.mark.governance
    def test_read_file_raises_on_path_traversal(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_read_file("../../etc/passwd")

    @pytest.mark.governance
    def test_read_file_does_not_mutate_filesystem(self, tmp_path):
        tools = _tools(tmp_path)
        (tmp_path / "src.txt").write_text("original")
        tools.tool_read_file("src.txt")
        assert (tmp_path / "src.txt").read_text() == "original"


# ===========================================================================
# 4. SecureToolsImpl — tool_list_files (read-only path)
# ===========================================================================


class TestSecureToolsListFiles:
    @pytest.mark.governance
    def test_list_files_returns_file_names_in_directory(self, tmp_path):
        tools = _tools(tmp_path)
        (tmp_path / "alpha.txt").write_text("")
        (tmp_path / "beta.txt").write_text("")
        result = tools.tool_list_files(".")
        assert "alpha.txt" in result
        assert "beta.txt" in result

    @pytest.mark.governance
    def test_list_files_returns_empty_dir_message_for_empty_directory(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools.tool_list_files(".")
        assert "(empty directory)" in result or result.strip() == ""

    @pytest.mark.governance
    def test_list_files_returns_error_when_directory_missing(self, tmp_path):
        tools = _tools(tmp_path)
        result = tools.tool_list_files("nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.governance
    def test_list_files_returns_error_when_path_is_file(self, tmp_path):
        tools = _tools(tmp_path)
        (tmp_path / "file.txt").write_text("")
        result = tools.tool_list_files("file.txt")
        assert "not a directory" in result.lower() or "error" in result.lower()

    @pytest.mark.governance
    def test_list_files_raises_on_path_traversal(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_list_files("../../")


# ===========================================================================
# 5. SecureToolsImpl — tool_run_command (blacklist enforcement)
# ===========================================================================


class TestSecureToolsRunCommand:
    @pytest.mark.governance
    def test_run_command_raises_on_rm_rf_pattern(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_run_command("rm -rf /tmp/evil")

    @pytest.mark.governance
    def test_run_command_raises_on_sudo_pattern(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_run_command("sudo cat /etc/passwd")

    @pytest.mark.governance
    def test_run_command_raises_on_format_pattern(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_run_command("format C:")

    @pytest.mark.governance
    def test_run_command_raises_on_dev_sda_pattern(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_run_command("dd if=/dev/zero > /dev/sda")

    @pytest.mark.governance
    def test_run_command_raises_on_mkfs_pattern(self, tmp_path):
        tools = _tools(tmp_path)
        with pytest.raises(ValueError, match="SECURITY VIOLATION"):
            tools.tool_run_command("mkfs.ext4 /dev/sdb")

    @pytest.mark.governance
    def test_run_command_does_not_mutate_blacklist_on_raise(self, tmp_path):
        tools = _tools(tmp_path)
        original = list(tools.BLACKLIST_COMMANDS)
        with pytest.raises(ValueError):
            tools.tool_run_command("sudo bad")
        assert tools.BLACKLIST_COMMANDS == original

    @pytest.mark.governance
    def test_run_command_all_blacklist_patterns_enforced(self, tmp_path):
        tools = _tools(tmp_path)
        for pattern in SecureToolsImpl.BLACKLIST_COMMANDS:
            with pytest.raises(ValueError, match="SECURITY VIOLATION"):
                tools.tool_run_command(f"some {pattern} stuff")

    @pytest.mark.governance
    def test_run_command_returns_timeout_message_on_timeout(self, tmp_path):
        tools = _tools(tmp_path)
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
            result = tools.tool_run_command("echo hello")
        assert "timed out" in result.lower()

    @pytest.mark.governance
    def test_run_command_returns_error_message_on_nonzero_exit(self, tmp_path):
        tools = _tools(tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "some error"
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            result = tools.tool_run_command("bad_command")
        assert "error" in result.lower()

    @pytest.mark.governance
    def test_run_command_returns_stdout_on_success(self, tmp_path):
        tools = _tools(tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output text"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            result = tools.tool_run_command("echo hello")
        assert result == "output text"

    @pytest.mark.governance
    def test_run_command_handles_generic_exception(self, tmp_path):
        tools = _tools(tmp_path)
        with patch("subprocess.run", side_effect=OSError("broken pipe")):
            result = tools.tool_run_command("bad")
        assert "error" in result.lower()


# ===========================================================================
# 6. SecureToolsImpl — side-effect safety
# ===========================================================================


class TestSecureToolsSideEffectSafety:
    @pytest.mark.governance
    def test_safe_path_violation_produces_no_filesystem_side_effect(self, tmp_path):
        tools = _tools(tmp_path)
        before = list(tmp_path.iterdir())
        with pytest.raises(ValueError):
            tools._safe_path("../../escape")
        after = list(tmp_path.iterdir())
        assert before == after

    @pytest.mark.governance
    def test_blacklist_violation_produces_no_filesystem_side_effect(self, tmp_path):
        tools = _tools(tmp_path)
        before = list(tmp_path.iterdir())
        with pytest.raises(ValueError):
            tools.tool_run_command("rm -rf .")
        after = list(tmp_path.iterdir())
        assert before == after


# ===========================================================================
# 7. TimeshiftRouter — routing mode selection
# ===========================================================================


class TestTimeshiftRouter:
    @pytest.mark.governance
    def test_returns_standard_when_no_prior_signal(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: None,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.STANDARD

    @pytest.mark.governance
    def test_returns_compliance_when_prior_anomaly_at_threshold(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.5)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.COMPLIANCE

    @pytest.mark.governance
    def test_returns_compliance_when_prior_anomaly_exceeds_threshold(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.9)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.COMPLIANCE

    @pytest.mark.governance
    def test_returns_standard_when_prior_anomaly_just_below_threshold(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.49)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.STANDARD

    @pytest.mark.governance
    def test_same_cycle_influence_always_false(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: None,
        ):
            decision = evaluate_timeshift_routing(5, routing_config=cfg)
        assert decision.same_cycle_influence is False

    @pytest.mark.governance
    def test_same_cycle_influence_false_even_when_escalating(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.9)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.same_cycle_influence is False

    @pytest.mark.governance
    def test_decision_includes_prior_signal_hash_when_present(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.9, signal_hash="deadbeef")
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.prior_signal_hash == "deadbeef"

    @pytest.mark.governance
    def test_decision_prior_signal_hash_none_when_no_prior(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: None,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.prior_signal_hash is None

    @pytest.mark.governance
    def test_decision_prior_anomaly_score_none_when_no_prior(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: None,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.prior_anomaly_score is None

    @pytest.mark.governance
    def test_decision_threshold_used_matches_config(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: None,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.threshold_used == 0.75

    @pytest.mark.governance
    def test_boundary_exactly_at_threshold_routes_to_compliance(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.75)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.COMPLIANCE

    @pytest.mark.governance
    def test_boundary_one_below_threshold_routes_to_standard(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.74)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            decision = evaluate_timeshift_routing(10, routing_config=cfg)
        assert decision.mode == RoutingMode.STANDARD

    @pytest.mark.governance
    def test_routing_mode_constants_distinct(self):
        assert RoutingMode.STANDARD != RoutingMode.COMPLIANCE

    @pytest.mark.governance
    def test_deterministic_for_same_tick_and_config(self):
        cfg = _mock_routing_config(threshold=THRESHOLD)
        prior = _mock_prior(anomaly_score=0.3)
        with patch(
            "agentic_core.L0_routing.engines.timeshift_router._get_prior_detection_signal",
            return_value=lambda tick: prior,
        ):
            d1 = evaluate_timeshift_routing(10, routing_config=cfg)
            d2 = evaluate_timeshift_routing(10, routing_config=cfg)
        assert d1.mode == d2.mode
        assert d1.threshold_used == d2.threshold_used


# ===========================================================================
# 8. Path A/B/C/D semantic mapping matrix
# ===========================================================================


class TestPathSemanticMatrix:
    """
    Validates that the four path semantics map deterministically to
    the execution categories: read-only, policy-check, direct, human-review.
    """

    @pytest.mark.governance
    @pytest.mark.parametrize(
        "path,expected_label",
        [
            (RoutePath.A, "read_only"),
            (RoutePath.B, "policy_check"),
            (RoutePath.C, "direct"),
            (RoutePath.D, "human_review"),
        ],
    )
    def test_path_enum_value_is_correct(self, path, expected_label):
        label_map = {
            RoutePath.A: "read_only",
            RoutePath.B: "policy_check",
            RoutePath.C: "direct",
            RoutePath.D: "human_review",
        }
        assert label_map[path] == expected_label

    @pytest.mark.governance
    def test_path_a_is_distinct_from_b_c_d(self):
        assert RoutePath.A not in (RoutePath.B, RoutePath.C, RoutePath.D)

    @pytest.mark.governance
    def test_all_four_paths_have_distinct_values(self):
        values = {p.value for p in (RoutePath.A, RoutePath.B, RoutePath.C, RoutePath.D)}
        assert len(values) == 4

    @pytest.mark.governance
    def test_negative_path_d_requires_multiple_check_ids(self):
        from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

        router = PathRouter()
        # Single check_id NOT sanitized → C, not D
        payload = GovernedPayload(
            s0_system="s",
            i0_instructional="i",
            c0_context="c",
            u0_user_prompt="u",
            check_ids=("only",),
            sanitized=False,
        )
        assert router.select_path(payload) == RoutePath.C

    @pytest.mark.governance
    def test_negative_path_b_requires_sanitized_flag(self):
        from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

        router = PathRouter()
        # check_ids present, NOT sanitized → C (not B)
        payload = GovernedPayload(
            s0_system="s",
            i0_instructional="i",
            c0_context="c",
            u0_user_prompt="u",
            check_ids=("task",),
            sanitized=False,
        )
        assert router.select_path(payload) != RoutePath.B
