"""
Golden Context Mixin - Anti-Context Drift Protection.

Injects a concise summary of the SSOT structure blueprint into the message
context to prevent agents from "forgetting" the rules during long execution loops.

COGNITIVE HARDENING (Feb 2026):
- Landmine #3 Prevention: Context Drift
- Injects "The Law" at the end of message lists
- Ensures agents remember structural rules even 50+ turns deep
"""

import logging
from typing import Any, Final

logger = logging.getLogger(__name__)

# The Golden Context: A concise summary of the SSOT Law
# This is injected to remind agents of the structural rules
GOLDEN_CONTEXT_SUMMARY: Final[str] = """
=== SOVEREIGN SSOT LAW (Golden Context Injection) ===

You are operating within a governed repository. These rules are IMMUTABLE:

1. **BASE AGENTS LOCATION**: All *BaseAgent.py files MUST reside in `agentic_core/base_agents/`.
   - NEVER place base agents in layer folders (L0-L6).
   - Constitutional override: LocationAgent.validate_file_location() enforces this.

2. **LAYER HIERARCHY (L0-L6)**:
   - L0: Maintenance (scripts, healing, bootstrapping)
   - L1: Cognition (thought engine, intent analysis, planning)
   - L2: Execution (tool registry, MCP, action handlers)
   - L3: Orchestration (workflow engines, meta-learning)
   - L4: State (validation context, ledger, memory)
   - L5: Safety (guardrails, validators, gravity)
   - L6: Observability (dashboards, telemetry, logging)

3. **DEPTH RULES**:
   - agentic_core: Depth 3 (some L4 approved folders go to depth 4)
   - apps_rg, apps_lic, apps_shared: Depth 2
   - tests: Depth 3 (type/domain/test_file.py)

4. **FORBIDDEN PATTERNS**:
   - No unknown layers (all agents must have valid layer assignment)
   - No duplicates (one canonical agent per file)
   - No hardcoded paths (use structure_blueprint_config.py constants)

5. **SSOT FILES**:
   - Structure: `agentic_core/L5_safety/config/structure_blueprint_config.py`
   - Agent Registry: `agent_discovery_full.json`

REMEMBER: When in doubt, consult the SSOT. Do not hallucinate file locations.
=== END GOLDEN CONTEXT ===
"""


class GoldenContextMixin:
    """
    Mixin that provides golden context injection capabilities.

    Inherit from this mixin to gain the ability to inject SSOT rules
    into message contexts, preventing context drift during long loops.
    """

    _golden_context_cache: str | None = None

    def get_golden_context(self) -> str:
        """
        Get the golden context summary.

        Returns:
            The SSOT law summary string.
        """
        if self._golden_context_cache is None:
            self._golden_context_cache = GOLDEN_CONTEXT_SUMMARY.strip()
        return self._golden_context_cache

    def inject_golden_context(
        self,
        current_messages: list[dict[str, Any]],
        role: str = "system",
    ) -> list[dict[str, Any]]:
        """
        Inject the golden context into the message list.

        This appends a system message containing the SSOT rules to the
        END of the message list, ensuring the agent "remembers" the rules
        even in deep conversation contexts.

        Args:
            current_messages: The current list of messages.
            role: The role for the injected message (default: "system").

        Returns:
            A new message list with the golden context appended.
        """
        if not current_messages:
            current_messages = []

        # Create a copy to avoid mutating the original
        messages = list(current_messages)

        # Create the golden context message
        golden_message = {
            "role": role,
            "content": self.get_golden_context(),
        }

        # Append to the end so it's fresh in the context window
        messages.append(golden_message)

        logger.debug(f"[GoldenContextMixin] Injected golden context. Total messages: {len(messages)}")

        return messages

    # guardian: allow-magic-config
    def should_inject_golden_context(
        self,
        current_messages: list[dict[str, Any]],
        # guardian: allow-magic-config
        threshold: int = 10,
    ) -> bool:
        """
        Determine if golden context should be injected.

        Injection is recommended when:
        - Message count exceeds the threshold
        - No recent golden context injection exists

        Args:
            current_messages: The current list of messages.
            threshold: Minimum message count before injection (default: 10).

        Returns:
            True if injection is recommended.
        """
        if len(current_messages) < threshold:
            return False

        # Check if we recently injected (last 5 messages)
        recent_messages = current_messages[-5:] if len(current_messages) >= 5 else current_messages
        for msg in recent_messages:
            content = msg.get("content", "")
            if "SOVEREIGN SSOT LAW" in content:
                return False

        return True


__all__ = ["GoldenContextMixin", "GOLDEN_CONTEXT_SUMMARY"]
