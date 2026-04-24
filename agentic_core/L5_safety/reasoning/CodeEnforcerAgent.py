"""Code Enforcer Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_enforcer_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.3 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling = consumer migration window)
Category: deprecated-delegating-shim
Canonical replacement: agentic_core.L5_safety.utils.code_enforcer_util
Consumers at authorization (4):
  - agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py (dispatch-dict values)
  - agentic_core/L3_orchestration/reasoning/engines/AgentFactory.py (create_pattern_enforcer + lazy loader)
  - agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeEnforcerAgent' dispatch)
  - ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py

Policy interpretation (pragmatic constitutional \u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after 2026-07-23 will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeEnforcerAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_CodeEnforcerAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_enforcer_util import (
    CodeEnforcer as _CodeEnforcer,
)


class CodeEnforcerAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Enforcer Agent - now delegates to code_enforcer_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_enforcer_util directly.
    """

    def __init__(self):
        """Initialize CodeEnforcerAgent (deprecated, use code_enforcer_util instead)."""
        super().__init__(name="CodeEnforcerAgent", layer="L5")

        warnings.warn(
            "CodeEnforcerAgent is deprecated. Use agentic_core.L5_safety.utils.code_enforcer_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._enforcer = _CodeEnforcer()

    def validate_file(self, file_path: Path) -> list[Any]:
        """Validate a file for code violations."""
        return self._enforcer.validate_file(file_path)

    def enforce_standards(self, file_path: Path) -> dict[str, Any]:
        """Enforce code standards on a file."""
        return self._enforcer.enforce_standards(file_path)
