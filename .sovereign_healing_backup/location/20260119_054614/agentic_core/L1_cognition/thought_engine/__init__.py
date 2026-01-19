from __future__ import annotations
"""
L1_cognition/thought_engine – Sovereign Territory

Purpose:
    Chain-of-thought, tree-of-thought, ReAct pattern implementations. Reference: Yao et al. (2022) ReAct paper.

Best Practices:
    - Single responsibility per module
    - Explicit imports only from approved layers (gravity compliance)
    - All public functions/classes fully typed and documented
    - No side effects unless explicitly in L2_execution or L4_state
    - No raw strings — use prompt_governance for prompts
    - No inline Pydantic models — use schemas/models

Current Status (January 7, 2026):
    - Territory claimed and protected
    - Canonical cognitive agents established
    - L2 Builder agents (with healing) archived from L1 (superseded)

Canonical Exports:
    - CanonBaseAgent: Base class for cognitive agents
    - RgReflectionAgent: Cognitive reflection and meta-reasoning
    
Note: StructuralEngineerAgent, SystemArchitectAgent, and RgStrategicPlannerAgent
      have evolved to L2_execution/ToolRegistry/ with healing capabilities.
"""

# Graceful imports with fallbacks for missing modules
try:
    from .CanonBaseAgent import CanonBaseAgent
except ImportError:
    try:
        from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent
    except ImportError:
        CanonBaseAgent = None

try:
    from .ReflectionAgent import RgReflectionAgent as ReflectionAgent
except ImportError:
    ReflectionAgent = None

# Public API surface — expose only what's available
__all__ = []
if CanonBaseAgent is not None:
    __all__.append("CanonBaseAgent")
if ReflectionAgent is not None:
    __all__.append("ReflectionAgent")
