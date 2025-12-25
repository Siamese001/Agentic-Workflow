"""
Runtime Shared Modules
Resurrected from archives - provides RAG components, safety tools, and optimization utilities.
"""

# RAG Components
from .rag_components import (

    SemanticCache,
    SelfRAGProcessor,
    KnowledgeGraphInjector,
    EpisodicMemory,
    FewShotInjector,
)

# Safety Components
from .pii_scrubber import PIIScrubber
from .bias_auditor import BiasAuditor
from .constitutional_ai import ConstitutionalAISystem

# Optimization Components
# TODO: Systematic Repair (Option 2) - syntax errors require fixing
# from .hyde_processor import HyDEProcessor
# from .tone_model import ToneModel
from .claim_confidence import ClaimConfidenceScorer
from .prompt_optimizer import PromptOptimizer

# Infrastructure Components
from .checkpoint_manager import CheckpointManager, get_checkpoint_manager
from .shared_infrastructure import SharedInfrastructure, get_shared_infrastructure
from .envelope_factory import Envelope, EnvelopeFactory

__all__ = [
    # RAG
    "SemanticCache",
    "SelfRAGProcessor",
    "KnowledgeGraphInjector",
    "EpisodicMemory",
    "FewShotInjector",
    # Safety
    "PIIScrubber",
    "BiasAuditor",
    "ConstitutionalAISystem",
    # Optimization
    # "HyDEProcessor",  # TODO: Repair hyde_processor.py
    # "ToneModel",  # TODO: Repair tone_model.py
    "ClaimConfidenceScorer",
    "PromptOptimizer",
    # Infrastructure
    "CheckpointManager",
    "get_checkpoint_manager",
    "SharedInfrastructure",
    "get_shared_infrastructure",
    "Envelope",
    "EnvelopeFactory",
]
