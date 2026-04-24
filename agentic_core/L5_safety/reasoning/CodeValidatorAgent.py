"""Code Validator Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_validator_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.3 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling = consumer migration window)
Category: deprecated-delegating-shim
Canonical replacement: agentic_core.L5_safety.utils.code_validator_util
Consumers at authorization (3):
  - agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeValidatorAgent' dispatch)
  - agentic_core/L5_safety/utils/runners/code_validator_runner.py (subprocess runner)
  - ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py

Policy interpretation (pragmatic constitutional \u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after 2026-07-23 will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeValidatorAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_CodeValidatorAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_validator_util import (
    CodeValidator as _CodeValidator,
)
from agentic_core.L5_safety.utils.code_validator_util import (
    RuleSet,
    Violation,
)


class CodeValidatorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Validator Agent - now delegates to code_validator_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_validator_util directly.
    """

    def __init__(self, ruleset: RuleSet | None = None, **kwargs: Any) -> None:
        """Initialize CodeValidatorAgent (deprecated, use code_validator_util instead)."""
        super().__init__(**kwargs)

        warnings.warn(
            "CodeValidatorAgent is deprecated. Use agentic_core.L5_safety.utils.code_validator_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.ruleset = ruleset or RuleSet()
        self._validator = _CodeValidator(self.ruleset)
        self._validation_results: list[Violation] = []

    def validate_syntax(self, file_path: Path) -> list[Violation]:
        """Validate Python syntax for a file."""
        return self._validator.validate_syntax(file_path)

    def validate_canon(self, file_path: Path) -> list[Violation]:
        """Validate canonical patterns for a file."""
        return self._validator.validate_canon(file_path)

    def validate_async(self, file_path: Path) -> list[Violation]:
        """Validate async/await usage for a file."""
        return self._validator.validate_async(file_path)

    def validate_prints(self, file_path: Path) -> list[Violation]:
        """Validate print statement usage for a file."""
        return self._validator.validate_prints(file_path)

    def validate_file(self, file_path: Path) -> list[Violation]:
        """Validate a single file for all code rules."""
        return self._validator.validate_file(file_path)

    def validate_directory(self, directory: Path) -> list[Violation]:
        """Validate all Python files in a directory."""
        report = self._validator.validate_directory(directory)
        return report.violations
