# [CANON KEY 0] AutonomousPromptEvolutionAgent - L0 Maintenance Evolution
# Territory: agentic_core/L0_maintenance/scripts
# Purpose: Sovereign self-correction of prompt governance artifacts
# Logic: Triggered by PromptValidationAgent findings to generate version-upgrades

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from agentic_core.prompt_governance.rendering.sovereign_prompt_renderer import get_sovereign_prompt_renderer
from agentic_core.prompt_governance.version_registry.prompt_registry import get_prompt_registry

class AutonomousPromptEvolutionAgent:
    """
    Sovereign agent for autonomous evolution of prompt templates.

    Responsibilities (per Master Constitution):
    - Detect evolution needs based on validation drift.
    - Propose v2+ Jinja templates using SubAtomic LLM reasoning.
    - Physically write versioned artifacts to prompt_governance zones.
    - Register new versions in the version_registry for active deployment.
    """

    EVOLUTION_PROMPT = """
You are a sovereign prompt engineer evolving Canon Key 1 templates.

Current template performance issues:
{% for issue in issues %}
- {{ issue }}
{% endfor %}

Task: Evolve the template to v2+ while preserving sovereignty, Jinja syntax, and tagged structure.

Output EXACTLY this JSON format:
{
  "proposed_version": "v2",
  "improved_template": "full Jinja content here",
  "change_rationale": "sovereign justification",
  "expected_impact": "specific metric improvement"
}

Original Template to Evolve:
{{ current_template }}
"""

    async def execute(self, ctx: Any) -> None:
        """
        Phase 3 Monitor / Escalation entry point.
        """
        if not hasattr(ctx, "engine") or ctx.engine is None:
            return # Safety bypass if LLM access is restricted

        trigger = self._detect_evolution_need(ctx)
        if not trigger:
            return

        print(f"\n[*] AUTONOMOUS PROMPT EVOLUTION: Self-correcting {trigger['template']}")

        renderer = get_sovereign_prompt_renderer()
        registry = get_prompt_registry()

        template_path = Path(trigger["path"])
        try:
            current_content = template_path.read_text(encoding="utf-8")
        except Exception:
            return

        evolution_input = renderer.render(
            template_name="code_healing.jinja",
            context={
                "code_block": self.EVOLUTION_PROMPT,
                "violations": trigger["issues"],
                "current_template": current_content
            }
        )

        try:
            proposal_raw = await ctx.engine.resilient_mutation(
                file_path=str(template_path.name),
                code=evolution_input,
                task="Evolve sovereign prompt template",
                round_num=1,
                fission_active=False,
            )
            
            proposal = json.loads(proposal_raw)
            new_version = proposal.get("proposed_version", "v2")
            new_content = proposal["improved_template"]

            # Write new version physically (e.g. reasoning_chain_v2.jinja)
            new_file_name = f"{template_path.stem}_{new_version}{template_path.suffix}"
            new_path = template_path.parent / new_file_name
            new_path.write_text(new_content, encoding="utf-8")

            # Register in registry (marking previous as inactive)
            registry.register_prompt(
                template_name=template_path.name, # logical key
                version=new_version,
                purpose=proposal.get("change_rationale", "Autonomous drift repair"),
                active=True
            )

            print(f"    [EVOLVED] {template_path.name} -> {new_version}")
            
            if hasattr(ctx, "audit_log"):
                ctx.audit_log.record(
                    file_name=template_path.name,
                    action="AUTONOMOUS_PROMPT_EVOLUTION",
                    source="v1",
                    destination=new_version,
                    reason=proposal.get("change_rationale")
                )

            ctx.report(self.__class__.__name__, 0, True, f"Evolved {template_path.name} to {new_version}")

        except Exception as e:
            print(f"    [!] Evolution failed: {e}")
            ctx.report(self.__class__.__name__, 0, False, f"Evolution failure: {str(e)}")

    def _detect_evolution_need(self, ctx: Any) -> Optional[Dict[str, Any]]:
        """
        Heuristic trigger: evaluates context for prompt validation failures.
        """
        if getattr(ctx, "prompt_validation_issues", None):
            # Heuristic: Target the first template cited in the validation issues
            # In a production run, this would involve regex parsing the issues list
            return {
                "template": "reasoning_chain.jinja",
                "path": Path(ctx.project_root) / "agentic_core/prompt_governance/templates/reasoning_chain.jinja",
                "issues": ctx.prompt_validation_issues
            }
        return None

def get_autonomous_prompt_evolution_agent():
    return AutonomousPromptEvolutionAgent()
