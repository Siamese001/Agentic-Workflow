import logging
import traceback
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "cognitive_recovery_mixin", "p0_governance")
_emit_reads_policy_state("p0", "cognitive_recovery_mixin", "policy_binding")
_emit_snapshots_state("p0", "cognitive_recovery_mixin", "state_snapshot")
emit_replay_key("p0", "cognitive_recovery_mixin")
emit_determinism_digest("p0", "cognitive_recovery_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        from agentic_core.infrastructure.SemanticKnowledgeClient import SemanticKnowledgeClient

        return SemanticKnowledgeClient()

    def consult_knowledge_base(
        self, query: str, namespace: str = "architecture-docs"
    ) -> list[dict[str, Any]]:
        """
        Generic query to the semantic brain.
        Useful for 'Just-in-Time' learning about system architecture.
        """
        try:
            client = self._get_cognitive_client()
            results = client.search(query, namespace, top_k=3)
            return [
                {"id": r.id, "content": r.content, "score": r.score, "metadata": r.metadata} for r in results
            ]
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Brain Freeze (Knowledge Query Failed): {e}")
            return []

    def perform_cognitive_rca(self, exception: Exception) -> str | None:
        """
        When an error occurs, this method queries the 'healing-patterns' namespace
        to see if this specific error has a known fix or RCA document.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CognitiveRecoveryMixin.perform_cognitive_rca")

        error_msg = f"{type(exception).__name__}: {str(exception)}"
        tb = traceback.format_exc()
        query = f"Fix for error: {error_msg} Context: {tb[:200]}"
        logger.info(f"[{self.__class__.__name__}] 🧠 Consulted Semantic Memory for: {error_msg}")
        try:
            client = self._get_cognitive_client()
            patterns = client.find_healing_pattern(query)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Cognitive RCA failed: {e}")
            return None
        if patterns:
            best_match = patterns[0]
            if best_match.score > 0.8:
                advice = f"\n✅ KNOWN ISSUE IDENTIFIED\n-----------------------\nPattern ID: {best_match.id}\nConfidence: {best_match.score:.2f}\nSource: {best_match.metadata.get('source', 'Unknown')}\n\nSuggested Fix Context:\n{best_match.content[:500]}...\n"
                logger.info(advice)
                return advice
            else:
                logger.info(
                    f"[{self.__class__.__name__}] No high-confidence healing patterns found (Best: {best_match.score:.2f})."
                )
        else:
            logger.info(
                f"[{self.__class__.__name__}] This appears to be a novel error (No memory records found)."
            )
        return None
