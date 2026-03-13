from __future__ import annotations

"\nSovereign GitKraken Healing Strategy – Phase 17D (Dec 27, 2025)\nAutonomous version control operations using official GitKraken MCP.\nReplaces all direct subprocess git calls.\n"
import logging
from typing import Any


def get_git_client():
    raise NotImplementedError("P1_core.gitkraken_mcp_client_1 was removed; see RCA_P1_core_dead_imports.md")


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
        """Initialize GitKraken healing strategy with MCP client."""
        self.name = "GitKrakenHealing"
        self.priority = 1
        self.git_client = get_git_client()
        self.commits_today = 0
        Logger.info("[L0 GITKRAKEN HEALING] Strategy initialized")

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
            Logger.info("[L0 GITKRAKEN HEALING] GitKraken healing disabled in config")
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
        Logger.info(f"[L0 GITKRAKEN HEALING] Diagnosed {len(fixes)} version control operations")
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
            Logger.warning("[L0 GITKRAKEN HEALING] GitKraken healing disabled in config")
            return False
        try:
            files: Any = fix.get("files", [])
            summary: Any = fix.get("summary", "Sovereignty healing commit")
            if not files:
                Logger.error("[L0 GITKRAKEN HEALING] No files in fix")
                return False
            Logger.info(f"[L0 GITKRAKEN HEALING] Creating healing commit for {len(files)} file(s)")
            result: Any = await self._create_healing_commit(files, summary)
            if result:
                commit_sha: Any = result.get("commit_sha", "unknown")
                Logger.info(
                    f"[L0 GITKRAKEN HEALING] Commit Successful: {(commit_sha[:8] if len(commit_sha) > 8 else commit_sha)}"
                )
                if config.GITKRAKEN_HEALING_AUTO_PR:
                    pr_desc: Any = "\n".join(
                        [f"- {i.get('reason', 'Unknown reason')}" for i in fix.get("details", [])]
                    )
                    Logger.info("[L0 GITKRAKEN HEALING] Creating PR for review")
                    await self._create_pr(summary, pr_desc)
                self.commits_today += 1
                return True
            else:
                Logger.error("[L0 GITKRAKEN HEALING] Failed to create commit")
                return False
        except Exception as e:
            Logger.error(f"[L0 GITKRAKEN HEALING] Sovereign Git operation failed: {e}")
            return False

    async def _create_healing_commit(self, files: list[str], message: str) -> dict[str, Any]:
        """
        Create a healing commit via GitKraken MCP.

        Args:
            files: List of file paths to commit
            message: Commit message

        Returns:
            Result dictionary with commit SHA or None if failed
        """
        try:
            Logger.info(f"[L0 GITKRAKEN HEALING] Adding {len(files)} file(s) to staging")
            add_result = await self.git_client.add(files)
            if not add_result or add_result.get("status") != "success":
                Logger.error(f"[L0 GITKRAKEN HEALING] Failed to add files: {add_result}")
                return None
            Logger.info(f"[L0 GITKRAKEN HEALING] Creating commit: {message}")
            commit_result = await self.git_client.commit(message)
            if commit_result and commit_result.get("status") == "success":
                return {"commit_sha": commit_result.get("sha", "unknown"), "status": "success"}
            else:
                Logger.error(f"[L0 GITKRAKEN HEALING] Failed to create commit: {commit_result}")
                return None
        except Exception as e:
            Logger.error(f"[L0 GITKRAKEN HEALING] Commit creation failed: {e}")
            return None

    async def _create_pr(self, title: str, description: str) -> bool:
        """
        Create a pull request via GitKraken MCP.

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
            Logger.info(f"[L0 GITKRAKEN HEALING] Creating PR: {full_title}")
            pr_result = await self.git_client.create_pr(
                title=full_title,
                description=full_description,
                source_branch=healing_branch,
                target_branch="main",
            )
            if pr_result and pr_result.get("status") == "success":
                Logger.info(
                    f"[L0 GITKRAKEN HEALING] PR created successfully: {pr_result.get('pr_url', 'unknown')}"
                )
                return True
            else:
                Logger.error(f"[L0 GITKRAKEN HEALING] Failed to create PR: {pr_result}")
                return False
        except Exception as e:
            Logger.error(f"[L0 GITKRAKEN HEALING] PR creation failed: {e}")
            return False

    def reset_daily_counter(self) -> Any:
        """Reset the daily commit counter (should be called at midnight)."""
        self.commits_today = 0
        Logger.info("[L0 GITKRAKEN HEALING] Daily counter reset")


async def create_gitkraken_healing_strategy() -> GitKrakenHealingStrategy:
    """
    Factory function to create a GitKraken healing strategy.

    Returns:
        Initialized GitKrakenHealingStrategy instance
    """
    return GitKrakenHealingStrategy()
