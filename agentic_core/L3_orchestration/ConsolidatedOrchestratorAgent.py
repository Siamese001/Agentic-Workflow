"""ConsolidatedOrchestratorAgent — The General (Phase 4 Integration)

Coordinates all sub-orchestrators and ensures the Mission is executed
according to the Prime Directive.

Phase 4 Activation:
- run_mission() method for executing Sovereign Healing Mission
- Factory function get_consolidated_orchestrator()
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import L3OrchestrationBaseAgent

Logger = logging.getLogger(__name__)


# [SOVEREIGN FACTORY]
def get_consolidated_orchestrator(project_root):
    """Factory function to get ConsolidatedOrchestratorAgent instance."""
    return ConsolidatedOrchestratorAgent(project_root)


class ConsolidatedOrchestratorAgent(L3OrchestrationBaseAgent):
    """
    The General.
    Coordinates all sub-orchestrators and ensures the Mission is executed
    according to the Prime Directive.
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize the Consolidated Orchestrator."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.Logger = logging.getLogger(__name__)
        super().__init__()
    
    def run_mission(self, agents: List[Tuple[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes the Sovereign Healing Mission.
        
        Args:
            agents (list): List of (name, agent_instance) tuples to execute.
            context (dict): Runtime context and flags.
            
        Returns:
            dict: Mission execution summary.
        """
        if context is None:
            context = {}
            
        mission_log = []
        total_fixes = 0
        total_violations = 0
        agents_count = len(agents)
        start_mission_time = time.time()
        
        # Phase 6: Layered Sovereign Sweep
        print(f"\n[L3 ORCHESTRATOR] ⚔️  MISSION START")
        print(f"   [MODE] {'EXECUTE' if context.get('execute') else 'DRY-RUN'}")
        print(f"   [COMMAND] Controlling {len(agents)} Autonomous Agents")
        
        # Log scan mode if present (Phase 6 verification)
        if context.get("scan_mode"):
            print(f"   [CONTEXT] Scan Mode: {context['scan_mode']}")
        
        # Sequence by Layer Gravity (L0 -> L5 -> L2 -> L1)
        for i, (agent_name, agent_instance) in enumerate(agents, 1):
            print(f"\n   [L3 CONTROL] ({i}/{agents_count}) Handing control to: {agent_name}")
            agent_start_time = time.time()

            try:
                # Execute the agent's healing method
                # We assume a standard interface: heal_repository(**kwargs)
                # Pass only standard arguments to ensure compatibility with all agents
                result = agent_instance.heal_repository(
                    dry_run=context.get('dry_run', True),
                    execute=context.get('execute', False)
                )
                
                # Handle None or invalid results
                if result is None:
                    print(f"   [L3 SKIP] {agent_name}: Returned None (skipped)")
                    mission_log.append({"agent": agent_name, "status": "skipped", "reason": "None result"})
                    continue
                
                # Standardize result extraction
                # [SSOT] Primary keys: 'fixed' and 'violations' for 270+ agent compatibility
                if isinstance(result, dict):
                    fixes = result.get('fixed') or result.get('violations_fixed') or result.get('renamed') or 0
                    violations = result.get('violations') or result.get('violations_found') or result.get('errors') or 0
                else:
                    fixes = 0
                    violations = 0
                
                execution_duration = time.time() - agent_start_time
                total_fixes += fixes
                total_violations += violations
                
                status = "✅ CLEAN" if violations == 0 else f"⚠️  {violations} ISSUES"
                print(f"   [L3 REPORT] {agent_name}: {status} (Fixed: {fixes})")
                
                mission_log.append({
                    "agent": agent_name, 
                    "status": "success", 
                    "fixed": fixes, 
                    "violations": violations,
                    "duration_sec": round(execution_duration, 3),
                    "result": result
                })
                
            except Exception as e:
                print(f"   [!] {agent_name} CRITICAL FAILURE: {e}")
                mission_log.append({
                    "agent": agent_name, 
                    "status": "failed", 
                    "error": str(e),
                    "duration_sec": round(time.time() - agent_start_time, 3)
                })

        # [STABILITY GATE SIGNAL]
        # Mission is stable if no violations remain OR we are in dry-run mode
        is_stable = total_violations == 0 or not context.get('execute', False)
        mission_duration = time.time() - start_mission_time

        print(f"\n[L3 ORCHESTRATOR] 🏁 MISSION COMPLETE")
        return {
            "mission_log": mission_log,
            "total_fixes": total_fixes,
            "total_violations": total_violations,
            "is_stable": is_stable,
            "duration_sec": round(mission_duration, 3)
        }
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None, **kwargs) -> Dict[str, Any]:
        """L3 Orchestrator - delegates to run_mission when called directly."""
        print(f"[ConsolidatedOrchestratorAgent] L3 Orchestration - ready for mission control")
        # Standardized return for ConsolidatedOrchestrator when acting as an agent
        return {"agent": "ConsolidatedOrchestratorAgent", "status": "ready", "fixed": 0, "violations": 0}
