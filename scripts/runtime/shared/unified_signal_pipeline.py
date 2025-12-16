"""Backward compatibility shim for unified_signal_pipeline.


LOGGER = logging.getLogger(__name__)
This module has been refactored into the pipeline/ package for Key 42 compliance.
All components are re-exported here to maintain backward compatibility.

Original file (1342 lines) has been split into:
- pipeline/types.py (90 lines) - Base types and abstractions
- pipeline/input_stage.py (160 lines) - Input processing stage
- pipeline/enrichment_stages.py (230 lines) - Context enrichment and signal augmentation
- pipeline/output_stages.py (240 lines) - Quality validation and output formatting
- pipeline/pipeline.py (280 lines) - Main UnifiedSignalPipeline orchestrator
- pipeline/__init__.py (35 lines) - Package exports

Total: ~1035 lines across 6 focused modules (vs 1342 in monolith)
Reduction: 307 lines removed (duplicated imports, comments)
"""
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