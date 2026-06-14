"""Tests for tools/git/worktree_runtime_links.py (item #2 — runtime-cache junctions).

Hermetic: builds a fake primary checkout + worktree under tmp_path and verifies the
linker creates a directory link (junction on Windows / symlink on POSIX), is idempotent,
respects the disable env, and skips absent sources. No git, no network.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.git.worktree_runtime_links import (  # noqa: E402
    DEFAULT_LINK_DIRS,
    link_dirs_from_env,
    link_runtime_dirs,
    summarize,
)


def _seed_primary(primary: Path, rel: str, content: str = "hot") -> Path:
    d = primary / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / "marker.txt").write_text(content, encoding="utf-8")
    return d


def test_links_existing_cache_dir(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "wt"
    worktree.mkdir(parents=True)
    _seed_primary(primary, "data/cache/chromadb", "vectors")

    report = link_runtime_dirs(primary, worktree, dirs=("data/cache/chromadb",))

    assert [d["dir"] for d in report["linked"]] == ["data/cache/chromadb"]
    assert report["errors"] == []
    linked = worktree / "data/cache/chromadb"
    assert linked.exists()
    # Content is reachable THROUGH the link back to the primary.
    assert (linked / "marker.txt").read_text(encoding="utf-8") == "vectors"


def test_idempotent_second_call_skips(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "wt"
    worktree.mkdir(parents=True)
    _seed_primary(primary, "data/cache/sparse")

    first = link_runtime_dirs(primary, worktree, dirs=("data/cache/sparse",))
    assert len(first["linked"]) == 1

    second = link_runtime_dirs(primary, worktree, dirs=("data/cache/sparse",))
    assert second["linked"] == []
    assert any(s["reason"] == "destination_exists" for s in second["skipped"])


def test_absent_source_is_skipped(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    primary.mkdir()
    worktree = tmp_path / "wt"
    worktree.mkdir()

    report = link_runtime_dirs(primary, worktree, dirs=("data/cache/nope",))
    assert report["linked"] == []
    assert any(s["reason"] == "source_absent" for s in report["skipped"])


def test_disable_env_no_ops(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "wt"
    worktree.mkdir(parents=True)
    _seed_primary(primary, "data/cache/r1b")

    report = link_runtime_dirs(
        primary, worktree, dirs=("data/cache/r1b",), env={"WORKTREE_LINK_DIRS_DISABLE": "1"}
    )
    assert report["disabled"] is True
    assert report["linked"] == []
    assert not (worktree / "data/cache/r1b").exists()


def test_same_root_is_noop(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    _seed_primary(primary, "data/cache/chromadb")
    report = link_runtime_dirs(primary, primary, dirs=("data/cache/chromadb",))
    assert report["linked"] == []
    assert any(s["reason"] == "primary_unresolved_or_same" for s in report["skipped"])


def test_env_override_parses_csv() -> None:
    dirs = link_dirs_from_env({"WORKTREE_LINK_DIRS": "a/b, c/d ,"})
    assert dirs == ("a/b", "c/d")
    # Unset -> defaults.
    assert link_dirs_from_env({}) == DEFAULT_LINK_DIRS


def test_summarize_mentions_linked_dirs(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "wt"
    worktree.mkdir(parents=True)
    _seed_primary(primary, "data/cache/chromadb")
    report = link_runtime_dirs(primary, worktree, dirs=("data/cache/chromadb",))
    text = summarize(report)
    assert "data/cache/chromadb" in text
