"""Quality validation and output formatting stages.

Extracted from unified_signal_pipeline.py for Key 42 compliance.
Contains QualityValidationStage and OutputFormattingStage.
"""

import hashlib
import time
from typing import Any, Dict, List

from .types import PipelineStage

logger = __import__('logging').getLogger(__name__)


class QualityValidationStage(PipelineStage):
    """Validates signal quality against standards."""

    def __init__(self):
        """Initialize quality validation stage."""
        try:
            from ..bias_auditor import BiasAuditor
            from ..pii_scrubber import PIIScrubber
            from ..constitutional_ai import ConstitutionalAISystem
            from ..rag_components import SemanticCache
            self.bias_auditor = BiasAuditor()
            self.pii_scrubber = PIIScrubber()
            self.constitutional_ai = ConstitutionalAISystem()
            self.semantic_cache = SemanticCache()
        except ImportError:
            self.bias_auditor = None
            self.pii_scrubber = None
            self.constitutional_ai = None
            self.semantic_cache = None
            logger.warning("Quality validation components not available")

    async def execute(self, envelope: Any) -> Any:
        """Validate quality."""
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            content = self._extract_content(envelope.payload)

            if not content:
                envelope.mark_stage_skipped(stage_name, "No content to validate")
                return envelope

            cache_key = f"quality_validated_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key) if self.semantic_cache else None

            if cached:
                self._update_envelope_with_validation(envelope, cached)
                envelope.mark_stage_complete(stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": True})
                return envelope

            validation_results = await self._perform_validations(content, envelope)
            self._update_envelope_with_validation(envelope, validation_results)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, validation_results)

            envelope.mark_stage_complete(stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": False})
            return envelope

        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content(self, payload: Any) -> str:
        """Extract content from payload."""
        if hasattr(payload, 'text'):
            return payload.text
        elif hasattr(payload, 'sections'):
            return str(payload.sections)
        return str(payload)

    async def _perform_validations(self, content: str, envelope: Any) -> Dict[str, Any]:
        """Perform all quality validations."""
        results = {"passed": True, "issues": []}

        if self.bias_auditor:
            bias_result = self.bias_auditor.audit_bias(content)
            results["bias_audit"] = bias_result
            if bias_result.get("violations"):
                results["passed"] = False
                results["issues"].append("bias_detected")

        if self.pii_scrubber:
            pii_result = self.pii_scrubber.scrub_pii(content)
            results["pii_scan"] = pii_result
            if pii_result.get("matches"):
                results["issues"].append("pii_detected")

        if self.constitutional_ai:
            constitutional_result = self.constitutional_ai.review_content(content)
            results["constitutional_review"] = constitutional_result
            if constitutional_result.get("violations"):
                results["passed"] = False
                results["issues"].append("constitutional_violation")

        return results

    def _update_envelope_with_validation(self, envelope: Any, validation: Dict[str, Any]) -> None:
        """Update envelope with validation results."""
        if hasattr(envelope.payload, 'metadata'):
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
        try:
            from ..rag_components import SemanticCache
            self.semantic_cache = SemanticCache()
        except ImportError:
            self.semantic_cache = None
            logger.warning("SemanticCache not available")

    async def execute(self, envelope: Any) -> Any:
        """Format output."""
        start_time = time.time()
        stage_name = self.stage_name

        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed")
            return envelope

        envelope.mark_stage_start(stage_name)

        try:
            content = self._extract_content(envelope.payload)

            if not content:
                envelope.mark_stage_skipped(stage_name, "No content to format")
                return envelope

            cache_key = f"output_formatted_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key) if self.semantic_cache else None

            if cached:
                self._update_envelope_with_formatted_output(envelope, cached)
                envelope.mark_stage_complete(stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": True})
                return envelope

            formatted = await self._format_output(content, envelope)
            self._update_envelope_with_formatted_output(envelope, formatted)

            if self.semantic_cache:
                self.semantic_cache.set(cache_key, formatted)

            envelope.mark_stage_complete(stage_name, (time.time() - start_time) * 1000, metadata={"cache_hit": False})
            return envelope

        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content(self, payload: Any) -> str:
        """Extract content from payload."""
        if hasattr(payload, 'text'):
            return payload.text
        elif hasattr(payload, 'sections'):
            return str(payload.sections)
        return str(payload)

    async def _format_output(self, content: str, envelope: Any) -> Dict[str, Any]:
        """Format output based on engine type."""
        payload_type = envelope.payload.payload_type.value if hasattr(envelope.payload, 'payload_type') else "unknown"

        formatted = {
            "formatted_content": content,
            "format_type": payload_type,
            "metadata": {
                "word_count": len(content.split()),
                "char_count": len(content)
            }
        }

        if payload_type == "resume_data":
            formatted["sections"] = self._format_resume_sections(content)
        elif payload_type == "outreach_data":
            formatted["message"] = self._format_outreach_message(content)

        return formatted

    def _format_resume_sections(self, content: str) -> Dict[str, str]:
        """Format resume sections."""
        return {
            "summary": content[:200],
            "experience": content[200:500],
            "skills": content[500:]
        }

    def _format_outreach_message(self, content: str) -> Dict[str, str]:
        """Format outreach message."""
        return {
            "subject": content[:50],
            "body": content[50:],
            "signature": "Best regards"
        }

    def _update_envelope_with_formatted_output(self, envelope: Any, formatted: Dict[str, Any]) -> None:
        """Update envelope with formatted output."""
        if hasattr(envelope.payload, 'metadata'):
            envelope.payload.metadata.update(formatted)
        else:
            envelope.metadata.update({f"formatted_{k}": v for k, v in formatted.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "output_formatting"
