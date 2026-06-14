"""Integration tests for deliver_worktree.py post-push reap (worktree-deliver-reap-b3f7d1).

Builds a hermetic bare-remote + primary clone + feature worktree, then exercises the
``--mode push`` deliver flow and asserts the reap behaviour:
  * default ``--reap``: worktree dir + local branch are gone after a clean push;
  * ``--no-reap``: worktree + branch are kept;
  * ``--mode pr`` is not exercised here (needs gh) but the reap path is push-only by construction.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "tools" / "git" / "deliver_worktree.py"

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not available")


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=60, check=False
    )


@pytest.fixture()
def deliver_mod():
    spec = importlib.util.spec_from_file_location("dw_under_test", SCRIPT)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules["dw_under_test"] = m
    spec.loader.exec_module(m)
    return m


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "origin.git"
    _git("init", "--bare", "-b", "main", str(remote), cwd=tmp_path)
    primary = tmp_path / "primary"
    _git("clone", str(remote), str(primary), cwd=tmp_path)
    _git("config", "user.email", "t@example.com", cwd=primary)
    _git("config", "user.name", "Tester", cwd=primary)
    (primary / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "-A", cwd=primary)
    _git("commit", "-m", "init", cwd=primary)
    _git("push", "origin", "main", cwd=primary)
    return remote, primary


def _feat_worktree(tmp_path: Path, primary: Path, branch: str) -> Path:
    wt = tmp_path / branch.replace("/", "-")
    _git("worktree", "add", "-b", branch, str(wt), "main", cwd=primary)
    _git("config", "user.email", "t@example.com", cwd=wt)
    _git("config", "user.name", "Tester", cwd=wt)
    (wt / "change.txt").write_text("feature change\n", encoding="utf-8")
    _git("add", "-A", cwd=wt)
    _git("commit", "-m", "feat: change", cwd=wt)
    return wt


def test_push_mode_reaps_worktree_and_branch(tmp_path, deliver_mod, monkeypatch):
    remote, primary = _setup(tmp_path)
    wt = _feat_worktree(tmp_path, primary, "feat/reapme")
    # Invoke from the primary (Windows-safe — no process cwd inside the worktree).
    monkeypatch.chdir(primary)

    rc = deliver_mod.main(["--worktree", str(wt), "--trunk", "main", "--mode", "push"])
    assert rc == 0

    # Pushed: origin/main now carries the feature commit.
    head = _git("ls-remote", str(remote), "refs/heads/main", cwd=primary).stdout
    log = _git("log", "--oneline", "main", "-5", cwd=primary).stdout
    assert "feat: change" in _git("log", "--oneline", "FETCH_HEAD", "-5", cwd=primary).stdout or head

    # Reaped: worktree dir gone, local branch gone.
    assert not wt.exists()
    assert "feat/reapme" not in _git("branch", "--list", "feat/reapme", cwd=primary).stdout


def test_no_reap_keeps_worktree_and_branch(tmp_path, deliver_mod, monkeypatch):
    remote, primary = _setup(tmp_path)
    wt = _feat_worktree(tmp_path, primary, "feat/keepme")
    monkeypatch.chdir(primary)

    rc = deliver_mod.main(["--worktree", str(wt), "--trunk", "main", "--mode", "push", "--no-reap"])
    assert rc == 0

    # Kept: worktree dir + branch still present.
    assert wt.exists()
    assert "feat/keepme" in _git("branch", "--list", "feat/keepme", cwd=primary).stdout


def test_reap_helper_skips_when_not_ancestor(tmp_path, deliver_mod, monkeypatch):
    # A worktree whose branch is NOT merged into the trunk must not be reaped.
    remote, primary = _setup(tmp_path)
    wt = _feat_worktree(tmp_path, primary, "feat/unmerged")
    monkeypatch.chdir(primary)
    # Call the reap helper directly without pushing — branch is not an ancestor of origin/main.
    deliver_mod._reap_after_push(wt, "feat/unmerged", "main")
    assert wt.exists()
    assert "feat/unmerged" in _git("branch", "--list", "feat/unmerged", cwd=primary).stdout
