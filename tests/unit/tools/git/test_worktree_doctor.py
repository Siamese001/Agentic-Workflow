"""Tests for tools/git/worktree_doctor.py (items #4/#6 classification + #2 --link repair).

Builds a real temp git repo with chat/feat/codex worktrees and verifies the doctor's
classification, recommended actions, the .keep-worktree opt-out, and the --link path.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.git import worktree_doctor as doctor  # noqa: E402


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30, check=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t.t")
    _git(root, "config", "user.name", "t")
    (root / "f.txt").write_text("x", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "init")
    return root


def _add_wt(repo: Path, name: str, branch: str, *, diverge: bool = False) -> Path:
    wt = repo.parent / ".chat-worktrees" / name
    _git(repo, "worktree", "add", "-q", str(wt), "-b", branch)
    if diverge:
        (wt / "e.txt").write_text("e", encoding="utf-8")
        _git(wt, "add", "-A")
        _git(wt, "commit", "-qm", "unmerged")
    return wt


def _by_branch(result: dict) -> dict[str, dict]:
    return {r["branch"]: r for r in result["worktrees"]}


def test_classifies_kinds(repo: Path) -> None:
    _add_wt(repo, "chat-a", "chat/a")
    _add_wt(repo, "feat-b", "feat/b")
    _add_wt(repo, "codex-c", "codex/c")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    rows = _by_branch(result)
    assert rows["main"]["kind"] == "protected"
    assert rows["chat/a"]["kind"] == "ephemeral"
    assert rows["feat/b"]["kind"] == "long-lived"
    assert rows["codex/c"]["kind"] == "non-canonical"
    assert rows["codex/c"]["canonical"] is False
    assert rows["feat/b"]["canonical"] is True


def test_merged_clean_ephemeral_is_reapable(repo: Path) -> None:
    _add_wt(repo, "chat-a", "chat/a")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    row = _by_branch(result)["chat/a"]
    assert row["merged"] is True
    assert row["clean"] is True
    assert row["action"].startswith("REAPABLE")


def test_merged_clean_feat_is_stale_manual(repo: Path) -> None:
    _add_wt(repo, "feat-b", "feat/b")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    row = _by_branch(result)["feat/b"]
    assert row["action"].startswith("stale-merged")


def test_unmerged_is_active(repo: Path) -> None:
    _add_wt(repo, "chat-a", "chat/a", diverge=True)
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    row = _by_branch(result)["chat/a"]
    assert row["merged"] is False
    assert row["action"].startswith("active")


def test_keep_marker_surfaced(repo: Path) -> None:
    wt = _add_wt(repo, "chat-a", "chat/a")
    (wt / ".keep-worktree").write_text("", encoding="utf-8")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    row = _by_branch(result)["chat/a"]
    assert row["keep_marker"] is True
    assert "keep-worktree" in row["action"]


def test_render_table_runs(repo: Path) -> None:
    _add_wt(repo, "chat-a", "chat/a")
    _add_wt(repo, "codex-c", "codex/c")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    text = doctor._render_table(result)
    assert "worktree-doctor" in text
    assert "non-canonical" in text


def test_do_link_into_worktree(repo: Path, capsys: pytest.CaptureFixture) -> None:
    # Seed a runtime cache in the primary, then --link it into a chat worktree.
    (repo / "data" / "cache" / "chromadb").mkdir(parents=True)
    (repo / "data" / "cache" / "chromadb" / "m.txt").write_text("v", encoding="utf-8")
    wt = _add_wt(repo, "chat-a", "chat/a")
    result = doctor.classify(repo, trunk_ref="main", do_fetch=False)
    rc = doctor._do_link(repo, result, str(wt))
    assert rc == 0
    linked = wt / "data" / "cache" / "chromadb"
    assert linked.exists()
    assert (linked / "m.txt").read_text(encoding="utf-8") == "v"
