"""Input processing stage for unified signal pipeline.

Extracted from unified_signal_pipeline.py for Key 42 compliance.
"""

import hashlib
import json
import time
from typing import Any, Dict

from .types import PipelineStage

logger = __import__('logging').getLogger(__name__)


class InputProcessingStage(PipelineStage):
    """Processes and normalizes input data."""

    def __init__(self):
        """Initialize input processing stage."""
        try:
            from ..rag_components import SemanticCache
            from ..hyde_processor import HyDEProcessor
            self.semantic_cache = SemanticCache()
            self.hyde_processor = HyDEProcessor()
        except ImportError:
            self.semantic_cache = None
            self.hyde_processor = None
            logger.warning("SemanticCache or HyDEProcessor not available")

    async def execute(self, envelope: Any) -> Any:
        """Process input data.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(f"Processing input for {envelope.payload.payload_type}")

            content = self._extract_content_from_payload(envelope.payload)

            cache_key = f"input_processed_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key) if self.semantic_cache else None

            if cached:
                self._update_payload_with_processed_data(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name,
                    (time.time() - start_time) * 1000,
                    metadata={"cache_hit": True}
                )
                return envelope

            processed = await self._process_content(content, envelope)
            self._update_payload_with_processed_data(envelope, processed)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, processed)

            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"cache_hit": False}
            )

            return envelope

        except Exception as e:
            logger.error(f"Input processing failed: {e}")
            envelope.mark_stage_failed(
                stage_name,
                str(e),
                (time.time() - start_time) * 1000
            )
            raise

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, 'text'):
            return payload.text
        elif hasattr(payload, 'sections'):
            return json.dumps(payload.sections)
        elif hasattr(payload, 'recipient_info'):
            return json.dumps({
                'recipient': payload.recipient_info,
                'campaign': payload.campaign_context
            })
        elif hasattr(payload, 'data'):
            return json.dumps(payload.data)
        else:
            return str(payload)

    async def _process_content(self, content: str, envelope: Any) -> Dict[str, Any]:
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
            "language": "en"
        }

        if self.hyde_processor:
            if envelope.payload.payload_type.value == "resume_data":
                query = f"resume achievements skills {content[:100]}"
            else:
                query = f"outreach personalization {content[:100]}"

            expanded = self.hyde_processor.expand_query_with_hyde(
                query, envelope.payload.payload_type.value
            )
            result["expanded_query"] = expanded

        return result

    def _update_payload_with_processed_data(self, envelope: Any, processed: Dict[str, Any]) -> None:
        """Update payload with processed data.

        Args:
            envelope: Signal envelope
            processed: Processed data
        """
        if hasattr(envelope.payload, 'metadata'):
            envelope.payload.metadata.update(processed)
        else:
            envelope.metadata.update({f"processed_{k}": v for k, v in processed.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "input_processing"
