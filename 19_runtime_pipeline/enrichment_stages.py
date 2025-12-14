"""Context enrichment and signal augmentation stages.


LOGGER = logging.getLogger(__name__)
Extracted from unified_signal_pipeline.py for Key 42 compliance.
Contains ContextEnrichmentStage and SignalAugmentationStage.
"""

from .types import PipelineStage
import hashlib
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


LOGGER = __import__('logging').getLogger(__name__)


class ContextEnrichmentStage(PipelineStage):
    """Enriches context with external data."""

    def __init__(self):
        """Initialize context enrichment stage."""
        try:
            from ..rag_components import (KnowledgeGraphInjector,
                                          SelfRAGProcessor, SemanticCache)
            self.kg_injector = KnowledgeGraphInjector()
            self.rag_processor = SelfRAGProcessor()
            self.semantic_cache = SemanticCache()
        except ImportError:
            self.kg_injector = None
            self.rag_processor = None
            self.semantic_cache = None
            logger.warning("RAG components not available")

    async def execute(self, envelope: Any) -> Any:
        """Enrich context."""
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            expanded_query = self._get_expanded_query(envelope)

            if not expanded_query:
                envelope.mark_stage_skipped(stage_name, "No expanded query available")
                return envelope

            cache_key = f"context_enriched_{hashlib.
                                            .sha256(expanded_query.
                                                    .encode()).
                                            .hexdigest()[:16]}"
            CACHED = self.semantic_cache.get(cache_key) if self.semantic_cache else None

            if cached:
                self._update_envelope_with_context(envelope, cached)
                envelope.mark_stage_complete(stage_name,
                                             (time.time() - start_time) * 1000,
                                             METADATA={"cache_hit": True})
                return envelope

            rag_results = self.rag_processor.retrieve_and_rerank(
                expanded_query, top_k=10, filters={"engine": envelope.payload.payload_type.value}
            ) if self.rag_processor else []

            kg_context = self.kg_injector.inject_context(
                expanded_query, envelope.payload.payload_type.value
            ) if self.kg_injector else {}

            ENRICHED = {
                "rag_results": rag_results,
                "knowledge_graph": kg_context,
                "combined_context": self._combine_contexts(rag_results, kg_context)
            }

            self._update_envelope_with_context(envelope, enriched)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, enriched)

            envelope.mark_stage_complete(stage_name,
                                         (time.time() - start_time) * 1000,
                                         METADATA={"cache_hit": False})
            return envelope

        except Exception as e:
            logger.error(f"Context enrichment failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _get_expanded_query(self, envelope: Any) -> str:
        """Get expanded query from envelope."""
        if hasattr(envelope.payload, 'metadata') and 'expanded_query' in envelope.payload.metadata:
            return envelope.payload.metadata['expanded_query']
        if 'processed_expanded_query' in envelope.metadata:
            return envelope.metadata['processed_expanded_query']
        return ""

    def _update_envelope_with_context(self, envelope: Any, enriched: Dict[str, Any]) -> None:
        """Update envelope with enriched context."""
        if hasattr(envelope.payload, 'metadata'):
            envelope.payload.metadata.update(enriched)
        else:
            envelope.metadata.update({f"enriched_{k}": v for k, v in enriched.items()})

    def _combine_contexts(self, rag_results: List[Dict], kg_context: Dict) -> str:
        """Combine RAG and KG contexts."""
        rag_text = "\n".join(r.get("text", "") for r in rag_results[:5])
        kg_text = "\n".join(f"{k}: {v}" for k, v in kg_context.items())
        return f"Retrieved Information:\n{rag_text}\n\nRelated Knowledge:\n{kg_text}"

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "context_enrichment"


class SignalAugmentationStage(PipelineStage):
    """Augments signal with various enhancements."""

    def __init__(self):
        """Initialize signal augmentation stage."""
        try:
            from ..claim_confidence import ClaimConfidenceScorer
            from ..prompt_optimizer import PromptOptimizer
            from ..rag_components import SemanticCache
            from ..tone_model import ToneModel
            self.claim_scorer = ClaimConfidenceScorer()
            self.prompt_optimizer = PromptOptimizer()
            self.tone_model = ToneModel()
            self.semantic_cache = SemanticCache()
        except ImportError:
            self.claim_scorer = None
            self.prompt_optimizer = None
            self.tone_model = None
            self.semantic_cache = None
            logger.warning("Signal augmentation components not available")

    async def execute(self, envelope: Any) -> Any:
        """Augment signal."""
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            CONTENT = self._extract_content(envelope.payload)

            if not content:
                envelope.mark_stage_skipped(stage_name, "No content to augment")
                return envelope

            cache_key = f"signal_augmented_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            CACHED = self.semantic_cache.get(cache_key) if self.semantic_cache else None

            if cached:
                self._update_envelope_with_augmentations(envelope, cached)
                envelope.mark_stage_complete(stage_name,
                                             (time.time() - start_time) * 1000,
                                             METADATA={"cache_hit": True})
                return envelope

            AUGMENTATIONS = await self._perform_augmentations(content, envelope)
            self._update_envelope_with_augmentations(envelope, augmentations)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, augmentations)

            envelope.mark_stage_complete(stage_name,
                                         (time.time() - start_time) * 1000,
                                         METADATA={"cache_hit": False})
            return envelope

        except Exception as e:
            logger.error(f"Signal augmentation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content(self, payload: Any) -> str:
        """Extract content from payload."""
        if hasattr(payload, 'text'):
            return payload.text
        elif hasattr(payload, 'sections'):
            return str(payload.sections)
        return str(payload)

    async def _perform_augmentations(self, content: str, envelope: Any) -> Dict[str, Any]:
        """Perform all signal augmentations."""
        RESULT = {}

        if self.claim_scorer:
            CLAIMS = self.claim_scorer.analyze_claims(content)
            RESULT["CLAIMS"] = claims

        if self.prompt_optimizer:
            OPTIMIZED = self.prompt_optimizer.optimize_prompt(content,
                                                              envelope.payload.payload_type.value)
            result["optimized_prompt"] = optimized

        if self.tone_model:
            TONE = self.tone_model.adapt_tone(content, target_formality="professional")
            result["tone_adapted"] = tone

        return result

    def _update_envelope_with_augmentations(self,
                                            envelope: Any,
                                            augmentations: Dict[str,
                                                                Any]) -> None:
        """Update envelope with augmentations."""
        if hasattr(envelope.payload, 'metadata'):
            envelope.payload.metadata.update(augmentations)
        else:
            envelope.metadata.update({f"augmented_{k}": v for k, v in augmentations.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "signal_augmentation"
