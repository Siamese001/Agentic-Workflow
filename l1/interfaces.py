"""L1 Interfaces - Planning Layer

This module defines abstract interfaces for all L1 planning operations.
All L1 implementations must inherit from these interfaces.

Layer: L1 (Planning)
Responsibilities:
- Pure planning and reasoning
- Task decomposition
- Uncertainty estimation
- Plan validation

Non-responsibilities:
- Tool execution (L2)
- Orchestration (L3)
- State management (L4)
- Safety/policy (L5)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from core.models.models import (
    WorkflowPlanBundle,
    ExecutionContext,
    ComplexityLevel,
    TaskDecomposition,
    UncertaintyEstimate,
)


@dataclass
class L1PlanRequest:
    """Input request for L1 planning operations."""
    mission: str
    context: ExecutionContext
    constraints: Optional[Dict[str, Any]] = None
    complexity_hint: Optional[ComplexityLevel] = None


@dataclass
class L1PlanResult:
    """Output result from L1 planning operations."""
    plan_bundle: WorkflowPlanBundle
    decomposition: TaskDecomposition
    uncertainty: UncertaintyEstimate
    metadata: Dict[str, Any]


class L1PlannerInterface(ABC):
    """Abstract interface for all L1 planning operations."""
    
    @abstractmethod
    async def plan_workflow(self, request: L1PlanRequest) -> L1PlanResult:
        """Create a comprehensive workflow plan."""
        pass
    
    @abstractmethod
    async def decompose_task(self, task: str, context: ExecutionContext) -> TaskDecomposition:
        """Decompose a task into executable subtasks."""
        pass
    
    @abstractmethod
    async def estimate_uncertainty(self, plan: WorkflowPlanBundle, context: ExecutionContext) -> UncertaintyEstimate:
        """Estimate uncertainty and confidence levels for a plan."""
        pass
    
    @abstractmethod
    async def validate_plan(self, plan: WorkflowPlanBundle, context: ExecutionContext) -> bool:
        """Validate that a plan is executable and safe."""
        pass


class L1StrategyPlannerInterface(L1PlannerInterface):
    """Interface for strategy-specific planning operations."""
    
    @abstractmethod
    async def plan_strategy(self, request: L1PlanRequest) -> L1PlanResult:
        """Plan strategy execution workflow."""
        pass


class L1DraftingPlannerInterface(L1PlannerInterface):
    """Interface for drafting-specific planning operations."""
    
    @abstractmethod
    async def plan_drafting(self, request: L1PlanRequest) -> L1PlanResult:
        """Plan content drafting workflow."""
        pass


class L1QAPlannerInterface(L1PlannerInterface):
    """Interface for QA-specific planning operations."""
    
    @abstractmethod
    async def plan_qa(self, request: L1PlanRequest) -> L1PlanResult:
        """Plan quality assurance workflow."""
        pass


class L1SafetyPlannerInterface(L1PlannerInterface):
    """Interface for safety-specific planning operations."""
    
    @abstractmethod
    async def plan_safety(self, request: L1PlanRequest) -> L1PlanResult:
        """Plan safety evaluation workflow."""
        pass


# =============================================================================
# Model Bias Injection Defense (ID 9) - L1 Pre-Check
# =============================================================================

@dataclass
class BiasIndicator:
    """Indicator of potential bias in planning inputs or outputs."""
    
    indicator_type: str
    description: str
    severity: str  # "high", "medium", "low"
    source_field: str
    confidence: float


@dataclass
class BiasPreCheckResult:
    """Result of bias pre-check before planning execution."""
    
    has_bias_indicators: bool
    indicators: List[BiasIndicator]
    recommendation: str  # "proceed", "review", "reject"
    confidence: float


class L1BiasPreCheckInterface(ABC):
    """
    Interface for detecting potential bias before L1 planning execution.
    
    Defends against Model Bias Injection (ID 9) by flagging potential
    bias indicators in planning inputs before execution proceeds.
    """
    
    @abstractmethod
    def check_input_bias(self, request: L1PlanRequest) -> BiasPreCheckResult:
        """
        Check planning request for potential bias indicators.
        
        Should be called before any L1 planning operation.
        """
        pass
    
    @abstractmethod
    def check_output_bias(self, result: L1PlanResult) -> BiasPreCheckResult:
        """
        Check planning result for potential bias indicators.
        
        Should be called after L1 planning to validate output.
        """
        pass
    
    @abstractmethod
    def get_bias_patterns(self) -> List[str]:
        """
        Get list of bias patterns being checked.
        """
        pass
