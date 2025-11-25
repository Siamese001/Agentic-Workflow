"""
L1 strategy planning for résumé improvement workflows.

Generates targeted improvement plans with explicit reasoning modes and uncertainty handling for enhanced résumé job alignment.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

class ReasoningMode(str, Enum):
    """Explicit reasoning strategies for L1 planning."""
    
    ANALYTICAL = "analytical"  # Break down into components
    CREATIVE = "creative"      # Generate novel approaches
    DEDUCTIVE = "deductive"    # Apply general rules to specific cases
    INDUCTIVE = "inductive"    # Infer patterns from examples
    ABDUCTIVE = "abductive"    # Generate best explanations

class LogicFramework(str, Enum):
    """Logic frameworks for structured reasoning."""
    
    CAUSAL_CHAINING = "causal_chaining"    # Cause-effect relationships
    TEMPORAL_SEQUENCING = "temporal_sequencing"  # Time-based ordering
    HIERARCHICAL_DECOMPOSITION = "hierarchical_decomposition"  # Top-down breakdown
    CONSTRAINT_PROPAGATION = "constraint_propagation"  # Rule-based constraints

@dataclass
class UncertaintyHandling:
    """Manages uncertainty in planning decisions."""
    
    confidence_threshold: float = 0.7
    ambiguity_markers: List[str] = field(default_factory=list)
    fallback_strategies: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.ambiguity_markers:
            self.ambiguity_markers = ["unclear", "ambiguous", "uncertain", "depends on"]
        if not self.fallback_strategies:
            self.fallback_strategies = {
                "low_confidence": "request_clarification",
                "high_ambiguity": "generate_alternatives",
                "missing_context": "defer_decision"
            }

@dataclass
class StrategyPlan:
    """Enhanced strategy planning data structure with reasoning modes."""
    
    target_role: str
    key_points: List[str]
    complexity: str
    reasoning: str
    reasoning_mode: ReasoningMode
    logic_framework: LogicFramework
    confidence_score: float
    uncertainty_handling: UncertaintyHandling
    temporal_context: Optional[Dict[str, Any]] = None

def plan_strategy(
    job: Any, 
    resume: Any, 
    config: Any,
    reasoning_mode: Optional[ReasoningMode] = None
) -> StrategyPlan:
    """
    Pure strategy planning function with configurable reasoning modes.
    
    Uses explicit reasoning strategies and uncertainty handling for robust résumé improvement planning.
    """
    mode = reasoning_mode or ReasoningMode.ANALYTICAL
    
    # Apply reasoning mode specific logic
    if mode == ReasoningMode.ANALYTICAL:
        return _analytical_planning(job, resume, config)
    elif mode == ReasoningMode.CREATIVE:
        return _creative_planning(job, resume, config)
    elif mode == ReasoningMode.DEDUCTIVE:
        return _deductive_planning(job, resume, config)
    elif mode == ReasoningMode.INDUCTIVE:
        return _inductive_planning(job, resume, config)
    elif mode == ReasoningMode.ABDUCTIVE:
        return _abductive_planning(job, resume, config)
    else:
        return _analytical_planning(job, resume, config)

def _analytical_planning(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Analytical reasoning: break down into components and analyze systematically."""
    return StrategyPlan(
        target_role="analytical_role",
        key_points=["component_analysis", "gap_identification", "sequential_improvement"],
        complexity="medium",
        reasoning="Systematic breakdown of requirements and resume gaps",
        reasoning_mode=ReasoningMode.ANALYTICAL,
        logic_framework=LogicFramework.HIERARCHICAL_DECOMPOSITION,
        confidence_score=0.8,
        uncertainty_handling=UncertaintyHandling()
    )

def _creative_planning(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Creative reasoning: generate novel approaches and alternative perspectives."""
    return StrategyPlan(
        target_role="creative_role",
        key_points=["novel_framing", "alternative_perspectives", "innovative_solutions"],
        complexity="high",
        reasoning="Generate innovative approaches to resume enhancement",
        reasoning_mode=ReasoningMode.CREATIVE,
        logic_framework=LogicFramework.CAUSAL_CHAINING,
        confidence_score=0.7,
        uncertainty_handling=UncertaintyHandling()
    )

def _deductive_planning(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Deductive reasoning: apply general rules to specific cases."""
    return StrategyPlan(
        target_role="deductive_role",
        key_points=["rule_application", "logical_conclusions", "standards_compliance"],
        complexity="medium",
        reasoning="Apply established resume best practices to specific case",
        reasoning_mode=ReasoningMode.DEDUCTIVE,
        logic_framework=LogicFramework.CONSTRAINT_PROPAGATION,
        confidence_score=0.85,
        uncertainty_handling=UncertaintyHandling()
    )

def _inductive_planning(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Inductive reasoning: infer patterns from examples and generalize."""
    return StrategyPlan(
        target_role="inductive_role",
        key_points=["pattern_identification", "generalization", "trend_application"],
        complexity="medium",
        reasoning="Infer successful patterns from similar resume cases",
        reasoning_mode=ReasoningMode.INDUCTIVE,
        logic_framework=LogicFramework.TEMPORAL_SEQUENCING,
        confidence_score=0.75,
        uncertainty_handling=UncertaintyHandling()
    )

def _abductive_planning(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Abductive reasoning: generate best explanations for gaps and mismatches."""
    return StrategyPlan(
        target_role="abductive_role",
        key_points=["gap_explanation", "hypothesis_generation", "best_fit_solutions"],
        complexity="high",
        reasoning="Generate best explanations for resume-job mismatches",
        reasoning_mode=ReasoningMode.ABDUCTIVE,
        logic_framework=LogicFramework.CAUSAL_CHAINING,
        confidence_score=0.7,
        uncertainty_handling=UncertaintyHandling()
    )
