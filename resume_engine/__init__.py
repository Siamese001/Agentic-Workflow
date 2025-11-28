#!/usr/bin/env python3
"""
Resume Engine - RG v10_12
Focused resume generation pipeline with L1-L5 architecture
Phase F: Resume Engine Consolidation - All non-deprecated capabilities integrated
"""

__version__ = "10_12"
__description__ = "Resume Engine with Lift & Shift + Enhanced capabilities"

# Core models and configuration
from .models import (
    ValidationSeverity,
    ResumeSection,
    GateDecision,
    BulletProvenance,
    ValidationResult,
    ThematicAnalysis,
    RAGEvidence,
    RAGCritique,
    RAGState,
    SkillRequirement,
    SkillCluster,
    MasterResumeIndex,
    CompetitiveIntelligence,
    RetrievalSource,
    FilePathsConfig,
    ArtistConfig,
    ValidatorConfig,
    WebRagConfig,
    EnricherConfig,
    ContentConstraintsConfig,
    SignalControlConfig,
    AppConfig,
    JDEnforcementRule,
    JDEnforcementResult
)

# State management
from .state import (
    StagingBufferError,
    ImmutableStagingBuffer,
    TextSanitizer,
    ValidationContext
)

# L2 - Extraction and Enrichment Layer
from .l2.extraction import (
    ClerkExtractor,
    DuplicateDetector,
    DataEnricher
)

# L5 - Validation Layer
from .l5.validation_engine import (
    ValidationRule,
    ValidationEngine,
    JDEnforcementValidator,
    PreFlightValidator
)

# Rendering Layer
from .rendering import FileRenderer

# Export main components
__all__ = [
    # Core models
    'ValidationSeverity',
    'ResumeSection', 
    'GateDecision',
    'BulletProvenance',
    'ValidationResult',
    'ThematicAnalysis',
    'RAGEvidence',
    'RAGCritique',
    'RAGState',
    'SkillRequirement',
    'SkillCluster',
    'MasterResumeIndex',
    'CompetitiveIntelligence',
    'RetrievalSource',
    
    # Configuration
    'FilePathsConfig',
    'ArtistConfig',
    'ValidatorConfig',
    'WebRagConfig',
    'EnricherConfig',
    'ContentConstraintsConfig',
    'SignalControlConfig',
    'AppConfig',
    'JDEnforcementRule',
    'JDEnforcementResult',
    
    # State management
    'StagingBufferError',
    'ImmutableStagingBuffer',
    'TextSanitizer',
    'ValidationContext',
    
    # L2 Components
    'ClerkExtractor',
    'DuplicateDetector',
    'DataEnricher',
    
    # L5 Components
    'ValidationRule',
    'ValidationEngine',
    'JDEnforcementValidator',
    'PreFlightValidator',
    
    # Rendering
    'FileRenderer'
]

def get_resume_engine_version():
    """Get the current resume engine version"""
    return __version__

def get_resume_engine_description():
    """Get the resume engine description"""
    return __description__
