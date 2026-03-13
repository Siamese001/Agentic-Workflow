from __future__ import annotations

"\nSovereign Vector Healing Strategy – Phase 17B (Dec 27, 2025)\nDetects and autonomously corrects Pinecone vector state drift.\nL4 state self-healing using official Pinecone MCP.\n"
import hashlib
import logging
from datetime import datetime
from typing import Any


def get_filesystem_client():
    raise NotImplementedError("P1_core.filesystem_mcp_client_1 was removed; see RCA_P1_core_dead_imports.md")


Logger: Any = logging.getLogger(__name__)


class VectorHealingStrategy:
    """
    Autonomous healing for Pinecone vector state drift.

    Detects and corrects vector inconsistencies by:
    - Re-embedding files with outdated or Missing vectors
    - Using SHA-256 content hashing for immutability checks
    - Routing all operations through Sovereign MCP clients
    - Enforcing daily healing limits to prevent runaway operations
    """

    def __init__(self):
        """Initialize vector healing strategy with MCP clients."""
        self.name = "VectorHealing"
        self.priority = 2
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        Logger.info("[L0 VECTOR HEALING] Strategy initialized")

    async def diagnose(self, issues: list[dict]) -> list[dict]:
        """
        Diagnose vector drift from auditor issues or proactive scan.

        Args:
            issues: List of issues from sovereignty auditor

        Returns:
            List of fix dictionaries with action details
        """
        fixes: Any = []
        if not config.PINECONE_VECTOR_HEALING_ENABLED:
            Logger.info("[L0 VECTOR HEALING] Vector healing disabled in config")
            return fixes
        for issue in issues:
            desc: Any = issue.get("description", "").lower()
            message: Any = issue.get("message", "").lower()
            if any(keyword in desc or keyword in message for keyword in ["vector", "embedding", "pinecone"]):
                fixes.append(
                    {
                        "action": "re_embed_file",
                        "file": issue.get("file"),
                        "reason": "Vector drift detected (L4 state inconsistency)",
                        "priority": self.priority,
                        "strategy": self.name,
                    }
                )
        Logger.info(f"[L0 VECTOR HEALING] Diagnosed {len(fixes)} vector drift issues")
        return fixes

    async def apply(self, fix: dict, ctx: Any = None) -> bool:
        """
        Apply vector healing fix using Sovereign Clients.

        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)

        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.PINECONE_VECTOR_HEALING_ENABLED:
            Logger.warning("[L0 VECTOR HEALING] Vector healing disabled in config")
            return False
        if self.processed_today >= config.VECTOR_HEALING_MAX_DAILY:
            Logger.warning("[L0 VECTOR HEALING] Daily limit reached. Aborting cycle.")
            return False
        try:
            file_path: Any = fix.get("file")
            if not file_path:
                Logger.error("[L0 VECTOR HEALING] No file path in fix")
                return False
            Logger.info(f"[L0 VECTOR HEALING] Reading file: {file_path}")
            content: Any = await self.fs_client.read_text(file_path)
            if not content:
                Logger.warning(f"[L0 VECTOR HEALING] Empty content for {file_path}")
                return False
            Logger.info(f"[L0 VECTOR HEALING] Generating embedding for {file_path}")
            embedding: Any = await self._get_embedding(content)
            if not embedding:
                Logger.error(f"[L0 VECTOR HEALING] Failed to generate embedding for {file_path}")
                return False
            vector_id: Any = hashlib.sha256(content.encode()).hexdigest()
            payload: Any = [
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "file_path": file_path,
                        "source": "sovereign_canon",
                        "healed_at": datetime.utcnow().isoformat(),
                        "healing_id": f"heal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        "content_hash": vector_id[:16],
                    },
                }
            ]
            Logger.info(f"[L0 VECTOR HEALING] Upserting vector for {file_path}")
            result: Any = await self.pinecone_client.upsert(
                vectors=payload, namespace=config.PINECONE_DEFAULT_NAMESPACE
            )
            if result and result.get("upserted_count", 0) > 0:
                self.processed_today += 1
                Logger.info(f"[L0 VECTOR HEALING] Vector synchronized for {file_path} | ID: {vector_id[:8]}")
                return True
            else:
                Logger.error(f"[L0 VECTOR HEALING] Upsert failed for {file_path}: {result}")
                return False
        except Exception as e:
            Logger.error(f"[L0 VECTOR HEALING] Vector healing failed for {fix.get('file', 'unknown')}: {e}")
            return False

    async def _get_embedding(self, content: str) -> list[float]:
        """
        Generate embedding using Pinecone Inference MCP.

        Args:
            content: Text content to embed

        Returns:
            Embedding vector or None if failed
        """
        try:
            result = await self.pinecone_client.inference_embed([content])
            if result and "data" in result and (len(result["data"]) > 0):
                embedding_data = result["data"][0]
                if "values" in embedding_data:
                    return embedding_data["values"]
                elif isinstance(embedding_data, list):
                    return embedding_data
            Logger.error(f"[L0 VECTOR HEALING] Invalid embedding result: {result}")
            return None
        except Exception as e:
            Logger.error(f"[L0 VECTOR HEALING] Embedding generation failed: {e}")
            return None

    def reset_daily_counter(self) -> Any:
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        Logger.info("[L0 VECTOR HEALING] Daily counter reset")


async def create_vector_healing_strategy() -> VectorHealingStrategy:
    """
    Factory function to create a vector healing strategy.

    Returns:
        Initialized VectorHealingStrategy instance
    """
    return VectorHealingStrategy()
