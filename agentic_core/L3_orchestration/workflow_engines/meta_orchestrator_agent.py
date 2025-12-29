# [CANON KEY 3] MetaOrchestratorAgent - Sovereign Meta-Governance Commander
# Territory: agentic_core/L3_orchestration/workflow_engines
# Canon Alignment: L3_orchestration — supreme coordination of evolutionary systems
# Execution: Phase 3 Global Monitor — Authorized via RUN_SPRAWL_SURGERY

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from agentic_core.prompt_governance.rendering.sovereign_prompt_renderer import get_sovereign_prompt_renderer

class MetaOrchestratorAgent:
    """
    Sovereign apex orchestrator — the central command for all meta-governance:
    - Synthesizes convergence planning, immune response, and agent prioritization.
    - Issues 'Supreme Directives' to L0 and L2 layers.
    - Maintains the long-term evolutionary vision of the repository.
    """

    META_FRAGMENTS = [
        "convergence_planning.jinja",
        "immune_response.jinja",
        "agent_prioritization.jinja",
        "self_reflection.jinja",
        "evolution_directive.jinja",
        "meta_coordination_directive.jinja",
        "meta_agent_activation.jinja",
        "meta_convergence_forecast.jinja",
    ]

    async def execute(self, ctx: Any) -> None:
        """
        Phase 3 monitor entry point — issues the master convergence command.
        """
        if not hasattr(ctx, "engine") or ctx.engine is None:
            return

        # [SAFETY GATE] Only activate during high-authorization surgery missions
        if not getattr(ctx, "RUN_SPRAWL_SURGERY", False):
            print("    [INFO] MetaOrchestratorAgent: Standing by (Awaiting RUN_SPRAWL_SURGERY)")
            return

        print("\n[*] SOVEREIGN META-ORCHESTRATION: Synthesizing Supreme Directive...")

        renderer = get_sovereign_prompt_renderer()

        # Assemble the supreme prompt via tagentic composition
        supreme_prompt = renderer.render_tagentic(
            base_template="meta_coordination_directive.jinja",  # Apex base
            fragments=self.META_FRAGMENTS,
            context={
                "mission_count": getattr(ctx, "mission_count", 0) + 1,
                "avg_reduction": getattr(ctx, "last_reduction_rate", 45),
                "converged_keys": getattr(ctx, "converged_keys", ["0", "1", "12"]),
                "persistent_keys": getattr(ctx, "persistent_keys", ["16", "18"]),
                "current_violations": len(getattr(ctx, "violations", [])),
                "behavioral_status": "L4 Ledger Active; L5 Safety Armed",
                "evolution_agents": ["AutonomousPromptEvolutionAgent", "AgenticCodeEvolutionAgent", "MetaLearningAgent"],
                "trigger_type": getattr(ctx, "last_immune_trigger", "none"),
                "severity": "nominal",
                "affected_systems": ["agentic_core", "prompt_governance"],
                "violations": getattr(ctx, "violation_summary", {}),
                "performance": getattr(ctx, "agent_performance_history", {}),
                "start_violations": getattr(ctx, "initial_violation_count", 0),
                "end_violations": len(getattr(ctx, "violations", [])),
                "achieved_keys": [k for k, v in getattr(ctx, "key_coverage", {}).items() if v == "zero"],
                "new_agents": getattr(ctx, "spawned_agents", []),
                "immune_count": getattr(ctx, "immune_activations", 0),
                "prompt_versions": 2, # Traceable via PromptRegistry
                "healer_count": 5,
                "insight_count": 3
            }
        )

        try:
            # Request the Supreme Directive from the SubAtomicEngine
            directive_raw = await ctx.engine.resilient_mutation(
                file_path="supreme_meta_directive",
                code=supreme_prompt,
                task="Generate sovereign master convergence directive",
                round_num=1,
                fission_active=False,
            )

            # Parse and validate the command structure
            try:
                directive = json.loads(directive_raw)
            except json.JSONDecodeError:
                # Fallback to raw capture if LLM fails JSON format laws
                directive = {"raw_directive": directive_raw}

            # Log to immutable directive history
            log_path = Path(ctx.project_root) / "logs" / "supreme_meta_directives.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                json.dump({
                    "timestamp": "2025-12-29T14:51:00",
                    "mission_id": getattr(ctx, "mission_id", "META-ROOT-001"),
                    "directive": directive
                }, f)
                f.write("\n")

            print(f"    [SUPREME COMMAND] Active Streams: {directive.get('active_evolution_streams', [])}")
            if "priority_directives" in directive:
                for cmd in directive["priority_directives"][:2]:
                    print(f"    [DIRECTIVE] {cmd}")
            
            if hasattr(ctx, "audit_log"):
                ctx.audit_log.record(
                    file_name="supreme_meta_directive",
                    action="SOVEREIGN_COMMAND_ISSUED",
                    source="MetaOrchestratorAgent",
                    destination="logs/supreme_meta_directives.jsonl",
                    reason=directive.get("sovereign_command", "Iterative convergence")
                )

            ctx.report(self.__class__.__name__, 3, True, "Supreme meta-directive issued to L0/L2 layers")

        except Exception as e:
            print(f"    [!] Supreme orchestration failure: {e}")
            ctx.report(self.__class__.__name__, 3, False, f"Meta-orchestration failed: {str(e)}")

def get_meta_orchestrator_agent():
    return MetaOrchestratorAgent()
