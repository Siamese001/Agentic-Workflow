"""Mock Cognitive Plane for testing.

Phase 2 - Pillar 1: Layering Model
Simple mock implementation that returns predefined plans.
"""

from typing import Any, Dict, List

from schemas.core_interfaces import (
    ICognitivePlane,
    PlanningRequest,
    PlanningResult,
    CognitiveCapability,
)


class MockCognitivePlane(ICognitivePlane):
    """Mock cognitive plane for testing.
    
    Returns predefined plans and reasoning results.
    Useful for testing orchestrator logic without real LLM calls.
    """
    
    def __init__(self, predefined_plans: List[Dict[str, Any]] = None):
        """Initialize mock cognitive plane.
        
        Args:
            predefined_plans: Optional list of plans to return
        """
        self.predefined_plans = predefined_plans or []
        self.plan_index = 0
        self.call_history: List[Dict[str, Any]] = []
    
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Generate a mock plan.
        
        Args:
            request: Planning request
            
        Returns:
            PlanningResult with mock plan
        """
        self.call_history.append({
            "method": "plan",
            "request": request.to_dict(),
        })
        
        if self.predefined_plans and self.plan_index < len(self.predefined_plans):
            plan = self.predefined_plans[self.plan_index]
            self.plan_index += 1
        else:
            # Default mock plan
            plan = [
                {
                    "type": "action",
                    "action_type": "tool_call",
                    "tool": "mock_tool",
                    "parameters": {"query": request.task},
                    "description": f"Mock action for: {request.task}",
                }
            ]
        
        return PlanningResult(
            success=True,
            plan=plan,
            reasoning_trace=[
                {"step": "think", "content": f"Planning for: {request.task}"},
                {"step": "decide", "content": "Decided on mock action"},
            ],
            confidence=0.9,
            metadata={"mock": True},
        )
    
    async def reason(
        self,
        query: str,
        context: Dict[str, Any],
        mode: str = "react",
    ) -> Dict[str, Any]:
        """Apply mock reasoning.
        
        Args:
            query: Query to reason about
            context: Context
            mode: Reasoning mode
            
        Returns:
            Mock reasoning result
        """
        self.call_history.append({
            "method": "reason",
            "query": query,
            "mode": mode,
        })
        
        return {
            "conclusion": f"Mock reasoning for: {query}",
            "reasoning_trace": [
                {"step": "analyze", "content": "Analyzed query"},
                {"step": "conclude", "content": "Reached conclusion"},
            ],
            "confidence": 0.85,
            "state_updates": {},
            "mission_complete": False,
        }
    
    async def decide(
        self,
        options: List[Dict[str, Any]],
        criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make a mock decision.
        
        Args:
            options: Options to choose from
            criteria: Decision criteria
            
        Returns:
            Mock decision
        """
        self.call_history.append({
            "method": "decide",
            "options_count": len(options),
        })
        
        # Just pick first option
        selected = options[0] if options else {}
        
        return {
            "selected": selected,
            "justification": "Mock decision - selected first option",
            "confidence": 0.8,
        }
    
    async def reflect(
        self,
        execution_trace: List[Dict[str, Any]],
        outcome: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mock reflection.
        
        Args:
            execution_trace: Execution history
            outcome: Final outcome
            
        Returns:
            Mock reflection
        """
        self.call_history.append({
            "method": "reflect",
            "trace_length": len(execution_trace),
        })
        
        return {
            "lessons_learned": ["Mock lesson 1", "Mock lesson 2"],
            "improvements": ["Mock improvement 1"],
            "success_factors": ["Mock success factor"],
            "confidence": 0.75,
        }
    
    def get_capabilities(self) -> List[CognitiveCapability]:
        """Get mock capabilities.
        
        Returns:
            All cognitive capabilities
        """
        return list(CognitiveCapability)
    
    def reset(self) -> None:
        """Reset mock state."""
        self.plan_index = 0
        self.call_history.clear()
