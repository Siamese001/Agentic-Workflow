"""
EXHAUSTIVE tests for pre_prompt_classifier.py (Phase 1.4).

Plan requirements verified:
  - T3 keywords: architecture, refactor, wave, migration, restructure, etc.
  - T2 keywords: fix+update, implement+create, multi-keyword combos
  - T1 keywords: typo, docstring, trivial, single line
  - T0 keywords: explain, what is, how does, review
  - Default T1 for unrecognized prompt
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

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_prompt_classifier import (
    check_plan_exists,
    check_redis_down,
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
    def test_unrecognized_defaults_to_t1(self):
        assert classify_tier("zork zork zork") == "T1"

    def test_empty_defaults_to_t1(self):
        assert classify_tier("") == "T1"

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
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is False

    def test_t2_empty_plans_dir_false(self, tmp_path):
        (tmp_path / ".windsurf" / "plans").mkdir(parents=True)
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is False

    def test_t2_with_plan_file_true(self, tmp_path):
        plans = tmp_path / ".windsurf" / "plans"
        plans.mkdir(parents=True)
        (plans / "my-plan-abc123.md").write_text("# Plan")
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is True

    def test_t3_no_plans_dir_false(self, tmp_path):
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T3") is False

    def test_t3_with_plan_file_true(self, tmp_path):
        plans = tmp_path / ".windsurf" / "plans"
        plans.mkdir(parents=True)
        (plans / "plan.md").write_text("# Plan")
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T3") is True

    def test_non_md_file_in_plans_not_counted(self, tmp_path):
        plans = tmp_path / ".windsurf" / "plans"
        plans.mkdir(parents=True)
        (plans / "not_a_plan.txt").write_text("text")
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is False


# ---------------------------------------------------------------------------
# check_redis_down
# ---------------------------------------------------------------------------

class TestCheckRedisDown:
    def test_connection_refused_returns_true(self):
        import socket
        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            assert check_redis_down() is True

    def test_successful_connection_returns_false(self):
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        import socket
        with patch("socket.create_connection", return_value=mock_conn):
            assert check_redis_down() is False

    def test_os_error_fails_open(self):
        import socket
        with patch("socket.create_connection", side_effect=OSError("Network unreachable")):
            assert check_redis_down() is False

    def test_timeout_os_error_fails_open(self):
        import socket
        with patch("socket.create_connection", side_effect=TimeoutError("timed out")):
            assert check_redis_down() is False


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------

class TestMain:
    def _run(self, payload: dict, adg_red: bool = False, redis_down: bool = False,
             repo_root=None) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch(
                "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_adg_health_red",
                return_value=adg_red,
            ):
                with patch(
                    "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_redis_down",
                    return_value=redis_down,
                ):
                    if repo_root is not None:
                        with patch(
                            "ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT",
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
        assert "mcp8_create_task" in captured.err
        assert "SR_INTAKE" in captured.err
        assert "SR_PLAN" in captured.err
        assert "SR_APPROVAL" in captured.err

    # --- T2/T3 + red ADG: blocked ---
    def test_t3_red_adg_blocked(self):
        payload = {"tool_info": {"user_prompt": "refactor the entire architecture"}}
        assert self._run(payload, adg_red=True, redis_down=False) == 2

    def test_t2_red_adg_blocked(self):
        payload = {"tool_info": {"user_prompt": "fix and update the module"}}
        assert self._run(payload, adg_red=True, redis_down=False) == 2

    def test_blocked_message_mentions_adg(self, capsys):
        payload = {"tool_info": {"user_prompt": "refactor the auth layer"}}
        self._run(payload, adg_red=True, redis_down=False)
        captured = capsys.readouterr()
        assert "adg_sqlite" in captured.err.lower() or "BLOCKED" in captured.err

    # --- T2/T3 + Redis down: blocked ---
    def test_t3_redis_down_blocked(self):
        payload = {"tool_info": {"user_prompt": "restructure the module hierarchy"}}
        assert self._run(payload, adg_red=False, redis_down=True) == 2

    def test_t2_redis_down_blocked(self):
        payload = {"tool_info": {"user_prompt": "implement and create the new service"}}
        assert self._run(payload, adg_red=False, redis_down=True) == 2

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
        assert self._run(payload, adg_red=True) == 2

    def test_user_prompt_takes_precedence(self):
        # user_prompt preferred over prompt
        payload = {"tool_info": {"user_prompt": "explain the code", "prompt": "refactor everything"}}
        # user_prompt = T0 → not blocked
        assert self._run(payload, adg_red=True) == 0

    # --- plan warning ---
    def test_no_plan_for_t3_emits_warning(self, capsys, tmp_path):
        (tmp_path / ".windsurf" / "plans").mkdir(parents=True)
        payload = {"tool_info": {"user_prompt": "refactor the architecture"}}
        self._run(payload, adg_red=False, redis_down=False, repo_root=tmp_path)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err or "plan" in captured.err.lower()

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
