from __future__ import annotations
"""
Sovereign Healing Engine – Phase 17 (Dec 27, 2025)
Autonomous self-correction using Filesystem and GitKraken MCPs.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
from agentic_core.L0_maintenance.P1_core.gitkraken_mcp_client import get_git_client
from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

class SovereignHealingEngine:
    """
    The brain of L0: Detects and transactionally repairs constitutional breaches.
    
    Features:
    - Autonomous Violation detection and correction
    - Transactional safety with rollback capability
    - MCP-routed file operations (Filesystem MCP)
    - MCP-routed version control (GitKraken MCP)
    - Configurable auto-apply, auto-commit, auto-PR
    """

    def __init__(self):
        """Initialize the healing engine with MCP clients."""
        self.transaction_manager = HealingTransaction()
        self.git_client = get_git_client()
        self.fs_client = get_filesystem_client()
        self.applied_fixes = 0
        Logger.info('[L0 HEALING] Engine initialized')

    async def execute_autonomous_cycle(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Full autonomous self-healing cycle with rollback safety.
        
        Args:
            issues: List of violations detected by auditor
            
        Returns:
            Healing cycle results
        """
        if not config.AUTONOMOUS_HEALING_ENABLED:
            Logger.info('[L0 HEALING] Autonomous mode disabled in config.')
            return {'status': 'disabled', 'applied_fixes': 0, 'message': 'Autonomous healing disabled in configuration'}
        if not issues:
            Logger.info('[L0 HEALING] No issues detected. Purity maintained.')
            return {'status': 'clean', 'applied_fixes': 0, 'message': 'No violations detected'}
        Logger.info(f'[L0 HEALING] Initiating autonomous cycle for {len(issues)} issues')
        target_issues: Any = issues[:config.HEALING_MAX_FIXES_PER_CYCLE]
        affected_files: Any = []
        try:
            Logger.info('[L0 HEALING] Starting transaction with backups')
            for issue in target_issues:
                action: Any = issue.get('action')
                if action == 'replace_import':
                    fix_successful: Any = await self._exec_replace_import(issue)
                elif action == 'replace_llm_sdk':
                    fix_successful: Any = await self._exec_replace_llm(issue)
                elif action == 'replace_io':
                    fix_successful: Any = await self._exec_replace_io(issue)
                else:
                    fix_successful: Any = await self._apply_fix(issue)
                if fix_successful:
                    self.applied_fixes += 1
                    file_path: Any = issue.get('file')
                    if file_path and file_path not in affected_files:
                        affected_files.append(file_path)
                else:
                    Logger.error(f"[L0 HEALING] Failed to apply fix for {issue.get('file', 'unknown')}")
                    if not config.HEALING_AUTO_APPLY:
                        raise Exception('Strict healing mode: failure on single fix triggers rollback')
            if self.applied_fixes > 0:
                Logger.info(f'[L0 HEALING] Successfully applied {self.applied_fixes} fixes')
                if config.HEALING_AUTO_COMMIT:
                    await self._create_healing_commit(affected_files)
                if config.HEALING_AUTO_PR:
                    await self._create_healing_pr()
                self.transaction_manager.commit()
                Logger.info(f'[L0 HEALING] Cycle complete. Applied {self.applied_fixes} fixes.')
                return {'status': 'success', 'applied_fixes': self.applied_fixes, 'affected_files': affected_files, 'message': f'Successfully healed {self.applied_fixes} violations'}
            else:
                Logger.warning('[L0 HEALING] No fixes were successfully applied')
                return {'status': 'no_fixes', 'applied_fixes': 0, 'message': 'No fixes could be applied'}
        except Exception as e:
            Logger.critical(f'[L0 HEALING] Cycle CRASHED. Rolling back state. Error: {e}')
            self.transaction_manager.rollback()
            return {'status': 'error', 'applied_fixes': 0, 'error': str(e), 'message': 'Healing cycle failed and was rolled back'}

    async def _apply_fix(self, issue: Dict[str, Any]) -> bool:
        """
        Determines the fix strategy and applies it via MCP.
        
        Args:
            issue: Violation details from auditor
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        file_path = issue.get('file')
        if not file_path:
            Logger.error('[L0 HEALING] Issue Missing file path')
            return False
        ViolationType = issue.get('type', '')
        message = issue.get('message', '')
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                Logger.warning(f'[L0 HEALING] File does not exist: {file_path}')
                return False
            self.transaction_manager.backup(path_obj)
            content = await self.fs_client.read_text(file_path)
            if not content:
                Logger.warning(f'[L0 HEALING] Could not read file: {file_path}')
                return False
            new_content = await self._generate_fix(content, ViolationType, message)
            if new_content and new_content != content:
                success = await self.fs_client.write_text(file_path, new_content)
                if success:
                    Logger.info(f'[L0 HEALING] Fixed {ViolationType} in {file_path}')
                    return True
                else:
                    Logger.error(f'[L0 HEALING] Failed to write healed content to {file_path}')
                    return False
            else:
                Logger.warning(f'[L0 HEALING] No fix generated for {file_path}')
                return False
        except Exception as e:
            Logger.error(f'[L0 HEALING] Error applying fix to {file_path}: {e}')
            return False

    async def _exec_replace_import(self, fix: Dict) -> bool:
        """
        Handles both import swap and instantiation swap.
        
        Args:
            fix: Fix dictionary with old_import, new_import, old_usage, new_usage
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        try:
            file_path = fix.get('file')
            if not file_path:
                return False
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False
            self.transaction_manager.backup(path_obj)
            content = await self.fs_client.read_text(file_path)
            if not content:
                return False
            content = re.sub(fix['old_import'], fix['new_import'], content)
            content = re.sub(fix['old_usage'], fix['new_usage'], content)
            return await self.fs_client.write_text(file_path, content)
        except Exception as e:
            Logger.error(f'[L0 HEALING] Error in _exec_replace_import: {e}')
            return False

    async def _exec_replace_llm(self, fix: Dict) -> bool:
        """
        Sophisticated LLM SDK removal.
        
        Args:
            fix: Fix dictionary with sdk, new_client, import_path
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        try:
            file_path = fix.get('file')
            if not file_path:
                return False
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False
            self.transaction_manager.backup(path_obj)
            content = await self.fs_client.read_text(file_path)
            if not content:
                return False
            if fix['new_client'] not in content:
                content = f"{fix['import_path']}\n{content}"
            content = re.sub(f"{fix['sdk']}\\(.*?\\)", f"{fix['new_client']}", content)
            return await self.fs_client.write_text(file_path, content)
        except Exception as e:
            Logger.error(f'[L0 HEALING] Error in _exec_replace_llm: {e}')
            return False

    async def _exec_replace_io(self, fix: Dict) -> bool:
        """
        Replace direct file I/O with Filesystem MCP client.
        
        Args:
            fix: Fix dictionary with operation, new_client, import_path
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        try:
            file_path = fix.get('file')
            if not file_path:
                return False
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False
            self.transaction_manager.backup(path_obj)
            content = await self.fs_client.read_text(file_path)
            if not content:
                return False
            if fix['new_client'] not in content:
                content = f"{fix['import_path']}\n{content}"
            content = content.replace('open(', f"# TODO: Use {fix['new_client']}.read_text() or write_text()\n# open(")
            content = content.replace('Path(', f"# TODO: Use {fix['new_client']} for file operations\n# Path(")
            return await self.fs_client.write_text(file_path, content)
        except Exception as e:
            Logger.error(f'[L0 HEALING] Error in _exec_replace_io: {e}')
            return False

    async def _generate_fix(self, content: str, ViolationType: str, message: str) -> Optional[str]:
        """
        Generate fixed content based on Violation type (legacy method).
        
        Args:
            content: Original file content
            ViolationType: Type of Violation (IMPORT_BREACH, PATH_BREACH, etc.)
            message: Violation message
            
        Returns:
            Fixed content or None if no fix available
        """
        new_content = content
        if 'HTTP' in message or 'requests' in message.lower():
            new_content = new_content.replace('import requests', '# Sovereign healing: Use get_fetch_client() from agentic_core.L2_execution.ToolRegistry.fetch_mcp_client')
            new_content = new_content.replace('requests.get(', '# await get_fetch_client().get_clean_content(')
            new_content = new_content.replace('requests.post(', '# await get_fetch_client().fetch_url(')
        if 'Redis' in message:
            new_content = new_content.replace('import redis', '# Sovereign healing: Use get_redis_client() from agentic_core.L4_state.caching.redis_mcp_client')
            new_content = new_content.replace('redis.Redis(', '# get_redis_client().')
        if 'Vector' in message or 'pinecone' in message.lower():
            new_content = new_content.replace('from pinecone import', '# Sovereign healing: Use get_pinecone_mcp_client() from agentic_core.L4_state.semantic_memory.pinecone_mcp_client\n# from pinecone import')
            new_content = new_content.replace('Pinecone(', '# get_pinecone_mcp_client().')
        if 'PATH_BREACH' in ViolationType or 'tools/' in message:
            new_content = new_content.replace('agentic_core/tools/', 'agentic_core/utils/')
            new_content = new_content.replace('from agentic_core.tools.', 'from agentic_core.utils.')
        return new_content if new_content != content else None

    async def _create_healing_commit(self, affected_files: List[str]):
        """
        Create a git commit for healed files.
        
        Args:
            affected_files: List of file paths that were healed
        """
        try:
            commit_message = f'[SOVEREIGN HEALING] Corrected {self.applied_fixes} constitutional breaches\n\nAutonomous healing cycle applied fixes to:\n'
            for file in affected_files[:10]:
                commit_message += f'- {file}\n'
            if len(affected_files) > 10:
                commit_message += f'... and {len(affected_files) - 10} more files\n'
            await self.git_client.add_and_commit(files=affected_files, message=commit_message)
            Logger.info(f'[L0 HEALING] Created healing commit for {len(affected_files)} files')
        except Exception as e:
            Logger.error(f'[L0 HEALING] Failed to create commit: {e}')

    async def _create_healing_pr(self):
        """Create a pull request for healed changes."""
        try:
            pr_title = f'{config.GITKRAKEN_PR_TITLE_PREFIX} Autonomous Sovereignty Restoration'
            pr_description = f'\n# Autonomous Sovereignty Restoration\n\nThis PR contains automated corrections for {self.applied_fixes} constitutional violations detected by the Sovereignty Auditor.\n\n## Healing Summary\n- **Fixes Applied:** {self.applied_fixes}\n- **Healing Mode:** Autonomous\n- **Transaction:** Committed with rollback safety\n\n## Review Notes\nAll fixes were applied using the Sovereign Healing Engine with:\n- Transactional safety (rollback on failure)\n- MCP-routed file operations (Filesystem MCP)\n- MCP-routed version control (GitKraken MCP)\n\nPlease review the changes to ensure they align with sovereignty requirements.\n'
            await self.git_client.create_pull_request(title=pr_title, description=pr_description, branch=config.GITKRAKEN_HEALING_BRANCH)
            Logger.info('[L0 HEALING] Created healing PR for review')
        except Exception as e:
            Logger.error(f'[L0 HEALING] Failed to create PR: {e}')

async def run_autonomous_healing(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run autonomous healing cycle on detected violations.
    
    Args:
        issues: List of violations from sovereignty auditor
        
    Returns:
        Healing cycle results
    """
    engine: Any = SovereignHealingEngine()
    return await engine.execute_autonomous_cycle(issues)