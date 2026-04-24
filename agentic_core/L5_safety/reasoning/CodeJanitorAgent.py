"""Code Janitor Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_janitor_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.3 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling = consumer migration window)
Category: deprecated-delegating-shim
Canonical replacement: agentic_core.L5_safety.utils.code_janitor_util
Consumers at authorization (2):
  - agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeJanitorAgent' dispatch)
  - agentic_core/L5_safety/validators/CodeJanitorAgent.py (W2-archive-bound; self-resolves on W6)

Policy interpretation (pragmatic constitutional \u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after 2026-07-23 will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeJanitorAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_CodeJanitorAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path

from agentic_core.L5_safety.utils.code_janitor_util import (
    CodeJanitor as _CodeJanitor,
)
from agentic_core.L5_safety.utils.code_janitor_util import (
    JanitorViolation,
)
from agentic_core.L5_safety.utils.code_janitor_util import (
    validate_indentation as _validate_indentation,
)
from agentic_core.L5_safety.utils.code_janitor_util import (
    validate_syntax as _validate_syntax,
)
from agentic_core.L5_safety.validators.CanonBaseAgent import CanonBaseAgent


class CodeJanitorAgent(CanonBaseAgent):
    """
    DEPRECATED: Code Janitor Agent - now delegates to code_janitor_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_janitor_util directly.
    """

    def __init__(self):
        """Initialize CodeJanitorAgent (deprecated, use code_janitor_util instead)."""
        super().__init__(name="CodeJanitorAgent")

        warnings.warn(
            "CodeJanitorAgent is deprecated. Use agentic_core.L5_safety.utils.code_janitor_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._janitor = _CodeJanitor()

    def validate_syntax(self, file_path: str) -> list[JanitorViolation]:
        """Validate Python syntax."""
        return _validate_syntax(file_path)

    def validate_indentation(self, file_path: str) -> list[JanitorViolation]:
        """Validate indentation consistency."""
        return _validate_indentation(file_path)

    def validate_file(self, file_path: Path) -> list[JanitorViolation]:
        """Run all janitor validations on a file."""
        return self._janitor.validate_file(file_path)
