#!/usr/bin/env python3
"""
Outreach Engine - RG v10_12
Modernized outreach capabilities with clean architecture
Phase F: LIC Capability Integration - All non-deprecated capabilities integrated
"""

__version__ = "10_12"
__description__ = "Outreach Engine with Lift & Shift + Enhanced capabilities"

# Core models and enums
from .models import (
    Route,
    Archetype,
    RouteConstraints,
    MessageContext,
    ValidationResult,
    ValidationSeverity
)

# L1 Planners - Hop-based Planning Layer
from .fusion_planner import (
    FusionPlanner,
    ValueProposition,
    MessageSectionPlan,
    FusionPlan
)

from .grounding_planner import (
    GroundingPlanner,
    GroundingPlan,
    Claim,
    Entity
)

from .persona_planner import (
    PersonaPlanner,
    PersonaPlan,
    ToneParameters,
    StyleGuidelines
)

from .profile_planner import (
    ProfilePlanner,
    ProfilePlan,
    ProfileSignals,
    ArchetypeInference
)

from .research_planner import (
    ResearchPlanner,
    ResearchPlan,
    QueryPlan,
    VectorParams
)

from .message_planner import (
    MessagePlanner,
    MessagePlan,
    MessageContent,
    SectionTemplate
)

# K Executors - Hop-based Execution Layer
from .k1_research import (
    K1ResearchExecutor,
    ResearchOutput
)

from .k2_insights import (
    K2InsightsExecutor,
    InsightOutput,
    ClaimScore
)

from .k3_draft import (
    K3DraftExecutor,
    DraftOutput,
    DraftSection
)

from .k4_regen import (
    K4RegenExecutor,
    RegenOutput,
    RegenViolation
)

from .k5_validation import (
    K5ValidationExecutor,
    ValidationOutput,
    ValidationViolation
)

from .k6_cta import (
    K6CTAExecutor,
    CTAOutput,
    CTAOption
)

from .k7_assembly import (
    K7AssemblyExecutor,
    AssemblyOutput,
    MessageComponent
)

# L3 Orchestrator - Hop-based Coordination Layer
from .orchestrator import (
    OutreachOrchestrator,
    OrchestratorOutput
)

from .routing import (
    RoutingEngine,
    RouteClassifier
)

# Configuration and parameter presets
from .config import (
    ContextManager,
    AdaptiveTemperatureController,
    ToolCallBudget,
    OutreachConfig
)

# RAG pipeline v75
from .rag import (
    RAGPipelineV75,
    HyDEProcessor,
    HybridRecall,
    CrossEncoderReranker,
    SelfRAGProcessor,
    EpisodicMemory,
    KnowledgeGraphInjector,
    FewShotInjector
)

# Insight models
from .insights import (
    SignalQualityScorer,
    ClaimConfidenceScorer,
    InsightsEngine
)

# CTA engine
from .cta import (
    CTAEngine,
    DateWindowEngine,
    ArchetypeCTA
)

# Tone and language rules
from .tone import (
    ToneEngine,
    TechnicalDensityScorer,
    LanguageMatcher
)

# Constraints and hygiene
from .constraints import (
    ConstraintEngine,
    ContentValidator,
    UnicodeHygiene,
    StructuralValidator
)

# Entity grounding framework
from .validation import (
    EntityGroundingFramework,
    PreGenerationExtractor,
    TeamWhitelist,
    EntityValidator,
    ValidationEngine,
    ErrorCodeRegistry
)

# Templates
from .templates import (
    TemplateEngine,
    CTATemplates,
    GreetingTemplates,
    SignatureTemplates,
    SystemTemplates
)

# K-node assembly engine
from .assembly import (
    KNodeAssemblyEngine,
    MessageAssembler
)

# Seniority engine
from .seniority import (
    SeniorityEngine,
    RecipientClassifier,
    SeniorityMapper
)

# Message schemas
from .schemas import (
    SenderProfile,
    RecipientProfile,
    JobDescription,
    MessageSchema,
    OutreachCampaign
)

# Export main components
__all__: list[str] = [
    # Core models
    'Route',
    'Archetype', 
    'RouteConstraints',
    'MessageContext',
    'ValidationResult',
    'ValidationSeverity',
    
    # Routing
    'RoutingEngine',
    'RouteClassifier',
    
    # Configuration
    'ContextManager',
    'AdaptiveTemperatureController',
    'ToolCallBudget',
    'OutreachConfig',
    
    # RAG Pipeline
    'RAGPipelineV75',
    'HyDEProcessor',
    'HybridRecall',
    'CrossEncoderReranker',
    'SelfRAGProcessor',
    'EpisodicMemory',
    'KnowledgeGraphInjector',
    'FewShotInjector',
    
    # Insights
    'SignalQualityScorer',
    'ClaimConfidenceScorer',
    'InsightsEngine',
    
    # CTA
    'CTAEngine',
    'DateWindowEngine',
    'ArchetypeCTA',
    
    # Tone
    'ToneEngine',
    'TechnicalDensityScorer',
    'LanguageMatcher',
    
    # Constraints
    'ConstraintEngine',
    'ContentValidator',
    'UnicodeHygiene',
    'StructuralValidator',
    
    # Grounding and Validation
    'EntityGroundingFramework',
    'PreGenerationExtractor',
    'TeamWhitelist',
    'EntityValidator',
    'ValidationEngine',
    'ErrorCodeRegistry',
    
    # Templates
    'TemplateEngine',
    'CTATemplates',
    'GreetingTemplates',
    'SignatureTemplates',
    'SystemTemplates',
    
    # Assembly
    'KNodeAssemblyEngine',
    'MessageAssembler',
    
    # Seniority
    'SeniorityEngine',
    'RecipientClassifier',
    'SeniorityMapper',
    
    # Schemas
    'SenderProfile',
    'RecipientProfile',
    'JobDescription',
    'MessageSchema',
    'OutreachCampaign'
]

def get_outreach_engine_version():
    """Get the current outreach engine version"""
    return __version__

def get_outreach_engine_description():
    """Get the outreach engine description"""
    return __description__
