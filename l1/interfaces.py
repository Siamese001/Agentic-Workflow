"""
Defines abstract interfaces for L1 planning operations in resume generation.

Ensures consistent planning implementation across all resume
generation components for improved code organization.
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
    """Input request for L1 resume planning operations.

    Ensures standardized planning requests for consistent
    resume generation across all components.
    """
    mission: str
    context: ExecutionContext
    constraints: Optional[Dict[str, Any]] = None
    complexity_hint: Optional[ComplexityLevel] = None


@dataclass
class L1PlanResult:
    """Output result from L1 resume planning operations.

    Provides structured planning results for consistent
    resume generation across all system components.
    """
    plan_bundle: WorkflowPlanBundle
    decomposition: TaskDecomposition
    uncertainty: UncertaintyEstimate
    metadata: Dict[str, Any]


class L1PlannerInterface(ABC):
    """Abstract interface for L1 resume planning operations.

    Ensures consistent planning behavior across all resume
    generation components for improved system reliability.
    """
    
    @abstractmethod
    async def plan_workflow(self, request: L1PlanRequest) -> L1PlanResult:
        """Creates comprehensive resume workflow plans.

        Ensures structured planning for consistent resume
        generation across all job applications.
        """
        pass
    
    @abstractmethod
    async def decompose_task(self, task: str, context: ExecutionContext) -> TaskDecomposition:
        """Decomposes resume tasks into executable subtasks.

        Enables systematic resume generation through proper
        task breakdown for improved quality.
        """
        pass
    
    @abstractmethod
    async def estimate_uncertainty(self, plan: WorkflowPlanBundle, context: ExecutionContext) -> UncertaintyEstimate:
        """Estimates uncertainty levels for resume planning.

        Provides confidence metrics to ensure resume
        generation meets quality standards.
        """
        pass
    
    @abstractmethod
    async def validate_plan(self, plan: WorkflowPlanBundle, context: ExecutionContext) -> bool:
        """Validates resume plans for execution and safety.

        Ensures generated resumes meet professional standards
        and job application requirements.
        """
        pass


class L1StrategyPlannerInterface(L1PlannerInterface):
    """Interface for resume strategy planning operations.

    Ensures consistent strategy planning for optimal
    job alignment and resume effectiveness.
    """
    
    @abstractmethod
    async def plan_strategy(self, request: L1PlanRequest) -> L1PlanResult:
        """Plans resume strategy execution workflow.

        Ensures strategic resume organization for maximum
        impact on job applications.
        """
        pass


class L1DraftingPlannerInterface(L1PlannerInterface):
    """Interface for resume content drafting planning.

    Ensures consistent drafting planning for high-quality
        resume content generation.
    """
    
    @abstractmethod
    async def plan_drafting(self, request: L1PlanRequest) -> L1PlanResult:
        """Plans resume content drafting workflow.

        Ensures structured content creation for professional
        resume presentation.
        """
        pass


class L1QAPlannerInterface(L1PlannerInterface):
    """Interface for resume quality assurance planning.

    Ensures consistent QA planning for resume
    accuracy and job alignment.
    """
    
    @abstractmethod
    async def plan_qa(self, request: L1PlanRequest) -> L1PlanResult:
        """Plans resume quality assurance workflow.

        Ensures thorough validation for resume
        correctness and professional standards.
        """
        pass


class L1SafetyPlannerInterface(L1PlannerInterface):
    """Interface for resume safety planning operations.

    Ensures consistent safety planning for professional
    and ethical resume generation.
    """
    
    @abstractmethod
    async def plan_safety(self, request: L1PlanRequest) -> L1PlanResult:
        """Plans resume safety evaluation workflow.

        Ensures resume content meets professional standards
        and ethical guidelines.
        """
        pass


# =============================================================================
# Model Bias Injection Defense (ID 9) - L1 Pre-Check
# =============================================================================

@dataclass
class BiasIndicator:
    """Indicator of potential bias in resume planning.

    Helps ensure resume generation remains fair and unbiased
    for professional job applications.
    """
    
    indicator_type: str
    description: str
    severity: str  # "high", "medium", "low"
    source_field: str
    confidence: float


@dataclass
class BiasPreCheckResult:
    """Result of bias pre-check for resume planning.

    Ensures resume generation maintains fairness and
    professional standards throughout the process.
    """
    
    has_bias_indicators: bool
    indicators: List[BiasIndicator]
    recommendation: str  # "proceed", "review", "reject"
    confidence: float


class L1BiasPreCheckInterface(ABC):
    """
    Interface for detecting bias in resume planning operations.

    Ensures resume generation remains fair and unbiased
    for professional job applications.
    """
    
    @abstractmethod
    def check_input_bias(self, request: L1PlanRequest) -> BiasPreCheckResult:
        """
        Checks resume planning requests for bias indicators.

        Ensures fair and unbiased resume generation
        before planning operations begin.
        """
        pass
    
    @abstractmethod
    def check_output_bias(self, result: L1PlanResult) -> BiasPreCheckResult:
        """
        Checks resume planning results for bias indicators.

        Validates that generated plans remain fair
        and unbiased for professional use.
        """
        pass
    
    @abstractmethod
    def get_bias_patterns(self) -> List[str]:
        """
        Gets bias patterns checked in resume planning.

        Provides transparency for bias detection
        in resume generation processes.
        """
        pass
