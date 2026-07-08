"""Git artifact auto-commit integration for ADG generation."""

from __future__ import annotations

import subprocess
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() or (candidate / "agentic_core").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


def _format_subprocess_failure(exc: subprocess.SubprocessError) -> tuple[str, str]:
    """Return bounded stdout/stderr fragments for logging."""
    stdout = getattr(exc, "stdout", "") or ""
    stderr = getattr(exc, "stderr", "") or ""
    return stdout.strip()[:200], stderr.strip()[:200]


ROOT = _discover_repo_root(Path(__file__).resolve().parent)


def _auto_commit_artifacts(adg_dir: Path, ts: str, node_count: int, edge_count: int) -> None:
    """Automatically commit newly generated ADG artifacts to git."""
    print("[ADG] Auto-committing artifacts to git...")

    try:
        artifact_patterns = [
            f"adg_snapshot_{ts}.json",
            f"adg_indexed_{ts}.sqlite",
            f"adg_file_graph_{ts}.json",
            f"adg_symbol_graph_{ts}.json",
            f"adg_governance_graph_{ts}.json",
            f"adg_graphsnap_{ts}.json",
        ]

        staged_count = 0
        skipped_ignored_count = 0

        for pattern in artifact_patterns:  # tqdm: bounded ~6-item list, no bar needed
            artifact_path = adg_dir / pattern
            if artifact_path.exists():
                try:
                    artifact_arg = str(artifact_path.resolve().relative_to(ROOT))
                except ValueError:
                    print(
                        f"[ADG] WARNING: Artifact is outside repository root; skipping auto-commit: {artifact_path}"
                    )
                    continue
                # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
                check_ignore = subprocess.run(
                    ["git", "check-ignore", artifact_arg],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if check_ignore.returncode == 0:
                    skipped_ignored_count += 1
                    continue
                if check_ignore.returncode != 1:
                    _stdout = (check_ignore.stdout or "").strip()[:200]
                    _stderr = (check_ignore.stderr or "").strip()[:200]
                    print("[ADG] WARNING: git check-ignore failed; skipping auto-commit")
                    if _stdout:
                        print(f"      stdout: {_stdout}")
                    if _stderr:
                        print(f"      stderr: {_stderr}")
                    return

                # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
                subprocess.run(
                    ["git", "add", artifact_arg],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
                staged_count += 1

        # Verify we are in a git worktree before staging deletions/commit.
        worktree_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if worktree_check.returncode != 0:
            print("[ADG] WARNING: Repository is not a git worktree; skipping auto-commit")
            return

        # Stage deletions of old artifacts only when Git knows this ignored tree.
        # Otherwise `git add -u artifacts/adg/` fails with a pathspec error.
        tracked_check = subprocess.run(
            ["git", "ls-files", "--", ADG_ARTIFACTS_DIR + "/"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if tracked_check.returncode != 0:
            print("[ADG] WARNING: git ls-files failed; skipping artifact deletion staging")
            return
        if tracked_check.stdout.strip():
            # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
            subprocess.run(
                ["git", "add", "-u", ADG_ARTIFACTS_DIR + "/"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
        else:
            print("[ADG] Git: no tracked ADG artifacts to stage for deletion")

        if skipped_ignored_count:
            print(
                f"[ADG] Git: skipped {skipped_ignored_count} ignored artifacts; staged {staged_count} trackable artifacts",
            )

        # If nothing is staged, skip commit cleanly
        # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
        staged_check = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if staged_check.returncode == 0:
            print("[ADG] Git: no staged artifact changes to commit")
            return

        commit_msg = f"ADG: regenerate artifacts {ts} - {node_count} modules, {edge_count} edges"
        # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
        result = subprocess.run(
            ["git", "commit", "--no-verify", "-m", commit_msg],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        print(f"[ADG] [OK] Git commit complete - {commit_msg}")

    except subprocess.CalledProcessError as e:
        stdout, stderr = _format_subprocess_failure(e)
        if "nothing to commit" in stdout or "nothing to commit" in stderr:
            print("[ADG] Git: no changes to commit (artifacts already committed)")
        else:
            print(f"[ADG] WARNING: Git commit failed (exit {e.returncode}):")
            if stdout:
                print(f"      stdout: {stdout}")
            if stderr:
                print(f"      stderr: {stderr}")
    except subprocess.TimeoutExpired as e:
        print(f"[ADG] WARNING: Git command timed out after {e.timeout}s")
    except FileNotFoundError:
        print("[ADG] WARNING: Git executable not found; skipping auto-commit")
