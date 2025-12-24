#!/usr/bin/env python3
"""
OrchestrationHandshake - Multi-Hop Agent Collaboration
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from agentic_core.L4_state.registry.subatomic_registry import SubAtomicRegistry
from agentic_core.config.P1_core.sovereign_env import get_env
from agentic_core.L3_orchestration.workflow_engines.cached_orchestrator import CachedOrchestrator

class OrchestrationHandshake(CachedOrchestrator):
    """
    Sovereign handshake protocol — now with deep L3 caching.
    """
    def __init__(self, project_root: Path, requesting_agent: str):
        super().__init__(project_root, mission_id=requesting_agent)
        self.registry = SubAtomicRegistry(project_root)

    def discover_capable_agents(self, task: str, min_confidence: float = 0.85) -> List[Dict]:
        """
        Discover agents/methods capable of task via hybrid registry search.
        Cache-first — Redis hit -> instant discovery.
        """
        cache_key = f"handshake_discover:{hashlib.sha256((task + str(min_confidence)).encode()).hexdigest()}"
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)

        results = self.registry.find_method(task, top_k=10)
        
        capable = []
        for r in results:
            if r['score'] >= min_confidence:
                meta = r['metadata']
                capable.append({
                    "agent_class": meta.get('agent_class', 'Unknown'),
                    "method": meta['method'],
                    "confidence": r['score'],
                    "docstring": meta['docstring'][:200]
                })
        
        # [CACHE WARM] Store discovery results for 1 hour
        if self.redis and capable:
            try:
                self.redis.set(cache_key, json.dumps(capable), ex=3600)
            except Exception: pass

        return sorted(capable, key=lambda x: x['confidence'], reverse=True)

    def delegate_task(
        self,
        task: str,
        args: Optional[Dict] = None,
        kwargs: Optional[Dict] = None,
        min_confidence: float = 0.85
    ) -> Dict:
        """
        Sovereign delegation — find best method and invoke.
        """
        args = args or {}
        kwargs = kwargs or {}
        
        # [CACHE] Check for identical recent delegation
        delegation_key = f"handshake_delegate:{hashlib.sha256((task + json.dumps(kwargs)).encode()).hexdigest()}"
        if self.redis:
            cached = self.redis.get(delegation_key)
            if cached:
                print(f"   [CACHE HIT] Handshake result reused for '{task[:30]}...'")
                return json.loads(cached)

        capable = self.discover_capable_agents(task, min_confidence)
        if not capable:
            return {
                "status": "no_capable_agent",
                "message": f"No agent found for task: {task[:50]}..."
            }

        best = capable[0]
        print(f"   [HANDSHAKE] {self.requesting_agent} -> {best['agent_class']}.{best['method']} ({best['confidence']:.2f})")

        try:
            # Invoke via registry
            method_meta = {
                'agent_class': best['agent_class'],
                'method': best['method']
            }
            result = self.registry.invoke_method(method_meta, **{**args, **kwargs})
            
            audit = {
                "status": "success",
                "delegated_to": f"{best['agent_class']}.{best['method']}",
                "confidence": best['confidence'],
                "result_summary": str(result)[:500] if result else "None"
            }
            # Cache successful delegation for 30 mins
            if self.redis:
                try:
                    self.redis.set(delegation_key, json.dumps(audit), ex=1800)
                except Exception: pass
            return audit
        except Exception as e:
            return {
                "status": "delegation_failed",
                "error": str(e)
            }

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
