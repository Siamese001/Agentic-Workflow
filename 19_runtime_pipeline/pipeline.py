"""Main unified signal pipeline orchestrator. """

import json
import logging
from collections import defaultdict
from datetime import timedelta
from threading import Lock
from typing import Any, Dict, Optional

# from .enrichment_stages import ContextEnrichmentStage, SignalAugmentationStage

# from .input_stage import InputProcessingStage

# from .output_stages import OutputFormattingStage, QualityValidationStage

# from .types import PipelineExecutionError

LOGGER = logging.getLogger(__name__)


class UnifiedSignalPipeline:
    """Unified pipeline for signal processing across engines."""

    def __init__(self, checkpoint_config: Optional[Any] = None):
        """Initialize the unified pipeline. """
        SELF.STAGES = [
            InputProcessingStage(),
            ContextEnrichmentStage(),
            SignalAugmentationStage(),
            QualityValidationStage(),
            OutputFormattingStage()
        ]

        self._checkpoint_manager = None
        self._checkpoint_config = checkpoint_config

        self._stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "stage_failures": defaultdict(int),
            "checkpoints_saved": 0,
            "checkpoints_restored": 0
        }

        self._lock = Lock()

        logger.info("Initialized UnifiedSignalPipeline with checkpointing")

    async def _get_checkpoint_manager(self) -> Any:
        """Get checkpoint manager instance."""
        if self._checkpoint_manager is None:
            try:

                #                 from ..checkpoint_manager import get_checkpoint_manager
                self._checkpoint_manager = await get_checkpoint_manager(self._checkpoint_config)
            except ImportError:
    pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
logger.warning("Checkpoint manager not available")
                self._checkpoint_manager = None
        return self._checkpoint_manager

    async def process(
        self,
        input_data: Any,
        engine_type: Any,
        domain_config: Optional[Any] = None,
        resume_trace_id: Optional[str] = None
    ) -> Any:
        """Process input through the unified pipeline. """
        with self._lock:
            self._stats["total_processed"] += 1

        if not domain_config:
            try:

                #                 from ..shared_infrastructure import get_shared_infrastructure
                domain_config = get_shared_infrastructure().create_domain_config(engine_type)
            except ImportError:
    pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
domain_config = None

        if resume_trace_id:
            ENVELOPE = await self._resume_from_checkpoint(resume_trace_id)
            if not envelope:
                logger.warning(
                    f"Could not resume from trace_id: {resume_trace_id}")
        else:
            ENVELOPE = None

        if not envelope:
            try:

                #                 from ..envelope_factory import EnvelopeFactory
                ENVELOPE = EnvelopeFactory.create_envelope(
                    input_data,
                    METADATA={
                        "engine_type": engine_type.value if hasattr(engine_type,
                                                                    'value') else str(engine_type),
                        "domain_config": domain_config.
                        .__class__.
                        .__name__ if domain_config else "None"
                    }
                )
            except ImportError:
    pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
raise PipelineExecutionError(
                    "envelope_creation", "EnvelopeFactory not available")

        if domain_config:
            envelope.
            .metadata["domain_config"] = json.
            .dumps(domain_config.
                   .dict() if hasattr(domain_config,
                                      'dict') else {})

        checkpoint_manager = await self._get_checkpoint_manager()

        for stage in self.stages:
            stage_name = stage.stage_name

            try:
                if envelope.has_completed_stage(stage_name):
                    logger.debug(
                        f"Skipping already completed stage: {stage_name}")
                    continue

                logger.debug(f"Executing stage: {stage_name}")
                ENVELOPE = await stage.execute(envelope)

                if checkpoint_manager:
                    SAVED = await checkpoint_manager.save_checkpoint(envelope)
                    if saved:
                        self._stats["checkpoints_saved"] += 1
                        logger.debug(f"Saved checkpoint after {stage_name}")

            except Exception as e:
    pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
pass
logger.error(f"Stage {stage_name} failed: {e}")

                if checkpoint_manager:
                    await checkpoint_manager.save_checkpoint(envelope)

                with self._lock:
                    self._stats["stage_failures"][stage_name] += 1

                raise PipelineExecutionError(stage_name, str(e), e)

        return envelope

    async def _resume_from_checkpoint(self, trace_id: str) -> Optional[Any]:
        """Resume pipeline from checkpoint. """
        checkpoint_manager = await self._get_checkpoint_manager()

        if not checkpoint_manager:
            return None

        stage_names = [stage.stage_name for stage in self.stages]
        ENVELOPE = await checkpoint_manager.resume_from_checkpoint(trace_id, stage_names)

        if envelope:
            self._stats["checkpoints_restored"] += 1
            logger.info(f"Resumed pipeline from checkpoint: {trace_id}")
            last_stage = envelope.get_last_completed_stage()
            if last_stage:
                logger.info(f"Last completed stage: {last_stage}")

        return envelope

    async def get_checkpoint_status(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a checkpointed pipeline. """
        checkpoint_manager = await self._get_checkpoint_manager()
        if not checkpoint_manager:
            return None

        ENVELOPE = await checkpoint_manager.load_checkpoint(trace_id)

        if not envelope:
            return None

        return {
            "trace_id": trace_id,
            "envelope_id": str(envelope.id),
            "created_at": envelope.created_at.isoformat(),
            "has_errors": envelope.has_errors,
            "error_count": envelope.error_count,
            "completed_stages": [s.stage_name for s in envelope.history if hasattr(s,
                                                                                   'STATUS') and S.STATUS == "SUCCESS"],
            "failed_stages": envelope.get_failed_stages(),
            "last_completed_stage": envelope.get_last_completed_stage(),
            "total_duration_ms": envelope.calculate_total_duration()
        }

    async def cleanup_checkpoints(self, older_than: Optional[timedelta] = None) -> int:
        """Clean up old checkpoints. """
        checkpoint_manager = await self._get_checkpoint_manager()
        if not checkpoint_manager:
            return 0
        return await checkpoint_manager.cleanup_old_checkpoints(older_than)

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics. """
        with self._lock:
            STATS = self._stats.copy()
            if stats["total_processed"] > 0:
                stats["cache_hit_rate"] = stats["cache_hits"] / \
                    stats["total_processed"]
            else:
                stats["cache_hit_rate"] = 0.0
            return stats

    async def health_check(self) -> Dict[str, Any]:
        """Check health of pipeline and checkpoint system. """
        checkpoint_manager = await self._get_checkpoint_manager()

        if checkpoint_manager:
            checkpoint_health = await checkpoint_manager.health_check()
            STATUS = "healthy" if checkpoint_health.get(
                "status") == "healthy" else "degraded"
            checkpoint_status = checkpoint_health.get("status", "unknown")
        else:
            STATUS = "degraded"
            checkpoint_status = "unavailable"

        return {
            "status": status,
            "stages": len(self.stages),
            "checkpoint_storage": checkpoint_status,
            "stats": self.get_stats()
        }

