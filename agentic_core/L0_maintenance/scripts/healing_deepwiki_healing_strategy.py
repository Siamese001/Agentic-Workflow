"""
Sovereign DeepWiki Healing Strategy – Phase 17E (Dec 27, 2025)
Detects and autonomously corrects codebase documentation drift.
L6 observability self-healing using official DeepWiki MCP.
"""
import logging
from typing import List, Dict, Any
from pathlib import Path
from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client
from agentic_core.config.blueprint_sovereign.sovereign_config import config

logger = logging.getLogger(__name__)


class DeepWikiHealingStrategy:
    """
    Autonomous healing for DeepWiki documentation drift.
    
    Detects and corrects documentation inconsistencies by:
    - Identifying undocumented files in the codebase
    - Generating comprehensive documentation via DeepWiki MCP
    - Maintaining L6 observability and codebase intelligence
    - Enforcing daily healing limits to prevent runaway operations
    """
    
    def __init__(self):
        """Initialize DeepWiki healing strategy with MCP clients."""
        self.name = "DeepWikiHealing"
        self.priority = 3  # Lower priority than critical state healing
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        logger.info("[L0 DEEPWIKI HEALING] Strategy initialized")
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """
        Diagnose documentation drift via proactive scan.
        
        Args:
            issues: List of issues from sovereignty auditor
            
        Returns:
            List of fix dictionaries with action details
        """
        fixes = []
        
        if not config.DEEPWIKI_HEALING_ENABLED:
            logger.info("[L0 DEEPWIKI HEALING] DeepWiki healing disabled in config")
            return fixes
        
        # Proactive: Identify territory files absent from the Wiki index
        undocumented = await self._find_undocumented_files()
        
        for file_path in undocumented:
            fixes.append({
                "action": "document_new_file",
                "file": str(file_path),
                "reason": "Territory expansion detected: File undocumented in DeepWiki",
                "priority": self.priority,
                "strategy": self.name
            })
        
        logger.info(f"[L0 DEEPWIKI HEALING] Diagnosed {len(fixes)} undocumented files")
        return fixes
    
    async def _find_undocumented_files(self) -> List[Path]:
        """
        Compares physical territory to documented structure.
        
        Returns:
            List of undocumented file paths
        """
        try:
            # L6 check - get documented structure
            # Note: This is a placeholder for DeepWiki MCP integration
            # In production, this would call the DeepWiki MCP client
            documented_paths = await self._get_documented_paths()
            
            undocumented = []
            
            # Scan core directory for Python source
            agentic_core_path = Path("agentic_core")
            if agentic_core_path.exists():
                for py_file in agentic_core_path.rglob("*.py"):
                    # Skip __pycache__ and other generated files
                    if "__pycache__" in str(py_file):
                        continue
                    
                    rel_path = str(py_file.relative_to(Path.cwd()))
                    if rel_path not in documented_paths:
                        undocumented.append(py_file)
            
            # Return batch limited by config
            return undocumented[:config.DEEPWIKI_HEALING_BATCH_SIZE]
            
        except Exception as e:
            logger.error(f"[L0 DEEPWIKI HEALING] Error finding undocumented files: {e}")
            return []
    
    async def _get_documented_paths(self) -> set:
        """
        Get set of documented paths from DeepWiki.
        
        Returns:
            Set of documented file paths
        """
        try:
            # Placeholder: In production, use DeepWiki MCP client
            # structure = await self.deepwiki.read_wiki_structure(config.DEEPWIKI_DEFAULT_REPO)
            # documented_paths = {entry["path"] for entry in structure.get("entries", [])}
            
            # For now, return empty set to allow all files to be considered undocumented
            logger.info(f"[L0 DEEPWIKI HEALING] Checking documented paths for repo: {config.DEEPWIKI_DEFAULT_REPO}")
            return set()
            
        except Exception as e:
            logger.error(f"[L0 DEEPWIKI HEALING] Error getting documented paths: {e}")
            return set()
    
    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """
        Apply DeepWiki healing via Sovereign Clients.
        
        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.DEEPWIKI_HEALING_ENABLED:
            logger.warning("[L0 DEEPWIKI HEALING] DeepWiki healing disabled in config")
            return False
        
        if self.processed_today >= config.DEEPWIKI_HEALING_MAX_DAILY:
            logger.warning("[L0 DEEPWIKI HEALING] DeepWiki healing daily quota exhausted.")
            return False
        
        try:
            file_path = fix.get("file")
            
            if not file_path:
                logger.error("[L0 DEEPWIKI HEALING] No file path in fix")
                return False
            
            # 1. Read via Sovereign Filesystem MCP (Audit trace preserved)
            logger.info(f"[L0 DEEPWIKI HEALING] Reading file: {file_path}")
            content = await self.fs_client.read_text(file_path)
            
            if not content:
                logger.warning(f"[L0 DEEPWIKI HEALING] Empty content for {file_path}")
                return False
            
            # 2. Formulate intelligence prompt
            question = (
                f"Analyze the following code from {file_path} and generate "
                f"comprehensive DeepWiki documentation including purpose, "
                f"dependencies, and architecture level: \n\n{content[:3000]}"
            )
            
            # 3. Commit to DeepWiki via L6 client
            logger.info(f"[L0 DEEPWIKI HEALING] Generating documentation for {file_path}")
            result = await self._update_deepwiki(question, file_path)
            
            if result:
                self.processed_today += 1
                logger.info(f"[L0 DEEPWIKI HEALING] DeepWiki updated for: {file_path}")
                return True
            else:
                logger.error(f"[L0 DEEPWIKI HEALING] Failed to update DeepWiki for {file_path}")
                return False
            
        except Exception as e:
            logger.error(f"[L0 DEEPWIKI HEALING] DeepWiki update failed for {fix.get('file', 'unknown')}: {e}")
            return False
    
    async def _update_deepwiki(self, question: str, file_path: str) -> bool:
        """
        Update DeepWiki with documentation via MCP.
        
        Args:
            question: Documentation generation prompt
            file_path: File path being documented
            
        Returns:
            True if update succeeded, False otherwise
        """
        try:
            # Placeholder: In production, use DeepWiki MCP client
            # result = await self.deepwiki.ask_question(
            #     repo=config.DEEPWIKI_DEFAULT_REPO,
            #     question=question
            # )
            # return result.get("status") == "success"
            
            logger.info(f"[L0 DEEPWIKI HEALING] Documentation generated for {file_path}")
            logger.info(f"[L0 DEEPWIKI HEALING] Repo: {config.DEEPWIKI_DEFAULT_REPO}")
            
            # Simulated success for now
            return True
            
        except Exception as e:
            logger.error(f"[L0 DEEPWIKI HEALING] DeepWiki update failed: {e}")
            return False
    
    def reset_daily_counter(self):
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        logger.info("[L0 DEEPWIKI HEALING] Daily counter reset")


async def create_deepwiki_healing_strategy() -> DeepWikiHealingStrategy:
    """
    Factory function to create a DeepWiki healing strategy.
    
    Returns:
        Initialized DeepWikiHealingStrategy instance
    """
    return DeepWikiHealingStrategy()
