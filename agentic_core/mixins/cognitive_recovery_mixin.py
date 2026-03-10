import logging
import traceback
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class CognitiveRecoveryMixin:
    """
    A mixin that gives agents access to the project's 'Semantic Brain'.
    Allows agents to look up architecture docs, API contracts, and
    healing patterns when they encounter unknown errors.

    Dependencies:
    - SemanticKnowledgeClient (Singleton)
    """

    def _get_cognitive_client(self):
        """Safe lazy retrieval of the singleton client."""
        from agentic_core.infrastructure.SemanticKnowledgeClient import (
            SemanticKnowledgeClient,
        )

        return SemanticKnowledgeClient()

    def consult_knowledge_base(
        self,
        query: str,
        namespace: str = "architecture-docs",
    ) -> list[dict[str, Any]]:
        """
        Generic query to the semantic brain.
        Useful for 'Just-in-Time' learning about system architecture.
        """
        try:
            client = self._get_cognitive_client()
            results = client.search(query, namespace, top_k=3)
            return [
                {
                    "id": r.id,
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in results
            ]
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Brain Freeze (Knowledge Query Failed): {e}")
            return []

    def perform_cognitive_rca(self, exception: Exception) -> str | None:
        """
        When an error occurs, this method queries the 'healing-patterns' namespace
        to see if this specific error has a known fix or RCA document.
        """
        error_msg = f"{type(exception).__name__}: {str(exception)}"
        tb = traceback.format_exc()

        query = f"Fix for error: {error_msg} Context: {tb[:200]}"

        logger.info(f"[{self.__class__.__name__}] 🧠 Consulted Semantic Memory for: {error_msg}")

        try:
            client = self._get_cognitive_client()
            patterns = client.find_healing_pattern(query)
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Cognitive RCA failed: {e}")
            return None

        if patterns:
            best_match = patterns[0]
            if best_match.score > 0.80:
                advice = f"""
✅ KNOWN ISSUE IDENTIFIED
-----------------------
Pattern ID: {best_match.id}
Confidence: {best_match.score:.2f}
Source: {best_match.metadata.get("source", "Unknown")}

Suggested Fix Context:
{best_match.content[:500]}...
"""
                logger.info(advice)
                return advice
            else:
                logger.info(
                    f"[{self.__class__.__name__}] No high-confidence healing patterns found (Best: {best_match.score:.2f}).",
                )
        else:
            logger.info(
                f"[{self.__class__.__name__}] This appears to be a novel error (No memory records found).",
            )

        return None
