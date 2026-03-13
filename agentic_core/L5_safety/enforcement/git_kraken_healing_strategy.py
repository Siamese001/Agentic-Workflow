from __future__ import annotations

"\nSovereign GitHub Healing Strategy – Phase 17D (Dec 27, 2025)\nAutonomous version control operations using GitHub MCP.\nReplaces all direct subprocess git calls.\nNote: GitKraken does not have an MCP server; using GitHub MCP instead.\n"
import logging
from typing import Any

from agentic_core.config.core.sovereign_config import get_sovereign_config

config = get_sovereign_config()
Logger: Any = logging.getLogger(__name__)


class GitKrakenHealingStrategy:
    """
    Autonomous healing for version control sovereignty.

    Detects and corrects version control violations by:
    - Grouping detected violations into atomic Git transactions
    - Creating healing commits via GitKraken MCP
    - Optionally creating PRs for review
    - Enforcing sovereignty over all version control operations
    """

    def __init__(self):
        """Initialize GitHub healing strategy with MCP tools."""
        self.name = "GitKrakenHealing"
        self.priority = 1
        self.commits_today = 0
        Logger.info("[L0 GITHUB HEALING] Strategy initialized")

    async def diagnose(self, issues: list[dict]) -> list[dict]:
        """
        Group detected violations into atomic Git transactions.

        Args:
            issues: List of issues from sovereignty auditor

        Returns:
            List of fix dictionaries with action details
        """
        fixes: Any = []
        if not config.GITKRAKEN_HEALING_ENABLED:
            Logger.info("[L0 GITHUB HEALING] GitHub healing disabled in config")
            return fixes
        file_groups: Any = {}
        for issue in issues:
            if "file" in issue:
                file_groups.setdefault(issue["file"], []).append(issue)
        for file_path, file_issues in file_groups.items():
            fixes.append(
                {
                    "action": "git_healing_commit",
                    "files": [file_path],
                    "file": file_path,
                    "summary": f"Sovereignty Fix: {len(file_issues)} violations in {file_path}",
                    "reason": f"Sovereignty Fix: {len(file_issues)} violations in {file_path}",
                    "details": file_issues,
                    "priority": self.priority,
                    "strategy": self.name,
                }
            )
        Logger.info(f"[L0 GITHUB HEALING] Diagnosed {len(fixes)} version control operations")
        return fixes

    async def apply(self, fix: dict, ctx: Any = None) -> bool:
        """
        Execute the commit and optional PR via the L3-routed MCP.

        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)

        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.GITKRAKEN_HEALING_ENABLED:
            Logger.warning("[L0 GITHUB HEALING] GitHub healing disabled in config")
            return False
        try:
            files: Any = fix.get("files", [])
            summary: Any = fix.get("summary", "Sovereignty healing commit")
            if not files:
                Logger.error("[L0 GITHUB HEALING] No files in fix")
                return False
            Logger.info(f"[L0 GITHUB HEALING] Creating healing commit for {len(files)} file(s)")
            result: Any = await self._create_healing_commit(files, summary)
            if result:
                commit_sha: Any = result.get("commit_sha", "unknown")
                Logger.info(
                    f"[L0 GITHUB HEALING] Commit Successful: {(commit_sha[:8] if len(commit_sha) > 8 else commit_sha)}"
                )
                if config.GITKRAKEN_HEALING_AUTO_PR:
                    pr_desc: Any = "\n".join(
                        [f"- {i.get('reason', 'Unknown reason')}" for i in fix.get("details", [])]
                    )
                    Logger.info("[L0 GITHUB HEALING] Creating PR for review")
                    await self._create_pr(summary, pr_desc)
                self.commits_today += 1
                return True
            else:
                Logger.error("[L0 GITHUB HEALING] Failed to create commit")
                return False
        except Exception as e:
            Logger.error(f"[L0 GITHUB HEALING] Sovereign Git operation failed: {e}")
            return False

    async def _create_healing_commit(self, files: list[str], message: str) -> dict[str, Any]:
        """
        Create a healing commit via GitHub MCP.

        Args:
            files: List of file paths to commit
            message: Commit message

        Returns:
            Result dictionary with commit SHA or None if failed
        """
        try:
            Logger.info(f"[L0 GITHUB HEALING] Committing {len(files)} file(s)")
            # Note: GitHub MCP uses mcp10_push_files which combines add+commit
            # This is a placeholder - actual implementation needs proper GitHub MCP integration
            Logger.warning("[L0 GITHUB HEALING] GitHub MCP integration not yet implemented")
            Logger.warning("[L0 GITHUB HEALING] Requires mcp10_push_files or mcp10_create_or_update_file")
            return None
        except Exception as e:
            Logger.error(f"[L0 GITHUB HEALING] Commit creation failed: {e}")
            return None

    async def _create_pr(self, title: str, description: str) -> bool:
        """
        Create a pull request via GitHub MCP.

        Args:
            title: PR title
            description: PR description

        Returns:
            True if PR created successfully, False otherwise
        """
        prefix = getattr(config, "GITKRAKEN_PR_TITLE_PREFIX", "[SOVEREIGN]")
        healing_branch = getattr(config, "GITKRAKEN_HEALING_BRANCH", "healing/auto-fix")
        try:
            full_title = f"{prefix} {title}"
            full_description = f"Autonomous system correction:\n{description}"
            Logger.info(f"[L0 GITHUB HEALING] Creating PR: {full_title}")
            # Note: GitHub MCP uses mcp10_create_pull_request
            # This is a placeholder - actual implementation needs proper GitHub MCP integration
            Logger.warning("[L0 GITHUB HEALING] GitHub MCP PR creation not yet implemented")
            Logger.warning("[L0 GITHUB HEALING] Requires mcp10_create_pull_request with owner/repo/head/base")
            return False
        except Exception as e:
            Logger.error(f"[L0 GITHUB HEALING] PR creation failed: {e}")
            return False

    def reset_daily_counter(self) -> Any:
        """Reset the daily commit counter (should be called at midnight)."""
        self.commits_today = 0
        Logger.info("[L0 GITHUB HEALING] Daily counter reset")


async def create_gitkraken_healing_strategy() -> GitKrakenHealingStrategy:
    """
    Factory function to create a GitKraken healing strategy.

    Returns:
        Initialized GitKrakenHealingStrategy instance
    """
    return GitKrakenHealingStrategy()
