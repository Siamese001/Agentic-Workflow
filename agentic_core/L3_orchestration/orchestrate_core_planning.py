# Ownership: agentic_core / L3_orchestration
# -*- coding: utf-8 -*-
"""Core Planning Orchestrator - Coordinates core agentic operations and strategic planning.

This orchestrator manages the planning phase for core operations,
including strategy definition, goal alignment, and resource coordination.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class PlanningLevel(Enum):
    """Levels of strategic planning."""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    CONTINGENCY = "contingency"


class GoalType(Enum):
    """Types of planning goals."""
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    COST_OPTIMIZATION = "cost_optimization"
    INNOVATION = "innovation"


class PlanningPhase(Enum):
    """Phases of the planning process."""
    ASSESSMENT = "assessment"
    DESIGN = "design"
    VALIDATION = "validation"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"


@dataclass
class StrategicGoal:
    """Definition of a strategic goal."""
    id: str
    name: str
    goal_type: GoalType
    description: str
    priority: int = 1  # 1-5, 5 being highest
    metrics: List[str] = field(default_factory=list)
    target_value: Optional[Any] = None
    deadline: Optional[str] = None


@dataclass
class PlanningObjective:
    """Definition of a planning objective."""
    id: str
    name: str
    planning_level: PlanningLevel
    strategic_goals: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CorePlan:
    """Definition of a core plan."""
    id: str
    name: str
    planning_level: PlanningLevel
    objectives: List[PlanningObjective]
    strategic_goals: List[StrategicGoal]
    phases: List[PlanningPhase]
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class CorePlanningConfig:
    """Configuration for core planning orchestrator."""
    enable_strategic_alignment: bool = True
    enable_risk_assessment: bool = True
    enable_resource_optimization: bool = True
    max_planning_horizon_days: int = 365
    min_objectives: int = 1
    max_objectives: int = 20
    log_level: str = "INFO"


@dataclass
class CorePlanningResult:
    """Result of core planning orchestration."""
    success: bool
    core_plan: Optional[CorePlan] = None
    strategic_roadmap: Dict[str, Any] = field(default_factory=dict)
    alignment_score: float = 0.0
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    risk_mitigation: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CorePlanningOrchestrator:
    """Orchestrator for planning core operations."""

    def __init__(self, config: Optional[CorePlanningConfig] = None):
        self.config = config or CorePlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, planning_request: Dict[str, Any]) -> CorePlanningResult:
        """Execute the core planning orchestration.
        
        Args:
            planning_request: Dictionary containing planning requirements and goals
            
        Returns:
            CorePlanningResult: Complete planning result with core plan and roadmap
        """
        self.logger.info(f"Starting core planning for: {planning_request.get('initiative', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(planning_request)
            
            # Parse strategic goals
            strategic_goals = self._parse_strategic_goals(planning_request)
            
            # Parse planning objectives
            objectives = self._parse_objectives(planning_request)
            
            # Create core plan
            core_plan = self._create_core_plan(planning_request, objectives, strategic_goals)
            
            # Generate strategic roadmap
            strategic_roadmap = self._generate_strategic_roadmap(core_plan)
            
            # Calculate alignment score
            alignment_score = self._calculate_alignment_score(core_plan)
            
            # Allocate resources
            resource_allocation = self._allocate_resources(core_plan)
            
            # Generate risk mitigation strategies
            risk_mitigation = self._generate_risk_mitigation(core_plan) if self.config.enable_risk_assessment else []
            
            result = CorePlanningResult(
                success=True,
                core_plan=core_plan,
                strategic_roadmap=strategic_roadmap,
                alignment_score=alignment_score,
                resource_allocation=resource_allocation,
                risk_mitigation=risk_mitigation,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "initiative": planning_request.get("initiative"),
                    "goal_count": len(strategic_goals),
                    "objective_count": len(objectives),
                    "orchestrator": "CorePlanningOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned core initiative: {len(strategic_goals)} goals, {alignment_score:.2f} alignment")
            return result
            
        except Exception as e:
            self.logger.error(f"Core planning failed: {str(e)}")
            return CorePlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "CorePlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate core planning request."""
        if not request:
            raise ValueError("Core planning request cannot be empty")
        
        if "initiative" not in request:
            raise ValueError("Initiative name is required in core planning request")
        
        if "planning_level" not in request:
            raise ValueError("Planning level is required in core planning request")

    def _parse_strategic_goals(self, request: Dict[str, Any]) -> List[StrategicGoal]:
        """Parse strategic goals from request."""
        goals = []
        raw_goals = request.get("strategic_goals", [])
        
        for raw_goal in raw_goals:
            if isinstance(raw_goal, dict):
                # Map strings to enums
                goal_mapping = {
                    "performance": GoalType.PERFORMANCE,
                    "scalability": GoalType.SCALABILITY,
                    "reliability": GoalType.RELIABILITY,
                    "security": GoalType.SECURITY,
                    "cost_optimization": GoalType.COST_OPTIMIZATION,
                    "innovation": GoalType.INNOVATION
                }
                
                goal = StrategicGoal(
                    id=raw_goal.get("id", f"goal_{len(goals)}"),
                    name=raw_goal.get("name", "unnamed"),
                    goal_type=goal_mapping.get(
                        raw_goal.get("goal_type", "performance"),
                        GoalType.PERFORMANCE
                    ),
                    description=raw_goal.get("description", ""),
                    priority=raw_goal.get("priority", 1),
                    metrics=raw_goal.get("metrics", []),
                    target_value=raw_goal.get("target_value"),
                    deadline=raw_goal.get("deadline")
                )
                goals.append(goal)
        
        return goals

    def _parse_objectives(self, request: Dict[str, Any]) -> List[PlanningObjective]:
        """Parse planning objectives from request."""
        objectives = []
        raw_objectives = request.get("objectives", [])
        
        for raw_obj in raw_objectives:
            if isinstance(raw_obj, dict):
                # Map strings to enums
                level_mapping = {
                    "strategic": PlanningLevel.STRATEGIC,
                    "tactical": PlanningLevel.TACTICAL,
                    "operational": PlanningLevel.OPERATIONAL,
                    "contingency": PlanningLevel.CONTINGENCY
                }
                
                objective = PlanningObjective(
                    id=raw_obj.get("id", f"obj_{len(objectives)}"),
                    name=raw_obj.get("name", "unnamed"),
                    planning_level=level_mapping.get(
                        raw_obj.get("planning_level", "operational"),
                        PlanningLevel.OPERATIONAL
                    ),
                    strategic_goals=raw_obj.get("strategic_goals", []),
                    requirements=raw_obj.get("requirements", []),
                    constraints=raw_obj.get("constraints", {}),
                    dependencies=raw_obj.get("dependencies", [])
                )
                objectives.append(objective)
        
        # Validate objective count
        if not (self.config.min_objectives <= len(objectives) <= self.config.max_objectives):
            raise ValueError(
                f"Number of objectives ({len(objectives)}) must be between "
                f"{self.config.min_objectives} and {self.config.max_objectives}"
            )
        
        return objectives

    def _create_core_plan(
        self, 
        request: Dict[str, Any], 
        objectives: List[PlanningObjective], 
        goals: List[StrategicGoal]
    ) -> CorePlan:
        """Create core plan from request, objectives, and goals."""
        # Map strings to enums
        level_mapping = {
            "strategic": PlanningLevel.STRATEGIC,
            "tactical": PlanningLevel.TACTICAL,
            "operational": PlanningLevel.OPERATIONAL,
            "contingency": PlanningLevel.CONTINGENCY
        }
        
        phase_mapping = {
            "assessment": PlanningPhase.ASSESSMENT,
            "design": PlanningPhase.DESIGN,
            "validation": PlanningPhase.VALIDATION,
            "implementation": PlanningPhase.IMPLEMENTATION,
            "monitoring": PlanningPhase.MONITORING
        }
        
        planning_level = level_mapping.get(
            request.get("planning_level", "operational"),
            PlanningLevel.OPERATIONAL
        )
        
        # Parse phases
        phases = []
        for raw_phase in request.get("phases", ["assessment", "design", "implementation"]):
            phase = phase_mapping.get(raw_phase, PlanningPhase.ASSESSMENT)
            phases.append(phase)
        
        return CorePlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("initiative", "unnamed_plan"),
            planning_level=planning_level,
            objectives=objectives,
            strategic_goals=goals,
            phases=phases,
            resource_requirements=request.get("resource_requirements", {}),
            risk_assessment=request.get("risk_assessment", {}),
            success_criteria=request.get("success_criteria", [])
        )

    def _generate_strategic_roadmap(self, plan: CorePlan) -> Dict[str, Any]:
        """Generate strategic roadmap from core plan."""
        roadmap = {
            "timeline": {},
            "milestones": [],
            "dependencies": {},
            "critical_path": []
        }
        
        # Generate timeline based on phases
        current_date = datetime.utcnow()
        phase_duration = {
            PlanningPhase.ASSESSMENT: 30,
            PlanningPhase.DESIGN: 45,
            PlanningPhase.VALIDATION: 15,
            PlanningPhase.IMPLEMENTATION: 90,
            PlanningPhase.MONITORING: 60
        }
        
        total_days = 0
        for phase in plan.phases:
            duration = phase_duration.get(phase, 30)
            roadmap["timeline"][phase.value] = {
                "start_date": (current_date + timedelta(days=total_days)).strftime("%Y-%m-%d"),
                "end_date": (current_date + timedelta(days=total_days + duration)).strftime("%Y-%m-%d"),
                "duration_days": duration
            }
            total_days += duration
        
        # Generate milestones from objectives
        for i, objective in enumerate(plan.objectives):
            milestone = {
                "id": f"milestone_{i+1}",
                "name": objective.name,
                "objective_id": objective.id,
                "phase": objective.planning_level.value,
                "estimated_completion": (current_date + timedelta(days=(i+1) * 30)).strftime("%Y-%m-%d")
            }
            roadmap["milestones"].append(milestone)
        
        # Build dependency graph
        roadmap["dependencies"] = {
            obj.id: obj.dependencies 
            for obj in plan.objectives
        }
        
        return roadmap

    def _calculate_alignment_score(self, plan: CorePlan) -> float:
        """Calculate strategic alignment score for the plan."""
        if not self.config.enable_strategic_alignment:
            return 0.0
        
        # Simple scoring algorithm
        score = 0.0
        max_score = 0.0
        
        # Score objectives alignment with goals
        for objective in plan.objectives:
            if objective.strategic_goals:
                # Higher score for objectives aligned with strategic goals
                score += len(objective.strategic_goals) * 0.2
            max_score += 1.0
        
        # Score goal priorities
        for goal in plan.strategic_goals:
            score += goal.priority * 0.1
            max_score += 0.5
        
        # Normalize score
        if max_score > 0:
            score = min(score / max_score, 1.0)
        
        return round(score, 2)

    def _allocate_resources(self, plan: CorePlan) -> Dict[str, Any]:
        """Allocate resources for the core plan."""
        if not self.config.enable_resource_optimization:
            return plan.resource_requirements
        
        allocation = {
            "human_resources": {},
            "technical_resources": {},
            "financial_resources": {},
            "timeline_allocation": {}
        }
        
        # Allocate based on objectives
        for objective in plan.objectives:
            obj_allocation = {
                "estimated_fte": 0.5,
                "required_skills": [],
                "budget_allocation": 0
            }
            
            # Adjust based on planning level
            if objective.planning_level == PlanningLevel.STRATEGIC:
                obj_allocation["estimated_fte"] = 1.0
                obj_allocation["budget_allocation"] = 100000
            elif objective.planning_level == PlanningLevel.TACTICAL:
                obj_allocation["estimated_fte"] = 0.75
                obj_allocation["budget_allocation"] = 50000
            
            allocation["human_resources"][objective.id] = obj_allocation
        
        return allocation

    def _generate_risk_mitigation(self, plan: CorePlan) -> List[Dict[str, Any]]:
        """Generate risk mitigation strategies."""
        mitigations = []
        
        # Common risks and mitigations
        risk_matrix = {
            "resource_shortage": {
                "mitigation": "Cross-training and flexible resource allocation",
                "probability": "medium",
                "impact": "high"
            },
            "scope_creep": {
                "mitigation": "Strict change control process and regular stakeholder reviews",
                "probability": "high",
                "impact": "medium"
            },
            "technical_debt": {
                "mitigation": "Regular refactoring sprints and architecture reviews",
                "probability": "medium",
                "impact": "high"
            },
            "stakeholder_alignment": {
                "mitigation": "Weekly status meetings and transparent communication",
                "probability": "medium",
                "impact": "high"
            }
        }
        
        for risk_type, risk_info in risk_matrix.items():
            mitigation = {
                "risk_type": risk_type,
                "description": risk_info["mitigation"],
                "probability": risk_info["probability"],
                "impact": risk_info["impact"],
                "mitigation_plan": f"Implement {risk_info['mitigation'].lower()}",
                "owner": "risk_manager",
                "review_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
            }
            mitigations.append(mitigation)
        
        return mitigations


# Factory function for easy instantiation
def create_core_planning_orchestrator(
    enable_strategic_alignment: bool = True,
    enable_risk_assessment: bool = True,
    **kwargs
) -> CorePlanningOrchestrator:
    """Create a configured core planning orchestrator."""
    config = CorePlanningConfig(
        enable_strategic_alignment=enable_strategic_alignment,
        enable_risk_assessment=enable_risk_assessment,
        **kwargs
    )
    return CorePlanningOrchestrator(config)


# Convenience function for direct usage
def orchestrate_core_planning(
    initiative: str,
    planning_level: str,
    strategic_goals: List[Dict[str, Any]],
    objectives: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan core initiative from simple parameters.
    
    Args:
        initiative: Name of the strategic initiative
        planning_level: Planning level (strategic, tactical, operational, contingency)
        strategic_goals: List of strategic goal definitions
        objectives: List of planning objective definitions
        config: Optional orchestrator configuration overrides
        
    Returns:
        Dict: Planning result with core plan and roadmap
    """
    # Build request
    request = {
        "initiative": initiative,
        "planning_level": planning_level,
        "strategic_goals": strategic_goals,
        "objectives": objectives
    }
    
    # Create orchestrator and execute
    orchestrator_config = CorePlanningConfig(**config) if config else None
    orchestrator = CorePlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "core_plan": {
            "id": result.core_plan.id,
            "name": result.core_plan.name,
            "planning_level": result.core_plan.planning_level.value,
            "objectives": [
                {
                    "id": o.id,
                    "name": o.name,
                    "planning_level": o.planning_level.value,
                    "strategic_goals": o.strategic_goals,
                    "requirements": o.requirements,
                    "constraints": o.constraints,
                    "dependencies": o.dependencies
                }
                for o in result.core_plan.objectives
            ],
            "strategic_goals": [
                {
                    "id": g.id,
                    "name": g.name,
                    "goal_type": g.goal_type.value,
                    "description": g.description,
                    "priority": g.priority,
                    "metrics": g.metrics,
                    "target_value": g.target_value,
                    "deadline": g.deadline
                }
                for g in result.core_plan.strategic_goals
            ],
            "phases": [p.value for p in result.core_plan.phases],
            "resource_requirements": result.core_plan.resource_requirements,
            "risk_assessment": result.core_plan.risk_assessment,
            "success_criteria": result.core_plan.success_criteria
        } if result.core_plan else None,
        "strategic_roadmap": result.strategic_roadmap,
        "alignment_score": result.alignment_score,
        "resource_allocation": result.resource_allocation,
        "risk_mitigation": result.risk_mitigation,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


def get_orchestrate_core_planning_config() -> Dict[str, object]:
    """Get configuration for orchestrate_core_planning."""
    return {"enabled": True, "version": "2.0"}