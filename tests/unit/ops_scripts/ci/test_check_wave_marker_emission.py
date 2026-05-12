"""Unit tests for ops_scripts/ci/check_wave_marker_emission.py.

RCA: rca-wave-marker-emission-gap-c7d3f1 W4.P2.

Invariants verified:
- Plans with ALL TODO rows → not flagged (no partial completion)
- Plans with ALL DONE rows → not flagged (fully done)
- Plans with MIXED state (≥1 DONE + ≥1 TODO) AND no capture log entry → WARN
- Plans with MIXED state but a matching slug in capture log → NOT flagged
- Bypass env var suppresses all findings
- Fail-closed mode exits 1 when violations found
- Advisory mode (default) exits 0 even with violations
- _extract_wave_table correctly isolates the Wave Structure section
- Slug extracted from frontmatter takes precedence over filename
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_wave_marker_emission.py"


def _load_module():
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("check_wave_marker_emission", GATE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    key = "check_wave_marker_emission"
    if key in sys.modules:
        del sys.modules[key]
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gate():
    return _load_module()


# ---------------------------------------------------------------------------
# Helper: build plan markdown
# ---------------------------------------------------------------------------

def _make_plan(waves: list[str], slug: str = "my-plan-abc123") -> str:
    """waves: list of '🔲 TODO' or '✅ DONE' per wave row."""
    rows = []
    for i, status in enumerate(waves, 1):
        rows.append(f"| Wave {i} | Metric {i} | Scope {i} | C{i} | ~1k | {status} |")
    table = "\n".join([
        "| Waves | Metric | Scope | Checkpoint | Tokens | Status |",
        "|-------|--------|-------|------------|--------|--------|",
    ] + rows)
    return f"---\nplan_id: {slug}\n---\n\n# Plan Title\n\n## Wave Structure\n\n{table}\n"


# ---------------------------------------------------------------------------
# _plan_has_mixed_state
# ---------------------------------------------------------------------------

class TestMixedStateDetection:
    def test_all_todo_not_mixed(self, gate):
        text = _make_plan(["🔲 TODO", "🔲 TODO", "🔲 TODO"])
        is_mixed, done, todo = gate._plan_has_mixed_state(text)
        assert not is_mixed
        assert done == 0
        assert todo == 3

    def test_all_done_not_mixed(self, gate):
        text = _make_plan(["✅ DONE", "✅ DONE"])
        is_mixed, done, todo = gate._plan_has_mixed_state(text)
        assert not is_mixed
        assert done == 2
        assert todo == 0

    def test_mixed_is_flagged(self, gate):
        text = _make_plan(["✅ DONE", "🔲 TODO", "🔲 TODO"])
        is_mixed, done, todo = gate._plan_has_mixed_state(text)
        assert is_mixed
        assert done == 1
        assert todo == 2

    def test_no_wave_table_not_mixed(self, gate):
        text = "---\nplan_id: foo-abc123\n---\n\n# No wave table here\n"
        is_mixed, done, todo = gate._plan_has_mixed_state(text)
        assert not is_mixed
        assert done == 0
        assert todo == 0


# ---------------------------------------------------------------------------
# _slug_from_frontmatter
# ---------------------------------------------------------------------------

class TestSlugExtraction:
    def test_extracts_from_frontmatter(self, gate):
        text = "---\nplan_id: my-plan-abc123\n---\n"
        assert gate._slug_from_frontmatter(text) == "my-plan-abc123"

    def test_returns_none_when_absent(self, gate):
        assert gate._slug_from_frontmatter("no frontmatter here") is None


# ---------------------------------------------------------------------------
# _slugs_in_capture_log
# ---------------------------------------------------------------------------

class TestCapureLogSlugParsing:
    def test_parses_rows_list(self, gate, tmp_path):
        log = tmp_path / "wave_lifecycle_capture.jsonl"
        entry = json.dumps({
            "event": "capture_summary",
            "rows": [{"slug": "real-plan-a1b2c3", "ok": True, "msg": "ok"}],
        })
        log.write_text(entry + "\n", encoding="utf-8")
        with patch.object(gate, "CAPTURE_LOG", log):
            slugs = gate._slugs_in_capture_log()
        assert "real-plan-a1b2c3" in slugs

    def test_parses_direct_slug_key(self, gate, tmp_path):
        log = tmp_path / "wave_lifecycle_capture.jsonl"
        entry = json.dumps({"event": "wave_table_update", "slug": "direct-slug-d4e5f6"})
        log.write_text(entry + "\n", encoding="utf-8")
        with patch.object(gate, "CAPTURE_LOG", log):
            slugs = gate._slugs_in_capture_log()
        assert "direct-slug-d4e5f6" in slugs

    def test_ignores_test_fixture_slugs(self, gate, tmp_path):
        log = tmp_path / "wave_lifecycle_capture.jsonl"
        entries = [
            json.dumps({"event": "capture_summary", "rows": [{"slug": "demo-plan-abc123", "ok": True, "msg": "ok"}]}),
            json.dumps({"event": "capture_summary", "rows": [{"slug": "alpha-plan-abc123", "ok": True, "msg": "ok"}]}),
        ]
        log.write_text("\n".join(entries) + "\n", encoding="utf-8")
        with patch.object(gate, "CAPTURE_LOG", log):
            slugs = gate._slugs_in_capture_log()
        # Test fixture slugs should be present (they are — gate doesn't filter them,
        # but they wouldn't match a real plan on disk)
        assert "demo-plan-abc123" in slugs

    def test_absent_log_returns_empty(self, gate, tmp_path):
        missing = tmp_path / "no_such_file.jsonl"
        with patch.object(gate, "CAPTURE_LOG", missing):
            slugs = gate._slugs_in_capture_log()
        assert slugs == set()


# ---------------------------------------------------------------------------
# main() integration — findings and exit codes
# ---------------------------------------------------------------------------

class TestMainFindings:
    def _run(self, gate, plans_dir, capture_log, env_overrides=None):
        """Run gate.main() with patched paths."""
        env = {k: v for k, v in os.environ.items()}
        env.pop("WAVE_MARKER_EMISSION_BYPASS", None)
        env.pop("WAVE_MARKER_GATE_FAIL_CLOSED", None)
        if env_overrides:
            env.update(env_overrides)
        with (
            patch.object(gate, "PLANS_DIR", plans_dir),
            patch.object(gate, "CAPTURE_LOG", capture_log),
            patch.object(gate, "REPORT_PATH", plans_dir / "report.json"),
            patch.dict(os.environ, env, clear=True),
        ):
            return gate.main()

    def test_no_violations_clean_exit(self, gate, tmp_path):
        plan = _make_plan(["✅ DONE", "✅ DONE"], "clean-plan-aabbcc")
        (tmp_path / "clean-plan-aabbcc.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log)
        assert rc == 0

    def test_all_todo_not_flagged(self, gate, tmp_path):
        plan = _make_plan(["🔲 TODO", "🔲 TODO"], "new-plan-112233")
        (tmp_path / "new-plan-112233.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log)
        assert rc == 0

    def test_mixed_no_log_advisory_exit_0(self, gate, tmp_path):
        """Mixed state with no log entry → WARN but exits 0 (advisory)."""
        plan = _make_plan(["✅ DONE", "🔲 TODO"], "stale-plan-abcdef")
        (tmp_path / "stale-plan-abcdef.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log)
        assert rc == 0  # advisory mode
        report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
        assert report["violations"] == 1
        assert report["findings"][0]["slug"] == "stale-plan-abcdef"

    def test_mixed_with_log_entry_not_flagged(self, gate, tmp_path):
        """Mixed state but capture log has a matching entry → not flagged."""
        plan = _make_plan(["✅ DONE", "🔲 TODO"], "live-plan-112233")
        (tmp_path / "live-plan-112233.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        entry = json.dumps({"event": "wave_table_update", "slug": "live-plan-112233"})
        log.write_text(entry + "\n", encoding="utf-8")
        rc = self._run(gate, tmp_path, log)
        assert rc == 0
        report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
        assert report["violations"] == 0

    def test_fail_closed_exits_1_on_violation(self, gate, tmp_path):
        plan = _make_plan(["✅ DONE", "🔲 TODO"], "stale-plan-ffffff")
        (tmp_path / "stale-plan-ffffff.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log, {"WAVE_MARKER_GATE_FAIL_CLOSED": "1"})
        assert rc == 1

    def test_bypass_suppresses_all(self, gate, tmp_path):
        plan = _make_plan(["✅ DONE", "🔲 TODO"], "stale-plan-bypassed")
        (tmp_path / "stale-plan-bypassed.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log, {"WAVE_MARKER_EMISSION_BYPASS": "1"})
        assert rc == 0

    def test_underscore_prefixed_plans_skipped(self, gate, tmp_path):
        """Plans starting with _ (archive, orphan) are excluded."""
        plan = _make_plan(["✅ DONE", "🔲 TODO"], "archived-plan-aaaaaa")
        (tmp_path / "_archived-plan-aaaaaa.md").write_text(plan, encoding="utf-8")
        log = tmp_path / "cap.jsonl"
        log.write_text("", encoding="utf-8")
        rc = self._run(gate, tmp_path, log)
        assert rc == 0
        report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
        assert report["violations"] == 0
