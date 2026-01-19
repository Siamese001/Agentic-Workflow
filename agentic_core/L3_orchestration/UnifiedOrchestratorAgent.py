"""
UnifiedOrchestratorAgent - Central Nervous System for Agentic Workflow

Architecture: Strategy Pattern
- Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
- Inherits from L3OrchestrationBaseAgent for standard logging/state management.

SSOT PRINCIPLE:
    All orchestration flows through this unified agent.
    Domain-specific logic is encapsulated in Strategy classes.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
import logging

from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import L3OrchestrationBaseAgent
from agentic_core.L3_orchestration.strategies.SafetyStrategy import SafetyStrategy
from agentic_core.L3_orchestration.strategies.RLStrategy import RLStrategy

Logger = logging.getLogger(__name__)


class UnifiedOrchestratorAgent(L3OrchestrationBaseAgent):
    """
    The Central Nervous System for Agentic Workflow.
    
    Architecture: Strategy Pattern
    - Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
    - Inherits from L3OrchestrationBaseAgent for standard logging/state management.
    """
    
    def __init__(self, agent_id: str = "unified_orchestrator_01"):
        super().__init__()
        self.agent_id = agent_id
        self.agent_type = "L3_Unified"
        self.logger = Logger
        
        # Initialize Strategies
        self.strategies = {
            "safety": SafetyStrategy(),
            "rl": RLStrategy(),
            # "planning": PlanningStrategy() # Future expansion
        }
        self.logger.info(f"UnifiedOrchestrator initialized with strategies: {list(self.strategies.keys())}")

    def dispatch(self, domain: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a request to the appropriate strategy.
        
        Args:
            domain (str): The strategy domain ('safety', 'rl').
            action (str): The method to call on the strategy.
            payload (dict): Data to pass to the strategy.
        """
        if domain not in self.strategies:
            error_msg = f"Unknown strategy domain: {domain}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        strategy = self.strategies[domain]
        
        # Dynamic dispatch check
        if not hasattr(strategy, action):
            error_msg = f"Strategy '{domain}' has no action '{action}'"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
             
        try:
            method = getattr(strategy, action)
            result = method(payload)
            self.logger.info(f"Dispatched {domain}.{action} successfully.")
            return {"status": "success", "data": result}
        except Exception as e:
            self.logger.error(f"Strategy execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}
