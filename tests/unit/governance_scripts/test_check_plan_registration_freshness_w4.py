"""Unit tests for W4 content-drift detection in check_plan_registration_freshness.py.

Covers:
  - content_drift_report() — no rows, digest match, digest mismatch, null-digest skip
  - main --digest-drift — advisory exit 0 on drift; fail-closed exit 1
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

GATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "ops_scripts" / "ci" / "check_plan_registration_freshness.py"
)
HELPER_PATH = (
    Path(__file__).resolve().parents[3]
    / ".claude" / "governance/scripts" / "_plan_registration.py"
)


def _load_gate(tmp_path, monkeypatch):
    """Load the gate module with REPO_ROOT overridden to tmp_path."""
    spec = importlib.util.spec_from_file_location("_gate_w4_test", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_gate_w4_test"] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    return mod


def _load_pr(tmp_path, monkeypatch):
    """Load _plan_registration with state redirected to tmp_path."""
    spec = importlib.util.spec_from_file_location("_pr_w4_test", HELPER_PATH)
    pr = importlib.util.module_from_spec(spec)
    sys.modules["_pr_w4_test"] = pr
    spec.loader.exec_module(pr)
    state = tmp_path / ".claude" / "state"
    state.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pr, "STATE_DIR", state)
    monkeypatch.setattr(pr, "QUEUE_PATH", state / "plan_registration_queue.jsonl")
    monkeypatch.setattr(pr, "CACHE_PATH", state / "plan_registration_cache.json")
    plans = tmp_path / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pr, "NEW_PLANS_DIR", plans)
    legacy = tmp_path / ".claude" / "plans"
    legacy.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pr, "PLANS_DIR", legacy)
    monkeypatch.setattr(pr, "PLAN_DIRS", [plans, legacy])
    return pr


def _write_plan(tmp_path, slug, content):
    """Write a plan file into tmp_path/plans/ and return the file path."""
    plan = tmp_path / "plans" / f"{slug}.md"
    plan.write_text(content, encoding="utf-8")
    return plan


# ---------------------------------------------------------------------------
# content_drift_report — unit tests
# ---------------------------------------------------------------------------


class TestContentDriftReport:
    def test_no_queue_rows_returns_empty(self, tmp_path, monkeypatch):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        # No plan files, no queue rows.
        result = gate.content_drift_report(pr)
        assert result == []

    def test_matching_digest_no_drift(self, tmp_path, monkeypatch):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        slug = "plan-abc-aaaaaa"
        content = "---\nai_summary: Good plan.\n---\n# body"
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        _write_plan(tmp_path, slug, content)
        pr.enqueue_plan(slug, f"plans/{slug}.md", content_digest=digest)
        result = gate.content_drift_report(pr)
        assert result == []

    def test_mismatched_digest_reported(self, tmp_path, monkeypatch):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        slug = "plan-xyz-bbbbbb"
        original = "---\nai_summary: Original.\n---\n# original body"
        stored_digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
        edited = original + "\n## New Wave"
        _write_plan(tmp_path, slug, edited)  # file has been edited
        pr.enqueue_plan(slug, f"plans/{slug}.md", content_digest=stored_digest)
        result = gate.content_drift_report(pr)
        assert len(result) == 1
        item = result[0]
        assert item["slug"] == slug
        assert item["stored_digest"] == stored_digest
        assert item["current_digest"] == hashlib.sha256(edited.encode("utf-8")).hexdigest()
        assert item["path"].startswith("plans/")

    def test_null_digest_in_queue_row_skipped(self, tmp_path, monkeypatch):
        """Plans with None stored digest (legacy marker path) are silently skipped."""
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        slug = "plan-leg-cccccc"
        content = "---\nai_summary: Legacy.\n---\n# body"
        _write_plan(tmp_path, slug, content)
        # Enqueue without digest (simulates legacy marker capture)
        pr.enqueue_plan(slug, f"plans/{slug}.md")
        result = gate.content_drift_report(pr)
        assert result == []  # no digest to compare — skip silently

    def test_plan_not_in_queue_skipped(self, tmp_path, monkeypatch):
        """On-disk plan with no queue row is silently skipped."""
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        slug = "plan-nqr-dddddd"
        _write_plan(tmp_path, slug, "---\n---\n# body")
        # No enqueue call — queue row doesn't exist.
        result = gate.content_drift_report(pr)
        assert result == []


# ---------------------------------------------------------------------------
# main --digest-drift integration tests
# ---------------------------------------------------------------------------


class TestMainDigestDrift:
    def _run_main(self, gate, argv, monkeypatch=None, env_override=None):
        """Run gate.main with optional env overrides, return exit code."""
        import os
        if env_override:
            for k, v in env_override.items():
                if monkeypatch:
                    monkeypatch.setenv(k, v)
        return gate.main(argv)

    def test_no_drift_exits_0(self, tmp_path, monkeypatch, capsys):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        monkeypatch.setattr(gate, "_load_helper", lambda: pr)
        monkeypatch.setenv("PLAN_REGISTRATION_BYPASS", "0")
        rc = gate.main(["--digest-drift"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "OK" in out

    def test_drift_detected_advisory_exits_0(self, tmp_path, monkeypatch, capsys):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        # Create drift: enqueue with stale digest, but file has been edited.
        slug = "plan-drft-eeeeee"
        old_content = "---\nai_summary: Old.\n---\n# old body"
        new_content = old_content + "\n## added wave"
        old_digest = hashlib.sha256(old_content.encode("utf-8")).hexdigest()
        _write_plan(tmp_path, slug, new_content)
        pr.enqueue_plan(slug, f"plans/{slug}.md", content_digest=old_digest)
        monkeypatch.setattr(gate, "_load_helper", lambda: pr)
        monkeypatch.delenv("PLAN_CONTENT_DRIFT_FAIL_CLOSED", raising=False)
        rc = gate.main(["--digest-drift"])
        assert rc == 0  # advisory
        err = capsys.readouterr().err
        assert "CONTENT_DRIFT" in err

    def test_drift_fail_closed_exits_1(self, tmp_path, monkeypatch, capsys):
        gate = _load_gate(tmp_path, monkeypatch)
        pr = _load_pr(tmp_path, monkeypatch)
        slug = "plan-drfc-ffffff"
        old_content = "---\nai_summary: Old.\n---\n# original"
        new_content = old_content + "\n## wave 2"
        old_digest = hashlib.sha256(old_content.encode("utf-8")).hexdigest()
        _write_plan(tmp_path, slug, new_content)
        pr.enqueue_plan(slug, f"plans/{slug}.md", content_digest=old_digest)
        monkeypatch.setattr(gate, "_load_helper", lambda: pr)
        monkeypatch.setenv("PLAN_CONTENT_DRIFT_FAIL_CLOSED", "1")
        rc = gate.main(["--digest-drift"])
        assert rc == 1
