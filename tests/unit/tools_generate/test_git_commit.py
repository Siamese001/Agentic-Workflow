"""Tests for ADG git artifact commit integration."""

from __future__ import annotations

from pathlib import Path
import subprocess

from tools.generate.integration import git_commit


def _completed(args: list[str], *, returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def test_auto_commit_skips_deletion_staging_when_no_tracked_adg_files(tmp_path, monkeypatch, capsys):
    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    (adg_dir / "adg_snapshot_07072026_2307.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(git_commit, "ROOT", tmp_path)
    monkeypatch.setattr(git_commit, "ADG_ARTIFACTS_DIR", "artifacts/adg")
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # noqa: ANN001
        calls.append(list(args))
        if args[:2] == ["git", "check-ignore"]:
            return _completed(list(args), returncode=0)
        if args[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
            return _completed(list(args), returncode=0, stdout="true\n")
        if args[:2] == ["git", "ls-files"]:
            return _completed(list(args), returncode=0, stdout="")
        if args[:3] == ["git", "diff", "--cached"]:
            return _completed(list(args), returncode=0)
        raise AssertionError(f"unexpected git command: {args}")

    monkeypatch.setattr(git_commit.subprocess, "run", fake_run)

    git_commit._auto_commit_artifacts(adg_dir, "07072026_2307", 10, 20)

    captured = capsys.readouterr()
    assert "no tracked ADG artifacts to stage for deletion" in captured.out
    assert ["git", "add", "-u", "artifacts/adg/"] not in calls
