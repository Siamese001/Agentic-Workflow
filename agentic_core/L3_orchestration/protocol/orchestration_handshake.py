#!/usr/bin/env python3
"""
OrchestrationHandshake - Multi-Hop Agent Collaboration
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from agentic_core.L4_state.registry.subatomic_registry import SubAtomicRegistry

class OrchestrationHandshake:
    """
    Sovereign handshake protocol — eternal agent collaboration.
    """
    def __init__(self, project_root: Path, requesting_agent: str):
        self.root = project_root
        self.requesting_agent = requesting_agent
        self.registry = SubAtomicRegistry(project_root)

    def delegate_task(
        self, 
        task: str, 
        kwargs: Optional[Dict] = None, 
        min_confidence: float = 0.88
    ) -> Dict:
        """
        Sovereign delegation: Find the best tool and use it.
        """
        kwargs = kwargs or {}
        
        # Discovery Phase
        candidates = self.registry.find_method(task, top_k=3)
        if not candidates or candidates[0]['score'] < min_confidence:
            return {"status": "failed", "reason": "No high-confidence agent found."}

        best = candidates[0]['metadata']
        print(f"   [HANDSHAKE] {self.requesting_agent} -> {best['method']} ({candidates[0]['score']:.2f})")

        # Execution Phase
        try:
            result = self.registry.invoke_method(best, **kwargs)
            return {
                "status": "success",
                "agent": best['method'],
                "result": str(result)[:500]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_mission(self, steps: List[Dict]) -> List[Dict]:
        """
        Multi-hop mission logic: Sequential delegation.
        """
        trail = []
        context = {}
        
        for i, step in enumerate(steps):
            print(f"   [MISSION] Step {i+1}: {step['task']}")
            # Pass results of previous step into current step's context
            step_kwargs = {**step.get('kwargs', {}), **context}
            
            outcome = self.delegate_task(step['task'], kwargs=step_kwargs)
            trail.append(outcome)
            
            if outcome['status'] != "success":
                print(f"   [!] Mission stalled at step {i+1}")
                break
            
            # Update context for the next hop
            context = {"previous_result": outcome['result']}
            
        return trail
