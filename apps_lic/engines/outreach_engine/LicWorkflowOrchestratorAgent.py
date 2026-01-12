from __future__ import annotations
"""HOP Workflow Orchestrator Agent - HOP-based Workflow Orchestration."""

__version__ = "13.1"

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_lic outreach-specific vs L3 core orchestration)
# - Intentional variant for domain-specific behavior
# - Consolidated 2026-01-06

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from apps_shared.utils.state_manager import StateManager
from apps_shared.utils.vector_memory import VectorMemoryStore
from apps_shared.utils.circuit_breaker import CircuitBreaker
from apps_lic.engines.outreach_engine.tools.code_interpreter import CodeInterpreterTool, ValidationToolkit

from apps_lic.domain.lic_models import OutreachMission, FactualGapError

from .HOP2ResearchAgent import HOP2ResearchAgent
from .HOP5GenerationAgent import HOP5GenerationAgent
from .HOP6ValidationAgent import HOP6ValidationAgent
from .HOP8QAReportAgent import HOP8QAReportAgent


class LicWorkflowOrchestratorAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.0: HOP-based Workflow Orchestrator
    
    The Orchestrator is configuration-driven and agent-agnostic.
    Implements S6→S2 meta-loop (Factual failure) and S5 retry (Creative failure).
    """
    
    def __init__(self) -> None:
        """Initialize orchestrator with all dependencies"""
        with open("config/agent_specs_LIC.json", 'r') as f:
            self.config = json.load(f)
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config["circuit_breaker"]["failure_threshold"],
            timeout_seconds=self.config["circuit_breaker"]["timeout_seconds"]
        )
        
        # Initialize API clients (stubs for now)
        self.search_client = None  # GoogleSearchClient(self.circuit_breaker)
        self.llm_client = None  # GeminiLLMClient(self.circuit_breaker)
        
        self.memory_store = VectorMemoryStore()
        self.code_tool = CodeInterpreterTool()
        self.validation_toolkit = ValidationToolkit()
        
        self.agents = {
            "HOP-2": HOP2ResearchAgent(self.config, self.memory_store, self.search_client, self.llm_client),
            "HOP-5": HOP5GenerationAgent(self.config, self.llm_client, self.code_tool),
            "HOP-6": HOP6ValidationAgent(self.config, self.validation_toolkit),
            "HOP-8": HOP8QAReportAgent(self.config)
        }
        
        self.hop_execution_order = self.config["hop_execution_order"]["hops"]
        print(f"[WorkflowOrchestratorAgent] Initialized with {len(self.agents)} agents")
    
    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """Execute complete workflow using HOP architecture"""
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n{'='*80}")
        print(f"HOP WORKFLOW ORCHESTRATOR v13.0")
        print(f"Mission ID: {mission.mission_id}")
        print(f"{'='*80}")
        
        start_time = datetime.now()
        state_mgr = StateManager(mission_id=mission.mission_id)
        
        factual_loop_count = 0
        creative_retry_count = 0
        max_factual_loops = 2
        max_creative_retries = 3
        
        try:
            while True:
                for hop_spec in self.hop_execution_order:
                    hop_id = hop_spec["hop_id"]
                    
                    if hop_id not in self.agents:
                        print(f"\n⚠ {hop_id} - Agent not implemented, skipping")
                        continue
                    
                    agent = self.agents[hop_id]
                    
                    try:
                        await agent.execute(state_mgr)
                    except FactualGapError as e:
                        factual_loop_count += 1
                        
                        if factual_loop_count >= max_factual_loops:
                            print(f"\n✗ Max factual loops ({max_factual_loops}) reached - HALTING")
                            raise ValueError(f"Max factual loops exceeded: {e}")
                        
                        print(f"\n⚠ Factual gap detected: {e}")
                        print(f"→ Triggering S6→S2 meta-loop (attempt {factual_loop_count}/{max_factual_loops})")
                        break
                    except Exception as e:
                        print(f"\n✗ Error in {hop_id}: {e}")
                        raise
                
                if state_mgr.state_exists("HOP-7"):
                    gate = state_mgr.read_state("HOP-7")
                    decision = gate.get("decision")
                    
                    if decision == "CREATIVE_FAILURE":
                        creative_retry_count += 1
                        
                        if creative_retry_count >= max_creative_retries:
                            print(f"\n✗ Max creative retries ({max_creative_retries}) reached - HALTING")
                            raise ValueError("Max creative retries exceeded")
                        
                        print(f"\n⚠ Creative failure detected")
                        print(f"→ Retrying HOP-5 with escalated temperature (attempt {creative_retry_count}/{max_creative_retries})")
                        
                        base_temp = 0.50
                        new_temp = min(0.95, base_temp + (creative_retry_count * 0.15))
                        
                        await self.agents["HOP-5"].execute(state_mgr, temperature=new_temp)
                        await self.agents["HOP-6"].execute(state_mgr)
                        continue
                    elif decision == "PASS":
                        break
                else:
                    break
        
        except Exception as e:
            print(f"\n✗ Workflow failed: {e}")
            return {
                "mission_id": mission.mission_id,
                "status": "failed",
                "error": str(e),
                "workflow_time": (datetime.now() - start_time).total_seconds()
            }
        
        workflow_time = (datetime.now() - start_time).total_seconds()
        
        validation = state_mgr.read_state("HOP-6") if state_mgr.state_exists("HOP-6") else {}
        generation = state_mgr.read_state("HOP-5") if state_mgr.state_exists("HOP-5") else {}
        
        passed = validation.get("passed", False)
        draft = generation.get("selected_draft", {})
        
        print(f"\n{'='*80}")
        print(f"WORKFLOW COMPLETE")
        print(f"Status: {'PASS' if passed else 'FAIL'}")
        print(f"Time: {workflow_time:.1f}s")
        print(f"Factual loops: {factual_loop_count}")
        print(f"Creative retries: {creative_retry_count}")
        print(f"{'='*80}\n")
        
        return {
            "mission_id": mission.mission_id,
            "status": "success" if passed else "failed_validation",
            "production_ready": passed,
            "message": draft.get("text", ""),
            "word_count": draft.get("word_count", 0),
            "workflow_time": workflow_time,
            "factual_loop_count": factual_loop_count,
            "creative_retry_count": creative_retry_count,
            "validation_summary": {
                "passed": passed,
                "critical_issues": validation.get("critical_issues", 0),
                "high_issues": validation.get("high_issues", 0)
            }
        }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, int]:
        """Operational agent - no repository healing required."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        print(f"[{self.__class__.__name__}] Operational agent - no healing required")
        return {"skipped": 1}


async def main():
    """Main execution entry point"""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    from apps_lic.domain.lic_models import OutreachMission
    
    mission = OutreachMission(
        mission_id="demo_v13_001",
        sender_profile={"name": "Amit Ayer", "title": "Chief AI Officer", "company": "Unify Consulting"},
        recipient_profile={"name": "Sarah Johnson", "title": "VP of Engineering", "company": "Tech Giants Corp"},
        JobDescription={"title": "Head of AI Platform", "company": "Tech Giants Corp", "location": "San Francisco, CA"},
        connection_status="not_connected",
        prior_message_count=0
    )
    
    orchestrator = LicWorkflowOrchestratorAgent()
    result = await orchestrator.execute_workflow(mission)
    
    print("\n" + "="*80)
    print("WORKFLOW RESULT")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
