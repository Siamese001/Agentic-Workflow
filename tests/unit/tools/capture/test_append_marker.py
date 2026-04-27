"""Unit tests for tools.capture.append_marker.

Covers every input path (CLI --marker, CLI --stdin, explicit session tag,
malformed input, unicode, concurrent appends) plus the classify_marker
pure function that is the primary validation surface.
"""

# pylint: disable=redefined-outer-name,unused-argument
# (pytest fixtures shadow outer names and pass-through args by design)

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import pytest

# Force imports to use the real module under test without polluting path.
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

from tools.capture import append_marker as am


# ---------------------------------------------------------------------------
# classify_marker — pure function, exhaustive edge cases
# ---------------------------------------------------------------------------

class TestClassifyMarker:
    def test_decision_captured_valid(self):
        assert am.classify_marker(
            "DECISION_CAPTURED: type=architecture_choice, repo_area=x, selected=y, outcome=executed"
        ) == "DECISION_CAPTURED"

    def test_deferred_scope_valid(self):
        assert am.classify_marker(
            "DEFERRED_SCOPE: plan=foo wave=W1 phase=P1 layer=L0 fan_in=0 surface=None coverage_gap_pct=0 est_tokens=100 reason=x"
        ) == "DEFERRED_SCOPE"

    def test_next_step_valid(self):
        assert am.classify_marker(
            "NEXT_STEP: plan=NEW:foo title=bar priority=P3 est_tokens=1000 reason=x"
        ) == "NEXT_STEP"

    def test_leading_whitespace_tolerated(self):
        assert am.classify_marker(
            "    DECISION_CAPTURED: type=x, "
        ) == "DECISION_CAPTURED"

    def test_trailing_whitespace_tolerated(self):
        assert am.classify_marker(
            "DECISION_CAPTURED: type=x,   \n"
        ) == "DECISION_CAPTURED"

    def test_empty_string(self):
        assert am.classify_marker("") is None

    def test_unrelated_prose(self):
        assert am.classify_marker("This response discusses DECISION_CAPTURED in passing") is None

    def test_wrong_prefix(self):
        assert am.classify_marker("DECISION: type=x,") is None

    def test_missing_type_field(self):
        # Schema requires type=<identifier>,
        assert am.classify_marker("DECISION_CAPTURED: repo_area=x, outcome=executed") is None

    def test_decision_captured_with_extra_whitespace_after_colon(self):
        assert am.classify_marker(
            "DECISION_CAPTURED:    type=architecture_choice, repo_area=x, outcome=executed"
        ) == "DECISION_CAPTURED"

    def test_deferred_scope_without_plan(self):
        # plan= is required
        assert am.classify_marker("DEFERRED_SCOPE: wave=W1 phase=P1") is None

    def test_next_step_without_plan(self):
        assert am.classify_marker("NEXT_STEP: title=bar priority=P3") is None


# ---------------------------------------------------------------------------
# append_marker — disk effects
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_queue(tmp_path, monkeypatch):
    """Redirect QUEUE_DIR / QUEUE_FILE to a per-test tmpdir."""
    q_dir = tmp_path / "capture"
    q_file = q_dir / "markers.jsonl"
    monkeypatch.setattr(am, "QUEUE_DIR", q_dir)
    monkeypatch.setattr(am, "QUEUE_FILE", q_file)
    return q_file


class TestAppendMarker:
    def test_appends_recognized_marker(self, tmp_queue):
        ok, _msg = am.append_marker(
            "DECISION_CAPTURED: type=test_strategy, repo_area=x, outcome=executed"
        )
        assert ok is True
        assert tmp_queue.exists()
        lines = tmp_queue.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        row = json.loads(lines[0])
        assert row["marker_type"] == "DECISION_CAPTURED"
        assert "received_at" in row
        assert "pid" in row

    def test_rejects_unrecognized_marker(self, tmp_queue):
        ok, msg = am.append_marker("just some prose text")
        assert ok is False
        assert "unrecognized marker" in msg
        assert not tmp_queue.exists()

    def test_rejects_empty_input(self, tmp_queue):
        ok, msg = am.append_marker("")
        assert ok is False
        assert msg == "empty input"

    def test_rejects_whitespace_only(self, tmp_queue):
        ok, _msg = am.append_marker("   \n\t  ")
        assert ok is False

    def test_session_hint_captured(self, tmp_queue):
        am.append_marker(
            "DECISION_CAPTURED: type=x, a=b",
            session_hint="abc123",
        )
        row = json.loads(tmp_queue.read_text(encoding="utf-8").splitlines()[0])
        assert row["session_hint"] == "abc123"

    def test_session_hint_from_env(self, tmp_queue, monkeypatch):
        monkeypatch.setenv("WINDSURF_SESSION_ID", "env-session-xyz")
        am.append_marker("DECISION_CAPTURED: type=x, a=b")
        row = json.loads(tmp_queue.read_text(encoding="utf-8").splitlines()[0])
        assert row["session_hint"] == "env-session-xyz"

    def test_unicode_content_preserved(self, tmp_queue):
        am.append_marker("DECISION_CAPTURED: type=x, selected=résumé ✓ 日本, outcome=executed")
        line = tmp_queue.read_text(encoding="utf-8").splitlines()[0]
        assert "résumé" in line
        assert "日本" in line
        # Must decode as valid JSON round-trip
        row = json.loads(line)
        assert "résumé" in row["raw"]

    def test_multiple_appends_each_one_line(self, tmp_queue):
        for i in range(3):
            am.append_marker(f"DECISION_CAPTURED: type=x, seq={i}, outcome=executed")
        lines = tmp_queue.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 3
        for i, ln in enumerate(lines):
            assert json.loads(ln)["raw"].endswith(f"seq={i}, outcome=executed")

    def test_appends_are_atomic_under_threads(self, tmp_queue):
        """Concurrent append_marker calls must not corrupt JSONL."""
        N = 20

        def worker(idx: int) -> None:
            am.append_marker(
                f"DECISION_CAPTURED: type=thread_test, seq={idx}, outcome=executed"
            )

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        lines = tmp_queue.read_text(encoding="utf-8").splitlines()
        assert len(lines) == N
        # Every line must parse as JSON
        for ln in lines:
            row = json.loads(ln)
            assert row["marker_type"] == "DECISION_CAPTURED"


# ---------------------------------------------------------------------------
# main() — CLI surface
# ---------------------------------------------------------------------------

class TestCLIMain:
    def test_cli_marker_single(self, tmp_queue, capsys):
        rc = am.main([
            "--marker",
            "DECISION_CAPTURED: type=x, repo_area=y, outcome=executed",
        ])
        assert rc == 0
        assert tmp_queue.exists()
        assert len(tmp_queue.read_text(encoding="utf-8").splitlines()) == 1

    def test_cli_marker_multiple(self, tmp_queue, capsys):
        rc = am.main([
            "--marker", "DECISION_CAPTURED: type=a, x=1, outcome=executed",
            "--marker", "DECISION_CAPTURED: type=b, x=2, outcome=executed",
        ])
        assert rc == 0
        assert len(tmp_queue.read_text(encoding="utf-8").splitlines()) == 2

    def test_cli_quiet_suppresses_success_stdout(self, tmp_queue, capsys):
        rc = am.main([
            "--marker", "DECISION_CAPTURED: type=x, a=b, outcome=executed",
            "--quiet",
        ])
        out = capsys.readouterr()
        assert rc == 0
        assert out.out == ""  # quiet means no success prints

    def test_cli_unrecognized_returns_0_with_warn(self, tmp_queue, capsys):
        # fail-open: unrecognized markers log a WARN but do not fail the command
        rc = am.main(["--marker", "not a marker"])
        out = capsys.readouterr()
        assert rc == 0
        assert "WARN" in out.err
        assert not tmp_queue.exists()

    def test_cli_stdin_extracts_markers_from_mixed_prose(self, tmp_queue, capsys, monkeypatch):
        prose = (
            "Some response prose.\n"
            "DECISION_CAPTURED: type=architecture_choice, repo_area=x, outcome=executed\n"
            "More prose.\n"
            "Another line with no marker.\n"
            "DEFERRED_SCOPE: plan=foo wave=W1 phase=P1 layer=L0 fan_in=0 surface=None coverage_gap_pct=0 est_tokens=1 reason=x\n"
        )
        monkeypatch.setattr("sys.stdin", _FakeStdin(prose))
        rc = am.main(["--stdin"])
        assert rc == 0
        lines = tmp_queue.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        types = [json.loads(l)["marker_type"] for l in lines]
        assert "DECISION_CAPTURED" in types
        assert "DEFERRED_SCOPE" in types

    def test_cli_stdin_empty_returns_0_with_warn(self, tmp_queue, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", _FakeStdin(""))
        rc = am.main(["--stdin"])
        out = capsys.readouterr()
        assert rc == 0
        assert "WARN" in out.err or "no recognizable" in out.err


class _FakeStdin:
    """Minimal stdin stand-in that behaves like a non-TTY pipe."""

    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> str:
        return self._text

    def isatty(self) -> bool:
        return False
