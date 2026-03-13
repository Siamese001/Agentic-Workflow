"""
File: agentic_core/base_agents/healer_interface.py
Description: Standardization layer for Healer Agents. Provides Mixins for new agents and Adapters for legacy ones.
"""

import logging
from typing import Any, Protocol, runtime_checkable

HEAL_RESULT_SCHEMA = {"status": "str", "details": "str", "artifacts": "list", "errors": "list"}


@runtime_checkable
class IHealerProtocol(Protocol):
    """The strict interface Phase 2 expects."""

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]: ...


from agentic_core.mixins.healer_agent_mixin import HealerAgentMixin


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
            if hasattr(self.agent, "fix"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.fix({file_path})")
                    res = self.agent.fix(file_path)
                    return self._wrap_legacy_result(res)
                else:
                    return {"status": "skipped", "details": "Legacy agent requires file path"}
            elif hasattr(self.agent, "run"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.run([{file_path}])")
                    res = self.agent.run([file_path])
                    return self._wrap_legacy_result(res)
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
        if isinstance(result, bool):
            return {
                "status": "success" if result else "failed",
                "details": "Legacy boolean return",
                "artifacts": [],
                "errors": [],
            }
        if isinstance(result, str):
            return {"status": "success", "details": result, "artifacts": [], "errors": []}
        if isinstance(result, list):
            return {
                "status": "success",
                "details": f"Modified {len(result)} files",
                "artifacts": result,
                "errors": [],
            }
        if isinstance(result, dict):
            return HealerAgentMixin()._normalize_result(result)
        return {"status": "unknown", "details": str(result), "artifacts": [], "errors": []}
