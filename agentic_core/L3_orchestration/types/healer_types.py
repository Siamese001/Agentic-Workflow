"""
File: agentic_core/base_agents/healer_interface.py
Description: Standardization layer for Healer Agents. Provides Mixins for new agents and Adapters for legacy ones.
"""

import logging
from typing import Any, Protocol, runtime_checkable

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Define the expected schema for Phase 2
HEAL_RESULT_SCHEMA = {
    "status": "str",  # success, partial_success, failed, skipped
    "details": "str",  # Human readable summary
    "artifacts": "list",  # List of modified files
    "errors": "list",  # List of error messages
}


@runtime_checkable
class IHealerProtocol(Protocol):
    """The strict interface Phase 2 expects."""

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]: ...


# Canonical definition moved to agentic_core/mixins/healer_agent_mixin.py
# Re-export for backward compatibility
from agentic_core.mixins.healer_agent_mixin import HealerAgentMixin  # noqa: F401


class LegacyAgentAdapter:
    """
    Universal Wrapper for LEGACY agents.
    Translates 'heal(violation)' calls into whatever method the legacy agent has.
    """

    def __init__(self, legacy_agent: Any):
        self.agent = legacy_agent
        self.name = legacy_agent.__class__.__name__

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Smartly routes the heal request to known legacy signatures.
        """
        file_path = violation.get("file") or violation.get("file_path")

        try:
            # STRATEGY 1: Agent has 'fix(file_path)'
            if hasattr(self.agent, "fix"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.fix({file_path})")
                    res = self.agent.fix(file_path)
                    return self._wrap_legacy_result(res)
                else:
                    return {"status": "skipped", "details": "Legacy agent requires file path"}

            # STRATEGY 2: Agent has 'run(files_list)' (Batch processor)
            elif hasattr(self.agent, "run"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.run([{file_path}])")
                    res = self.agent.run([file_path])
                    return self._wrap_legacy_result(res)

            # STRATEGY 3: Agent has 'resolve(violation)'
            elif hasattr(self.agent, "resolve"):
                logging.info(f"Adapter: Calling {self.name}.resolve(violation)")
                res = self.agent.resolve(violation)
                return self._wrap_legacy_result(res)

            else:
                return {
                    "status": "failed",
                    "errors": [f"Agent {self.name} has no recognized healing method (fix/run/resolve)"],
                }

        except Exception as e:
            return {"status": "failed", "errors": [f"Legacy Adapter Error: {str(e)}"]}

    def _wrap_legacy_result(self, result: Any) -> dict[str, Any]:
        """Converts arbitrary legacy returns (bools, strings, lists) to SSOT Schema."""
        # Case A: Boolean Success/Fail
        if isinstance(result, bool):
            return {
                "status": "success" if result else "failed",
                "details": "Legacy boolean return",
                "artifacts": [],
                "errors": [],
            }

        # Case B: String Message
        if isinstance(result, str):
            return {"status": "success", "details": result, "artifacts": [], "errors": []}

        # Case C: List of files
        if isinstance(result, list):
            return {
                "status": "success",
                "details": f"Modified {len(result)} files",
                "artifacts": result,
                "errors": [],
            }

        # Case D: Already a Dict (Just normalize it)
        if isinstance(result, dict):
            return HealerAgentMixin()._normalize_result(result)

        return {"status": "unknown", "details": str(result), "artifacts": [], "errors": []}
