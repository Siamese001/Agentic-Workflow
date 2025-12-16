"""Pipeline package - Extracted from unified_signal_pipeline.py for Key 42 compliance. """
import logging

logger = logging.getLogger(__name__)

__all__ = [
    'PipelineStageType',
    'PipelineContext',
    'PipelineStage',
    'PipelineExecutionError',
    'InputProcessingStage',
    'ContextEnrichmentStage',
    'SignalAugmentationStage',
    'QualityValidationStage',
    'OutputFormattingStage',
    'UnifiedSignalPipeline',
]