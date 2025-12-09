"""
V3.8 Resume Generation System - Package Initialization
Complete module initialization with all v3.8 components
"""

__version__ = "3.8.0"
__author__ = "Resume Generation Team"

# Import core configuration
from .config_RES_v3_8 import (
    CONFIG, 
    AppConfig,
    EnricherConfig,
    ContentConstraintsConfig,
    ReasoningConfig,
    DATA_DIR,
    OUTPUT_DIR,
    DEFAULT_GENERATION_TEMPERATURE,
    DEFAULT_MAX_RETRIES,
    GEMINI_AVAILABLE,
    SKLEARN_AVAILABLE,
    GEMINI_PREMIUM_MODEL,
    CLAUDE_PREMIUM_MODEL,
    OPENAI_SYNTHESIS_MODEL
)

# Import governor agents
from .governor_v3_8 import (
    PolicyAgent,
    CostRouter,
    ContextRelayLayer,
    CritiqueTool,
    HIL_Interface,
    TraceRegistry,
    MAX_RETRIES_PER_NODE,
    DEFAULT_MODEL,
    MODEL_TIERS
)

# Import workflow orchestrator
from .workflow_RES_v3_8 import (
    WorkflowOrchestrator,
    load_master_resume
)

# Import tool modules
from .clerk_RES_v3_8 import ClerkExtractor
from .enricher_RES_v3_8 import DataEnricher
from .artist_RES_v3_8 import ArtistGenerator
from .renderer_RES_v3_8 import FileRenderer
from .interpreter_RES_v3_8 import CodeInterpreterTool
from .qa_auditor_RES_v3_8 import QAReportGenerator
from .rag_RES_v3_8 import EnhancedJobDescriptionAnalyzer

# Import validators
from .validator_RES_v3_8 import (
    JDValidator,
    ValidationEngine,
    JDEnforcementValidator,
    AppTrackerQAValidator,
    PreFlightValidator,
    ConstraintFailureClassifier
)

# Import prompt management
from .prompts_RES_v3_8 import (
    PromptManager,
    load_prompts
)

# Import state management
from .state_manager_RES_v3_8 import (
    StateManager,
    ManifestManager
)

# Import models
from .models_RES import (
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
from .utils_RES_v3_8 import (
    text_utils,
    calculate_signal_score,
    setup_workflow_logging,
    create_directory_if_missing,
    sanitize_filename,
    WorkflowLogFilter,
    DuplicateDetector,
    reasoning_config_to_api_params,
    enhance_system_prompt_with_reasoning
)

# Import validation components
from .validation_context import ValidationContext
from .validation_engine import ValidationEngineCore
from .validation_external import ExternalValidator
from .validation_rules import ValidationRuleSet

# Exceptions imported from models_RES

# Import Gemini service if available
try:
    from .gemini_service import GeminiService
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
