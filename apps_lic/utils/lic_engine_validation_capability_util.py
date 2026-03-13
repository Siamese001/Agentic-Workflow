"""
LICEngineValidationCapability — Pure execution harness for LIC validation agents.

Extracts the shared validation scaffold that Cluster 5 engine agents repeat:

  1. Print status banner with agent name
  2. Delegate to agent-specific ``_validate()`` for issue collection
  3. Score: add_signal + record_result + status print (pass/fail)

The capability OWNS:
  - The execution scaffold (run_validation -> _validate -> score)
  - Logging format and status printing
  - Signal dispatch and result recording

The capability REJECTS:
  - Any domain-specific business logic
  - Knowledge of specific validation rules or domain concepts

If the validation *process* changes, update the Capability.
If the validation *rules* change, update the Agents.

[CREATED 2026-02-08] Cluster 5 extraction per Unified Architectural Directive.
"""

from __future__ import annotations

import logging
from typing import ClassVar

Logger = logging.getLogger(__name__)


class LICEngineValidationCapability:
    """Pure execution harness for LIC engine validation agents.

    Subclasses MUST:
        - Set SIGNAL_NAME  (e.g., "MY_DOMAIN_ISSUE")
        - Set VALIDATION_LABEL  (e.g., "Domain check passed")
        - Override _validate() → list[str]  returning issue descriptions

    Subclasses inherit:
        - run_validation(): the complete scaffold (log → validate → score)
    """

    SIGNAL_NAME: ClassVar[str] = ""
    VALIDATION_LABEL: ClassVar[str] = ""

    def _validate(self) -> list[str]:
        """Execute domain-specific validation checks.

        Returns:
            List of issue description strings. Empty list means pass.

        Raises:
            NotImplementedError: if subclass does not override.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _validate()")

    def run_validation(self) -> list[str]:
        """Execute the full validation scaffold.

        1. Log the start banner.
        2. Delegate to ``_validate()`` for domain-specific issue collection.
        3. If issues: ``add_signal()`` + ``record_result(False)`` + log fail.
           Else: ``record_result(True)`` + log pass.

        Returns:
            The list of issues (empty on pass).
        """
        agent_name = getattr(self, "name", self.__class__.__name__)
        if not self.SIGNAL_NAME:
            raise ValueError(f"{self.__class__.__name__} must set SIGNAL_NAME")
        if not self.VALIDATION_LABEL:
            raise ValueError(f"{self.__class__.__name__} must set VALIDATION_LABEL")
        print(f"   [{agent_name}] Checking {self.VALIDATION_LABEL}...")
        issues = self._validate()
        if issues:
            self.add_signal(self.SIGNAL_NAME)
            self.record_result(False, f"{self.VALIDATION_LABEL} issues: {len(issues)}")
            print(f"   [{agent_name}] ❌ {self.VALIDATION_LABEL} issues: {len(issues)}")
        else:
            self.record_result(True, self.VALIDATION_LABEL)
            print(f"   [{agent_name}] ✅ {self.VALIDATION_LABEL}")
        return issues
