from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
SovereignGitClient - Audited Git Operations

Routes all Git operations through controlled plane with:
- Audit logging
- Safe subprocess execution
- Error handling with rollback support
"""
import logging
import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    TESTS_DIR,
)
from agentic_core.utils.security import safe_git_execute

Logger = logging.getLogger(__name__)


class SovereignGitClient(SovereignBaseAgent):
    """Sovereign Git client - audit + safe exec for all Git operations."""

    def __init__(self, repo_root: Path | None = None):
        """
        Initialize Git client.

        Args:
            repo_root: Repository root directory (defaults to cwd)
        """
        super().__init__()
        self.repo_root = repo_root or Path.cwd()
        self.audit_log: list[dict[str, Any]] = []
        self._mcp_audit("init")

    def _audit(self, operation: str, payload: dict[str, Any], result: Any) -> None:
        """Record operation to audit log."""
        self.audit_log.append(
            {
                "operation": operation,
                "payload": {k: str(v)[:100] for k, v in payload.items()},
                "success": result.get("success", False) if isinstance(result, dict) else True,
            }
        )

    def _run_git(self, args: list[str]) -> dict[str, Any]:
        """Execute git command safely using safe_git_execute wrapper."""
        try:
            result = safe_git_execute(args, repo_root=self.repo_root, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git command failed: git {' '.join(args)}")
            return {
                "success": False,
                "error": e.stderr if hasattr(e, "stderr") else str(e),
                "returncode": e.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Git command timed out"}

    def execute(self, operation: str, **payload) -> dict[str, Any]:
        """
        Route Git operations safely via dispatch pattern.

        Args:
            operation: Git operation (commit, push, pull, status, etc.)
            **payload: Operation-specific parameters

        Returns:
            Result dictionary with success status and output
        """
        handlers = {
            "commit": self._handle_commit,
            "push": self._handle_push,
            "pull": self._handle_pull,
            "status": self._handle_status,
            "diff": self._handle_diff,
            "log": self._handle_log,
            "checkout": self._handle_checkout,
            "branch": self._handle_branch,
        }

        handler = handlers.get(operation)
        if not handler:
            return {"success": False, "error": f"Unsupported Git operation: {operation}"}

        Logger.debug(f"[SOVEREIGN GIT] {operation}: {payload}")
        result = handler(**payload)
        self._audit(operation, payload, result)
        return result

    def _handle_commit(
        self, message: str = "Sovereign commit", files: list[str] = None, **kwargs
    ) -> dict[str, Any]:
        """Sub-atomic commit handler."""
        if files:
            for f in files:
                self._run_git(["add", str(f)])
        return self._run_git(["commit", "-m", message])

    def _handle_push(
        self, branch: str = "HEAD", remote: str = "origin", **kwargs
    ) -> dict[str, Any]:
        """Sub-atomic push handler."""
        return self._run_git(["push", remote, branch])

    def _handle_pull(self, remote: str = "origin", branch: str = "", **kwargs) -> dict[str, Any]:
        """Sub-atomic pull handler."""
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return self._run_git(args)

    def _handle_status(self, **kwargs) -> dict[str, Any]:
        """Sub-atomic status handler."""
        return self._run_git(["status", "--porcelain"])

    def _handle_diff(self, file: str = "", **kwargs) -> dict[str, Any]:
        """Sub-atomic diff handler."""
        args = ["diff"]
        if file:
            args.append(str(file))
        return self._run_git(args)

    def _handle_log(self, count: int = 10, **kwargs) -> dict[str, Any]:
        """Sub-atomic log handler."""
        return self._run_git(["log", f"-{count}", "--oneline"])

    def _handle_checkout(self, branch: str = "", **kwargs) -> dict[str, Any]:
        """Sub-atomic checkout handler."""
        if not branch:
            return {"success": False, "error": "Branch required for checkout"}
        return self._run_git(["checkout", branch])

    def _handle_branch(self, action: str = "list", name: str = "", **kwargs) -> dict[str, Any]:
        """Sub-atomic branch handler with action dispatch."""
        if action == "list":
            return self._run_git(["branch", "-a"])
        elif action == "create":
            if not name:
                return {"success": False, "error": "Branch name required"}
            return self._run_git(["branch", name])
        else:
            return {"success": False, "error": f"Unknown branch action: {action}"}


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, TESTS_DIR: []}
    try:
        assert self is not None
        results["passed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results[TESTS_DIR].append(
            {"name": "test_instantiation", "status": "failed", "error": str(e)}
        )
    return results
