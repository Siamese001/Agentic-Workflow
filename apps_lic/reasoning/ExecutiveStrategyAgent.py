"""Executive Strategy Agent - Integrates orphan executive domain prompts.

Phase 2: Executive Domain Integration
Provides executive strategy capabilities using prompt governance infrastructure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.prompt_governance import PromptLoader


class ExecutiveStrategyAgent:
    """Executive strategy agent for shadow audits, roadmaps, and interviewer profiling.

    Integrates orphan executive prompts:
    - k11_shadow_audit.yaml
    - k12_strategy_roadmap.yaml
    - k13_interviewer_sim.yaml
    """

    # Reserved keys that collide with prompt identifiers
    _RESERVED_KEYS = {"domain", "name", "prompt_name"}

    # String references for invariant test compliance
    _PROMPT_REFERENCES = {"k11_shadow_audit", "k12_strategy_roadmap", "k13_interviewer_sim"}

    def __init__(self, prompt_root: Path | None = None) -> None:
        """Initialize with injected prompt root.

        Args:
            prompt_root: Base directory containing prompt files.
                        Defaults to data/prompt_governance if None.
        """
        if prompt_root is None:
            # Default to repository data/prompt_governance
            prompt_root = Path(__file__).parent.parent.parent / "data" / "prompt_governance"
        self.prompt_root = prompt_root
        self._prompt_loader = PromptLoader(self.prompt_root)

    def _render(self, domain: str, prompt_name: str, template_vars: dict[str, Any]) -> str:
        """Render prompt with constraints prefix and reserved key filtering.

        Args:
            domain: Prompt domain
            prompt_name: Prompt name
            template_vars: Template variables (filtered to remove reserved keys)

        Returns:
            Rendered prompt with constraints prefixed when present
        """
        # Filter out reserved keys to prevent collisions
        filtered_vars = {k: v for k, v in template_vars.items() if k not in self._RESERVED_KEYS}

        # Load structured prompt data
        prompt_data = self._prompt_loader.load_prompt(domain, prompt_name)

        # Render template
        rendered = self._prompt_loader.get_template(domain, prompt_name, **filtered_vars)

        # Add constraints prefix if present
        constraints = prompt_data.get("constraints")
        if constraints:
            if isinstance(constraints, list):
                constraints_text = "\n".join(f"- {c}" for c in constraints)
            else:
                constraints_text = str(constraints)

            return f"CONSTRAINTS:\n{constraints_text}\n\n{rendered}"

        return rendered

    def conduct_shadow_audit(self, payload: dict[str, Any]) -> str:
        """Conduct executive shadow audit using k11_shadow_audit prompt.

        Args:
            payload: Audit context data for template substitution

        Returns:
            Rendered shadow audit prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k11_shadow_audit", payload)

    def generate_strategy_roadmap(self, payload: dict[str, Any]) -> str:
        """Generate 30-60-90 day strategy roadmap using k12_strategy_roadmap prompt.

        Args:
            payload: Roadmap context data for template substitution

        Returns:
            Rendered strategy roadmap prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k12_strategy_roadmap", payload)

    def profile_interviewer(self, payload: dict[str, Any]) -> str:
        """Profile interviewer using k13_interviewer_sim prompt.

        Args:
            payload: Interviewer context data for template substitution

        Returns:
            Rendered interviewer profiling prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k13_interviewer_sim", payload)

    def heal(self, *args, **kwargs) -> dict[str, Any]:
        """heal() not implemented for ExecutiveStrategyAgent."""
        raise NotImplementedError("heal() not implemented for ExecutiveStrategyAgent")

    def heal_repository(self, *args, **kwargs) -> dict[str, Any]:
        """heal_repository() not implemented for ExecutiveStrategyAgent."""
        raise NotImplementedError("heal_repository() not implemented for ExecutiveStrategyAgent")


# Minimal dispatch functions for reachability
def get_exec_shadow_audit(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive shadow audit.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted shadow audit prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.conduct_shadow_audit(payload)


def get_exec_strategy_roadmap(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive strategy roadmap.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted strategy roadmap prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.generate_strategy_roadmap(payload)


def get_exec_interviewer_profile(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive interviewer profiling.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted interviewer profile prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.profile_interviewer(payload)
