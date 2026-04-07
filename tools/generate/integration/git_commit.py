"""Git artifact auto-commit integration for ADG generation."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


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

        for pattern in artifact_patterns:
            artifact_path = adg_dir / pattern
            if artifact_path.exists():
                # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
                check_ignore = subprocess.run(
                    ["git", "check-ignore", str(artifact_path)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if check_ignore.returncode == 0:
                    skipped_ignored_count += 1
                    continue

                # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
                subprocess.run(
                    ["git", "add", str(artifact_path)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
                staged_count += 1

        # Stage deletions of old artifacts (moved to _archive/)
        # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
        subprocess.run(
            ["git", "add", "-u", "artifacts/adg/"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

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

        commit_msg = f"ADG: regenerate artifacts {ts} — {node_count} modules, {edge_count} edges"
        # ruff: noqa: S603,S607 - Git command is trusted, internal tool usage
        result = subprocess.run(
            ["git", "commit", "--no-verify", "-m", commit_msg],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        print(f"[ADG] [OK] Git commit complete — {commit_msg}")

    except (ValueError, TypeError, RuntimeError) as e:
        if "nothing to commit" in e.stdout or "nothing to commit" in e.stderr:
            print("[ADG] Git: no changes to commit (artifacts already committed)")
        else:
            print(f"[ADG] WARNING: Git commit failed (exit {e.returncode}):")
            print(f"      stdout: {e.stdout.strip()[:200]}")
            print(f"      stderr: {e.stderr.strip()[:200]}")
