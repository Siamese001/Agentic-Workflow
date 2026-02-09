"""Unit tests for active_set_snapshot_check.py (drift detection hardening)."""

from __future__ import annotations

import json
import sys
from collections import namedtuple
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.active_set_snapshot_check import main

# Fake ActiveSetResult for mocking
FakeResult = namedtuple("FakeResult", ["count", "fingerprint", "agent_ids", "agents", "stats"])

SNAPSHOT_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "active_set_snapshot.json"


def _load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


class TestCurrentSnapshotPasses:
    """Live snapshot should match — no drift."""

    def test_passes_with_current_state(self):
        rc = main()
        assert rc == 0


class TestDriftDetectionOutput:
    """When fingerprint changes, output must include detailed diff info."""

    def _make_fake_result(self, count, fingerprint, agent_ids):
        return FakeResult(
            count=count,
            fingerprint=fingerprint,
            agent_ids=tuple(agent_ids),
            agents=(),
            stats={},
        )

    def test_drift_fails_without_tag(self, monkeypatch, capsys):
        snapshot = _load_snapshot()
        fake = self._make_fake_result(
            count=150,
            fingerprint="aaaa" * 16,
            agent_ids=["NewAgent"]
            + list(snapshot.get("first_10", []))[1:]
            + list(snapshot.get("last_10", [])),
        )
        monkeypatch.setattr(
            "ops_scripts.ci.active_set_helper.get_active_set",
            lambda _root: fake,
        )
        monkeypatch.delenv("COMMIT_MESSAGE", raising=False)

        rc = main()
        assert rc == 1
        captured = capsys.readouterr()
        assert "FAIL" in captured.out
        assert "old_count" in captured.out
        assert "new_count" in captured.out
        assert "old_fingerprint" in captured.out
        assert "new_fingerprint" in captured.out
        assert "old_first_10" in captured.out
        assert "new_first_10" in captured.out
        assert "old_last_10" in captured.out
        assert "new_last_10" in captured.out

    def test_drift_shows_added_removed(self, monkeypatch, capsys):
        snapshot = _load_snapshot()
        old_first = snapshot.get("first_10", [])
        modified_first = ["BrandNewAgent"] + old_first[1:]
        fake = self._make_fake_result(
            count=149,
            fingerprint="bbbb" * 16,
            agent_ids=modified_first + list(snapshot.get("last_10", [])),
        )
        monkeypatch.setattr(
            "ops_scripts.ci.active_set_helper.get_active_set",
            lambda _root: fake,
        )
        monkeypatch.delenv("COMMIT_MESSAGE", raising=False)

        rc = main()
        assert rc == 1
        captured = capsys.readouterr()
        assert "added:" in captured.out
        assert "BrandNewAgent" in captured.out
        assert "removed:" in captured.out
        assert old_first[0] in captured.out

    def test_bump_tag_allows_pass(self, monkeypatch, capsys, tmp_path):
        snapshot = _load_snapshot()

        fake = self._make_fake_result(
            count=148,
            fingerprint="cccc" * 16,
            agent_ids=list(snapshot.get("first_10", [])) + list(snapshot.get("last_10", [])),
        )
        monkeypatch.setattr(
            "ops_scripts.ci.active_set_helper.get_active_set",
            lambda _root: fake,
        )
        monkeypatch.setenv("COMMIT_MESSAGE", "ACTIVE_SET_SNAPSHOT_BUMP:test")

        # Redirect write_json_atomic to tmp_path so real snapshot is never modified
        tmp_out = tmp_path / "snapshot_out.json"
        monkeypatch.setattr(
            "ops_scripts.ci.baseline_io.write_json_atomic",
            lambda path, data: tmp_out.write_text(
                json.dumps(data, indent=2) + "\n",
                encoding="utf-8",
            ),
        )

        rc = main()
        captured = capsys.readouterr()
        assert rc == 0
        assert "WARN" in captured.out or "ACTIVE_SET_SNAPSHOT_BUMP" in captured.out
        # Verify tmp file got the write, not the real snapshot
        assert tmp_out.is_file()
        written = json.loads(tmp_out.read_text(encoding="utf-8"))
        assert written["count"] == 148
