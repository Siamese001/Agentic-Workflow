"""
V3.8 Resume Generation System - Package Initialization
Complete module initialization with all v3.8 components
"""

__version__ = "3.8.0"
__author__ = "Resume Generation Team"

# Import core configuration

# Import governor agents

# Import workflow orchestrator

# Import tool modules
from archives.legacy_resume_gen.Older Microservices Models.v3.8.clerk_RES_v3_8 import ClerkExtractor
from archives.legacy_resume_gen.Older Microservices Models.v3.8.enricher_RES_v3_8 import DataEnricher
from archives.legacy_resume_gen.Older Microservices Models.v3.8.artist_RES_v3_8 import ArtistGenerator
from archives.legacy_resume_gen.Older Microservices Models.v3.8.renderer_RES_v3_8 import FileRenderer
from archives.legacy_resume_gen.Older Microservices Models.v3.8.interpreter_RES_v3_8 import CodeInterpreterTool
from archives.legacy_resume_gen.Older Microservices Models.v3.8.qa_auditor_RES_v3_8 import QAReportGenerator
from archives.legacy_resume_gen.Older Microservices Models.v3.8.rag_RES_v3_8 import EnhancedJobDescriptionAnalyzer

# Import validators

# Import prompt management

# Import state management

# Import models
from runtime.compat.models_RES import ResumeSection, ValidationSeverity, HopStatus, GateDecision, BulletProvenance, CircuitState, HopCheckpoint, ImmutableStagingBuffer, JDEnforcementResult, JDEnforcementRule, RAGState, RAGTelemetry, ThematicAnalysis, ValidationResult, CompetitiveIntelligence, RAGMission, FactualFailureException, HopExecutionError, StagingBufferError
    # Enums
    ResumeSection,
    ValidationSeverity,
    HopStatus,
    GateDecision,
    
    # Data classes
    BulletProvenance,
    CircuitState,
    HopCheckpoint,
    ImmutableStagingBuffer,
    JDEnforcementResult,
    JDEnforcementRule,
    RAGState,
    RAGTelemetry,
    ThematicAnalysis,
    ValidationResult,
    CompetitiveIntelligence,
    RAGMission,
    
    # Exceptions (re-exported from exceptions module)
    FactualFailureException,
    HopExecutionError,
    StagingBufferError
)

# Import utilities

# Import validation components
from archives.legacy_resume_gen.Older Microservices Models.v3.8.validation_context import ValidationContext
from archives.legacy_resume_gen.Older Microservices Models.v3.8.validation_engine import ValidationEngineCore
from archives.legacy_resume_gen.Older Microservices Models.v3.8.validation_external import ExternalValidator
from archives.legacy_resume_gen.Older Microservices Models.v3.8.validation_rules import ValidationRuleSet

# Exceptions imported from models_RES

# Import Gemini service if available
try:
    from archives.legacy_resume_gen.Older Microservices Models.v2.gemini_service import GeminiService
    GEMINI_SERVICE_AVAILABLE = True
except ImportError:
    GEMINI_SERVICE_AVAILABLE = False

# Define public API
__all__ = [
    # Version
    '__version__',
    
    # Configuration
    'CONFIG',
    'AppConfig',
    'EnricherConfig',
    'ContentConstraintsConfig',
    'ReasoningConfig',
    'DATA_DIR',
    'OUTPUT_DIR',
    
    # Core workflow
    'WorkflowOrchestrator',
    'load_master_resume',
    
    # Governor agents
    'PolicyAgent',
    'CostRouter',
    'ContextRelayLayer',
    'CritiqueTool',
    'HIL_Interface',
    'TraceRegistry',
    
    # Tool modules
    'ClerkExtractor',
    'DataEnricher',
    'ArtistGenerator',
    'FileRenderer',
    'CodeInterpreterTool',
    'QAReportGenerator',
    'EnhancedJobDescriptionAnalyzer',
    
    # Validators
    'JDValidator',
    'ValidationEngine',
    'JDEnforcementValidator',
    'AppTrackerQAValidator',
    'PreFlightValidator',
    'ConstraintFailureClassifier',
    
    # Prompt management
    'PromptManager',
    
    # State management
    'StateManager',
    'ManifestManager',
    
    # Models and types
    'ResumeSection',
    'ValidationSeverity',
    'HopStatus',
    'GateDecision',
    'BulletProvenance',
    'CircuitState',
    'HopCheckpoint',
    'ImmutableStagingBuffer',
    'JDEnforcementResult',
    'JDEnforcementRule',
    'RAGState',
    'RAGTelemetry',
    'ThematicAnalysis',
    'ValidationResult',
    'CompetitiveIntelligence',
    'RAGMission',
    
    # Utilities
    'text_utils',
    'calculate_signal_score',
    'setup_workflow_logging',
    'create_directory_if_missing',
    'sanitize_filename',
    
    # Feature flags
    'GEMINI_AVAILABLE',
    'SKLEARN_AVAILABLE',
    'GEMINI_SERVICE_AVAILABLE',
    
    # Constants
    'MAX_RETRIES_PER_NODE',
    'DEFAULT_MODEL',
    'DEFAULT_GENERATION_TEMPERATURE',
    'DEFAULT_MAX_RETRIES'
]

# Initialize package-level logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Print initialization message if verbose
if __name__ == "__main__":
    print(f"V3.8 Resume Generation System initialized (version {__version__})")
    print(f"Gemini Available: {GEMINI_AVAILABLE}")
    print(f"Sklearn Available: {SKLEARN_AVAILABLE}")
    print(f"Configuration loaded from: {CONFIG}")
