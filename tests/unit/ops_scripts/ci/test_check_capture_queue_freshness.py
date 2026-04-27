"""Unit tests for ops_scripts.ci.check_capture_queue_freshness."""

# pylint: disable=redefined-outer-name,unused-argument

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
_SCRIPT = _REPO / "ops_scripts" / "ci" / "check_capture_queue_freshness.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("ccqf", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ccqf():
    return _load_module()


# ---------------------------------------------------------------------------
# evaluate()
# ---------------------------------------------------------------------------

class TestEvaluate:
    def test_missing_queue_returns_0(self, ccqf, tmp_path):
        code, msg = ccqf.evaluate(tmp_path / "nope.jsonl", 24)
        assert code == 0
        assert "missing" in msg

    def test_empty_queue_returns_0(self, ccqf, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("", encoding="utf-8")
        code, msg = ccqf.evaluate(p, 24)
        assert code == 0
        assert "empty" in msg

    def test_fresh_nonempty_returns_0(self, ccqf, tmp_path):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        code, msg = ccqf.evaluate(p, 24)
        assert code == 0
        assert "fresh" in msg

    def test_stale_nonempty_returns_1(self, ccqf, tmp_path):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        # Force the mtime backward by 48h.
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=48)).timestamp()
        os.utime(p, (old_ts, old_ts))
        code, msg = ccqf.evaluate(p, 24)
        assert code == 1
        assert "STALE" in msg
        assert "queue_to_ledger.py" in msg  # remediation points to drain

    def test_custom_threshold_tight(self, ccqf, tmp_path):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()
        os.utime(p, (old_ts, old_ts))
        # 24h threshold: fresh
        assert ccqf.evaluate(p, 24)[0] == 0
        # 1h threshold: stale
        assert ccqf.evaluate(p, 1)[0] == 1


# ---------------------------------------------------------------------------
# main() — strict vs advisory
# ---------------------------------------------------------------------------

class TestMain:
    def test_fresh_exits_0(self, ccqf, tmp_path, capsys):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        rc = ccqf.main(["--queue", str(p), "--max-age-hours", "24"])
        assert rc == 0

    def test_stale_strict_exits_1(self, ccqf, tmp_path, capsys, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=48)).timestamp()
        os.utime(p, (old_ts, old_ts))
        monkeypatch.delenv("CAPTURE_QUEUE_FRESHNESS_MODE", raising=False)
        rc = ccqf.main(["--queue", str(p), "--max-age-hours", "24"])
        assert rc == 1

    def test_stale_advisory_exits_0_but_warns(self, ccqf, tmp_path, capsys, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text('{"raw":"x"}\n', encoding="utf-8")
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=48)).timestamp()
        os.utime(p, (old_ts, old_ts))
        monkeypatch.setenv("CAPTURE_QUEUE_FRESHNESS_MODE", "advisory")
        rc = ccqf.main(["--queue", str(p), "--max-age-hours", "24"])
        err = capsys.readouterr().err
        assert rc == 0
        assert "ADVISORY" in err
        assert "STALE" in err

    def test_missing_queue_exits_0(self, ccqf, tmp_path, capsys):
        rc = ccqf.main(["--queue", str(tmp_path / "nope.jsonl"), "--max-age-hours", "24"])
        assert rc == 0
