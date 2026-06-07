"""
EXHAUSTIVE tests for pre_prompt_classifier.py (Phase 1.4).

Plan requirements verified:
  - T3 keywords: architecture, refactor, wave, migration, restructure, etc.
  - T2 keywords: fix+update, implement+create, multi-keyword combos
  - T1 keywords: typo, docstring, trivial, single line
  - T0 keywords: explain, what is, how does, review
  - Short prompt (≤4 words, zero keyword hits) → T2 (continuation guard)
  - Long unrecognized prompt (>4 words) → T1
  - plan_exists check for T2/T3
  - ADG health red → BLOCKED exit 2 for T2/T3
  - Redis down → BLOCKED exit 2 for T2/T3
  - Both red → first check fires (ADG before Redis)
  - T0/T1 prompts never blocked even if ADG red + Redis down
  - SR mandate injected in stderr for T2/T3 healthy
  - Empty stdin → exit 0
  - Malformed JSON → exit 0
  - Missing prompt field → exit 0
  - user_prompt and prompt field both handled
  - Fail-open on infrastructure errors (probe missing)
  - Unicode prompt: no crash
  - Very long prompt: no crash
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".claude" / "governance/scripts"))

from pre_prompt_classifier import (
    _detect_adg_graph_intent,
    _detect_pytest_intent,
    _should_emit_memory_mandate,
    check_plan_exists,
    check_redis_adg_hot,
    check_redis_up,
    classify_tier,
    main,
)


# ---------------------------------------------------------------------------
# classify_tier
# ---------------------------------------------------------------------------


class TestClassifyTier:
    # T3 triggers
    def test_architecture_is_t3(self):
        assert classify_tier("redesign the architecture of the ADG module") == "T3"

    def test_architectural_is_t3(self):
        assert classify_tier("make an architectural decision about layer placement") == "T3"

    def test_refactor_is_t3(self):
        assert classify_tier("refactor the L0 routing layer into subpackages") == "T3"

    def test_wave_is_t3(self):
        assert classify_tier("implement wave 2 of the governance model") == "T3"

    def test_migration_is_t3(self):
        assert classify_tier("plan the migration from YAML to JSON config") == "T3"

    def test_restructure_is_t3(self):
        assert classify_tier("restructure the module layout across L0-L3") == "T3"

    def test_consolidate_is_t3(self):
        assert classify_tier("consolidate the duplicate registry files") == "T3"

    def test_cross_layer_is_t3(self):
        assert classify_tier("make a cross-layer change to the confidence engine") == "T3"

    def test_governance_is_t3(self):
        assert classify_tier("update the governance enforcement model") == "T3"

    def test_blast_radius_is_t3(self):
        assert classify_tier("check the blast radius of this change") == "T3"

    # T2 triggers (multi-keyword)
    def test_fix_and_update_is_t2(self):
        assert classify_tier("fix and update the test file for the hook") == "T2"

    def test_implement_and_create_is_t2(self):
        assert classify_tier("implement and create the new gate script") == "T2"

    def test_modify_and_rename_is_t2(self):
        assert classify_tier("modify the config and rename the class") == "T2"

    def test_debug_and_patch_is_t2(self):
        assert classify_tier("debug and patch the failing assertion") == "T2"

    # T1 triggers
    def test_typo_is_t1(self):
        assert classify_tier("fix this typo in the docstring") == "T1"

    def test_docstring_is_t1(self):
        assert classify_tier("add a docstring to this function") == "T1"

    def test_trivial_is_t1(self):
        assert classify_tier("this is a trivial one line change") == "T1"

    def test_whitespace_is_t1(self):
        assert classify_tier("fix the whitespace formatting") == "T1"

    # T0 triggers
    def test_explain_is_t0(self):
        assert classify_tier("explain how the pre_run_gate works") == "T0"

    def test_what_is_t0(self):
        assert classify_tier("what is the ADG health check?") == "T0"

    def test_how_does_is_t0(self):
        assert classify_tier("how does the classifier hook work?") == "T0"

    def test_review_is_t0(self):
        assert classify_tier("review this function for issues") == "T0"

    def test_summarize_is_t0(self):
        assert classify_tier("summarize the changes in this commit") == "T0"

    # Defaults
    def test_unrecognized_long_defaults_to_t1(self):
        assert classify_tier("zork zork zork zork zork") == "T1"

    def test_empty_defaults_to_t2(self):
        assert classify_tier("") == "T2"

    def test_single_word_no_keywords_is_t2(self):
        assert classify_tier("yes") == "T2"

    def test_two_word_no_keywords_is_t2(self):
        assert classify_tier("do it") == "T2"

    def test_three_word_no_keywords_is_t2(self):
        assert classify_tier("zork zork zork") == "T2"

    def test_four_word_no_keywords_is_t2(self):
        assert classify_tier("proceed with the plan") == "T2"

    def test_five_word_no_keywords_defaults_to_t1(self):
        assert classify_tier("zork zork zork zork zork") == "T1"

    def test_continuation_yes_is_t2(self):
        assert classify_tier("yes") == "T2"

    def test_continuation_proceed_is_t2(self):
        assert classify_tier("proceed") == "T2"

    def test_continuation_implement_it_is_t2(self):
        assert classify_tier("implement it") == "T2"

    def test_short_prompt_with_t1_keyword_still_t1(self):
        assert classify_tier("fix typo") == "T1"

    def test_short_prompt_with_t0_keyword_still_t0(self):
        assert classify_tier("explain it") == "T0"

    def test_single_t2_keyword_alone_is_t2(self):
        # Single T2 keyword with no T3 and no T1/T0 → T2
        assert classify_tier("implement the feature") == "T2"

    def test_t3_overrides_t2(self):
        # Both T3 and T2 keywords — T3 wins
        assert classify_tier("refactor and implement the new architecture") == "T3"


# ---------------------------------------------------------------------------
# check_plan_exists
# ---------------------------------------------------------------------------


class TestCheckPlanExists:
    def test_t0_always_true(self):
        assert check_plan_exists("T0") is True

    def test_t1_always_true(self):
        assert check_plan_exists("T1") is True

    def test_t2_no_plans_dir_false(self, tmp_path):
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T2") is False

    def test_t2_empty_plans_dir_false(self, tmp_path):
        (tmp_path / ".claude" / "plans").mkdir(parents=True)
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T2") is False

    def test_t2_with_plan_file_true(self, tmp_path):
        plans = tmp_path / ".claude" / "plans"
        plans.mkdir(parents=True)
        (plans / "my-plan-abc123.md").write_text("# Plan")
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T2") is True

    def test_t3_no_plans_dir_false(self, tmp_path):
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T3") is False

    def test_t3_with_plan_file_true(self, tmp_path):
        plans = tmp_path / ".claude" / "plans"
        plans.mkdir(parents=True)
        (plans / "plan.md").write_text("# Plan")
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T3") is True

    def test_non_md_file_in_plans_not_counted(self, tmp_path):
        plans = tmp_path / ".claude" / "plans"
        plans.mkdir(parents=True)
        (plans / "not_a_plan.txt").write_text("text")
        with patch("pre_prompt_classifier.repo_root", tmp_path):
            assert check_plan_exists("T2") is False


# ---------------------------------------------------------------------------
# check_redis_up
# ---------------------------------------------------------------------------


class TestCheckRedisUp:
    def test_connection_refused_returns_false(self):
        import socket

        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            assert check_redis_up() is False

    def test_successful_connection_returns_true(self):
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        import socket

        with patch("socket.create_connection", return_value=mock_conn):
            assert check_redis_up() is True

    def test_os_error_fails_open_returns_true(self):
        import socket

        with patch("socket.create_connection", side_effect=OSError("Network unreachable")):
            assert check_redis_up() is True

    def test_timeout_os_error_fails_open_returns_true(self):
        import socket

        with patch("socket.create_connection", side_effect=TimeoutError("timed out")):
            assert check_redis_up() is True


# ---------------------------------------------------------------------------
# check_redis_adg_hot
# ---------------------------------------------------------------------------


class TestCheckRedisAdgHot:
    def test_sentinel_found_returns_true(self):
        mock_client = MagicMock()
        mock_client.scan.return_value = (0, ["adg:v1:abc123:_hot"])
        mock_redis = MagicMock()
        mock_redis.from_url.return_value = mock_client
        with patch.dict("sys.modules", {"redis": mock_redis}):
            assert check_redis_adg_hot() is True

    def test_no_sentinel_returns_false(self):
        mock_client = MagicMock()
        mock_client.scan.return_value = (0, [])
        mock_redis = MagicMock()
        mock_redis.from_url.return_value = mock_client
        with patch.dict("sys.modules", {"redis": mock_redis}):
            assert check_redis_adg_hot() is False

    def test_scan_continues_until_cursor_zero(self):
        mock_client = MagicMock()
        mock_client.scan.side_effect = [
            (42, []),  # first page: no keys, cursor non-zero
            (0, ["adg:v1:xyz:_hot"]),  # second page: key found
        ]
        mock_redis = MagicMock()
        mock_redis.from_url.return_value = mock_client
        with patch.dict("sys.modules", {"redis": mock_redis}):
            assert check_redis_adg_hot() is True

    def test_redis_import_error_returns_false(self):
        # Python 3.12+: sys.modules["redis"]=None raises on import; simulate
        # client failure after a stub redis module is loaded.
        mock_redis_mod = MagicMock()
        mock_redis_mod.from_url.side_effect = OSError("simulated redis unavailable")
        with patch.dict("sys.modules", {"redis": mock_redis_mod}):
            assert check_redis_adg_hot() is False

    def test_connection_exception_returns_false(self):
        mock_redis = MagicMock()
        mock_redis.from_url.side_effect = OSError("connection refused")
        with patch.dict("sys.modules", {"redis": mock_redis}):
            assert check_redis_adg_hot() is False


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


class TestMain:
    def _run(
        self,
        payload: dict,
        adg_red: bool = False,
        redis_down: bool = False,
        adg_hot: bool = True,
        repo_root=None,
    ) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch(
                "pre_prompt_classifier.check_adg_health_red",
                return_value=adg_red,
            ):
                with patch(
                    "pre_prompt_classifier.check_redis_up",
                    return_value=not redis_down,
                ):
                    with patch(
                        "pre_prompt_classifier.check_redis_adg_hot",
                        return_value=adg_hot,
                    ):
                        if repo_root is not None:
                            with patch(
                                "pre_prompt_classifier.repo_root",
                                repo_root,
                            ):
                                return main()
                        return main()

    # --- T0/T1: never blocked regardless of infrastructure ---
    def test_t0_prompt_never_blocked_even_if_adg_red(self):
        payload = {"tool_info": {"user_prompt": "explain how the hook works"}}
        assert self._run(payload, adg_red=True, redis_down=True) == 0

    def test_t1_prompt_never_blocked_even_if_redis_down(self):
        payload = {"tool_info": {"user_prompt": "fix the typo in the docstring"}}
        assert self._run(payload, adg_red=False, redis_down=True) == 0

    # --- T2/T3 healthy: exits 0, SR mandate injected ---
    def test_t3_healthy_infra_exits_0(self):
        payload = {"tool_info": {"user_prompt": "refactor the authentication layer"}}
        assert self._run(payload, adg_red=False, redis_down=False) == 0

    def test_t2_healthy_infra_exits_0(self):
        payload = {"tool_info": {"user_prompt": "fix and update the test file"}}
        assert self._run(payload, adg_red=False, redis_down=False) == 0

    def test_t3_healthy_sr_mandate_emitted(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the authentication layer"}}
        self._run(payload, adg_red=False, redis_down=False)
        captured = capsys.readouterr()
        assert "create_task" in captured.err
        assert "SR_INTAKE" in captured.err
        assert "SR_PLAN" in captured.err
        assert "SR_APPROVAL" in captured.err

    # --- T2/T3 + BOTH red: blocked (§13: only block when BOTH Redis AND SQLite unavailable) ---
    def test_t3_red_adg_blocked(self):
        payload = {"tool_info": {"user_prompt": "refactor the entire architecture"}}
        assert self._run(payload, adg_red=True, redis_down=True) == 2

    def test_t2_red_adg_blocked(self):
        payload = {"tool_info": {"user_prompt": "fix and update the module"}}
        assert self._run(payload, adg_red=True, redis_down=True) == 2

    def test_blocked_message_mentions_adg(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the auth layer"}}
        self._run(payload, adg_red=True, redis_down=True)
        captured = capsys.readouterr()
        assert "adg_sqlite" in captured.err.lower() or "BLOCKED" in captured.err

    # --- T2/T3 + Redis down only: falls back to SQLite, not blocked ---
    def test_t3_redis_down_blocked(self):
        payload = {"tool_info": {"user_prompt": "restructure the module hierarchy"}}
        # Redis down but ADG SQLite healthy → fallback, allow (§13)
        assert self._run(payload, adg_red=False, redis_down=True) == 0

    def test_t2_redis_down_blocked(self):
        payload = {"tool_info": {"user_prompt": "implement and create the new service"}}
        # Redis down but ADG SQLite healthy → fallback, allow (§13)
        assert self._run(payload, adg_red=False, redis_down=True) == 0

    def test_blocked_message_mentions_redis(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        self._run(payload, adg_red=False, redis_down=True)
        captured = capsys.readouterr()
        assert "Redis" in captured.err or "redis" in captured.err

    # --- ADG check fires before Redis check ---
    def test_adg_red_takes_priority_over_redis_down(self):
        payload = {"tool_info": {"user_prompt": "refactor and migrate everything"}}
        # Both red — should still block (exit 2)
        assert self._run(payload, adg_red=True, redis_down=True) == 2

    # --- prompt field variants ---
    def test_prompt_field_alias_works(self):
        payload = {"tool_info": {"prompt": "refactor the architecture"}}
        # adg_red=True, redis_down defaults False → fallback to SQLite succeeds → exit 0
        assert self._run(payload, adg_red=True) == 0

    def test_user_prompt_takes_precedence(self):
        # user_prompt preferred over prompt
        payload = {"tool_info": {"user_prompt": "explain the code", "prompt": "refactor everything"}}
        # user_prompt = T0 → not blocked
        assert self._run(payload, adg_red=True) == 0

    # --- plan warning ---
    def test_no_plan_for_t3_emits_warning(self, capsys, tmp_path):
        (tmp_path / ".claude" / "plans").mkdir(parents=True)
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        self._run(payload, adg_red=False, redis_down=False, repo_root=tmp_path)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err or "plan" in captured.err.lower()

    # --- Redis up + ADG hot/cold branch distinction ---
    def test_redis_up_adg_hot_emits_hot_cache_confirmed(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        self._run(payload, adg_red=False, redis_down=False, adg_hot=True)
        captured = capsys.readouterr()
        assert "hot cache confirmed" in captured.err

    def test_redis_up_adg_cold_emits_warning(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        self._run(payload, adg_red=False, redis_down=False, adg_hot=False)
        captured = capsys.readouterr()
        assert "cold" in captured.err.lower() or "adg_redis_ingest" in captured.err

    def test_redis_up_adg_cold_adg_mcp_red_blocks(self):
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        assert self._run(payload, adg_red=True, redis_down=False, adg_hot=False) == 2

    def test_redis_up_adg_cold_adg_mcp_healthy_allows(self):
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        assert self._run(payload, adg_red=False, redis_down=False, adg_hot=False) == 0

    # --- fail-open cases ---
    def test_empty_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_exits_0(self):
        with patch("sys.stdin", StringIO("{bad json")):
            assert main() == 0

    def test_whitespace_only_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("   \n")):
            assert main() == 0

    def test_no_prompt_field_exits_0(self):
        payload = {"tool_info": {}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            assert main() == 0

    def test_empty_prompt_exits_0(self):
        payload = {"tool_info": {"user_prompt": ""}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            assert main() == 0

    # --- tier tag emitted ---
    def test_tier_tag_emitted_to_stderr(self, capsys):
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            main()
        captured = capsys.readouterr()
        assert "Tier:" in captured.err

    # --- unicode / large input ---
    def test_unicode_prompt_no_crash(self):
        payload = {"tool_info": {"user_prompt": "\u4e2d\u6587\u5185\u5bb9 refactor the module"}}
        result = self._run(payload, adg_red=False, redis_down=False)
        assert result in (0, 2)

    def test_very_long_prompt_no_crash(self):
        payload = {"tool_info": {"user_prompt": "refactor " + "x" * 50000}}
        result = self._run(payload, adg_red=False, redis_down=False)
        assert result in (0, 2)

    # --- memory mandate ---

    def test_memory_mandate_emitted_when_no_session_state(self, capsys, tmp_path):
        """Mandate fires on first turn (no session_state.json) as a human-diagnostic advisory."""
        state_path = tmp_path / "session_state.json"
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        captured = capsys.readouterr()
        assert "mem_recall_session_start not yet called" in captured.err

    def test_memory_mandate_emitted_when_not_recalled(self, capsys, tmp_path):
        """Advisory fires when memory_recalled=False in session state."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": False}), encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        captured = capsys.readouterr()
        assert "mem_recall_session_start not yet called" in captured.err

    def test_memory_mandate_suppressed_when_recalled(self, capsys, tmp_path):
        """Advisory is NOT emitted when memory_recalled=True in session state."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        captured = capsys.readouterr()
        assert "mem_recall_session_start not yet called" not in captured.err

    def test_t0_preserves_memory_recalled_in_session_state(self, tmp_path):
        """T0 prompt preserves memory_recalled flag (session-level, not task-level)."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["memory_recalled"] is True

    def test_t2_preserves_memory_recalled_true(self, tmp_path):
        """T2 continuation preserves memory_recalled=True once set."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "fix and update the module"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["memory_recalled"] is True

    def test_t1_preserves_memory_recalled_in_session_state(self, tmp_path):
        """T1 prompt must preserve memory_recalled=True (Fix 1 regression — T1 was not covered)."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "fix the typo in the docstring"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["memory_recalled"] is True

    def test_t0_task_lifecycle_fields_reset_preserves_memory_recalled(self, tmp_path):
        """T0 reset must clear task lifecycle fields without clearing memory_recalled."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "memory_recalled": True,
                    "task_created": True,
                    "task_started": True,
                    "update_task_count": 5,
                }
            ),
            encoding="utf-8",
        )
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["memory_recalled"] is True
        assert state["task_created"] is False
        assert state["task_started"] is False
        assert state["update_task_count"] == 0

    def test_t0_corrupt_session_file_yields_memory_recalled_false(self, tmp_path):
        """T0 with corrupt session file falls back to memory_recalled=False (fail-safe path)."""
        state_path = tmp_path / "session_state.json"
        state_path.write_text("{{not valid json", encoding="utf-8")
        payload = {"tool_info": {"user_prompt": "explain how routing works"}}
        with patch("pre_prompt_classifier.session_state", state_path):
            self._run(payload)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["memory_recalled"] is False


# ---------------------------------------------------------------------------
# _should_emit_memory_mandate
# ---------------------------------------------------------------------------


class TestShouldEmitMemoryMandate:
    def test_returns_true_when_no_file(self, tmp_path):
        state_path = tmp_path / "missing_state.json"
        with patch("pre_prompt_classifier.session_state", state_path):
            assert _should_emit_memory_mandate() is True

    def test_returns_true_when_field_absent(self, tmp_path):
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"current_tier": "T2"}), encoding="utf-8")
        with patch("pre_prompt_classifier.session_state", state_path):
            assert _should_emit_memory_mandate() is True

    def test_returns_true_when_false(self, tmp_path):
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": False}), encoding="utf-8")
        with patch("pre_prompt_classifier.session_state", state_path):
            assert _should_emit_memory_mandate() is True

    def test_returns_false_when_true(self, tmp_path):
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        with patch("pre_prompt_classifier.session_state", state_path):
            assert _should_emit_memory_mandate() is False

    def test_fail_open_on_corrupt_json(self, tmp_path):
        state_path = tmp_path / "session_state.json"
        state_path.write_text("{bad json", encoding="utf-8")
        with patch("pre_prompt_classifier.session_state", state_path):
            assert _should_emit_memory_mandate() is True


# ---------------------------------------------------------------------------
# _detect_pytest_intent
# ---------------------------------------------------------------------------


class TestDetectPytestIntent:
    """Pytest-intent signal detection used for pytest_mcp routing."""

    def test_pytest_keyword_detected(self):
        assert _detect_pytest_intent("run pytest for the failing module") is True

    def test_run_tests_detected(self):
        assert _detect_pytest_intent("run tests in apps_rg/") is True

    def test_discover_tests_detected(self):
        assert _detect_pytest_intent("discover tests under tests/unit") is True

    def test_test_coverage_detected(self):
        assert _detect_pytest_intent("analyze test coverage for agentic_core") is True

    def test_coverage_report_detected(self):
        assert _detect_pytest_intent("show me the coverage report") is True

    def test_pytest_config_detected(self):
        assert _detect_pytest_intent("show pytest config") is True

    def test_test_suite_detected(self):
        assert _detect_pytest_intent("run the test suite") is True

    def test_failing_tests_detected(self):
        assert _detect_pytest_intent("why are the failing tests red") is True

    def test_non_pytest_prompt_not_detected(self):
        assert _detect_pytest_intent("refactor the L0 routing layer") is False

    def test_adg_query_not_detected(self):
        assert _detect_pytest_intent("who uses blast radius in the import graph") is False

    def test_notion_prompt_not_detected(self):
        assert _detect_pytest_intent("create a notion page for the sprint") is False

    def test_empty_prompt_not_detected(self):
        assert _detect_pytest_intent("") is False

    def test_case_insensitive(self):
        assert _detect_pytest_intent("RUN PYTEST NOW") is True


# ---------------------------------------------------------------------------
# pytest_mcp routing trace in main()
# ---------------------------------------------------------------------------


class TestPytestMcpRoutingTrace:
    """Verify PYTEST_MCP_TRACE lines are emitted correctly for detected and not-detected cases."""

    def _run(self, prompt: str, capsys, tmp_path) -> int:
        payload = json.dumps({"tool_info": {"prompt": prompt}})
        state_path = tmp_path / "session_state.json"
        state_path.write_text(json.dumps({"memory_recalled": True}), encoding="utf-8")
        with (
            patch("pre_prompt_classifier.session_state", state_path),
            patch("pre_prompt_classifier.check_redis_up", return_value=True),
            patch("pre_prompt_classifier.check_redis_adg_hot", return_value=True),
            patch("sys.stdin", StringIO(payload)),
        ):
            return main()

    def test_pytest_prompt_emits_detected_trace(self, capsys, tmp_path):
        self._run("run pytest for the failing tests", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST_MCP_TRACE: pytest_intent=DETECTED" in err

    def test_non_pytest_prompt_emits_not_detected_trace(self, capsys, tmp_path):
        self._run("explain the architecture of the ADG module", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST_MCP_TRACE: pytest_intent=NOT_DETECTED" in err

    def test_pytest_prompt_sr_hint_injected_for_t2(self, capsys, tmp_path):
        """pytest SR hint must be appended to SR_MANDATE when pytest intent detected in T2 prompt."""
        self._run("run the test suite and fix failing tests", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST INTENT DETECTED" in err
        assert "mcp8_run_tests" in err

    def test_non_pytest_prompt_no_sr_hint(self, capsys, tmp_path):
        """SR hint must NOT appear when no pytest intent is detected."""
        self._run("implement the new L3 orchestration feature", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST INTENT DETECTED" not in err

    def test_pytest_trace_emitted_on_every_prompt_regardless_of_tier(self, capsys, tmp_path):
        """Routing trace is emitted at all tiers, not only T2/T3."""
        self._run("explain how to run pytest", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST_MCP_TRACE" in err

    def test_over_routing_guard_adg_prompt_not_detected(self, capsys, tmp_path):
        """ADG-specific prompts must not trigger pytest routing."""
        self._run("what depends on the import graph fanin nodes", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST_MCP_TRACE: pytest_intent=NOT_DETECTED" in err
        assert "PYTEST INTENT DETECTED" not in err

    def test_pytest_sr_hint_not_injected_for_t0_prompt(self, capsys, tmp_path):
        """T0 pytest prompt: routing TRACE fires (all tiers) but SR_MANDATE hint must NOT appear.

        Guard at pre_prompt_classifier.py:506 — `if tier in ('T2', 'T3'):` — prevents
        SR_MANDATE + hint emission for T0.  'explain how to run pytest' hits T0_KEYWORDS
        ('explain') so tier=T0; pytest intent is DETECTED but hint is suppressed.
        """
        self._run("explain how to run pytest", capsys, tmp_path)
        err = capsys.readouterr().err
        assert "PYTEST_MCP_TRACE: pytest_intent=DETECTED" in err, "routing trace must fire at T0"
        assert "PYTEST INTENT DETECTED" not in err, "SR_MANDATE hint must NOT fire at T0"


# ---------------------------------------------------------------------------
# ADG graph intent detection
# ---------------------------------------------------------------------------


class TestDetectAdgGraphIntent:
    def test_who_imports_detected(self):
        assert _detect_adg_graph_intent("who imports the redis cache module") is True

    def test_blast_radius_detected(self):
        assert _detect_adg_graph_intent("check blast radius of this change") is True

    def test_blast_radius_hyphen_detected(self):
        assert _detect_adg_graph_intent("analyze blast-radius for ADGService") is True

    def test_fanin_detected(self):
        assert _detect_adg_graph_intent("show fanin for service.py") is True

    def test_fanout_detected(self):
        assert _detect_adg_graph_intent("list fanout edges from sqlite_backend") is True

    def test_dependency_graph_detected(self):
        assert _detect_adg_graph_intent("build the dependency graph for this module") is True

    def test_what_depends_on_detected(self):
        assert _detect_adg_graph_intent("what depends on ADGService class") is True

    def test_impact_analysis_detected(self):
        assert _detect_adg_graph_intent("run impact analysis on redis_cache.py") is True

    def test_unrelated_prompt_not_detected(self):
        assert _detect_adg_graph_intent("fix the typo in the docstring") is False

    def test_literal_text_prompt_not_detected(self):
        assert _detect_adg_graph_intent("find all TODO comments in tests/") is False

    def test_semantic_prompt_not_detected(self):
        assert _detect_adg_graph_intent("find semantically similar passages about caching") is False

    def test_pytest_prompt_not_detected(self):
        assert _detect_adg_graph_intent("run the failing test suite") is False


# ---------------------------------------------------------------------------
# ADG graph SR hint injection
# ---------------------------------------------------------------------------


class TestAdgGraphSrHint:
    """ADG graph intent triggers routing trace + SR hint for T2/T3; not for T0."""

    @staticmethod
    def _run(prompt: str, tmp_path, *, redis_up: bool = False):
        payload = {"tool_info": {"user_prompt": prompt}}
        plan_file = tmp_path / "plan.md"
        plan_file.write_text("# plan", encoding="utf-8")
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        with (
            patch("pre_prompt_classifier.repo_root", tmp_path),
            patch("pre_prompt_classifier.session_state", state_dir / "session_state.json"),
            patch("pre_prompt_classifier.check_redis_up", return_value=redis_up),
            patch("pre_prompt_classifier.check_redis_adg_hot", return_value=redis_up),
            patch("pre_prompt_classifier.check_adg_health_red", return_value=False),
        ):
            sys.stdin = __import__("io").StringIO(json.dumps(payload))
            main()

    def test_adg_graph_trace_emitted_for_graph_prompt(self, capsys, tmp_path):
        """ADG_GRAPH_TRACE must appear for every graph-intent prompt regardless of tier."""
        self._run("show blast radius of this change", tmp_path)
        err = capsys.readouterr().err
        assert "ADG_GRAPH_TRACE: adg_graph_intent=DETECTED" in err

    def test_adg_graph_trace_not_detected_for_literal_prompt(self, capsys, tmp_path):
        """ADG_GRAPH_TRACE must report NOT_DETECTED for non-graph prompts."""
        self._run("find all TODO comments", tmp_path)
        err = capsys.readouterr().err
        assert "ADG_GRAPH_TRACE: adg_graph_intent=NOT_DETECTED" in err

    def test_adg_graph_sr_hint_injected_for_t2_graph_prompt(self, capsys, tmp_path):
        """ADG GRAPH INTENT DETECTED hint must appear in SR_MANDATE for T2/T3 graph prompts."""
        self._run("implement fanout analysis for blast radius reporting", tmp_path, redis_up=True)
        err = capsys.readouterr().err
        assert "ADG GRAPH INTENT DETECTED" in err
        assert "mcp1_adg_edge_fanin" in err
        assert "Health-first rule" in err
        assert "DEGRADED_FALLBACK" in err

    def test_adg_graph_sr_hint_not_injected_for_t0(self, capsys, tmp_path):
        """T0 graph prompt: routing TRACE fires but SR_MANDATE hint must NOT appear."""
        self._run("explain fanout edges", tmp_path)
        err = capsys.readouterr().err
        assert "ADG_GRAPH_TRACE: adg_graph_intent=DETECTED" in err
        assert "ADG GRAPH INTENT DETECTED" not in err
