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
        self.repo_root = Path(repo_root) if repo_root else Path(".")
        self._check_git_available()

    def _check_git_available(self) -> bool:
        """Check if git is available and this is a git repo."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
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

        # Stash any current changes
        subprocess.run(
            ["git", "stash", "push", "-m", f"Pre-repair stash for {name}"],
            cwd=self.repo_root,
            capture_output=True,
            check=False,
        )

        # Create checkpoint branch from current HEAD
        subprocess.run(
            ["git", "branch", name],
            cwd=self.repo_root,
            capture_output=True,
            check=False,
        )

        return name

    def rollback_to_checkpoint(self, checkpoint_name: str) -> bool:
        """Rollback to a checkpoint.

        Args:
            checkpoint_name: Name of checkpoint to rollback to

        Returns:
            True if rollback succeeded
        """
        try:
            # Reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", checkpoint_name],
                cwd=self.repo_root,
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[GitIntegration] Rollback failed: {e}")
            return False

    def get_current_branch(self) -> str | None:
        """Get current git branch name.

        Returns:
            Branch name or None if not in a repo
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip() or None
        except subprocess.CalledProcessError:
            return None

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes.

        Returns:
            True if working tree is dirty
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def stage_files(self, file_paths: list[str]) -> bool:
        """Stage files for commit.

        Args:
            file_paths: List of file paths to stage

        Returns:
            True if staging succeeded
        """
        try:
            subprocess.run(
                ["git", "add"] + file_paths,
                cwd=self.repo_root,
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[GitIntegration] Staging failed: {e}")
            return False

    def commit_changes(self, message: str) -> bool:
        """Commit staged changes.

        Args:
            message: Commit message

        Returns:
            True if commit succeeded
        """
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_root,
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[GitIntegration] Commit failed: {e}")
            return False

    def get_changed_files(self) -> list[str]:
        """Get list of changed files.

        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # Line format: XY filename (where X/Y are status codes)
                    parts = line.split()
                    if len(parts) >= 2:
                        files.append(parts[1])

            return files
        except subprocess.CalledProcessError:
            return []

    def get_summary(self) -> dict[str, Any]:
        """Get git status summary.

        Returns:
            Dictionary with git status
        """
        return {
            "repo_root": str(self.repo_root),
            "current_branch": self.get_current_branch(),
            "has_uncommitted_changes": self.has_uncommitted_changes(),
            "changed_files": self.get_changed_files(),
        }
