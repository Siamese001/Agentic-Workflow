from __future__ import annotations
"""
Git Safety Handler - L5 Safety Layer

Uses GitKraken MCP to manage rollback points and hardened commits
for Atomic Fission events. Ensures L4 State is always protected with
automated snapshots and verification.

Strategy:
- Create backup branch before fission
- Stage and commit only after L5 verification passes
- Update Redis source of truth
- Enable safe rollback on failure
"""
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
Logger: Any = logging.getLogger(__name__)

class GitSafetyHandlerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    L5 Safety Layer: Uses GitKraken MCP to manage rollback points
    and hardened commits for Atomic Fission events.
    
    Process:
    1. Create backup branch before L4 mutation
    2. Execute fission with L1 Cognition
    3. Verify with Sequential Thinking MCP
    4. Commit only if verification passes
    5. Update Redis state registry
    """

    def __init__(self, McpRouterAgent) -> None:
        """
        Initialize Git Safety Handler.
        
        Args:
            McpRouterAgent: MCPRouter instance for MCP calls
        """
        self.router = McpRouterAgent
        Logger.info('[OK] Git Safety Handler initialized')

    async def create_rollback_point(self, file_path: str) -> str:
        """
        Creates a temporary branch before L4 mutation.
        
        Args:
            file_path: File being fissioned
            
        Returns:
            Branch name created
        """
        timestamp: Any = datetime.now().strftime('%Y%m%d_%H%M%S')
        branch_name: Any = f'fission_backup_{timestamp}'
        Logger.info(f'🛡️  Creating rollback point: {branch_name}')
        try:
            await self.router.call_mcp('gitkraken', {'action': 'create_branch', 'name': branch_name})
            Logger.info(f'   [OK] Backup branch created: {branch_name}')
            return branch_name
        except Exception as e:
            Logger.error(f'   [X] Failed to create backup branch: {e}')
            raise

    async def verify_clean_state(self, file_path: str) -> bool:
        """
        Verify that the current branch is clean before fission.
        
        Args:
            file_path: File to check
            
        Returns:
            True if clean, False otherwise
        """
        Logger.info(f'[SCAN] Verifying clean state for {file_path}')
        try:
            result: Any = await self.router.call_mcp('gitkraken', {'action': 'status', 'file': file_path})
            is_clean: Any = result.get('status') == 'clean'
            if is_clean:
                Logger.info(f'   [OK] Clean state verified')
            else:
                Logger.warning(f'   [!]  Uncommitted changes detected')
            return is_clean
        except Exception as e:
            Logger.error(f'   [X] Failed to verify state: {e}')
            return False

    async def stage_files(self, file_paths: List[str]) -> bool:
        """
        Stage files for commit.
        
        Args:
            file_paths: List of file paths to stage
            
        Returns:
            True if successful, False otherwise
        """
        Logger.info(f'📦 Staging {len(file_paths)} files')
        try:
            for file_path in file_paths:
                await self.router.call_mcp('gitkraken', {'action': 'stage', 'file': file_path})
                Logger.info(f'   [OK] Staged: {file_path}')
            return True
        except Exception as e:
            Logger.error(f'   [X] Failed to stage files: {e}')
            return False

    async def finalize_fission(self, original_file: str, new_files: List[str]) -> bool:
        """
        Commits changes only after L5 Verification passes.
        
        Args:
            original_file: Original monolithic file
            new_files: List of new decomposed files
            
        Returns:
            True if successful, False otherwise
        """
        Logger.info(f'🏁 Finalizing fission for {original_file}')
        try:
            summary: Any = f'Hardened Fission: Decomposed {original_file} into {len(new_files)} modules'
            all_files: Any = [original_file] + new_files
            if not await self.stage_files(all_files):
                Logger.error('   [X] Failed to stage files')
                return False
            await self.router.call_mcp('gitkraken', {'action': 'commit', 'message': summary})
            Logger.info(f'   [OK] Hardened commit successful')
            await self.router.call_mcp('redis', {'action': 'set', 'key': f'status:{original_file}', 'value': 'FISSION_COMPLETE'})
            Logger.info(f'   [OK] Redis state updated')
            return True
        except Exception as e:
            Logger.error(f'   [X] Fission finalization failed: {e}')
            return False

    async def rollback_to_branch(self, branch_name: str) -> bool:
        """
        Rollback to a specific backup branch.
        
        Args:
            branch_name: Branch to rollback to
            
        Returns:
            True if successful, False otherwise
        """
        Logger.info(f'🔙 Rolling back to branch: {branch_name}')
        try:
            await self.router.call_mcp('gitkraken', {'action': 'checkout', 'branch': branch_name})
            Logger.info(f'   [OK] Rollback successful')
            return True
        except Exception as e:
            Logger.error(f'   [X] Rollback failed: {e}')
            return False

    async def get_commit_history(self, file_path: str, limit: int=10) -> List[Dict]:
        """
        Get commit history for a file.
        
        Args:
            file_path: File to get history for
            limit: Maximum number of commits to retrieve
            
        Returns:
            List of commit information
        """
        Logger.info(f'📜 Getting commit history for {file_path}')
        try:
            result: Any = await self.router.call_mcp('gitkraken', {'action': 'log', 'file': file_path, 'limit': limit})
            commits: Any = result.get('commits', [])
            Logger.info(f'   [OK] Retrieved {len(commits)} commits')
            return commits
        except Exception as e:
            Logger.error(f'   [X] Failed to get commit history: {e}')
            return []

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
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
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

def get_git_safety_handler(McpRouterAgent: Any) -> GitSafetyHandlerAgent:
    """
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Factory function to create GitSafetyHandlerAgent instance.
    
    Args:
        McpRouterAgent: MCPRouter instance
        
    Returns:
        GitSafetyHandlerAgent instance
    """
    return GitSafetyHandlerAgent(McpRouterAgent=McpRouterAgent)
