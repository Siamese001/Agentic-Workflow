"""Tests for post_agent_work_classification_audit.py (plan-reflex detection).

Operating Model 2026-06-10: advisory hook logs plan-creation reflexes on
sub-threshold work. Always exits 0 — never blocks the response.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_work_classification_audit.py"


def _load_module():
    sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))
    spec = importlib.util.spec_from_file_location("post_agent_work_classification_audit", HOOK_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    key = "post_agent_work_classification_audit"
    if key in sys.modules:
        del sys.modules[key]
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hook():
    return _load_module()


class TestWorkClassificationAudit:
    def test_plan_creation_intent_logs_violation(self, hook, tmp_path, capsys) -> None:
        payload = json.dumps({"response": "I'll create a new plan file for this bug fix."})
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop("WORK_CLASSIFICATION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "plan-reflex" in captured.err
        rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        assert rows[0]["kind"] == "plan_creation_reflex"

    def test_plan_slug_reference_logs_violation(self, hook, tmp_path, capsys) -> None:
        payload = json.dumps(
            {"response": "Next step: write plans/fix-export-bug-a1b2c3.md with the scope."}
        )
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop("WORK_CLASSIFICATION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        assert log_path.exists()
        assert "new plan slug reference" in log_path.read_text(encoding="utf-8")

    def test_spawn_task_suppression_no_violation(self, hook, tmp_path, capsys) -> None:
        payload = json.dumps(
            {"response": "This is BUG_DEFERRED — I'll spawn_task instead of minting a plan."}
        )
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop("WORK_CLASSIFICATION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "plan-reflex" not in captured.err
        assert not log_path.exists()

    def test_plan_mint_ok_suppression_no_violation(self, hook, tmp_path) -> None:
        payload = json.dumps(
            {"response": "PLAN_MINT_OK=1 — I'll create a new plan for this multi-wave effort."}
        )
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop("WORK_CLASSIFICATION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        assert not log_path.exists()

    def test_bypass_env_skips_audit(self, hook, tmp_path, capsys) -> None:
        payload = json.dumps({"response": "I'll create a new plan file for this."})
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {"WORK_CLASSIFICATION_AUDIT_BYPASS": "1"}, clear=False),
        ):
            rc = hook.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "plan-reflex" not in captured.err
        assert not log_path.exists()

    def test_empty_response_exits_clean(self, hook, tmp_path) -> None:
        log_path = tmp_path / "work_classification_violations.jsonl"
        with (
            patch.object(hook, "VIOLATIONS_FILE", log_path),
            patch("sys.stdin", io.StringIO("")),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop("WORK_CLASSIFICATION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        assert not log_path.exists()
