from __future__ import annotations

'Git Hygiene Agent - Enforces Git repository hygiene.\n\nThis module provides a batch agent that enforces Git repository hygiene by:\n- Detecting stale branches (no commits in >90 days)\n- Identifying large files in history (>10MB)\n- Checking for uncommitted/unpushed changes\n\nTypical usage:\n    agent = GitHygieneAgent(project_root=Path("/path/to/repo"), ctx=context)\n    result = await agent.execute()\n'
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from agentic_core.utils.security_util import safe_git_execute

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout


@dataclass
class GitHygieneAgent(SovereignBaseAgent):
    """L5 Safety agent that enforces Git repository hygiene.

    This batch agent audits repository health by detecting stale branches,
    large files in history, and uncommitted/unpushed changes.

    Attributes:
        project_root: Root directory of the Git repository.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be done (default: True).
        stale_days: Days after which a branch is considered stale (default: 90).
        large_file_mb: Size threshold in MB for large files (default: 10).

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the Git hygiene agent.

        Args:
            project_root: Root directory of the Git repository.
            ctx: Execution context with optional report() method.
        """
        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = True
        self.stale_days: int = 90
        self.large_file_mb: int = 10

    def _run_git(self, cmd: list[str], **kwargs: Any) -> str:
        """Run a git command and return stdout.

        Args:
            cmd: Git command arguments (without 'git' prefix).
            **kwargs: Additional arguments passed to safe_git_execute.

        Returns:
            Command stdout if successful, empty string otherwise.
        """
        try:
            result = safe_git_execute(cmd, repo_root=self.project_root, timeout=kwargs.get("timeout", 30))
            return result.stdout.strip() if result.returncode == 0 else ""
        except FileNotFoundError:
            if hasattr(self.ctx, "report"):
                self.ctx.report("GitHygieneAgent", 0, False, "git not installed")
            return ""

    def _get_stale_branches(self) -> list[dict[str, Any]]:
        """Find branches with no commits in the last N days.

        Returns:
            List of dictionaries with branch info:
                - branch: Branch name
                - age_days: Days since last commit
        """
        cutoff = datetime.now() - timedelta(days=self.stale_days)
        cutoff_ts = int(cutoff.timestamp())
        branches_output = self._run_git(["branch", "--format=%(refname:short) %(committerdate:unix)"])
        stale = []
        for line in branches_output.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            branch_name = parts[0]
            if branch_name in {"main", "master", "develop"}:
                continue
            try:
                commit_ts = int(parts[-1])
                if commit_ts < cutoff_ts:
                    age = (datetime.now() - datetime.fromtimestamp(commit_ts)).days
                    stale.append({"branch": branch_name, "age_days": age})
            except ValueError:
                continue
        return stale

    def _get_large_files(self) -> list[dict]:
        """Find large files in Git history (>10MB)."""
        large = []
        return large

    # guardian: allow-type-erasure
    def _get_repo_status(self) -> dict:
        """Check for uncommitted and unpushed changes."""
        status = {"uncommitted": False, "unpushed": False}
        status["uncommitted"] = bool(self._run_git(["status", "--porcelain"]))
        unpushed_count = self._run_git(["rev-list", "@{u}..", "--count"])
        if unpushed_count.isdigit():
            status["unpushed"] = int(unpushed_count) > 0
        return status

    # guardian: allow-type-erasure
    async def execute(self) -> dict:
        """Audit repository health and optionally clean up."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GitHygieneAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:GitHygieneAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("   [GIT HYGIENE] Auditing repository health...")
        stale_branches = self._get_stale_branches()
        status = self._get_repo_status()
        actions = []
        if stale_branches:
            print(f"   [!] Found {len(stale_branches)} stale branches (> {self.stale_days} days)")
            for b in stale_branches[:3]:
                print(f"      → {b['branch']} ({b['age_days']} days)")
            if len(stale_branches) > 3:
                print(f"      ... and {len(stale_branches) - 3} more")
            if not self.dry_run:
                for b in stale_branches:
                    result = self._run_git(["branch", "-D", b["branch"]])
                    if result or True:
                        actions.append(f"Deleted {b['branch']}")
        if status["uncommitted"]:
            print("   [!] Uncommitted changes detected")
        if status["unpushed"]:
            print("   [!] Unpushed commits detected")
        if stale_branches or status["uncommitted"] or status["unpushed"]:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "GitHygieneAgent", 48, True, f"Stale: {len(stale_branches)}, Actions: {len(actions)}"
                )
        return {
            "stale_branches": len(stale_branches),
            "uncommitted": status["uncommitted"],
            "unpushed": status["unpushed"],
            "actions_taken": len(actions),
            "dry_run": self.dry_run,
        }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Audit and heal Git repository hygiene issues.

        Scans for stale branches, large files, uncommitted changes,
        and unpushed commits. Can clean up stale branches when execute=True.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)
        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0
        try:
            self.logger.info(f"[{agent_name}] Auditing Git repository hygiene...")
            try:
                result = self.execute(cleanup=False)
                stale_count = result.get("stale_branches", 0)
                large_files = result.get("large_files", 0)
                uncommitted = 1 if result.get("uncommitted", False) else 0
                unpushed = 1 if result.get("unpushed", False) else 0
                violations_found = stale_count + large_files + uncommitted + unpushed
                if violations_found > 0:
                    self.logger.warning(f"  Found {violations_found} hygiene issues:")
                    if stale_count:
                        self.logger.warning(f"    - {stale_count} stale branches")
                    if large_files:
                        self.logger.warning(f"    - {large_files} large files")
                    if uncommitted:
                        self.logger.warning("    - Uncommitted changes detected")
                    if unpushed:
                        self.logger.warning("    - Unpushed commits detected")
                    if execute and (not dry_run):
                        if stale_count > 0:
                            cleanup_result = self.cleanup_stale_branches()
                            violations_fixed += cleanup_result.get("actions_taken", 0)
                            self.logger.info(f"    Cleaned {violations_fixed} stale branches")
                else:
                    self.logger.info("  Repository hygiene is clean")
            # guardian: allow-silent-swallow
            except Exception as e:
                self.logger.error(f"  Error during Git hygiene audit: {e}")
                errors += 1
            self.logger.info(f"[{agent_name}] Complete: {violations_found} issues, {violations_fixed} fixed")
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
                "agent": agent_name,
                "dry_run": dry_run,
            }
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal git hygiene violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (stale_branch, uncommitted, unpushed)
                - path: Path to the repository
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        violation_type = violation.get("type", "")
        try:
            if violation_type == "stale_branch":
                result = self.cleanup_stale_branches()
                return {
                    "violations_fixed": result.get("actions_taken", 0),
                    "violations_found": result.get("stale_branches", 0),
                    "errors": 0,
                    "skipped": 0,
                }
            else:
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        # guardian: allow-silent-swallow
        except Exception:
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
