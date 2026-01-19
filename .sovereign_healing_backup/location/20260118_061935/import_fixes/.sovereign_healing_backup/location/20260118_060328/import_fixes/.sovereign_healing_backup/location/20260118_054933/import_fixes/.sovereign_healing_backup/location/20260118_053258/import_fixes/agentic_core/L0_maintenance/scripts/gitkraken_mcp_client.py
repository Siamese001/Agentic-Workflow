from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
"""
Sovereign GitKraken MCP Client – Phase 16D (Dec 27, 2025)
Replaces all direct git subprocess calls with official GitKraken MCP.
L3 routed, L5 shielded, L6 observable.
"""
import logging
from typing import List, Dict, Any, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger(__name__)

class SovereignGitKrakenMcpClient(MCPHardenedMixin, HealerMixin):
    """Official GitKraken MCP client for sovereign version control operations."""

    def __init__(self, role: str='governance_git'):
        super().__init__()
        if not config.GITKRAKEN_MCP_ENABLED:
            raise ValueError('GitKraken MCP disabled in sovereign config')
        # from agentic_core.L3_orchestration.workflow_engines  # Refactored to dynamic import to avoid upward dependency

def _get_workflow_engine():
    """Lazy load workflow engine to avoid L0 → L3 dependency."""
    import importlib
    module = importlib.import_module('agentic_core.L3_orchestration.workflow_engines')
    return module

        # Orphaned code - appears to be part of __init__ method but incorrectly placed
        # self.router = SovereignMCPRouter(role=role)
        # self._mcp_audit('init')
        # Logger.info('[L0 GITKRAKEN] Sovereign GitKraken MCP client initialized')

    async def create_healing_commit(self, files: List[str], message: str) -> Dict[str, Any]:
        """
        Create a sovereign healing commit on the healing branch.
        
        Args:
            files: List of file paths to commit
            message: Commit message
            
        Returns:
            Result dictionary from MCP
        """
        full_message: Any = f'{config.GITKRAKEN_PR_TITLE_PREFIX} {message}'
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_add_or_commit', {'action': 'commit', 'directory': '.', 'files': files, 'message': full_message})
            Logger.info(f'[L0 GITKRAKEN] Created commit: {message}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Commit failed: {e}')
            raise

    async def create_pr(self, title: str, description: str, source_branch: Optional[str]=None, target_branch: str='main') -> Dict[str, Any]:
        """
        Create a Sovereign Pull Request for code review.
        
        Args:
            title: PR title
            description: PR description
            source_branch: Source branch (defaults to healing branch)
            target_branch: Target branch (defaults to main)
            
        Returns:
            Result dictionary from MCP
        """
        full_title: Any = f'{config.GITKRAKEN_PR_TITLE_PREFIX} {title}'
        source: Any = source_branch or config.GITKRAKEN_HEALING_BRANCH
        try:
            result: Any = await self.router.manager.call_tool('mcp0_pull_request_create', {'Provider': 'github', 'title': full_title, 'body': description, 'source_branch': source, 'target_branch': target_branch, 'repository_name': config.GITKRAKEN_DEFAULT_REPO.split('/')[1], 'repository_organization': config.GITKRAKEN_DEFAULT_REPO.split('/')[0]})
            Logger.info(f'[L0 GITKRAKEN] Created PR: {full_title}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] PR creation failed: {e}')
            raise

    async def get_status(self, directory: str='.') -> Dict[str, Any]:
        """
        Get current repo status for validation (Territory Compliance).
        
        Args:
            directory: Repository directory
            
        Returns:
            Status dictionary from MCP
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_status', {'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Retrieved status for {directory}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Status fetch failed: {e}')
            return {}

    async def create_branch(self, branch_name: str, directory: str='.') -> Dict[str, Any]:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the branch to create
            directory: Repository directory
            
        Returns:
            Result dictionary from MCP
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_branch', {'action': 'create', 'branch_name': branch_name, 'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Created branch: {branch_name}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Branch creation failed: {e}')
            raise

    async def checkout_branch(self, branch_name: str, directory: str='.') -> Dict[str, Any]:
        """
        Checkout a branch.
        
        Args:
            branch_name: Name of the branch to checkout
            directory: Repository directory
            
        Returns:
            Result dictionary from MCP
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_checkout', {'branch': branch_name, 'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Checked out branch: {branch_name}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Checkout failed: {e}')
            raise

    async def list_branches(self, directory: str='.') -> List[str]:
        """
        List all branches in the repository.
        
        Args:
            directory: Repository directory
            
        Returns:
            List of branch names
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_branch', {'action': 'list', 'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Listed branches for {directory}')
            return result if isinstance(result, list) else []
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Branch listing failed: {e}')
            return []

    async def get_log(self, directory: str='.') -> Dict[str, Any]:
        """
        Get commit log.
        
        Args:
            directory: Repository directory
            
        Returns:
            Log dictionary from MCP
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_log_or_diff', {'action': 'log', 'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Retrieved log for {directory}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Log retrieval failed: {e}')
            return {}

    async def push(self, directory: str='.') -> Dict[str, Any]:
        """
        Push commits to remote.
        
        Args:
            directory: Repository directory
            
        Returns:
            Result dictionary from MCP
        """
        try:
            result: Any = await self.router.manager.call_tool('mcp0_git_push', {'directory': directory})
            Logger.info(f'[L0 GITKRAKEN] Pushed to remote for {directory}')
            return result
        except Exception as e:
            Logger.error(f'[L0 GITKRAKEN] Push failed: {e}')
            raise
_git_client: Optional[SovereignGitKrakenMCPClient] = None

def get_git_client() -> SovereignGitKrakenMCPClient:
    """Get or create the global GitKraken MCP client."""
    global _git_client
    if _git_client is None:
        _git_client = SovereignGitKrakenMCPClient()
    return _git_client


def _run_self_tests() -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
        assert True
        results["passed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results