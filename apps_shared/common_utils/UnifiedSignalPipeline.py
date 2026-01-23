"""Unified Signal Pipeline - Shared signal augmentation across engines.

This module provides a unified pipeline for signal augmentation that both
resume and outreach engines can use, eliminating duplication while
maintaining domain-specific optimizations.
"""

import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from .claim_confidence import ClaimConfidenceScorer, analyze_claims
from .core.checkpoint_manager import CheckpointConfig, CheckpointManager, get_checkpoint_manager
from .core.envelope import EnvelopeFactory, PipelineStageStatus, SignalEnvelope
from .hyde_processor import HyDEProcessor
from .prompt_optimizer import PromptOptimizer, optimize_prompt
from .rag_components import KnowledgeGraphInjector, SelfRAGProcessor, semantic_cache
from .signal_infrastructure import DomainConfig, EngineType, get_shared_infrastructure
from .signal_quality_pipeline import SignalQualityPipeline
from .tone_model import ToneModel, adapt_tone

logger = logging.getLogger(__name__)


class PipelineStageType(Enum):
    """Stages in the unified signal pipeline."""

    INPUT_PROCESSING = "input_processing"
    CONTEXT_ENRICHMENT = "context_enrichment"
    SIGNAL_AUGMENTATION = "signal_augmentation"
    QUALITY_VALIDATION = "quality_validation"
    OUTPUT_FORMATTING = "output_formatting"


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""

    engine_type: EngineType
    domain_config: DomainConfig
    original_input: Any
    processed_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    cache_keys: set[str] = field(default_factory=set)

    def get_cache_key(self, component: str, data: Any) -> str:
        """Generate cache key for component.

        Args:
            component: Component name
            data: Data to hash

        Returns:
            Cache key
        """
        content = json.dumps(data, sort_keys=True, default=str)
        hash_key = hashlib.sha256(f"{component}:{content}".encode()).hexdigest()[:16]
        self.cache_keys.add(hash_key)
        return hash_key


class PipelineStage(ABC):
    """Abstract base for pipeline stages."""

    @abstractmethod
    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Execute the pipeline stage.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        pass

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Get stage name."""
        pass


class InputProcessingStage(PipelineStage):
    """Processes and normalizes input data."""

    def __init__(self):
        """Initialize input processing stage."""
        self.semantic_cache = SemanticCache()
        self.hyde_processor = HyDEProcessor()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Process input data.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        # Check if already completed
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        # Mark stage start
        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Processing input for {envelope.payload.payload_type}")

            # Extract content from payload
            content = self._extract_content_from_payload(envelope.payload)

            # Check cache first
            cache_key = f"input_processed_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key)

            if cached:
                # Update payload with cached data
                self._update_payload_with_processed_data(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": True}
                )
                return envelope

            # Process content
            processed = await self._process_content(content, envelope)

            # Update envelope
            self._update_payload_with_processed_data(envelope, processed)

            # Cache result
            self.semantic_cache.set(cache_key, processed)

            # Mark complete
            envelope.mark_stage_complete(
                stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": False}
            )

            return envelope

        except Exception as e:
            logger.error(f"Input processing failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            # Extract text from resume sections
            return json.dumps(payload.sections)
        elif hasattr(payload, "recipient_info"):
            # Extract text from outreach data
            return json.dumps(
                {"recipient": payload.recipient_info, "campaign": payload.campaign_context}
            )
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    async def _process_content(self, content: str, envelope: SignalEnvelope) -> dict[str, Any]:
        """Process text content.

        Args:
            content: Text to process
            envelope: Signal envelope

        Returns:
            Processed data
        """
        result = {
            "word_count": len(content.split()),
            "char_count": len(content),
            "language": "en",  # Would detect in real implementation
        }

        # HyDE expansion for better retrieval
        if envelope.payload.payload_type.value == "resume_data":
            query = f"resume achievements skills {content[:100]}"
        else:
            query = f"outreach personalization {content[:100]}"

        expanded = self.hyde_processor.expand_query_with_hyde(
            query, envelope.payload.payload_type.value
        )
        result["expanded_query"] = expanded

        return result

    def _update_payload_with_processed_data(
        self, envelope: SignalEnvelope, processed: dict[str, Any]
    ) -> None:
        """Update payload with processed data.

        Args:
            envelope: Signal envelope
            processed: Processed data
        """
        # Add processed data to payload metadata
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(processed)
        else:
            # For raw text or dict payloads, store in envelope metadata
            envelope.metadata.update({f"processed_{k}": v for k, v in processed.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "input_processing"


class ContextEnrichmentStage(PipelineStage):
    """Enriches context with external data."""

    def __init__(self):
        """Initialize context enrichment stage."""
        self.kg_injector = KnowledgeGraphInjector()
        self.rag_processor = SelfRAGProcessor()
        self.semantic_cache = SemanticCache()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Enrich context.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        # Check if already completed
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        # Mark stage start
        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Enriching context for {envelope.payload.payload_type}")

            # Get expanded query from previous stage
            expanded_query = self._get_expanded_query(envelope)

            if not expanded_query:
                envelope.mark_stage_skipped(stage_name, "No expanded query available")
                return envelope

            # Check cache
            cache_key = (
                f"context_enriched_{hashlib.sha256(expanded_query.encode()).hexdigest()[:16]}"
            )
            cached = self.semantic_cache.get(cache_key)

            if cached:
                self._update_envelope_with_context(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": True}
                )
                return envelope

            # RAG retrieval
            rag_results = self.rag_processor.retrieve_and_rerank(
                expanded_query, top_k=10, filters={"engine": envelope.payload.payload_type.value}
            )

            # Knowledge graph injection
            kg_context = self.kg_injector.inject_context(
                expanded_query, envelope.payload.payload_type.value
            )

            # Combine results
            enriched = {
                "rag_results": rag_results,
                "knowledge_graph": kg_context,
                "combined_context": self._combine_contexts(rag_results, kg_context),
            }

            # Update envelope
            self._update_envelope_with_context(envelope, enriched)

            # Cache result
            self.semantic_cache.set(cache_key, enriched)

            # Mark complete
            envelope.mark_stage_complete(
                stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": False}
            )

            return envelope

        except Exception as e:
            logger.error(f"Context enrichment failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _get_expanded_query(self, envelope: SignalEnvelope) -> str:
        """Get expanded query from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Expanded query string
        """
        # Check payload metadata first
        if hasattr(envelope.payload, "metadata") and "expanded_query" in envelope.payload.metadata:
            return envelope.payload.metadata["expanded_query"]

        # Check envelope metadata
        if "processed_expanded_query" in envelope.metadata:
            return envelope.metadata["processed_expanded_query"]

        return ""

    def _update_envelope_with_context(
        self, envelope: SignalEnvelope, enriched: dict[str, Any]
    ) -> None:
        """Update envelope with enriched context.

        Args:
            envelope: Signal envelope
            enriched: Enriched context data
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(enriched)
        else:
            envelope.metadata.update({f"enriched_{k}": v for k, v in enriched.items()})

    def _combine_contexts(self, rag_results: list[dict], kg_context: dict) -> str:
        """Combine RAG and KG contexts.

        Args:
            rag_results: RAG retrieval results
            kg_context: Knowledge graph context

        Returns:
            Combined context string
        """
        # Extract key info from RAG
        rag_text = "\n".join(r.get("text", "") for r in rag_results[:5])

        # Extract key info from KG
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
        self.claim_scorer = ClaimConfidenceScorer()
        self.prompt_optimizer = PromptOptimizer()
        self.tone_model = ToneModel()
        self.shared_infra = get_shared_infrastructure()
        self.semantic_cache = SemanticCache()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Augment signal.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        # Check if already completed
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        # Mark stage start
        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Augmenting signal for {envelope.payload.payload_type}")

            # Get base content from envelope
            content = self._extract_content_from_payload(envelope.payload)

            if not content:
                envelope.mark_stage_skipped(stage_name, "No content to augment")
                return envelope

            # Check cache
            cache_key = f"signal_augmented_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key)

            if cached:
                self._update_envelope_with_augmented(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": True}
                )
                return envelope

            # Perform augmentation
            augmented = await self._perform_augmentation(content, envelope)

            # Update envelope
            self._update_envelope_with_augmented(envelope, augmented)

            # Cache result
            self.semantic_cache.set(cache_key, augmented)

            # Mark complete
            envelope.mark_stage_complete(
                stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": False}
            )

            return envelope

        except Exception as e:
            logger.error(f"Signal augmentation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "recipient_info"):
            return json.dumps(
                {"recipient": payload.recipient_info, "campaign": payload.campaign_context}
            )
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    async def _perform_augmentation(self, content: str, envelope: SignalEnvelope) -> dict[str, Any]:
        """Perform signal augmentation.

        Args:
            content: Content to augment
            envelope: Signal envelope

        Returns:
            Augmented data
        """
        augmented = {}

        # Claim confidence scoring
        claims = analyze_claims(content)
        augmented["claims"] = claims
        augmented["claim_confidence"] = (
            sum(c.confidence for c in claims) / len(claims) if claims else 0.5
        )

        # Prompt optimization
        if envelope.payload.payload_type.value == "resume_data":
            optimized = optimize_prompt(
                content, strategy="achievement_focused", constraints=["use_metrics", "action_verbs"]
            )
        else:
            optimized = optimize_prompt(
                content,
                strategy="personalization_focused",
                constraints=["professional_tone", "value_proposition"],
            )
        augmented["optimized_prompt"] = optimized

        # Tone adaptation
        if envelope.payload.payload_type.value == "resume_data":
            tone = adapt_tone(content, "professional_achievements")
        else:
            tone = adapt_tone(content, "engaging_professional")
        augmented["adapted_tone"] = tone

        # Signal quality assessment
        domain_config = json.loads(envelope.metadata.get("domain_config", "{}"))
        assessment = self.shared_infra.assess_signal(
            content,
            EngineType(envelope.metadata.get("engine_type")),
            domain_config,
            self._get_enriched_context(envelope),
        )
        augmented["quality_assessment"] = assessment

        return augmented

    def _get_enriched_context(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched context from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched context
        """
        if (
            hasattr(envelope.payload, "metadata")
            and "combined_context" in envelope.payload.metadata
        ):
            return envelope.payload.metadata["combined_context"]

        # Check envelope metadata
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                return value

        return {}

    def _update_envelope_with_augmented(
        self, envelope: SignalEnvelope, augmented: dict[str, Any]
    ) -> None:
        """Update envelope with augmented data.

        Args:
            envelope: Signal envelope
            augmented: Augmented data
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(augmented)
        else:
            envelope.metadata.update({f"augmented_{k}": v for k, v in augmented.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "signal_augmentation"


class QualityValidationStage(PipelineStage):
    """Validates signal quality against standards."""

    def __init__(self):
        """Initialize quality validation stage."""
        self.signal_pipeline = SignalQualityPipeline()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Validate quality.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        # Check if already completed
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        # Mark stage start
        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Validating quality for {envelope.payload.payload_type}")

            # Get augmented signal from envelope
            augmented = self._get_augmented_signal(envelope)
            assessment = augmented.get("quality_assessment")

            if not assessment:
                envelope.mark_stage_skipped(stage_name, "No quality assessment to validate")
                return envelope

            # Run through signal quality pipeline
            content = self._extract_content_from_payload(envelope.payload)
            quality_result = self.signal_pipeline.process_signal(
                content, envelope.payload.payload_type.value, self._get_enriched_context(envelope)
            )

            # Determine if passes validation
            validation = {
                "passes_quality_gate": quality_result.is_pass,
                "quality_score": quality_result.composite_score,
                "flags": quality_result.flags,
                "recommendations": quality_result.recommendations,
            }

            # Update envelope
            self._update_envelope_with_validation(envelope, validation)

            # Mark complete
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"quality_score": quality_result.composite_score},
            )

            return envelope

        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _get_augmented_signal(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get augmented signal from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Augmented signal data
        """
        if hasattr(envelope.payload, "metadata"):
            return envelope.payload.metadata

        # Check envelope metadata
        for key, value in envelope.metadata.items():
            if key.startswith("augmented_") or "augmented" in key:
                return value

        return {}

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    def _get_enriched_context(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched context from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched context
        """
        if (
            hasattr(envelope.payload, "metadata")
            and "combined_context" in envelope.payload.metadata
        ):
            return envelope.payload.metadata["combined_context"]

        # Check envelope metadata
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                return value

        return {}

    def _update_envelope_with_validation(
        self, envelope: SignalEnvelope, validation: dict[str, Any]
    ) -> None:
        """Update envelope with validation results.

        Args:
            envelope: Signal envelope
            validation: Validation results
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(validation)
        else:
            envelope.metadata.update({f"validation_{k}": v for k, v in validation.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "quality_validation"


class OutputFormattingStage(PipelineStage):
    """Formats output for the specific engine."""

    def __init__(self):
        """Initialize output formatting stage."""
        pass

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Format output.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        # Check if already completed
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        # Mark stage start
        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Formatting output for {envelope.payload.payload_type}")

            # Collect all processed data
            formatted = {
                "engine_type": envelope.payload.payload_type.value,
                "envelope_id": str(envelope.id),
                "trace_id": envelope.trace_id,
                "payload": envelope.payload.dict()
                if hasattr(envelope.payload, "dict")
                else envelope.payload,
                "metadata": envelope.metadata,
                "processing_timestamp": datetime.utcnow().isoformat(),
            }

            # Engine-specific formatting
            if envelope.payload.payload_type.value == "resume_data":
                formatted["resume_format"] = self._format_resume_output(envelope)
            else:
                formatted["outreach_format"] = self._format_outreach_output(envelope)

            # Add audit trail
            formatted["stage_history"] = [r.dict() for r in envelope.history]

            # Update envelope
            self._update_envelope_with_formatted(envelope, formatted)

            # Mark complete
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"output_format": formatted.get("format_type", "default")},
            )

            return envelope

        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _format_resume_output(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Format resume-specific output.

        Args:
            envelope: Signal envelope

        Returns:
            Formatted resume output
        """
        return {
            "bullet_points": self._extract_bullets(envelope),
            "achievements": self._extract_achievements(envelope),
            "skills_highlighted": self._extract_skills(envelope),
            "sections": self._get_resume_sections(envelope),
        }

    def _format_outreach_output(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Format outreach-specific output.

        Args:
            envelope: Signal envelope

        Returns:
            Formatted outreach output
        """
        return {
            "personalization_points": self._extract_personalization(envelope),
            "call_to_action": self._extract_cta(envelope),
            "value_proposition": self._extract_value_prop(envelope),
            "recipient_info": self._get_recipient_info(envelope),
        }

    def _extract_bullets(self, envelope: SignalEnvelope) -> list[str]:
        """Extract bullet points from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of bullet points
        """
        # Check augmented data for bullets
        augmented = self._get_augmented_data(envelope)
        if "optimized_prompt" in augmented:
            content = augmented["optimized_prompt"]
            bullets = [b.strip() for b in content.split("\n") if b.strip().startswith("•")]
            return bullets[:5]  # Limit to 5 bullets
        return []

    def _extract_achievements(self, envelope: SignalEnvelope) -> list[str]:
        """Extract achievements from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of achievements
        """
        augmented = self._get_augmented_data(envelope)
        claims = augmented.get("claims", [])
        return [c.claim for c in claims if hasattr(c, "claim") and c.confidence > 0.7][:3]

    def _extract_skills(self, envelope: SignalEnvelope) -> list[str]:
        """Extract skills from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of skills
        """
        # Check payload for skills
        if hasattr(envelope.payload, "skills"):
            return envelope.payload.skills

        # Extract from content
        content = self._extract_content_from_payload(envelope.payload)
        skill_keywords = ["python", "java", "leadership", "analytics", "communication"]
        return [skill for skill in skill_keywords if skill.lower() in content.lower()]

    def _get_resume_sections(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get resume sections from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Resume sections
        """
        if hasattr(envelope.payload, "sections"):
            return envelope.payload.sections
        return {}

    def _extract_personalization(self, envelope: SignalEnvelope) -> list[str]:
        """Extract personalization points from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of personalization points
        """
        enriched = self._get_enriched_data(envelope)
        if "rag_results" in enriched:
            return [r.get("text", "")[:100] for r in enriched["rag_results"][:3]]
        return []

    def _extract_cta(self, envelope: SignalEnvelope) -> str:
        """Extract call to action from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Call to action text
        """
        adapted = self._get_adapted_tone(envelope)
        if adapted and "discuss" in adapted.lower():
            return "Let's discuss how I can contribute to your team."
        return "I would welcome the opportunity to discuss this further."

    def _extract_value_proposition(self, envelope: SignalEnvelope) -> str:
        """Extract value proposition from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Value proposition text
        """
        augmented = self._get_augmented_data(envelope)
        claims = augmented.get("claims", [])
        if claims and len(claims) > 0:
            first_claim = claims[0]
            return first_claim.claim if hasattr(first_claim, "claim") else str(first_claim)
        return "Experienced professional with proven track record"

    def _get_recipient_info(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get recipient information from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Recipient information
        """
        if hasattr(envelope.payload, "recipient_info"):
            return envelope.payload.recipient_info
        return {}

    def _get_augmented_data(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get augmented data from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Augmented data
        """
        if hasattr(envelope.payload, "metadata"):
            return envelope.payload.metadata

        # Check envelope metadata
        for key, value in envelope.metadata.items():
            if key.startswith("augmented_"):
                return value

        return {}

    def _get_enriched_data(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched data from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched data
        """
        if hasattr(envelope.payload, "metadata"):
            return {k: v for k, v in envelope.payload.metadata.items() if k.startswith("enriched_")}

        # Check envelope metadata
        enriched = {}
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                enriched[key.replace("enriched_", "")] = value

        return enriched

    def _get_adapted_tone(self, envelope: SignalEnvelope) -> str:
        """Get adapted tone from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Adapted tone text
        """
        augmented = self._get_augmented_data(envelope)
        return augmented.get("adapted_tone", "")

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    def _update_envelope_with_formatted(
        self, envelope: SignalEnvelope, formatted: dict[str, Any]
    ) -> None:
        """Update envelope with formatted output.

        Args:
            envelope: Signal envelope
            formatted: Formatted output
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(formatted)
        else:
            envelope.metadata.update({f"formatted_{k}": v for k, v in formatted.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "output_formatting"


class UnifiedSignalPipeline:
    """Unified pipeline for signal processing across engines."""

    def __init__(self, checkpoint_config: CheckpointConfig | None = None):
        """Initialize the unified pipeline.

        Args:
            checkpoint_config: Optional checkpoint configuration
        """
        self.stages = [
            InputProcessingStage(),
            ContextEnrichmentStage(),
            SignalAugmentationStage(),
            QualityValidationStage(),
            OutputFormattingStage(),
        ]

        # Initialize checkpoint manager
        self._checkpoint_manager = None
        self._checkpoint_config = checkpoint_config

        # Statistics
        self._stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "stage_failures": defaultdict(int),
            "checkpoints_saved": 0,
            "checkpoints_restored": 0,
        }

        # Thread safety
        self._lock = threading.Lock()

        logger.info("Initialized UnifiedSignalPipeline with checkpointing")

    async def _get_checkpoint_manager(self) -> CheckpointManager:
        """Get checkpoint manager instance.

        Returns:
            CheckpointManager instance
        """
        if self._checkpoint_manager is None:
            self._checkpoint_manager = await get_checkpoint_manager(self._checkpoint_config)
        return self._checkpoint_manager

    async def process(
        self,
        input_data: Any,
        engine_type: EngineType,
        domain_config: DomainConfig | None = None,
        resume_trace_id: str | None = None,
    ) -> SignalEnvelope:
        """Process input through the unified pipeline.

        Args:
            input_data: Input data to process
            engine_type: Type of engine
            domain_config: Domain-specific configuration
            resume_trace_id: Optional trace ID to resume from

        Returns:
            Processed signal envelope
        """
        with self._lock:
            self._stats["total_processed"] += 1

        # Create domain config if not provided
        if not domain_config:
            domain_config = get_shared_infrastructure().create_domain_config(engine_type)

        # Check for resume
        if resume_trace_id:
            envelope = await self._resume_from_checkpoint(resume_trace_id)
            if not envelope:
                logger.warning(f"Could not resume from trace_id: {resume_trace_id}")
                # Fall through to create new envelope
        else:
            envelope = None

        # Create new envelope if not resuming
        if not envelope:
            envelope = EnvelopeFactory.create_envelope(
                input_data,
                metadata={
                    "engine_type": engine_type.value,
                    "domain_config": domain_config.__class__.__name__,
                },
            )

        # Add domain config to envelope
        envelope.metadata["domain_config"] = json.dumps(domain_config.dict())

        # Execute stages with checkpointing
        checkpoint_manager = await self._get_checkpoint_manager()

        for stage in self.stages:
            stage_name = stage.stage_name

            try:
                # Check if stage already completed (for resumed envelopes)
                if envelope.has_completed_stage(stage_name):
                    logger.debug(f"Skipping already completed stage: {stage_name}")
                    continue

                # Execute stage
                logger.debug(f"Executing stage: {stage_name}")
                envelope = await stage.execute(envelope)

                # Save checkpoint after successful stage
                saved = await checkpoint_manager.save_checkpoint(envelope)
                if saved:
                    self._stats["checkpoints_saved"] += 1
                    logger.debug(f"Saved checkpoint after {stage_name}")

            except Exception as e:
                logger.error(f"Stage {stage_name} failed: {e}")

                # Save checkpoint with error state
                await checkpoint_manager.save_checkpoint(envelope)

                with self._lock:
                    self._stats["stage_failures"][stage_name] += 1

                # Re-raise exception
                raise PipelineExecutionError(
                    f"Pipeline failed at stage {stage_name}", envelope, stage_name, e
                )

        return envelope

    async def _resume_from_checkpoint(self, trace_id: str) -> SignalEnvelope | None:
        """Resume pipeline from checkpoint.

        Args:
            trace_id: Trace ID to resume from

        Returns:
            Envelope if found, None otherwise
        """
        checkpoint_manager = await self._get_checkpoint_manager()

        stage_names = [stage.stage_name for stage in self.stages]
        envelope = await checkpoint_manager.resume_from_checkpoint(trace_id, stage_names)

        if envelope:
            self._stats["checkpoints_restored"] += 1
            logger.info(f"Resumed pipeline from checkpoint: {trace_id}")
            last_stage = envelope.get_last_completed_stage()
            if last_stage:
                logger.info(f"Last completed stage: {last_stage}")

        return envelope

    async def get_checkpoint_status(self, trace_id: str) -> dict[str, Any] | None:
        """Get status of a checkpointed pipeline.

        Args:
            trace_id: Trace ID of pipeline

        Returns:
            Status dictionary if found
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        envelope = await checkpoint_manager.load_checkpoint(trace_id)

        if not envelope:
            return None

        return {
            "trace_id": trace_id,
            "envelope_id": str(envelope.id),
            "created_at": envelope.created_at.isoformat(),
            "updated_at": envelope.updated_at.isoformat(),
            "has_errors": envelope.has_errors,
            "error_count": envelope.error_count,
            "completed_stages": [
                s.stage_name for s in envelope.history if s.status == PipelineStageStatus.SUCCESS
            ],
            "failed_stages": envelope.get_failed_stages(),
            "last_completed_stage": envelope.get_last_completed_stage(),
            "total_duration_ms": envelope.calculate_total_duration(),
        }

    async def cleanup_checkpoints(self, older_than: timedelta | None = None) -> int:
        """Clean up old checkpoints.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of checkpoints cleaned up
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        return await checkpoint_manager.cleanup_old_checkpoints(older_than)

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = self._stats.copy()
            if stats["total_processed"] > 0:
                stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_processed"]
            else:
                stats["cache_hit_rate"] = 0.0
            return stats

    async def health_check(self) -> dict[str, Any]:
        """Check health of pipeline and checkpoint system.

        Returns:
            Health status
        """
        # Check checkpoint manager health
        checkpoint_manager = await self._get_checkpoint_manager()
        checkpoint_health = await checkpoint_manager.health_check()

        return {
            "status": "healthy" if checkpoint_health["status"] == "healthy" else "degraded",
            "stages": len(self.stages),
            "checkpoint_storage": checkpoint_health["status"],
            "stats": self.get_stats(),
        }


class PipelineExecutionError(Exception):
    """Error raised when pipeline execution fails."""

    def __init__(
        self,
        message: str,
        envelope: SignalEnvelope,
        failed_stage: str,
        cause: Exception | None = None,
    ):
        """Initialize pipeline execution error.

        Args:
            message: Error message
            envelope: Signal envelope at failure
            failed_stage: Name of failed stage
            cause: Optional cause exception
        """
        super().__init__(message)
        self.envelope = envelope
        self.failed_stage = failed_stage
        self.cause = cause


# Global pipeline instance
_pipeline: UnifiedSignalPipeline | None = None
_pipeline_lock = threading.Lock()


def get_unified_pipeline() -> UnifiedSignalPipeline:
    """Get the global unified pipeline instance.

    Returns:
        UnifiedSignalPipeline instance
    """
    global _pipeline
    with _pipeline_lock:
        if _pipeline is None:
            _pipeline = UnifiedSignalPipeline()
    return _pipeline


# Convenience functions
def process_resume_signal(input_data: Any, strict_mode: bool = True) -> dict[str, Any]:
    """Process resume signal through unified pipeline.

    Args:
        input_data: Resume input data
        strict_mode: Use strict quality thresholds

    Returns:
        Processed output
    """
    pipeline = get_unified_pipeline()

    # Create resume config
    infra = get_shared_infrastructure()
    config = infra.create_domain_config(EngineType.RESUME)

    return pipeline.process(input_data, EngineType.RESUME, config)


def process_outreach_signal(input_data: Any, strict_mode: bool = True) -> dict[str, Any]:
    """Process outreach signal through unified pipeline.

    Args:
        input_data: Outreach input data
        strict_mode: Use strict quality thresholds

    Returns:
        Processed output
    """
    pipeline = get_unified_pipeline()

    # Create outreach config
    infra = get_shared_infrastructure()
    config = infra.create_domain_config(EngineType.OUTREACH)

    return pipeline.process(input_data, EngineType.OUTREACH, config)
