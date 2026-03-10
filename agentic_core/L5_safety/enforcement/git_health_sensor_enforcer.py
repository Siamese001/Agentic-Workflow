#!/usr/bin/env python3
"""Git Health Sensor - Deterministic binary sensor for Git repository health.

Zero-Ambiguity Standard: Named with _sensor.py suffix
Category: SENSOR (Deterministic binary check)

Monitors Git repository health and provides structured context for L0 healing operations.
Detects uncommitted changes, merge conflicts, and detached HEAD states.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from agentic_core.L5_safety.config.detection_signal_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DetectionSignal,
    FailureContext,
    ImpactAssessment,
    ImpactScope,
    Severity,
)

Logger = logging.getLogger(__name__)


class GitHealthSensor:
    """
    Deterministic binary sensor for Git repository health.

    Performs the following checks:
    - Uncommitted Changes: Dirty working directory (Severity.HIGH)
    - Merge Conflicts: Active conflict markers (Severity.CRITICAL)
    - Detached HEAD: Risk to mission trace persistence (Severity.MEDIUM)
    """

    def __init__(self, repo_root: Path | str | None = None):
        """
        Initialize the Git health sensor.

        Args:
            repo_root: Path to the Git repository root. If None, uses current directory.
        """
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.sensor_name = "GitHealthSensor"

    def _run_git_command(self, args: list[str]) -> tuple[int, str, str]:
        """
        Run a git command and return exit code, stdout, stderr.

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            # guardian: allow-magic-config (pre-existing, moved from L0)
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Git command timed out"
        except FileNotFoundError:
            return -1, "", "Git not found in PATH"
        # guardian: allow-silent-swallow (pre-existing, moved from L0)
        except Exception as e:
            return -1, "", str(e)

    def _check_uncommitted_changes(self) -> DetectionSignal | None:
        """
        Check for uncommitted changes in the working directory.

        Returns:
            DetectionSignal if dirty, None if clean
        """
        exit_code, stdout, stderr = self._run_git_command(["status", "--porcelain"])

        if exit_code != 0:
            Logger.warning(f"Git status failed: {stderr}")
            return None

        if not stdout.strip():
            return None  # Clean working directory

        # Parse affected files
        affected_files = []
        for line in stdout.strip().split("\n"):
            if line:
                # Format: XY filename
                file_path = line[3:].strip()
                if file_path:
                    affected_files.append(Path(file_path))

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="uncommitted_changes",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Working directory has {len(affected_files)} uncommitted changes. "
                f"Healing agents cannot safely perform atomic git commits on unsaved work.",
                related_files=affected_files,
                system_state={"git_status": full_status},
            ),
            severity=Severity.HIGH,
            impact=ImpactAssessment(
                scope=ImpactScope.SYSTEM_WIDE,
                affected_components=["git", "healing", "commit"],
                estimated_blast_radius=len(affected_files),
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
            suggested_fix="Commit or stash uncommitted changes before running healing operations.",
        )

    def _check_merge_conflicts(self) -> DetectionSignal | None:
        """
        Check for active merge conflicts.

        Returns:
            DetectionSignal if conflicts exist, None if clean
        """
        # Check for unmerged paths
        exit_code, stdout, stderr = self._run_git_command(["diff", "--name-only", "--diff-filter=U"])

        if exit_code != 0:
            Logger.warning(f"Git diff failed: {stderr}")
            return None

        if not stdout.strip():
            return None  # No conflicts

        # Parse conflicted files
        conflicted_files = [Path(f.strip()) for f in stdout.strip().split("\n") if f.strip()]

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="merge_conflicts",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Repository has {len(conflicted_files)} files with merge conflicts. "
                f"All automated structural surgery is BLOCKED until conflicts are resolved.",
                related_files=conflicted_files,
                system_state={"git_status": full_status},
            ),
            severity=Severity.CRITICAL,
            impact=ImpactAssessment(
                scope=ImpactScope.COMPONENT,
                affected_components=["git", "merge", "healing"],
                estimated_blast_radius=len(conflicted_files),
                recovery_complexity="high",
            ),
            is_auto_fixable=False,
            suggested_fix="Resolve merge conflicts manually before running healing operations.",
        )

    def _check_detached_head(self) -> DetectionSignal | None:
        """
        Check if repository is in detached HEAD state.

        Returns:
            DetectionSignal if detached, None if on branch
        """
        exit_code, stdout, stderr = self._run_git_command(["symbolic-ref", "-q", "HEAD"])

        if exit_code == 0:
            return None  # On a branch, not detached

        # Confirm detached state
        exit_code2, head_ref, _ = self._run_git_command(["rev-parse", "--short", "HEAD"])

        if exit_code2 != 0:
            return None  # Can't determine state

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="detached_head",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Repository is in detached HEAD state at {head_ref.strip()}. "
                f"This poses a risk to mission trace persistence.",
                system_state={"git_status": full_status, "head_ref": head_ref.strip()},
            ),
            severity=Severity.MEDIUM,
            impact=ImpactAssessment(
                scope=ImpactScope.SYSTEM_WIDE,
                affected_components=["git", "branch", "trace"],
                estimated_blast_radius=0,
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
            suggested_fix="Checkout a branch before running healing operations: git checkout <branch>",
        )

    def check_repository_health(self) -> DetectionSignal:
        """
        Perform all Git health checks and return the most severe signal.

        Returns:
            DetectionSignal with is_failure=True if any blocker found,
            or is_failure=False if repository is healthy.
        """
        Logger.info(f"[{self.sensor_name}] Checking repository health at {self.repo_root}")

        # Check in order of severity (CRITICAL first)
        signals = []

        # 1. Merge conflicts (CRITICAL)
        conflict_signal = self._check_merge_conflicts()
        if conflict_signal:
            signals.append(conflict_signal)
            Logger.warning(f"[{self.sensor_name}] Merge conflicts detected")

        # 2. Uncommitted changes (HIGH)
        uncommitted_signal = self._check_uncommitted_changes()
        if uncommitted_signal:
            signals.append(uncommitted_signal)
            Logger.warning(f"[{self.sensor_name}] Uncommitted changes detected")

        # 3. Detached HEAD (MEDIUM)
        detached_signal = self._check_detached_head()
        if detached_signal:
            signals.append(detached_signal)
            Logger.warning(f"[{self.sensor_name}] Detached HEAD detected")

        # Return most severe signal, or healthy signal if none
        if signals:
            # Sort by severity (highest first)
            signals.sort(key=lambda s: s.severity.value, reverse=True)
            return signals[0]

        # Repository is healthy
        Logger.info(f"[{self.sensor_name}] Repository is healthy")
        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="repository_health",
            is_failure=False,
            failure_context=FailureContext(
                error_message="Repository is healthy. No blockers detected.",
            ),
            severity=Severity.INFO,
            impact=ImpactAssessment(
                scope=ImpactScope.ISOLATED,
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
        )

    def get_all_signals(self) -> list[DetectionSignal]:
        """
        Get all detection signals (not just the most severe).

        Returns:
            List of all DetectionSignal objects for each check.
        """
        signals = []

        conflict_signal = self._check_merge_conflicts()
        if conflict_signal:
            signals.append(conflict_signal)

        uncommitted_signal = self._check_uncommitted_changes()
        if uncommitted_signal:
            signals.append(uncommitted_signal)

        detached_signal = self._check_detached_head()
        if detached_signal:
            signals.append(detached_signal)

        return signals


def check_git_health(repo_root: Path | str | None = None) -> DetectionSignal:
    """
    Convenience function to check Git repository health.

    Args:
        repo_root: Path to the Git repository root. If None, uses current directory.

    Returns:
        DetectionSignal with health status.
    """
    sensor = GitHealthSensor(repo_root)
    return sensor.check_repository_health()


if __name__ == "__main__":
    # Quick test
    import json

    signal = check_git_health()
    print(json.dumps(signal.to_dict(), indent=2, default=str))
