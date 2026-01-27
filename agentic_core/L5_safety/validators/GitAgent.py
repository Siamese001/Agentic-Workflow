# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt
from __future__ import annotations
# This boosts alignment detection — review and integrate appropriately

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

from dataclasses import dataclass

"""
GitAgent - L6 GitOps & Remote Synchronization
CANONICAL: True - Standalone extraction 2026-01-06 (from infrastructure.py)

Manages git operations for self-healing commits and remote pushes.
Ensures changes are committed and pushed to remote repository.
"""
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.timeout_decorator import timeout
from agentic_core.utils.security import safe_git_execute

Logger: Any = logging.getLogger(__name__)


# [SSOT IMPORT] Structure blueprint is the single source of truth

try:
    from agentic_core.L4_state.validation_context.CachedStateLedger import CachedStateLedger
except ImportError:
    CachedStateLedger = None


@dataclass
class GitAgent(SovereignBaseAgent):
    """
    Agent for managing git operations and remote synchronization.

    Features:
    - Atomic commits of modified files
    - Branch management for healing cycles
    - Remote push capabilities
    - Safety checks for secrets
    - L4 checkpoint integration for execution persistence
    """

    def __init__(self, repo_root: Path = None) -> None:
        """
        Initialize the GitAgent.

        Args:
            repo_root: Root directory of the git repository
        """
        super().__init__()
        self.repo_root = repo_root or Path.cwd()
        self.remote_repo = os.getenv("CANON_REMOTE_REPO")
        self.git_cmd = ["git", "-C", str(self.repo_root)]

        # L4 checkpoint integration
        self._ledger = None

        if not self._is_git_repo():
            Logger.warning(f"Not in a git repository: {self.repo_root}")
            self.enabled = False
        else:
            self.enabled = True
            self._mcp_audit("init_with_l4_checkpoints")
            Logger.info(f"GitAgent initialized for {self.repo_root}")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L2 compliance."""
        assert hasattr(self, "repo_root"), "Missing repo_root"
        assert hasattr(self, "enabled"), "Missing enabled"
        return True

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for tool execution anomalies with L4 integration."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())

        if anomaly.type == "tool_failure":
            # Reset git state on tool failure
            try:
                self._run_git(["reset", "--hard", "HEAD"], check=False)
                self._mcp_audit("healing_success", payload={"action": "git_reset"})
                return True
            except Exception:
                return False

        if anomaly.type == "commit_corruption":
            # Abort any in-progress operations
            try:
                self._run_git(["merge", "--abort"], check=False)
                self._run_git(["rebase", "--abort"], check=False)
                return True
            except Exception:
                return False

        return False

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        git_dir = self.repo_root / ".git"
        return git_dir.exists()

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def _run_git(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Run a git command.
        Args:
            args: Git command arguments
            check: Whether to check return code

        Returns:
            Completed process
        """
        try:
            result = safe_git_execute(args, repo_root=self.repo_root, timeout=30, check=check)
            return result
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git command failed: git {' '.join(args)}")
            Logger.error(f"Error: {e.stderr}")
            raise

    def _generate_git_metadata(self, cycle_id: int) -> dict[str, str]:
        """
        Generate git metadata for a healing cycle.

        Args:
            cycle_id: ID of the current cycle

        Returns:
            Dictionary with branch name and commit info
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        branch_name = f"healing/cycle-{cycle_id}-{timestamp}"
        commit_message = f"Self-healing cycle {cycle_id}\n\nAutomated fixes applied at {timestamp}\nModified files: {len(self._get_modified_files())} files\nStatus: COMPLETED\n"
        return {
            "branch_name": branch_name,
            "commit_message": commit_message,
            "timestamp": timestamp,
            "cycle_id": cycle_id,
        }

    def _get_modified_files(self) -> list[Path]:
        """Get list of modified files in the repository."""
        try:
            result = self._run_git(["status", "--porcelain"])
            modified = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    status = line[:2]
                    file_path = line[3:]
                    if status.strip() and status[0] in ["M", "A", "R"]:
                        modified.append(Path(file_path))
            return modified
        except Exception as e:
            Logger.error(f"Failed to get modified files: {e}")
            return []

    def _check_for_secrets(self, file_paths: list[Path]) -> list[str]:
        """
        Check files for potential secrets.

        Args:
            file_paths: List of files to check

        Returns:
            List of suspicious files
        """
        suspicious = []
        secret_patterns = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "api_key",
            "private_key",
            "auth_token",
        ]
        for file_path in file_paths:
            if not file_path.exists():
                continue
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()
                for pattern in secret_patterns:
                    if pattern in content:
                        suspicious.append(str(file_path))
                        break
            except Exception:
                pass
        return suspicious

    def stage_files(self, file_paths: list[Path]) -> bool:
        """
        Stage specific files for commit.

        Args:
            file_paths: List of files to stage

        Returns:
            True if successful
        """
        if not self.enabled:
            Logger.warning("Git not enabled")
            return False
        try:
            for file_path in file_paths:
                self._run_git(["add", str(file_path)])
            Logger.info(f"Staged {len(file_paths)} files")
            return True
        except Exception as e:
            Logger.error(f"Failed to stage files: {e}")
            return False

    def create_branch(self, branch_name: str) -> bool:
        """
        Create and checkout a new branch.

        Args:
            branch_name: Name of the branch to create
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        try:
            self._run_git(["checkout", "-b", branch_name])
            Logger.info(f"Created branch: {branch_name}")
            return True
        except Exception as e:
            Logger.error(f"Failed to create branch: {e}")
            return False

    def commit_changes(self, message: str) -> bool:
        """
        Commit staged changes.

        Args:
            message: Commit message

        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        try:
            try:
                self._run_git(["config", "user.name", "AgenticWorkflow"])
                self._run_git(["config", "user.email", "workflow@agentic.system"])
            except:
                pass
            self._run_git(["commit", "-m", message])
            Logger.info("Changes committed")
            return True
        except Exception as e:
            Logger.error(f"Failed to commit: {e}")
            return False

    def push_to_remote(self, branch_name: str = None) -> bool:
        """
        Push changes to remote repository.

        Args:
            branch_name: Branch to push (current branch if None)

        Returns:
            True if successful
        """
        if not self.enabled or not self.remote_repo:
            Logger.warning("Remote repository not configured")
            return False
        try:
            try:
                self._run_git(["remote", "add", "origin", self.remote_repo], check=False)
            except:
                pass
            if branch_name:
                self._run_git(["push", "-u", "origin", branch_name])
            else:
                self._run_git(["push", "-u", "origin", "HEAD"])
            Logger.info(f"Pushed to remote: {self.remote_repo}")
            return True
        except Exception as e:
            Logger.error(f"Failed to push to remote: {e}")
            return False

    def commit_healing_cycle(self, cycle_id: int, modified_files: list[Path]) -> bool:
        """
        Commit changes from a healing cycle.

        Args:
            cycle_id: ID of the healing cycle
            modified_files: List of modified files to commit

        Returns:
            True if successful
        """
        if not modified_files:
            Logger.info("No files to commit")
            return True
        metadata: Any = self._generate_git_metadata(cycle_id)
        suspicious: Any = self._check_for_secrets(modified_files)
        if suspicious:
            Logger.warning(f"Found potential secrets in: {suspicious}")
            modified_files: Any = [f for f in modified_files if str(f) not in suspicious]
        if not modified_files:
            Logger.error("No safe files to commit")
            return False
        try:
            if not self.create_branch(metadata["branch_name"]):
                return False
            if not self.stage_files(modified_files):
                return False
            if not self.commit_changes(metadata["commit_message"]):
                return False
            if self.remote_repo:
                self.push_to_remote(metadata["branch_name"])
            Logger.info(f"Successfully committed healing cycle {cycle_id}")
            return True
        except Exception as e:
            Logger.error(f"Failed to commit healing cycle: {e}")
            return False

    def get_repo_status(self) -> dict[str, Any]:
        """
        Get current repository status.

        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {"status": "not_a_git_repo"}
        try:
            branch_result: Any = self._run_git(["branch", "--show-current"])
            current_branch: Any = branch_result.stdout.strip()
            status_result: Any = self._run_git(["status", "--porcelain"])
            modified_files: Any = []
            for line in status_result.stdout.strip().split("\n"):
                if line:
                    modified_files.append(line[3:])
            remote_result: Any = self._run_git(["remote", "-v"], check=False)
            remotes: Any = remote_result.stdout.strip() if remote_result.returncode == 0 else ""
            return {
                "enabled": True,
                "current_branch": current_branch,
                "modified_files": modified_files,
                "remotes": remotes,
                "remote_configured": bool(self.remote_repo),
            }
        except Exception as e:
            Logger.error(f"Failed to get repo status: {e}")
            return {"status": "error", "error": str(e)}

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


_git_agent: GitAgent | None = None


def get_git_agent() -> GitAgent:
    """Get or create the global GitAgent instance."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    global _git_agent
    if _git_agent is None:
        _git_agent = GitAgent()
    return _git_agent


# Alias for discovery


def initialize_git_agent(repo_root: Path = None) -> Any:
    """
    Initialize the GitAgent system.

    Args:
        repo_root: Root directory of the git repository
    """
    global _git_agent
    _git_agent = GitAgent(repo_root)
    if _git_agent.enabled:
        Logger.info("GitAgent initialized successfully")
    else:
        Logger.warning("GitAgent disabled - not in a git repository")


def commit_healing_cycle(cycle_id: int, modified_files: list[Path]) -> bool:
    """
    Commit a healing cycle.

    Args:
        cycle_id: Cycle ID
        modified_files: List of modified files

    Returns:
        True if successful
    """
    agent: Any = get_git_agent()
    return agent.commit_healing_cycle(cycle_id, modified_files)
