"""Pipeline package - Extracted from unified_signal_pipeline.py for Key 42 compliance.

This package contains the modular components of the unified signal pipeline:
- types: Base types, enums, and abstract classes
- input_stage: Input processing stage
- enrichment_stages: Context enrichment and signal augmentation stages
- output_stages: Quality validation and output formatting stages
- pipeline: Main UnifiedSignalPipeline orchestrator
"""

from .types import (
    PipelineStageType,
    PipelineContext,
    PipelineStage,
    PipelineExecutionError
)
from .input_stage import InputProcessingStage
from .enrichment_stages import ContextEnrichmentStage, SignalAugmentationStage
from .output_stages import QualityValidationStage, OutputFormattingStage
from .pipeline import UnifiedSignalPipeline

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
