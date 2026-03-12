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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)
GOLDEN_CONTEXT_SUMMARY: Final[str] = '\n=== SOVEREIGN SSOT LAW (Golden Context Injection) ===\n\nYou are operating within a governed repository. These rules are IMMUTABLE:\n\n1. **BASE AGENTS LOCATION**: All *BaseAgent.py files MUST reside in `agentic_core/base_agents/`.\n   - NEVER place base agents in layer folders (L0-L6).\n   - Constitutional override: LocationAgent.validate_file_location() enforces this.\n\n2. **LAYER HIERARCHY (L0-L6)**:\n   - L0: Maintenance (scripts, healing, bootstrapping)\n   - L1: Cognition (thought engine, intent analysis, planning)\n   - L2: Execution (tool registry, MCP, action handlers)\n   - L3: Orchestration (workflow engines, meta-learning)\n   - L4: State (validation context, ledger, memory)\n   - L5: Safety (guardrails, validators, gravity)\n   - L6: Observability (dashboards, telemetry, logging)\n\n3. **DEPTH RULES**:\n   - agentic_core: Depth 3 (some L4 approved folders go to depth 4)\n   - apps_rg, apps_lic, apps_shared: Depth 2\n   - tests: Depth 3 (type/domain/test_file.py)\n\n4. **FORBIDDEN PATTERNS**:\n   - No unknown layers (all agents must have valid layer assignment)\n   - No duplicates (one canonical agent per file)\n   - No hardcoded paths (use structure_blueprint_config.py constants)\n\n5. **SSOT FILES**:\n   - Structure: `agentic_core/L5_safety/config/structure_blueprint_config.py`\n   - Agent Registry: `agent_discovery_full.json`\n\nREMEMBER: When in doubt, consult the SSOT. Do not hallucinate file locations.\n=== END GOLDEN CONTEXT ===\n'

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

    def inject_golden_context(self, current_messages: list[dict[str, Any]], role: str='system') -> list[dict[str, Any]]:
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
        messages = list(current_messages)
        golden_message = {'role': role, 'content': self.get_golden_context()}
        messages.append(golden_message)
        logger.debug(f'[GoldenContextMixin] Injected golden context. Total messages: {len(messages)}')
        return messages

    # guardian: allow-magic-config
    def should_inject_golden_context(self, current_messages: list[dict[str, Any]], threshold: int=10) -> bool:
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
        recent_messages = current_messages[-5:] if len(current_messages) >= 5 else current_messages
        for msg in recent_messages:
            content = msg.get('content', '')
            if 'SOVEREIGN SSOT LAW' in content:
                return False
        return True
__all__ = ['GoldenContextMixin', 'GOLDEN_CONTEXT_SUMMARY']
