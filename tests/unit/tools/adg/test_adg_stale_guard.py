from __future__ import annotations

import subprocess

from tools.adg.adg_stale_guard import ADGStalenessChecker


class FakeClient:
    def __init__(self, meta: dict[str, str]) -> None:
        self._meta = meta

    def meta(self) -> dict[str, str]:
        return self._meta


def test_changed_files_since_uses_epoch_after(monkeypatch):
    captured: dict[str, object] = {}

    def _fake_run(argv, **kwargs):  # noqa: ANN001
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="tools/adg/adg_stale_guard.py\n", stderr="")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    checker = ADGStalenessChecker(client=object())

    files = checker._get_files_changed_since(1782690438.1574242)

    assert files == ["tools/adg/adg_stale_guard.py"]
    assert "--after=@1782690438" in captured["argv"]


def test_staleness_uses_sqlite_mtime_not_reingest_time(monkeypatch):
    checker = ADGStalenessChecker(
        client=FakeClient({"sqlite_mtime": "1000", "ingested_at": "2000"}),
    )
    captured: dict[str, float] = {}
    monkeypatch.setattr(checker, "_get_last_python_commit_time", lambda: 1500.0)

    def _changed_since(since_timestamp: float) -> list[str]:
        captured["since_timestamp"] = since_timestamp
        return ["tools/adg/adg_stale_guard.py"]

    monkeypatch.setattr(checker, "_get_files_changed_since", _changed_since)

    result = checker.check()

    assert result.is_stale is True
    assert result.ingest_time == 1000.0
    assert captured["since_timestamp"] == 1000.0
