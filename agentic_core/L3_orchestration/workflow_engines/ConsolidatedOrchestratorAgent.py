"""ConsolidatedOrchestratorAgent — The General (Phase 3 Migration)

PHASE 3 MIGRATION:
This class is now a thin wrapper around UnifiedOrchestratorAgent for backward compatibility.
All orchestration logic has been moved to:
- UnifiedOrchestratorAgent: Generic execution engine
- HealingStrategy: 5-tier healing logic

Legacy scripts that import get_consolidated_orchestrator() will continue to work,
but they now use the unified orchestration system under the hood.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, healer, memory, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Logger = logging.getLogger(__name__)


def get_consolidated_orchestrator(project_root: Path = None):
    """
    Factory function to get a UnifiedOrchestratorAgent configured with HealingStrategy.
    
    PHASE 3 MIGRATION: This now returns a UnifiedOrchestratorAgent instead of
    ConsolidatedOrchestratorAgent. The interface is compatible for most use cases.
    
    Args:
        project_root: Root path for the project (defaults to cwd)
        
    Returns:
        UnifiedOrchestratorAgent configured with HealingStrategy
    """
    from agentic_core.L3_orchestration.unified_orchestrator import UnifiedOrchestratorAgent
    from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
    
    project_root = Path(project_root) if project_root else Path.cwd()
    strategy = HealingStrategy(project_root=project_root)
    
    return UnifiedOrchestratorAgent(
        strategy=strategy,
        project_root=project_root,
        name="ConsolidatedOrchestrator"
    )


class ConsolidatedOrchestratorAgent:
    """
    DEPRECATED: Use UnifiedOrchestratorAgent with HealingStrategy instead.
    
    This class is maintained for backward compatibility only.
    New code should use:
        from agentic_core.L3_orchestration.unified_orchestrator import UnifiedOrchestratorAgent
        from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
        
        orchestrator = UnifiedOrchestratorAgent(strategy=HealingStrategy(project_root))
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize the Consolidated Orchestrator wrapper."""
        import warnings
        warnings.warn(
            "ConsolidatedOrchestratorAgent is deprecated. Use UnifiedOrchestratorAgent with HealingStrategy instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self._unified_orchestrator = get_consolidated_orchestrator(self.project_root)
    
    def run_mission(self, agents: List[Tuple[str, Any]] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes the Sovereign Healing Mission.
        
        PHASE 3 MIGRATION: This now delegates to UnifiedOrchestratorAgent.run_mission().
        
        Args:
            agents: DEPRECATED - Ignored. Agents are now determined by HealingStrategy.
            context: Runtime context and flags (dry_run, execute, etc.)
            
        Returns:
            dict: Mission execution summary compatible with legacy format.
        """
        if context is None:
            context = {}
        
        # Delegate to unified orchestrator
        result = self._unified_orchestrator.run_mission(context)
        
        # Map to legacy format for backward compatibility
        return {
            "mission_log": [
                {
                    "agent": r.get("agent_name", "unknown"),
                    "status": r.get("status", "unknown").lower(),
                    "fixed": r.get("violations_fixed", 0),
                    "violations": r.get("violations_found", 0),
                    "duration_sec": r.get("execution_time_ms", 0) / 1000,
                }
                for r in result.get("agent_results", [])
            ],
            "total_fixes": result.get("total_fixed", 0),
            "total_violations": result.get("total_violations", 0),
            "is_stable": result.get("is_stable", True),
            "duration_sec": result.get("execution_time_ms", 0) / 1000,
        }
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None, **kwargs) -> Dict[str, Any]:
        """L3 Orchestrator - delegates to run_mission when called directly."""
        context = {"dry_run": dry_run, "execute": execute}
        result = self.run_mission(context=context)
        return {
            "agent": "ConsolidatedOrchestratorAgent",
            "status": "PASS" if result.get("is_stable") else "FAIL",
            "fixed": result.get("total_fixes", 0),
            "violations": result.get("total_violations", 0),
        }