"""
Goal Injection - Strategic Goal State Injection for Prompts
Ported from legacy_engines/retrieval_enhancements.py and goal_alignment_engine.py

Adds strategic goals to prompts at optimal positions
to improve output relevance and alignment.
"""

import logging
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GoalType(Enum):
    """Types of strategic goals"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"


class GoalPriority(Enum):
    """Priority levels for goals"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class StrategicGoal:
    """Individual strategic goal"""
    goal_id: str
    goal_type: GoalType
    priority: GoalPriority
    description: str
    success_metrics: List[str]
    constraints: List[str] = field(default_factory=list)
    context: Dict[str, object] = field(default_factory=dict)


@dataclass
class GoalState:
    """Complete goal state for injection"""
    primary_goals: List[StrategicGoal]
    success_metrics: List[str]
    constraints: List[str]
    context: Dict[str, object]
    injection_position: str = "prefix"  # prefix, suffix, inline


@dataclass
class InjectionResult:
    """Result of goal injection"""
    original_prompt: str
    enhanced_prompt: str
    injected_goals: List[StrategicGoal]
    injection_position: str
    goal_count: int
    enhancement_score: float


class GoalStateInjector:
    """
    Strategic Goal State Injection
    
    Adds strategic goals to prompts at optimal positions
    to improve output relevance and alignment.
    """
    
    def __init__(self, default_goals: Optional[List[StrategicGoal]] = None):
        """
        Initialize goal state injector.
        
        Args:
            default_goals: Optional default goals to always include
        """
        self.default_goals = default_goals or []
        self.goal_templates = self._load_goal_templates()
        self.injection_history: List[InjectionResult] = []
    
    def inject_goals(
        self,
        prompt: str,
        goals: Optional[List[StrategicGoal]] = None,
        context: Optional[Dict[str, object]] = None,
        position: str = "prefix"
    ) -> InjectionResult:
        """
        Inject strategic goals into prompt.
        
        Args:
            prompt: Original prompt
            goals: Strategic goals to inject
            context: Additional context for goal formatting
            position: Where to inject goals (prefix, suffix, inline)
            
        Returns:
            InjectionResult with enhanced prompt
        """
        context = context or {}
        all_goals = (goals or []) + self.default_goals
        
        if not all_goals:
            return InjectionResult(
                original_prompt=prompt,
                enhanced_prompt=prompt,
                injected_goals=[],
                injection_position=position,
                goal_count=0,
                enhancement_score=0.0
            )
        
        # Sort goals by priority
        sorted_goals = sorted(all_goals, key=lambda g: g.priority.value)
        
        # Generate goal injection text
        goal_text = self._format_goals_for_injection(sorted_goals, context)
        
        # Inject at specified position
        if position == "prefix":
            enhanced_prompt = f"{goal_text}\n\n{prompt}"
        elif position == "suffix":
            enhanced_prompt = f"{prompt}\n\n{goal_text}"
        elif position == "inline":
            enhanced_prompt = self._inject_inline(prompt, goal_text)
        else:
            enhanced_prompt = f"{goal_text}\n\n{prompt}"
        
        # Calculate enhancement score
        enhancement_score = self._calculate_enhancement_score(sorted_goals)
        
        result = InjectionResult(
            original_prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            injected_goals=sorted_goals,
            injection_position=position,
            goal_count=len(sorted_goals),
            enhancement_score=enhancement_score
        )
        
        self.injection_history.append(result)
        
        logger.info(f"Injected {len(sorted_goals)} goals at {position} position")
        
        return result
    
    def _format_goals_for_injection(
        self, 
        goals: List[StrategicGoal], 
        context: Dict[str, object]
    ) -> str:
        """Format goals for injection into prompt."""
        lines = ["[STRATEGIC GOALS]"]
        
        for i, goal in enumerate(goals, 1):
            priority_label = goal.priority.name
            lines.append(f"\n{i}. [{priority_label}] {goal.description}")
            
            if goal.success_metrics:
                lines.append(f"   Success Metrics: {', '.join(goal.success_metrics[:3])}")
            
            if goal.constraints:
                lines.append(f"   Constraints: {', '.join(goal.constraints[:3])}")
        
        # Add context if provided
        if context.get("target_role"):
            lines.append(f"\nTarget Role: {context['target_role']}")
        if context.get("industry"):
            lines.append(f"Industry: {context['industry']}")
        
        lines.append("\n[END GOALS]")
        
        return "\n".join(lines)
    
    def _inject_inline(self, prompt: str, goal_text: str) -> str:
        """Inject goals inline within the prompt."""
        # Find optimal injection point (after first paragraph or instruction)
        paragraphs = prompt.split("\n\n")
        
        if len(paragraphs) > 1:
            return f"{paragraphs[0]}\n\n{goal_text}\n\n" + "\n\n".join(paragraphs[1:])
        
        return f"{goal_text}\n\n{prompt}"
    
    def _calculate_enhancement_score(self, goals: List[StrategicGoal]) -> float:
        """Calculate enhancement score based on goals."""
        if not goals:
            return 0.0
        
        # Weight by priority
        priority_weights = {
            GoalPriority.CRITICAL: 1.0,
            GoalPriority.HIGH: 0.8,
            GoalPriority.MEDIUM: 0.5,
            GoalPriority.LOW: 0.3
        }
        
        total_weight = sum(priority_weights.get(g.priority, 0.5) for g in goals)
        
        # Normalize to 0-1 scale
        enhancement_score = min(total_weight / 3.0, 1.0)
        
        return round(enhancement_score, 3)
    
    def _load_goal_templates(self) -> Dict[GoalType, str]:
        """Load goal templates by type."""
        return {
            GoalType.BUSINESS: "Achieve business outcome: {description}",
            GoalType.TECHNICAL: "Implement technical solution: {description}",
            GoalType.COMMUNICATION: "Communicate effectively: {description}",
            GoalType.COMPLIANCE: "Ensure compliance with: {description}",
            GoalType.QUALITY: "Maintain quality standard: {description}",
            GoalType.EFFICIENCY: "Optimize for efficiency: {description}"
        }
    
    def create_goal(
        self,
        goal_id: str,
        goal_type: GoalType,
        description: str,
        priority: GoalPriority = GoalPriority.MEDIUM,
        success_metrics: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ) -> StrategicGoal:
        """Create a strategic goal."""
        return StrategicGoal(
            goal_id=goal_id,
            goal_type=goal_type,
            priority=priority,
            description=description,
            success_metrics=success_metrics or [],
            constraints=constraints or []
        )
    
    def create_goal_state(
        self,
        goals: List[StrategicGoal],
        context: Optional[Dict[str, object]] = None
    ) -> GoalState:
        """Create a complete goal state for injection."""
        all_metrics = []
        all_constraints = []
        
        for goal in goals:
            all_metrics.extend(goal.success_metrics)
            all_constraints.extend(goal.constraints)
        
        return GoalState(
            primary_goals=goals,
            success_metrics=list(set(all_metrics)),
            constraints=list(set(all_constraints)),
            context=context or {}
        )
    
    def get_injection_stats(self) -> Dict[str, object]:
        """Get injection statistics."""
        if not self.injection_history:
            return {}
        
        recent = self.injection_history[-20:]
        
        return {
            'total_injections': len(self.injection_history),
            'recent_injections': len(recent),
            'avg_goals_per_injection': sum(r.goal_count for r in recent) / len(recent),
            'avg_enhancement_score': sum(r.enhancement_score for r in recent) / len(recent),
            'position_breakdown': self._get_position_breakdown(recent)
        }
    
    def _get_position_breakdown(self, results: List[InjectionResult]) -> Dict[str, int]:
        """Get breakdown of injection positions."""
        breakdown = {}
        for result in results:
            pos = result.injection_position
            breakdown[pos] = breakdown.get(pos, 0) + 1
        return breakdown


# builder functions
def create_goal_injector(default_goals: Optional[List[StrategicGoal]] = None) -> GoalStateInjector:
    """Create goal state injector instance."""
    return GoalStateInjector(default_goals)


def inject_goals(
    prompt: str,
    goals: List[StrategicGoal],
    position: str = "prefix"
) -> InjectionResult:
    """Convenience function to inject goals into prompt."""
    injector = GoalStateInjector()
    return injector.inject_goals(prompt, goals, position=position)


def create_business_goal(
    goal_id: str,
    description: str,
    priority: GoalPriority = GoalPriority.MEDIUM
) -> StrategicGoal:
    """Create a business goal."""
    return StrategicGoal(
        goal_id=goal_id,
        goal_type=GoalType.BUSINESS,
        priority=priority,
        description=description,
        success_metrics=["ROI improvement", "Revenue growth", "Cost reduction"]
    )


def create_quality_goal(
    goal_id: str,
    description: str,
    priority: GoalPriority = GoalPriority.HIGH
) -> StrategicGoal:
    """Create a quality goal."""
    return StrategicGoal(
        goal_id=goal_id,
        goal_type=GoalType.QUALITY,
        priority=priority,
        description=description,
        success_metrics=["Accuracy", "Completeness", "Consistency"]
    )
