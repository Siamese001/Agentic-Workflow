"""[SSOT] Logic Node for Resume Flow Routing.
Mirrors the k1_router pattern from apps_lic but for Resume Generation domain.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .ThematicAnalysisNode import ThematicAnalysisNode, ThematicAnalysisOutput

logger = logging.getLogger(__name__)


@dataclass
class ResumeFlowResult:
    """Result of resume flow routing decision."""

    flow_type: str  # "tailor_existing", "generate_scratch", "enhance_current"
    confidence: float
    required_hops: list[str]
    validation_required: bool
    retry_enabled: bool


@dataclass
class RGFlowOutput:
    """Resume flow routing output."""

    flow_result: ResumeFlowResult
    entrance_gates_passed: list[str]
    metadata: dict[str, Any]


class RGFlowRouter:
    """
    [Enhanced] Logic Node for Resume Flow Routing.
    Integrates K.0 Thematic Analysis to determine strategy based on
    differentiator strength and authenticity requirements.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        # Integration of K.0 Node
        self.thematic_node = ThematicAnalysisNode(config)

        # Default flow configurations
        self.flow_configs = self.config.get(
            "flow_configs",
            {
                "strategic_tailor_node": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5", "HOP-6"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "tailor_existing": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "generate_scratch": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "enhance_current": {
                    "required_hops": ["HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": False,
                },
            },
        )

        # Flow decision keywords
        self.tailor_keywords = ["tailor", "customize", "modify", "adapt", "update", "improve"]
        self.generate_keywords = ["create", "generate", "build", "make", "new", "from scratch"]
        self.enhance_keywords = ["enhance", "optimize", "improve", "refine", "polish"]

    def __call__(self, state: dict[str, Any]) -> RGFlowOutput:
        """
        Executes resume flow routing using functor pattern with upstream Thematic Analysis.

        Args:
            state: Current workflow state containing:
                - task_description: str
                - has_master_resume: bool
                - job_description: str
                - quality_requirements: Dict[str, Any]

        Returns:
            RGFlowOutput: Complete routing decision
        """
        if not state:
            raise ValueError("Resume flow routing state cannot be empty")

        # 1. Run K.0 Analysis if not already present
        if "thematic_analysis" not in state:
            jd = state.get("job_description", "")
            company = state.get("company_name", "Unknown")
            thematic_output = self.thematic_node(jd, company)

            # Inject K.0 output into state
            state["thematic_analysis"] = thematic_output
            state["primary_theme"] = thematic_output.primary_theme

        return self.execute_routing(state)

    def determine_next_hop(self, state: dict[str, Any]) -> str:
        """
        Determines the next hop identifier for resume workflow routing.

        Args:
            state: Current workflow state

        Returns:
            str: Next hop identifier
        """
        if not state:
            raise ValueError("Routing state cannot be empty")

        result = self.execute_routing(state)
        return f"flow_{result.flow_result.flow_type}"

    def execute_routing(self, context: dict[str, Any]) -> RGFlowOutput:
        """Execute resume flow routing logic.

        Args:
            context: Execution context with resume parameters

        Returns:
            RGFlowOutput with flow decision and metadata
        """
        logger.info("Executing RG flow routing")

        entrance_gates_passed = []

        # Gate 1: Task description analysis
        task_description = context.get("task_description", "")
        if not task_description:
            raise ValueError("GATE_1_FAILED: Task description is required")
        entrance_gates_passed.append("GATE_1_TASK_ANALYZED")
        logger.info(f"Gate 1: Task = {task_description[:50]}...")

        # Gate 2: Master resume availability check
        has_master_resume = context.get("has_master_resume", False)
        entrance_gates_passed.append("GATE_2_RESUME_AVAILABILITY_CHECKED")
        logger.info(f"Gate 2: Master resume available = {has_master_resume}")

        # Gate 3: Job description validation
        job_description = context.get("job_description", "")
        if not job_description:
            raise ValueError("GATE_3_FAILED: Job description is required")
        entrance_gates_passed.append("GATE_3_JOB_DESCRIPTION_VALIDATED")
        logger.info(f"Gate 3: Job description validated ({len(job_description)} chars)")

        # Gate 4: Flow classification
        thematic_analysis = context.get("thematic_analysis")
        if thematic_analysis:
            flow_result = self._classify_flow_with_thematic_analysis(
                task_description,
                has_master_resume,
                thematic_analysis,
            )
        else:
            flow_result = self._classify_flow(task_description, has_master_resume)
        entrance_gates_passed.append("GATE_4_FLOW_CLASSIFIED")
        logger.info(f"Gate 4: Flow = {flow_result.flow_type}")

        # Gate 5: Quality requirements validation
        quality_requirements = context.get("quality_requirements", {})
        if quality_requirements:
            entrance_gates_passed.append("GATE_5_QUALITY_REQUIREMENTS_APPLIED")
            logger.info(f"Gate 5: Quality requirements applied = {list(quality_requirements.keys())}")

        # Gate 6: Final routing validation
        self._validate_routing_requirements(flow_result, context)
        entrance_gates_passed.append("GATE_6_ROUTING_VALIDATED")
        logger.info("Gate 6: Routing requirements validated")

        # Gate 7: Final approval
        entrance_gates_passed.append("GATE_7_FINAL_APPROVAL")
        logger.info("Gate 7: All entrance gates passed")

        # Build output
        output = RGFlowOutput(
            flow_result=flow_result,
            entrance_gates_passed=entrance_gates_passed,
            metadata={
                "router_id": "RGFlowRouter",
                "task_description": task_description[:100],
                "has_master_resume": has_master_resume,
                "job_description_length": len(job_description),
            },
        )

        logger.info(f"RG flow routing complete: {flow_result.flow_type}")

        return output

    def _classify_flow(self, task_description: str, has_master_resume: bool) -> ResumeFlowResult:
        """Classify the resume generation flow based on task, context, and K.0 Thematic Analysis.

        Args:
            task_description: User's task description
            has_master_resume: Whether master resume is available

        Returns:
            ResumeFlowResult with flow classification
        """
        task_lower = task_description.lower()

        # Enhanced Routing Logic: Check for strong differentiators from K.0 analysis
        # This would be available in the context from the __call__ method
        # For now, we'll add the logic structure that will be used when thematic analysis is present

        # Check for tailor-specific keywords
        if any(keyword in task_lower for keyword in self.tailor_keywords):
            if has_master_resume:
                return ResumeFlowResult(
                    flow_type="tailor_existing",
                    confidence=0.95,
                    required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                    validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                    retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
                )
            else:
                logger.warning("Tailor requested but no master resume available - falling back to generate")

        # Check for generate-specific keywords
        if any(keyword in task_lower for keyword in self.generate_keywords):
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.90,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

        # Check for enhance-specific keywords
        if any(keyword in task_lower for keyword in self.enhance_keywords):
            return ResumeFlowResult(
                flow_type="enhance_current",
                confidence=0.85,
                required_hops=self.flow_configs["enhance_current"]["required_hops"],
                validation_required=self.flow_configs["enhance_current"]["validation_required"],
                retry_enabled=self.flow_configs["enhance_current"]["retry_enabled"],
            )

        # Default logic: if master resume exists, tailor; otherwise generate
        if has_master_resume:
            return ResumeFlowResult(
                flow_type="tailor_existing",
                confidence=0.70,
                required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
            )
        else:
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.70,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

    def _classify_flow_with_thematic_analysis(
        self,
        task_description: str,
        has_master_resume: bool,
        thematic_analysis: ThematicAnalysisOutput,
    ) -> ResumeFlowResult:
        """Enhanced flow classification using K.0 Thematic Analysis insights.

        Args:
            task_description: User's task description
            has_master_resume: Whether master resume is available
            thematic_analysis: K.0 Thematic Analysis output

        Returns:
            ResumeFlowResult with enhanced flow classification
        """
        task_lower = task_description.lower()

        # 2. Enhanced Routing Logic based on differentiator strength
        differentiators = thematic_analysis.competitive_intelligence.differentiator_keywords

        # If strong differentiators exist, route to high-precision tailoring
        if len(differentiators) > 3:
            return ResumeFlowResult(
                flow_type="strategic_tailor_node",
                confidence=0.98,
                required_hops=self.flow_configs["strategic_tailor_node"]["required_hops"],
                validation_required=self.flow_configs["strategic_tailor_node"]["validation_required"],
                retry_enabled=self.flow_configs["strategic_tailor_node"]["retry_enabled"],
            )

        # Check for tailor-specific keywords
        if any(keyword in task_lower for keyword in self.tailor_keywords):
            if has_master_resume:
                return ResumeFlowResult(
                    flow_type="tailor_existing",
                    confidence=0.95,
                    required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                    validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                    retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
                )
            else:
                logger.warning("Tailor requested but no master resume available - falling back to generate")

        # Check for generate-specific keywords
        if any(keyword in task_lower for keyword in self.generate_keywords):
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.90,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

        # Check for enhance-specific keywords
        if any(keyword in task_lower for keyword in self.enhance_keywords):
            return ResumeFlowResult(
                flow_type="enhance_current",
                confidence=0.85,
                required_hops=self.flow_configs["enhance_current"]["required_hops"],
                validation_required=self.flow_configs["enhance_current"]["validation_required"],
                retry_enabled=self.flow_configs["enhance_current"]["retry_enabled"],
            )

        # Default logic: if master resume exists, tailor; otherwise generate
        if has_master_resume:
            return ResumeFlowResult(
                flow_type="tailor_existing",
                confidence=0.70,
                required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
            )
        else:
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.70,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

    def _validate_routing_requirements(self, flow_result: ResumeFlowResult, context: dict[str, Any]) -> None:
        """Validate that routing requirements are met.

        Args:
            flow_result: The classified flow result
            context: Execution context

        Raises:
            ValueError: If routing requirements are not met
        """
        # Check if master resume is required but not available
        if flow_result.flow_type in ["tailor_existing", "enhance_current"]:
            if not context.get("has_master_resume", False):
                raise ValueError(
                    f"ROUTING_VALIDATION_FAILED: Flow '{flow_result.flow_type}' requires master resume",
                )

        # Check if job description meets minimum length
        job_description = context.get("job_description", "")
        if len(job_description) < 50:
            raise ValueError("ROUTING_VALIDATION_FAILED: Job description too short (minimum 50 characters)")
