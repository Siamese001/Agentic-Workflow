"""
Sovereign Vector Healing Strategy – Phase 17B (Dec 27, 2025)
Detects and autonomously corrects Pinecone vector state drift.
L4 state self-healing using official Pinecone MCP.
"""
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import get_pinecone_mcp_client
from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client
from agentic_core.config.blueprint_sovereign.sovereign_config import config

logger = logging.getLogger(__name__)


class VectorHealingStrategy:
    """
    Autonomous healing for Pinecone vector state drift.
    
    Detects and corrects vector inconsistencies by:
    - Re-embedding files with outdated or missing vectors
    - Using SHA-256 content hashing for immutability checks
    - Routing all operations through Sovereign MCP clients
    - Enforcing daily healing limits to prevent runaway operations
    """
    
    def __init__(self):
        """Initialize vector healing strategy with MCP clients."""
        self.name = "VectorHealing"
        self.priority = 2  # Important but not critical
        self.pinecone_client = get_pinecone_mcp_client()
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        logger.info("[L0 VECTOR HEALING] Strategy initialized")
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """
        Diagnose vector drift from auditor issues or proactive scan.
        
        Args:
            issues: List of issues from sovereignty auditor
            
        Returns:
            List of fix dictionaries with action details
        """
        fixes = []
        
        if not config.PINECONE_VECTOR_HEALING_ENABLED:
            logger.info("[L0 VECTOR HEALING] Vector healing disabled in config")
            return fixes
        
        for issue in issues:
            desc = issue.get("description", "").lower()
            message = issue.get("message", "").lower()
            
            # Detect vector-related issues
            if any(keyword in desc or keyword in message for keyword in ["vector", "embedding", "pinecone"]):
                fixes.append({
                    "action": "re_embed_file",
                    "file": issue.get("file"),
                    "reason": "Vector drift detected (L4 state inconsistency)",
                    "priority": self.priority,
                    "strategy": self.name
                })
        
        logger.info(f"[L0 VECTOR HEALING] Diagnosed {len(fixes)} vector drift issues")
        return fixes
    
    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """
        Apply vector healing fix using Sovereign Clients.
        
        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)
            
        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.PINECONE_VECTOR_HEALING_ENABLED:
            logger.warning("[L0 VECTOR HEALING] Vector healing disabled in config")
            return False
        
        if self.processed_today >= config.VECTOR_HEALING_MAX_DAILY:
            logger.warning("[L0 VECTOR HEALING] Daily limit reached. Aborting cycle.")
            return False
        
        try:
            file_path = fix.get("file")
            if not file_path:
                logger.error("[L0 VECTOR HEALING] No file path in fix")
                return False
            
            # 1. Read file via Sovereign Filesystem MCP (Audit Trail Maintained)
            logger.info(f"[L0 VECTOR HEALING] Reading file: {file_path}")
            content = await self.fs_client.read_text(file_path)
            
            if not content:
                logger.warning(f"[L0 VECTOR HEALING] Empty content for {file_path}")
                return False
            
            # 2. Generate sovereign embedding
            logger.info(f"[L0 VECTOR HEALING] Generating embedding for {file_path}")
            embedding = await self._get_embedding(content)
            
            if not embedding:
                logger.error(f"[L0 VECTOR HEALING] Failed to generate embedding for {file_path}")
                return False
            
            # Use SHA-256 of content for ID (Immutability check)
            vector_id = hashlib.sha256(content.encode()).hexdigest()
            
            # 3. Upsert via Sovereign Pinecone MCP
            payload = [{
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "file_path": file_path,
                    "source": "sovereign_canon",
                    "healed_at": datetime.utcnow().isoformat(),
                    "healing_id": f"heal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    "content_hash": vector_id[:16]  # First 16 chars of hash
                }
            }]
            
            logger.info(f"[L0 VECTOR HEALING] Upserting vector for {file_path}")
            result = await self.pinecone_client.upsert(
                vectors=payload,
                namespace=config.PINECONE_DEFAULT_NAMESPACE
            )
            
            if result and result.get("upserted_count", 0) > 0:
                self.processed_today += 1
                logger.info(f"[L0 VECTOR HEALING] Vector synchronized for {file_path} | ID: {vector_id[:8]}")
                return True
            else:
                logger.error(f"[L0 VECTOR HEALING] Upsert failed for {file_path}: {result}")
                return False
            
        except Exception as e:
            logger.error(f"[L0 VECTOR HEALING] Vector healing failed for {fix.get('file', 'unknown')}: {e}")
            return False
    
    async def _get_embedding(self, content: str) -> List[float]:
        """
        Generate embedding using Pinecone Inference MCP.
        
        Args:
            content: Text content to embed
            
        Returns:
            Embedding vector or None if failed
        """
        try:
            # Use Pinecone Inference MCP for embedding generation
            result = await self.pinecone_client.inference_embed([content])
            
            if result and "data" in result and len(result["data"]) > 0:
                # Extract embedding from first result
                embedding_data = result["data"][0]
                if "values" in embedding_data:
                    return embedding_data["values"]
                elif isinstance(embedding_data, list):
                    return embedding_data
            
            logger.error(f"[L0 VECTOR HEALING] Invalid embedding result: {result}")
            return None
            
        except Exception as e:
            logger.error(f"[L0 VECTOR HEALING] Embedding generation failed: {e}")
            return None
    
    def reset_daily_counter(self):
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        logger.info("[L0 VECTOR HEALING] Daily counter reset")


async def create_vector_healing_strategy() -> VectorHealingStrategy:
    """
    Factory function to create a vector healing strategy.
    
    Returns:
        Initialized VectorHealingStrategy instance
    """
    return VectorHealingStrategy()
