"""
Unified Planning Coordinator

Consolidates 4 fragmented planners (Message, Strategic, Persona, Profile)
into a single coordinator using strategy pattern. Provides unified planning
interface with quality scoring, adaptive adjustment, and validation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import hashlib
import functools
from dataclasses import dataclass


@dataclass
class PlanValidationResult:
    """Result of plan validation."""
    valid: bool
    reasons: List[str]
    rollback_steps: List[Dict[str, Any]]
    feasible: bool
    constraints_satisfied: bool


class PlanStrategy(ABC):
    """Base planning strategy interface."""
    
    @abstractmethod
    def generate(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate plan for goal.
        
        Returns standardized plan:
        {
            "steps": [...],
            "constraints": [...],
            "estimated_cost": float,
            "domain": str
        }
        """
        pass


class MessagePlanningStrategy(PlanStrategy):
    """Strategy for message/communication planning."""
    
    def generate(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate message plan."""
        return {
            "steps": [
                {"action": "draft", "description": "Draft message"},
                {"action": "refine", "description": "Refine tone and clarity"},
                {"action": "send", "description": "Send message"}
            ],
            "constraints": ["tone", "length", "audience"],
            "estimated_cost": 3,
            "domain": "message",
            "feasible": True
        }


class StrategicPlanningStrategy(PlanStrategy):
    """Strategy for strategic/high-level planning."""
    
    def generate(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic plan."""
        return {
            "steps": [
                {"action": "analyze", "description": "Analyze goal and constraints"},
                {"action": "prioritize", "description": "Prioritize objectives"},
                {"action": "allocate", "description": "Allocate resources"},
                {"action": "execute", "description": "Execute strategy"}
            ],
            "constraints": ["resources", "timeline", "scope"],
            "estimated_cost": 4,
            "domain": "strategic",
            "feasible": True
        }


class PersonaPlanningStrategy(PlanStrategy):
    """Strategy for persona-based planning."""
    
    def generate(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate persona plan."""
        persona = context.get("persona", "default")
        return {
            "steps": [
                {"action": "identify_persona", "description": f"Identify {persona} persona"},
                {"action": "adapt_approach", "description": "Adapt approach to persona"},
                {"action": "execute", "description": "Execute persona-aligned plan"}
            ],
            "constraints": ["persona_consistency", "authenticity"],
            "estimated_cost": 3,
            "domain": "persona",
            "feasible": True
        }


class ProfilePlanningStrategy(PlanStrategy):
    """Strategy for profile/user-specific planning."""
    
    def generate(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate profile plan."""
        profile = context.get("profile", "default")
        return {
            "steps": [
                {"action": "load_profile", "description": f"Load {profile} profile"},
                {"action": "customize", "description": "Customize for profile"},
                {"action": "execute", "description": "Execute profile-specific plan"}
            ],
            "constraints": ["profile_compliance", "personalization"],
            "estimated_cost": 3,
            "domain": "profile",
            "feasible": True
        }


class PlanningCoordinator:
    """
    Unified planning hub - consolidates 4 fragmented planners.
    
    Provides:
    - Single entrypoint for all planning domains
    - Standardized plan format
    - Quality scoring and adaptive adjustment
    - Plan validation and feasibility checking
    - Caching for repeated goals
    """
    
    def __init__(self):
        """Initialize planning coordinator with all strategies."""
        self.strategies: Dict[str, PlanStrategy] = {
            'message': MessagePlanningStrategy(),
            'strategic': StrategicPlanningStrategy(),
            'persona': PersonaPlanningStrategy(),
            'profile': ProfilePlanningStrategy(),
        }
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.plans_generated = 0
        self.plans_cached = 0
        self.plans_adjusted = 0
    
    def plan(
        self,
        goal: str,
        domain: str,
        context: Dict[str, Any],
        feedback: Optional[str] = None,
        max_adjustments: int = 3
    ) -> Dict[str, Any]:
        """
        Generate unified plan.
        
        Args:
            goal: Planning goal
            domain: Planning domain (message, strategic, persona, profile)
            context: Planning context
            feedback: Feedback from previous attempt (for adaptive adjustment)
            max_adjustments: Maximum adaptive adjustment iterations
            
        Returns:
            Standardized plan with score and validation
        """
        self.plans_generated += 1
        
        # Adaptive adjustment from feedback
        if feedback:
            context = context.copy()
            context["feedback"] = feedback
            context["instruction"] = f"Adjust plan based on: {feedback}"
        
        # Check cache
        cache_key = self._make_cache_key(goal, domain, context)
        if cache_key in self.cache:
            self.plans_cached += 1
            cached_plan = self.cache[cache_key].copy()
            cached_plan["cached"] = True
            return cached_plan
        
        # Get strategy
        strategy = self.strategies.get(domain.lower())
        if not strategy:
            raise ValueError(f"Unknown planning domain: {domain}")
        
        # Generate raw plan
        raw_plan = strategy.generate(goal, context)
        
        # Optimize plan
        optimized_plan = self._optimize_plan(raw_plan, context)
        
        # Validate plan
        validation = self._validate_plan(optimized_plan, context)
        
        # Score plan
        score = self._score_plan(optimized_plan, validation)
        
        # Adaptive adjustment if score low
        if score < 0.7 and max_adjustments > 0:
            self.plans_adjusted += 1
            return self.plan(
                goal,
                domain,
                context,
                feedback="Previous plan score low — simplify and retry",
                max_adjustments=max_adjustments - 1
            )
        
        # Build final plan
        final_plan = {
            "goal": goal,
            "domain": domain,
            "steps": optimized_plan.get("steps", []),
            "constraints": optimized_plan.get("constraints", []),
            "estimated_cost": optimized_plan.get("estimated_cost", 0),
            "score": score,
            "valid": validation.valid,
            "validation_reasons": validation.reasons,
            "rollback_steps": validation.rollback_steps,
            "cached": False
        }
        
        # Cache plan
        self.cache[cache_key] = final_plan.copy()
        
        return final_plan
    
    def _make_cache_key(self, goal: str, domain: str, context: Dict[str, Any]) -> str:
        """Create stable cache key."""
        context_str = str(sorted(context.items()))
        key_input = f"{goal}|{domain}|{context_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()
    
    def _optimize_plan(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize plan (priority, parallelization, resource allocation).
        
        Args:
            plan: Raw plan
            context: Planning context
            
        Returns:
            Optimized plan
        """
        optimized = plan.copy()
        
        # Reorder steps by priority if available
        if "priorities" in context:
            steps = optimized.get("steps", [])
            # Simple priority-based reordering
            optimized["steps"] = sorted(
                steps,
                key=lambda s: context["priorities"].get(s.get("action"), 0),
                reverse=True
            )
        
        # Estimate cost based on step count
        optimized["estimated_cost"] = len(optimized.get("steps", []))
        
        return optimized
    
    def _validate_plan(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> PlanValidationResult:
        """
        Validate plan for feasibility and constraints.
        
        Args:
            plan: Plan to validate
            context: Planning context
            
        Returns:
            Validation result
        """
        valid = True
        reasons = []
        feasible = True
        constraints_satisfied = True
        
        # Check step count
        max_steps = context.get("max_steps", 20)
        if len(plan.get("steps", [])) > max_steps:
            valid = False
            feasible = False
            reasons.append(f"Too many steps: {len(plan['steps'])} > {max_steps}")
        
        # Check estimated cost
        if "budget" in context:
            budget = context["budget"]
            cost = plan.get("estimated_cost", 0)
            if cost > budget:
                valid = False
                reasons.append(f"Over budget: {cost} > {budget}")
        
        # Check constraints
        constraints = plan.get("constraints", [])
        required_constraints = context.get("required_constraints", [])
        missing = [c for c in required_constraints if c not in constraints]
        if missing:
            constraints_satisfied = False
            reasons.append(f"Missing constraints: {missing}")
        
        # Generate rollback steps (reverse order)
        rollback_steps = list(reversed(plan.get("steps", [])))
        
        return PlanValidationResult(
            valid=valid,
            reasons=reasons,
            rollback_steps=rollback_steps,
            feasible=feasible,
            constraints_satisfied=constraints_satisfied
        )
    
    def _score_plan(
        self,
        plan: Dict[str, Any],
        validation: PlanValidationResult
    ) -> float:
        """
        Score plan quality (0.0 to 1.0).
        
        Heuristic:
        - Completeness: Number of steps
        - Feasibility: Validation result
        - Cost: Estimated cost
        - Constraint satisfaction: All constraints met
        
        Args:
            plan: Plan to score
            validation: Validation result
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        
        # Completeness: steps cover goal (max 10 steps = 1.0)
        step_count = len(plan.get("steps", []))
        completeness = min(1.0, step_count / 10.0)
        score += completeness * 0.3
        
        # Feasibility: validation passed
        if validation.feasible:
            score += 0.3
        
        # Cost efficiency: fewer steps is better
        cost = plan.get("estimated_cost", 0)
        cost_efficiency = max(0.0, 1.0 - (cost / 20.0))
        score += cost_efficiency * 0.2
        
        # Constraint satisfaction
        if validation.constraints_satisfied:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get planning statistics."""
        return {
            "plans_generated": self.plans_generated,
            "plans_cached": self.plans_cached,
            "plans_adjusted": self.plans_adjusted,
            "cache_hit_rate": (self.plans_cached / self.plans_generated * 100) if self.plans_generated > 0 else 0,
            "cache_size": len(self.cache),
            "adjustment_rate": (self.plans_adjusted / self.plans_generated * 100) if self.plans_generated > 0 else 0
        }
    
    def clear_cache(self) -> None:
        """Clear plan cache."""
        self.cache.clear()


# Global instance
planning_coordinator = PlanningCoordinator()
