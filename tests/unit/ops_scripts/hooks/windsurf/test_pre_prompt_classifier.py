"""
Tests for ops_scripts/hooks/windsurf/pre_prompt_classifier.py (Phase 1.4).

Covers:
  - T3 classification (architecture/refactor/wave keywords)
  - T2 classification (multi-keyword modify/implement)
  - T1 classification (trivial keywords)
  - T0 classification (explain/review keywords)
  - Default T1 for unrecognized prompt
  - plan_exists check for T2/T3
  - ADG health stale detection
  - Always exits 0 (never blocks)
  - Empty stdin → exit 0
  - Malformed JSON → exit 0
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_prompt_classifier import (
    check_adg_health_stale,
    check_plan_exists,
    classify_tier,
    main,
)


class TestClassifyTier:
    def test_architecture_is_t3(self):
        assert classify_tier("redesign the architecture of the ADG module") == "T3"

    def test_refactor_is_t3(self):
        assert classify_tier("refactor the L0 layer into subpackages") == "T3"

    def test_wave_is_t3(self):
        assert classify_tier("implement wave 2 of the governance model") == "T3"

    def test_multi_modify_is_t2(self):
        assert classify_tier("fix and update the test file for the hook") == "T2"

    def test_implement_is_t2(self):
        assert classify_tier("implement and create the new gate script") == "T2"

    def test_typo_is_t1(self):
        assert classify_tier("fix this typo in the docstring") == "T1"

    def test_explain_is_t0(self):
        assert classify_tier("explain how the pre_run_gate works") == "T0"

    def test_what_is_t0(self):
        assert classify_tier("what is the ADG health check?") == "T0"

    def test_unrecognized_is_t1(self):
        assert classify_tier("zork zork zork") == "T1"

    def test_empty_is_t1(self):
        assert classify_tier("") == "T1"


class TestCheckPlanExists:
    def test_non_t2_t3_always_true(self):
        assert check_plan_exists("T0") is True
        assert check_plan_exists("T1") is True

    def test_t2_no_plans_dir(self, tmp_path):
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is False

    def test_t2_with_plan_file(self, tmp_path):
        plans = tmp_path / ".windsurf" / "plans"
        plans.mkdir(parents=True)
        (plans / "my-plan-abc123.md").write_text("# Plan")
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T2") is True

    def test_t3_no_plan_false(self, tmp_path):
        (tmp_path / ".windsurf" / "plans").mkdir(parents=True)
        with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
            assert check_plan_exists("T3") is False


class TestCheckAdgHealthStale:
    def test_no_artifacts_dir_is_stale(self, tmp_path):
        assert check_adg_health_stale(tmp_path) is True

    def test_no_snapshots_is_stale(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert check_adg_health_stale(tmp_path) is True

    def test_snapshot_present_not_stale(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_20260101.json").write_text("{}")
        assert check_adg_health_stale(tmp_path) is False


class TestMain:
    def _run(self, payload: dict) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_always_exits_0_for_t3_prompt(self):
        payload = {"tool_info": {"prompt": "refactor the entire architecture across all layers"}}
        assert self._run(payload) == 0

    def test_always_exits_0_for_safe_prompt(self):
        payload = {"tool_info": {"prompt": "explain the ADG framework"}}
        assert self._run(payload) == 0

    def test_empty_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_exits_0(self):
        with patch("sys.stdin", StringIO("{bad json")):
            assert main() == 0

    def test_no_prompt_field_exits_0(self):
        payload = {"tool_info": {}}
        assert self._run(payload) == 0

    def test_t2_with_no_plan_exits_0_warns(self, tmp_path):
        plans = tmp_path / ".windsurf" / "plans"
        plans.mkdir(parents=True)
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_x.json").write_text("{}")
        payload = {"tool_info": {"prompt": "fix and update the authentication module"}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.pre_prompt_classifier.REPO_ROOT", tmp_path):
                result = main()
        assert result == 0
