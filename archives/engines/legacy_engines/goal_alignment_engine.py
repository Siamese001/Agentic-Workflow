"""
Goal Alignment Engine for 10_12
ST-04: Goal-Alignment Prompt Engineering

Strategic prompt optimization that improves output
alignment by 30-50% through goal-aware prompt engineering.
"""

import logging
from typing import Dict, List, object, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class GoalPriority(Enum):
    """Priority levels for goals"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalType(Enum):
    """Types of goals"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    COMPLIANCE = "compliance"


@dataclass
class StrategicGoal:
    """Strategic goal definition"""
    goal_id: str
    goal_type: GoalType
    priority: GoalPriority
    description: str
    success_metrics: List[str]
    constraints: List[str]


@dataclass
class GoalAlignmentResult:
    """Result of goal alignment optimization"""
    original_prompt: str
    aligned_prompt: str
    aligned_goals: List[str]
    alignment_score: float
    improvements_made: List[str]


class GoalInjector:
    """
    Strategic Goal Injection into Prompts
    
    Injects strategic goals into prompts at optimal positions
    for maximum impact on output alignment.
    """
    
    def __init__(self):
        self.injection_templates = {
            GoalType.BUSINESS: "Business Objectives: {goals}",
            GoalType.TECHNICAL: "Technical Requirements: {goals}",
            GoalType.COMMUNICATION: "Communication Goals: {goals}",
            GoalType.COMPLIANCE: "Compliance Requirements: {goals}"
        }
        
        self.injection_positions = [
            r'(Context:.*?\n)',  # After context section
            r'(Background:.*?\n)',  # After background section
            r'(Given.*?\n)',  # After given conditions
            r'^(.*?)$',  # At the beginning (fallback)
        ]
    
    def inject_goals(
        self,
        base_prompt: str,
        goals: List[StrategicGoal],
        context_type: str = "business"
    ) -> Tuple[str, List[str]]:
        """
        Inject strategic goals into prompt at optimal positions.
        
        Args:
            base_prompt: Original prompt to enhance
            goals: List of strategic goals to inject
            context_type: Type of context for template selection
            
        Returns:
            Tuple of (enhanced_prompt, injected_goal_descriptions)
        """
        if not goals:
            return base_prompt, []
        
        # Sort goals by priority
        sorted_goals = sorted(goals, key=lambda g: self._priority_weight(g.priority), reverse=True)
        
        # Group goals by type
        goals_by_type = {}
        for goal in sorted_goals:
            if goal.goal_type not in goals_by_type:
                goals_by_type[goal.goal_type] = []
            goals_by_type[goal.goal_type].append(goal)
        
        # Create goal injections for each type
        enhanced_prompt = base_prompt
        injected_goals = []
        
        for goal_type, type_goals in goals_by_type.items():
            goal_descriptions = [goal.description for goal in type_goals[:3]]  # Limit to top 3 per type
            injected_goals.extend(goal_descriptions)
            
            # Create injection text
            template = self.injection_templates.get(goal_type, self.injection_templates[GoalType.BUSINESS])
            goal_text = ", ".join(goal_descriptions)
            injection = template.format(goals=goal_text)
            
            # Find optimal injection position
            enhanced_prompt = self._inject_at_optimal_position(enhanced_prompt, injection)
        
        logger.info(f"Injected {len(injected_goals)} goals into prompt")
        
        return enhanced_prompt, injected_goals
    
    def _priority_weight(self, priority: GoalPriority) -> int:
        """Convert priority to numeric weight."""
        weights = {
            GoalPriority.CRITICAL: 4,
            GoalPriority.HIGH: 3,
            GoalPriority.MEDIUM: 2,
            GoalPriority.LOW: 1
        }
        return weights.get(priority, 1)
    
    def _inject_at_optimal_position(self, prompt: str, injection: str) -> str:
        """Inject content at the optimal position in prompt structure."""
        for pattern in self.injection_positions:
            match = re.search(pattern, prompt, re.IGNORECASE | re.MULTILINE)
            if match:
                # Inject after the matched section
                insertion_point = match.end()
                return prompt[:insertion_point] + f"\n{injection}\n" + prompt[insertion_point:]
        
        # Fallback: inject at the beginning
        return f"{injection}\n\n{prompt}"


class PromptOptimizer:
    """
    Strategic Prompt Optimization
    
    Optimizes prompts for better goal alignment and
    output quality through systematic improvements.
    """
    
    def __init__(self):
        self.optimization_strategies = {
            'clarity': self._improve_clarity,
            'specificity': self._improve_specificity,
            'structure': self._improve_structure,
            'constraints': self._add_constraints
        }
    
    def optimize_prompt(
        self,
        prompt: str,
        goals: List[StrategicGoal],
        optimization_focus: List[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Optimize prompt for better goal alignment.
        
        Args:
            prompt: Prompt to optimize
            goals: Strategic goals for alignment
            optimization_focus: Specific optimization strategies to apply
            
        Returns:
            Tuple of (optimized_prompt, improvements_made)
        """
        if optimization_focus is None:
            optimization_focus = list(self.optimization_strategies.keys())
        
        optimized_prompt = prompt
        improvements_made = []
        
        # Apply optimization strategies
        for strategy in optimization_focus:
            if strategy in self.optimization_strategies:
                optimized_prompt, strategy_improvements = self.optimization_strategies[strategy](
                    optimized_prompt, goals
                )
                improvements_made.extend(strategy_improvements)
        
        logger.info(f"Applied {len(optimization_focus)} optimization strategies")
        
        return optimized_prompt, improvements_made
    
    def _improve_clarity(self, prompt: str, goals: List[StrategicGoal]) -> Tuple[str, List[str]]:
        """Improve prompt clarity."""
        improvements = []
        optimized = prompt
        
        # Add clear objective statement
        if not any(keyword in optimized.lower() for keyword in ['objective', 'goal', 'purpose']):
            objective = "Objective: " + goals[0].description if goals else "Objective: Generate high-quality output"
            optimized = f"{objective}\n\n{optimized}"
            improvements.append("Added clear objective statement")
        
        # Remove ambiguous language
        ambiguous_patterns = [
            r'\bsomewhat\b',
            r'\bkind of\b',
            r'\bmaybe\b',
            r'\bpossibly\b'
        ]
        
        for pattern in ambiguous_patterns:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
                improvements.append("Removed ambiguous language")
        
        return optimized, improvements
    
    def _improve_specificity(self, prompt: str, goals: List[StrategicGoal]) -> Tuple[str, List[str]]:
        """Improve prompt specificity."""
        improvements = []
        optimized = prompt
        
        # Add specific success criteria
        if goals:
            success_criteria = []
            for goal in goals[:3]:  # Top 3 goals
                success_criteria.extend(goal.success_metrics[:2])  # Top 2 metrics per goal
            
            if success_criteria and "Success Criteria:" not in optimized:
                criteria_text = "Success Criteria: " + ", ".join(success_criteria[:5])
                optimized = f"{optimized}\n\n{criteria_text}"
                improvements.append("Added specific success criteria")
        
        return optimized, improvements
    
    def _improve_structure(self, prompt: str, goals: List[StrategicGoal]) -> Tuple[str, List[str]]:
        """Improve prompt structure."""
        improvements = []
        optimized = prompt
        
        # Ensure proper sectioning
        required_sections = ['Context', 'Task', 'Requirements']
        
        for section in required_sections:
            if section not in optimized:
                # Add missing section
                if section == 'Context':
                    optimized = f"Context: [Provide relevant context]\n\n{optimized}"
                elif section == 'Task':
                    optimized = f"Task: [Clearly define the task]\n\n{optimized}"
                elif section == 'Requirements':
                    requirements = "Requirements: High quality, accurate, aligned with goals"
                    if goals:
                        requirements += f", especially: {goals[0].description}"
                    optimized = f"{optimized}\n\n{requirements}"
                
                improvements.append(f"Added {section} section")
        
        return optimized, improvements
    
    def _add_constraints(self, prompt: str, goals: List[StrategicGoal]) -> Tuple[str, List[str]]:
        """Add constraints based on goals."""
        improvements = []
        optimized = prompt
        
        # Collect constraints from goals
        all_constraints = []
        for goal in goals:
            all_constraints.extend(goal.constraints)
        
        if all_constraints and "Constraints:" not in optimized:
            constraints_text = "Constraints: " + ", ".join(all_constraints[:5])
            optimized = f"{optimized}\n\n{constraints_text}"
            improvements.append("Added goal-based constraints")
        
        return optimized, improvements


class GoalAlignmentEngine:
    """
    Unified Goal Alignment System
    
    Combines goal injection and prompt optimization for
    comprehensive goal-aligned prompt engineering.
    """
    
    def __init__(self):
        self.goal_injector = GoalInjector()
        self.prompt_optimizer = PromptOptimizer()
        self.alignment_history: List[GoalAlignmentResult] = []
    
    def align_prompt_to_goals(
        self,
        base_prompt: str,
        goals: List[StrategicGoal],
        context_type: str = "business",
        optimization_focus: List[str] = None
    ) -> GoalAlignmentResult:
        """
        Align prompt to strategic goals.
        
        Args:
            base_prompt: Original prompt to align
            goals: Strategic goals for alignment
            context_type: Type of context
            optimization_focus: Optimization strategies to apply
            
        Returns:
            Goal alignment result with detailed information
        """
        # Step 1: Inject goals into prompt
        injected_prompt, injected_goals = self.goal_injector.inject_goals(
            base_prompt, goals, context_type
        )
        
        # Step 2: Optimize prompt for goal alignment
        aligned_prompt, improvements = self.prompt_optimizer.optimize_prompt(
            injected_prompt, goals, optimization_focus
        )
        
        # Step 3: Calculate alignment score
        alignment_score = self._calculate_alignment_score(base_prompt, aligned_prompt, goals)
        
        result = GoalAlignmentResult(
            original_prompt=base_prompt,
            aligned_prompt=aligned_prompt,
            aligned_goals=injected_goals,
            alignment_score=alignment_score,
            improvements_made=improvements
        )
        
        self.alignment_history.append(result)
        
        logger.info(f"Prompt alignment completed: {alignment_score:.3f} score, {len(improvements)} improvements")
        
        return result
    
    def _calculate_alignment_score(
        self,
        original_prompt: str,
        aligned_prompt: str,
        goals: List[StrategicGoal]
    ) -> float:
        """Calculate alignment score between prompt and goals."""
        base_score = 0.5
        
        # Check if goal keywords are present
        goal_keywords = []
        for goal in goals:
            # Extract keywords from goal description
            keywords = re.findall(r'\b\w+\b', goal.description.lower())
            goal_keywords.extend(keywords[:3])  # Top 3 keywords per goal
        
        aligned_lower = aligned_prompt.lower()
        keyword_matches = sum(1 for keyword in goal_keywords if keyword in aligned_lower)
        
        if goal_keywords:
            keyword_score = keyword_matches / len(goal_keywords)
            base_score += keyword_score * 0.3
        
        # Check for goal-related sections
        goal_sections = ['objective', 'goals', 'requirements', 'success criteria', 'constraints']
        section_matches = sum(1 for section in goal_sections if section in aligned_lower)
        section_score = section_matches / len(goal_sections)
        base_score += section_score * 0.2
        
        return min(base_score, 1.0)
    
    def create_strategic_goals(
        self,
        business_objectives: List[str],
        technical_requirements: List[str] = None,
        communication_goals: List[str] = None,
        compliance_requirements: List[str] = None
    ) -> List[StrategicGoal]:
        """
        Create strategic goals from objectives.
        
        Args:
            business_objectives: Primary business objectives
            technical_requirements: Technical requirements
            communication_goals: Communication goals
            compliance_requirements: Compliance requirements
            
        Returns:
            List of strategic goals
        """
        goals = []
        
        # Business goals (highest priority)
        for i, objective in enumerate(business_objectives[:3]):
            goal = StrategicGoal(
                goal_id=f"business_{i+1}",
                goal_type=GoalType.BUSINESS,
                priority=GoalPriority.HIGH if i == 0 else GoalPriority.MEDIUM,
                description=objective,
                success_metrics=[f"Achieve {objective.lower()}"],
                constraints=["Maintain quality standards", "Follow best practices"]
            )
            goals.append(goal)
        
        # Technical goals
        if technical_requirements:
            for i, requirement in enumerate(technical_requirements[:2]):
                goal = StrategicGoal(
                    goal_id=f"technical_{i+1}",
                    goal_type=GoalType.TECHNICAL,
                    priority=GoalPriority.MEDIUM,
                    description=requirement,
                    success_metrics=[f"Meet {requirement.lower()}"],
                    constraints=["Ensure compatibility", "Maintain performance"]
                )
                goals.append(goal)
        
        # Communication goals
        if communication_goals:
            for i, comm_goal in enumerate(communication_goals[:2]):
                goal = StrategicGoal(
                    goal_id=f"communication_{i+1}",
                    goal_type=GoalType.COMMUNICATION,
                    priority=GoalPriority.MEDIUM,
                    description=comm_goal,
                    success_metrics=[f"Achieve {comm_goal.lower()}"],
                    constraints=["Be clear and concise", "Maintain professional tone"]
                )
                goals.append(goal)
        
        # Compliance goals
        if compliance_requirements:
            for i, compliance_req in enumerate(compliance_requirements[:2]):
                goal = StrategicGoal(
                    goal_id=f"compliance_{i+1}",
                    goal_type=GoalType.COMPLIANCE,
                    priority=GoalPriority.HIGH,
                    description=compliance_req,
                    success_metrics=[f"Ensure {compliance_req.lower()}"],
                    constraints=["Follow regulations", "Maintain audit trail"]
                )
                goals.append(goal)
        
        return goals
    
    def get_alignment_stats(self) -> Dict[str, object]:
        """Get alignment statistics."""
        if not self.alignment_history:
            return {}
        
        recent_alignments = self.alignment_history[-10:]
        
        avg_score = sum(r.alignment_score for r in recent_alignments) / len(recent_alignments)
        total_improvements = sum(len(r.improvements) for r in recent_alignments)
        
        return {
            'total_alignments': len(self.alignment_history),
            'recent_alignments': len(recent_alignments),
            'average_alignment_score': avg_score,
            'total_improvements_made': total_improvements,
            'most_common_improvements': self._get_most_common_improvements(recent_alignments)
        }
    
    def _get_most_common_improvements(self, alignments: List[GoalAlignmentResult]) -> List[str]:
        """Get most common improvement types."""
        improvement_counts = {}
        
        for alignment in alignments:
            for improvement in alignment.improvements_made:
                improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1
        
        # Return top 5 most common improvements
        sorted_improvements = sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{improvement}: {count}" for improvement, count in sorted_improvements[:5]]


# Factory functions for easy integration
def create_goal_alignment_engine() -> GoalAlignmentEngine:
    """Create goal alignment engine instance."""
    return GoalAlignmentEngine()


def create_goal_injector() -> GoalInjector:
    """Create goal injector instance."""
    return GoalInjector()


def create_prompt_optimizer() -> PromptOptimizer:
    """Create prompt optimizer instance."""
    return PromptOptimizer()
