"""L1 Cognition Layer — Propose-only cognitive processing.

This layer provides cognitive processing, pattern recognition, and reasoning.
No execution, routing, or persistence logic belongs in this layer.
Only cognitive interfaces, reasoning engines, and telemetry are exported.
"""

# Cognitive interfaces and reasoning
from .P1_interfaces import *  # Primary interfaces only
from .engines import *  # Cognitive engines only
from .reasoning import *  # Reasoning utilities only
from .types import *  # Cognitive types only

# Telemetry and validation
from .telemetry import *  # Cognitive telemetry only
from .validators import *  # Cognitive validation only

# Explicitly forbid execution and routing imports
__all__ = [
    # Cognitive interfaces
    "CognitiveInterface",
    "PatternRecognizer",
    "InferenceEngine",
    
    # Reasoning engines
    "CognitiveEngine", 
    "MemoryEmbedder",
    "MetaClient",
    "ASTValidatorAgent",
    
    # Cognitive types
    "CognitiveContext",
    "InferenceResult",
    "PatternMatch",
    
    # Telemetry
    "CognitiveTelemetry",
    "PerformanceMetrics",
    
    # Validation
    "CognitiveValidator",
    "ReasoningValidator"
]

# Sovereignty assertion: This layer contains NO execution or routing logic
# L1 may only propose actions; execution belongs to L2, routing to L3
