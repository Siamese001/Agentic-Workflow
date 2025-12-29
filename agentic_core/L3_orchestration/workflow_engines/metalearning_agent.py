# [CANON KEY 3] MetaLearningAgent - Global Orchestration Optimizer
# Territory: agentic_core/L3_orchestration/workflow_engines
# Purpose: Analyzes mission telemetry to optimize execution order and reflect on convergence
# Logic: Uses self_reflection.jinja and agent_prioritization.jinja meta-prompts

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from agentic_core.prompt_governance.rendering.sovereign_prompt_renderer import get_sovereign_prompt_renderer

class MetaLearningAgent:
    """
    Sovereign agent for post-mission analysis and optimization.

    Responsibilities:
    - Aggregate success/failure metrics from Phase 1 and Phase 2.
    - Perform "Self-Reflection" via LLM to identify strategy gaps.
    - Generate an optimized 'priority_order.json' for the next mission run.
    - Log high-level meta-insights to the L4 Ledger.
    """

    def __init__(self):
        self.memory_path = Path(__file__).parent.parent.parent.parent / "runtime" / "mission_memory.json"

    async def execute(self, ctx: Any) -> None:
        """
        Phase 3 Global Monitor entry point.
        Executes after all healing and batch surgeries are complete.
        """
        if not hasattr(ctx, "report") or not hasattr(ctx, "engine"):
            return

        print("\n[*] META-LEARNING PHASE: Reflecting on mission performance...")

        renderer = get_sovereign_prompt_renderer()
        
        # 1. Gather Telemetry Data
        telemetry = self._calculate_telemetry(ctx)
        
        # 2. Perform Self-Reflection (Meta-Prompt)
        reflection_prompt = renderer.render(
            template_name="self_reflection.jinja",
            context={
                "start_violations": getattr(ctx, "initial_violation_count", 0),
                "end_violations": len(getattr(ctx, "violations", [])),
                "achieved_keys": [k for k, v in getattr(ctx, "key_coverage", {}).items() if v == "zero"],
                "new_agents": getattr(ctx, "spawned_agents", []),
                "immune_count": getattr(ctx, "immune_activations", 0)
            }
        )

        # 3. Optimize Agent Prioritization (Meta-Prompt)
        prioritization_prompt = renderer.render(
            template_name="agent_prioritization.jinja",
            context={
                "violations": self._get_violation_map(ctx),
                "performance": telemetry
            }
        )

        try:
            # Run Reflection Inference
            reflection_raw = await ctx.engine.resilient_mutation(
                file_path="meta_learning_reflection",
                code=reflection_prompt,
                task="Perform sovereign self-reflection",
                round_num=1,
                fission_active=False
            )
            reflection = json.loads(reflection_raw)
            print(f"    [REFLECTION] Success Level: {reflection.get('mission_success_level')}")
            print(f"    [INSIGHT] {reflection.get('sovereign_insight')}")

            # Run Prioritization Inference
            priority_raw = await ctx.engine.resilient_mutation(
                file_path="meta_learning_priority",
                code=prioritization_prompt,
                task="Optimize agent execution order",
                round_num=1,
                fission_active=False
            )
            priority_data = json.loads(priority_raw)
            
            # Persist optimization for next run
            self._update_mission_memory(priority_data.get("recommended_order", []))
            print(f"    [OPTIMIZED] New priority order established for next mission.")

            ctx.report(self.__class__.__name__, 3, True, "Meta-learning loop complete")

        except Exception as e:
            print(f"    [!] Meta-learning failed: {e}")
            ctx.report(self.__class__.__name__, 3, False, f"Meta-learning failure: {str(e)}")

    def _calculate_telemetry(self, ctx: Any) -> Dict[str, Any]:
        """Aggregates success rates and reduction metrics from the report."""
        telemetry = {}
        # Logic to parse ctx.report and calculate success/reduction per agent
        # (Simplified for implementation)
        return telemetry

    def _get_violation_map(self, ctx: Any) -> Dict[int, int]:
        """Groups current violations by Canon Key."""
        # Logic to map current ctx.violations to their respective keys
        return {}

    def _update_mission_memory(self, priority_order: List[str]) -> None:
        """Saves optimization data to the runtime mission memory."""
        memory = {}
        if self.memory_path.exists():
            memory = json.loads(self.memory_path.read_text())
        
        memory["next_priority_order"] = priority_order
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(json.dumps(memory, indent=2))

def get_meta_learning_agent():
    return MetaLearningAgent()
