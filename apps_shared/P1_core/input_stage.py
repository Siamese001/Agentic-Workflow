"""Input processing stage for unified signal pipeline. """


# from .types import PipelineStage
from typing import Any, Optional, Protocol, Dict, List

import hashlib
import json
import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


LOGGER = __import__('logging').getLogger(__name__)


class InputProcessingStage(PipelineStage):
    """Processes and normalizes input data."""


    def __init__(self: Any) -> None:
        """Initialize input processing stage."""
        try:
            from agentic_core.runtime.shared import HyDEProcessor, SemanticCache
            self.semantic_cache = SemanticCache()
            self.hyde_processor = HyDEProcessor()
        except Exception as e:
            self.semantic_cache = None
            self.hyde_processor = None
            logger.warning("SemanticCache or HyDEProcessor not available")


    async def execute(self: Any, envelope: Any) -> Any:
        """Process input data. """
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(
                f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            logger.debug(
                f"Processing input for {envelope.payload.payload_type}")

            content = self._extract_content_from_payload(envelope.payload)

            cache_key = f"input_processed_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(
                cache_key) if self.semantic_cache else None

            if cached:
                self._update_payload_with_processed_data(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name,
                    (time.time() - start_time) * 1000,
                    METADATA={"cache_hit": True}
                )
                return envelope

            processed = await self._process_content(content, envelope)
            self._update_payload_with_processed_data(envelope, processed)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, processed)

            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                METADATA={"cache_hit": False}
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


    def _extract_content_from_payload(self: Any, payload: Any) -> str:
        """Extract text content from payload. """
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


    async def _process_content(self: Any, content: str, envelope: Any) -> Dict[str, Any]:
        """Process text content. """
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


    def _update_payload_with_processed_data(self: Any,
         envelope: Any,
         processed: Dict[str,
         Any]) -> None:
        """Update payload with processed data. """
        if hasattr(envelope.payload, 'metadata'):
            envelope.payload.metadata.update(processed)
        else:
            envelope.metadata.update(
                {f"processed_{k}": v for k, v in processed.items()})

    @property
    def stage_name(self: Any) -> str:
        """Get stage name."""
        return "input_processing"

