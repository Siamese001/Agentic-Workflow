"""Tests for post_agent_work_classification_audit (Stop chain, fail-open).

Detects plan-creation reflex phrases on sub-threshold work and logs violations to
``artifacts/governance/work_classification_violations.jsonl``. Never blocks (exit 0).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_agent_work_classification_audit.py"


@pytest.fixture()
def audit_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    name = "_post_agent_work_classification_audit_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    log = tmp_path / "work_classification_violations.jsonl"
    monkeypatch.setattr(mod, "VIOLATIONS_FILE", log)
    monkeypatch.delenv("WORK_CLASSIFICATION_AUDIT_BYPASS", raising=False)
    return mod, log


def _run_main(mod, payload: dict, monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr(sys, "stdin", StringIO(json.dumps(payload)))
    return mod.main()


class TestPostAgentWorkClassificationAudit:
    def test_bypass_exits_0_no_log(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        monkeypatch.setenv("WORK_CLASSIFICATION_AUDIT_BYPASS", "1")
        rc = _run_main(
            mod,
            {"response": "I'll create a new plan file for this one-line typo fix."},
            monkeypatch,
        )
        assert rc == 0
        assert not log.exists()

    def test_empty_response_exits_0_no_log(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        rc = _run_main(mod, {}, monkeypatch)
        assert rc == 0
        assert not log.exists()

    def test_clean_response_exits_0_no_log(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        rc = _run_main(
            mod,
            {"response": "Fixed the bug directly in apps_rg/runtime/foo.py and ran pytest."},
            monkeypatch,
        )
        assert rc == 0
        assert not log.exists()

    def test_spawn_task_suppression_exits_0_no_log(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        rc = _run_main(
            mod,
            {"response": "Deferring to spawn_task for the systemic backlog item."},
            monkeypatch,
        )
        assert rc == 0
        assert not log.exists()

    def test_plan_mint_ok_suppression_exits_0_no_log(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        rc = _run_main(
            mod,
            {"response": "User authorized PLAN_MINT_OK=1; I'll create a new plan for the multi-wave migration."},
            monkeypatch,
        )
        assert rc == 0
        assert not log.exists()

    def test_plan_creation_intent_logs_violation_but_exits_0(
        self, audit_mod, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mod, log = audit_mod
        rc = _run_main(
            mod,
            {"response": "I'll create a new plan for this typo fix."},
            monkeypatch,
        )
        assert rc == 0
        assert log.exists()
        row = json.loads(log.read_text(encoding="utf-8").strip())
        assert row["kind"] == "plan_creation_reflex"
        assert row["label"] == "plan-creation intent phrase"
        assert "remedy" in row
        captured = capsys.readouterr()
        assert "work-classification" in captured.err

    def test_plan_slug_reference_logs_violation(
        self, audit_mod, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod, log = audit_mod
        rc = _run_main(
            mod,
            {"response": "Next step: write plans/my-migration-a1b2c3.md for wave 1."},
            monkeypatch,
        )
        assert rc == 0
        assert log.exists()
        row = json.loads(log.read_text(encoding="utf-8").strip())
        assert row["label"] == "new plan slug reference"

    def test_list_content_payload_shape(self, audit_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        mod, log = audit_mod
        payload = {
            "content": [{"text": "I will mint a new plan file for this bug."}],
        }
        rc = _run_main(mod, payload, monkeypatch)
        assert rc == 0
        assert log.exists()
