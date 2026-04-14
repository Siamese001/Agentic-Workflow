"""Git integration for ADG Repair Orchestrator.

Provides git checkpointing and rollback capabilities.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GitIntegration:
    """Git integration for repair operations.

    Provides:
    - Pre-fix git checkpoints (branches/tags)
    - Post-commit verification
    - Rollback to checkpoints
    - Change summary generation

    Usage:
        git = GitIntegration(repo_root=Path("."))

        checkpoint = git.create_checkpoint("repair-20240312-0512")

        # Apply fixes...

        if not git.verify_clean_working_tree():
            git.rollback_to_checkpoint(checkpoint)
    """

    def __init__(self, repo_root: Path | str | None = None):
        """Initialize git integration.

        Args:
            repo_root: Repository root path (default: current directory)
        """
        self.repo_root = Path(repo_root).resolve() if repo_root else Path(".").resolve()
        self.git_available = self._check_git_available()

    def _run_git(self, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
        if not self.git_available:
            raise RuntimeError(f"Git is unavailable or {self.repo_root} is not a repository")

        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=check,
            timeout=30,
        )

    def _check_git_available(self) -> bool:
        """Check if git is available and this is a git repo."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def create_checkpoint(self, name: str | None = None) -> str:
        """Create a git checkpoint (stash + branch).

        Args:
            name: Checkpoint name (default: auto-generated)

        Returns:
            Checkpoint name
        """
        if name is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            name = f"adg-repair-{timestamp}"

        if not self.git_available:
            raise RuntimeError("Cannot create checkpoint outside a git repository")

        existing = self._run_git(["rev-parse", "--verify", name], check=False)
        if existing.returncode == 0:
            raise RuntimeError(f"Checkpoint already exists: {name}")

        self._run_git(["branch", name])

        return name

    def rollback_to_checkpoint(self, checkpoint_name: str) -> bool:
        """Rollback to a checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to rollback to

        Returns:
            True if rollback succeeded
        """
        try:
            verify = self._run_git(["rev-parse", "--verify", checkpoint_name], check=False)
            if verify.returncode != 0:
                return False
            self._run_git(["reset", "--hard", checkpoint_name])
            return True
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def get_current_branch(self) -> str | None:
        """Get current git branch name.

        Returns:
            Branch name or None if not in a repo
        """
        try:
            result = self._run_git(["branch", "--show-current"])
            return result.stdout.strip() or None
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes.

        Returns:
            True if working tree is dirty
        """
        try:
            result = self._run_git(["status", "--porcelain"])
            return bool(result.stdout.strip())
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def stage_files(self, file_paths: list[str]) -> bool:
        """Stage files for commit.

        Args:
            file_paths: List of file paths to stage

        Returns:
            True if staging succeeded
        """
        if not file_paths:
            return True
        try:
            self._run_git(["add", "--", *file_paths])
            return True
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def commit_changes(self, message: str) -> bool:
        """Commit staged changes.

        Args:
            message: Commit message

        Returns:
            True if commit succeeded
        """
        try:
            self._run_git(["commit", "-m", message])
            return True
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def get_changed_files(self) -> list[str]:
        """Get list of changed files.

        Returns:
            List of changed file paths
        """
        try:
            result = self._run_git(["status", "--porcelain=v1", "-z"])
            entries = [entry for entry in result.stdout.split("\x00") if entry]
            files: list[str] = []
            for entry in entries:
                payload = entry[3:]
                if " -> " in payload:
                    _, new_path = payload.split(" -> ", 1)
                    files.append(new_path)
                else:
                    files.append(payload)

            return files
        except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return []

    def get_summary(self) -> dict[str, Any]:
        """Get git status summary.

        Returns:
            Dictionary with git status
        """
        return {
            "repo_root": str(self.repo_root),
            "git_available": self.git_available,
            "current_branch": self.get_current_branch(),
            "has_uncommitted_changes": self.has_uncommitted_changes(),
            "changed_files": self.get_changed_files(),
        }
