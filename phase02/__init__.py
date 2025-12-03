#!/usr/bin/env python3
"""
Phase 2 Semantic Structural & Code Diff Planning

This package implements the complete Phase 2 pipeline for semantic structural
and code diff planning with zero-loss guarantees and comprehensive 88 K-key
validation.

Components:
- common: Shared data structures and constants
- ssot_filesystem_loader: SSoT and filesystem state loading
- semantic_cache_loader: Phase 0.5 semantic cache loading
- structural_diff_engine: Structural difference computation
- semantic_diff_engine: Semantic difference computation
- composite_intent_generator: Intent computation and generation
- unified_plan_generator: Migration plan generation
- phase02_orchestrator: Complete pipeline orchestration

Usage:
    from phase02 import Phase02Orchestrator, Phase2Config
    
    config = Phase2Config(dry_run=True, verbose=True)
    orchestrator = Phase02Orchestrator(config)
    success = orchestrator.run_pipeline()
"""

from .common import (
    # Data structures
    ValidationResult,
    Phase2Step,
    Phase2TransactionManifest,
    SSoTState,
    FilesystemState,
    SemanticCacheState,
    StructuralDiff,
    SemanticDiff,
    CompositeIntent,
    Operation,
    MigrationPlan,
    Phase2Config,
    
    # Enums
    OperationType,
    DiffType,
    
    # Constants
    ALL_PHASE2_VALIDATION_KEYS,
    ALLOWED_OPERATIONS,
    PROTECTED_PATHS,
    PHASE02_SCHEMA_VERSION,
    PHASE02_MODE
)

from .ssot_filesystem_loader import SSoTFilesystemLoader
from .semantic_cache_loader import SemanticCacheLoader
from .structural_diff_engine import StructuralDiffEngine
from .semantic_diff_engine import SemanticDiffEngine
from .composite_intent_generator import CompositeIntentGenerator
from .unified_plan_generator import UnifiedPlanGenerator
from .orchestrator import Phase02Orchestrator

__version__ = "1.0.0"
__description__ = "Phase 2 Semantic Structural & Code Diff Planning"
__author__ = "Agentic-Workflow"

__all__ = [
    # Main orchestrator
    "Phase02Orchestrator",
    
    # Configuration
    "Phase2Config",
    
    # Components
    "SSoTFilesystemLoader",
    "SemanticCacheLoader", 
    "StructuralDiffEngine",
    "SemanticDiffEngine",
    "CompositeIntentGenerator",
    "UnifiedPlanGenerator",
    
    # Data structures
    "ValidationResult",
    "Phase2Step",
    "Phase2TransactionManifest",
    "SSoTState",
    "FilesystemState",
    "SemanticCacheState",
    "StructuralDiff",
    "SemanticDiff",
    "CompositeIntent",
    "Operation",
    "MigrationPlan",
    
    # Enums
    "OperationType",
    "DiffType",
    
    # Constants
    "ALL_PHASE2_VALIDATION_KEYS",
    "ALLOWED_OPERATIONS",
    "PROTECTED_PATHS",
    "PHASE02_SCHEMA_VERSION",
    "PHASE02_MODE"
]
