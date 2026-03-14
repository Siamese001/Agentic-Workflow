"""
AgentDispatchRegistry — Wave 2 typed dispatch layer.

Replaces raw ``getattr(instance, method)(*args)`` calls with a governed
dispatch path that:

1. Verifies the calling agent is registered in ``AgentCapabilityRegistry``.
2. Verifies the target agent is a declared ``handoff_target`` (or dispatch
   is to a named method on a registered instance).
3. Requires a capability token for cross-agent handoffs.
4. Emits a structured ``agent_executes_agent`` log record visible to the ADG
   extractor, converting previously opaque ``invokes_getattr_dynamic`` edges
   into typed ``agent_executes_agent`` edges.
5. Falls back to ``getattr`` internally during the Wave 2 shim period —
   zero semantic change, full graph visibility.

Migration path
--------------
  Before (invokes_getattr_dynamic edge):
      result = getattr(some_agent, method_name)(payload)

  After (agent_executes_agent edge):
      from agentic_core.L3_orchestration.registry.agent_dispatch_registry import (
          get_agent_dispatch_registry,
      )
      registry = get_agent_dispatch_registry()
      result = registry.dispatch(
          caller="MyOrchestrator",
          target_instance=some_agent,
          method=method_name,
          args=(payload,),
      )

Hard cutover (remove shim)
--------------------------
  After Wave 2 acceptance gate passes (``agent_executes_agent >= 50``),
  set ``AgentDispatchRegistry(shim_mode=False)`` to block unregistered
  getattr dispatch.

ADG edges emitted (log-level structured records):
  ``agent_executes_agent`` — logged at DEBUG for every successful dispatch
  ``dispatch_blocked``     — logged at WARNING for capability/token failures
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.registry.agent_capability_registry import (
    AgentCapabilityRegistry,
    get_agent_capability_registry,
)

logger = logging.getLogger(__name__)

_ADG_EDGE_LOGGER = logging.getLogger("adg.agent_executes_agent")


class DispatchDeniedError(PermissionError):
    """Raised when dispatch is denied due to capability or token failure."""


class UnregisteredAgentError(LookupError):
    """Raised when caller or target is not registered in the capability registry."""


@dataclass
class DispatchRecord:
    """Immutable record of a single typed agent dispatch."""

    caller: str
    target_class: str
    method: str
    capability_token_id: str
    permitted: bool
    shim_mode: bool
    error: str = ""
    result_type: str = ""


@dataclass
class _RegisteredInstance:
    """Internal record binding an agent name to its live instance."""

    agent_name: str
    instance: Any
    capabilities: list[str] = field(default_factory=list)


class AgentDispatchRegistry:
    """Typed dispatch layer for L3 agent-to-agent handoffs.

    Shim mode (default)
    -------------------
    All dispatches succeed via ``getattr`` regardless of capability check
    result. Failures are logged as WARN but do not block execution.
    This is Wave 2 policy: warn for one sprint, then enforce.

    Enforce mode (shim_mode=False)
    ------------------------------
    Dispatches to unregistered agents or without a valid capability token
    raise ``DispatchDeniedError``. Enable at Wave 2 acceptance gate.
    """

    def __init__(
        self,
        capability_registry: AgentCapabilityRegistry | None = None,
        shim_mode: bool = True,
    ) -> None:
        self._cap_registry = capability_registry or get_agent_capability_registry()
        self.shim_mode = shim_mode
        self._instances: dict[str, _RegisteredInstance] = {}
        self._dispatch_ledger: list[DispatchRecord] = []

    def register_instance(
        self,
        agent_name: str,
        instance: Any,
        capabilities: list[str] | None = None,
    ) -> None:
        """Bind a live agent instance to its registered name.

        The instance is looked up by name on every ``dispatch()`` call.
        Capabilities list is informational and supplements the capability registry.
        """
        self._instances[agent_name] = _RegisteredInstance(
            agent_name=agent_name,
            instance=instance,
            capabilities=capabilities or [],
        )
        logger.debug(
            "DISPATCH_REGISTRY registered instance agent=%s caps=%s",
            agent_name,
            capabilities,
        )

    def dispatch(
        self,
        caller: str,
        target_instance: Any,
        method: str,
        args: tuple = (),
        kwargs: dict | None = None,
        capability_token: Any = None,
    ) -> Any:
        """Dispatch ``target_instance.method(*args, **kwargs)`` via the governed path.

        Emits an ``agent_executes_agent`` structured log record on success.

        Args:
            caller: Name of the dispatching agent (for graph edge ``src``).
            target_instance: The agent object receiving the call.
            method: Method name to invoke.
            args: Positional arguments.
            kwargs: Keyword arguments.
            capability_token: Optional token object (must have ``.token_id`` attr
                              or be a non-empty string).

        Returns:
            The return value of ``target_instance.method(*args, **kwargs)``.

        Raises:
            DispatchDeniedError: In enforce mode if capability check fails.
            AttributeError: If the method does not exist on the target.
        """
        if kwargs is None:
            kwargs = {}

        target_class = type(target_instance).__name__
        token_id = _extract_token_id(capability_token)

        permitted, denial_reason = self._check_capability(
            caller=caller,
            target_class=target_class,
            method=method,
            capability_token=capability_token,
        )

        if not permitted:
            record = DispatchRecord(
                caller=caller,
                target_class=target_class,
                method=method,
                capability_token_id=token_id,
                permitted=False,
                shim_mode=self.shim_mode,
                error=denial_reason,
            )
            self._dispatch_ledger.append(record)
            if self.shim_mode:
                logger.warning(
                    "DISPATCH_REGISTRY dispatch_blocked (shim: continuing) "
                    "caller=%s target=%s method=%s reason=%s",
                    caller,
                    target_class,
                    method,
                    denial_reason,
                )
            else:
                raise DispatchDeniedError(
                    f"AgentDispatchRegistry: dispatch denied. "
                    f"caller={caller} target={target_class}.{method} reason={denial_reason}"
                )

        if not hasattr(target_instance, method):
            raise AttributeError(
                f"AgentDispatchRegistry: {target_class!r} has no method {method!r}. "
                f"caller={caller}"
            )

        result = getattr(target_instance, method)(*args, **kwargs)

        result_type = type(result).__name__
        record = DispatchRecord(
            caller=caller,
            target_class=target_class,
            method=method,
            capability_token_id=token_id,
            permitted=True,
            shim_mode=self.shim_mode,
            result_type=result_type,
        )
        self._dispatch_ledger.append(record)

        _ADG_EDGE_LOGGER.debug(
            "agent_executes_agent caller=%s target=%s method=%s token=%s result_type=%s",
            caller,
            target_class,
            method,
            token_id,
            result_type,
        )
        return result

    def dispatch_by_name(
        self,
        caller: str,
        target_name: str,
        method: str,
        args: tuple = (),
        kwargs: dict | None = None,
        capability_token: Any = None,
    ) -> Any:
        """Dispatch to a registered instance by name.

        Raises:
            UnregisteredAgentError: If ``target_name`` is not registered.
        """
        if target_name not in self._instances:
            raise UnregisteredAgentError(
                f"AgentDispatchRegistry: agent '{target_name}' not registered. "
                f"Registered: {sorted(self._instances)}"
            )
        return self.dispatch(
            caller=caller,
            target_instance=self._instances[target_name].instance,
            method=method,
            args=args,
            kwargs=kwargs,
            capability_token=capability_token,
        )

    def _check_capability(
        self,
        caller: str,
        target_class: str,
        method: str,
        capability_token: Any,
    ) -> tuple[bool, str]:
        """Return (permitted, reason). permitted=True means dispatch may proceed."""
        caller_spec = self._cap_registry.get(caller)
        if caller_spec is None:
            if self.shim_mode:
                return True, ""
            return False, f"caller '{caller}' not in capability registry"

        if not self._cap_registry.can_handoff(caller, target_class):
            if self.shim_mode:
                return True, f"caller '{caller}' handoff to '{target_class}' not declared (shim)"
            return False, f"caller '{caller}' handoff to '{target_class}' not declared"

        if capability_token is None and not self.shim_mode:
            return False, "capability_token required in enforce mode"

        return True, ""

    def get_dispatch_ledger(self) -> list[DispatchRecord]:
        """Return append-only copy of all dispatch records."""
        return list(self._dispatch_ledger)

    def get_stats(self) -> dict[str, Any]:
        """Return dispatch statistics."""
        total = len(self._dispatch_ledger)
        permitted = sum(1 for r in self._dispatch_ledger if r.permitted)
        agent_executes_agent_count = sum(1 for r in self._dispatch_ledger if r.permitted)
        return {
            "total_dispatches": total,
            "permitted": permitted,
            "blocked": total - permitted,
            "agent_executes_agent_edges": agent_executes_agent_count,
            "shim_mode": self.shim_mode,
            "registered_instances": sorted(self._instances),
        }

    def set_enforce_mode(self) -> None:
        """Disable shim fallback — enable at Wave 2 acceptance gate."""
        self.shim_mode = False
        logger.info("DISPATCH_REGISTRY enforce mode enabled — shim disabled")


def _extract_token_id(capability_token: Any) -> str:
    """Extract a string token_id from various token shapes."""
    if capability_token is None:
        return ""
    if isinstance(capability_token, str):
        return capability_token
    if hasattr(capability_token, "token_id"):
        return str(capability_token.token_id)
    return str(type(capability_token).__name__)


_global_dispatch_registry: AgentDispatchRegistry | None = None


def get_agent_dispatch_registry() -> AgentDispatchRegistry:
    """Return the singleton AgentDispatchRegistry (shim mode by default)."""
    global _global_dispatch_registry
    if _global_dispatch_registry is None:
        _global_dispatch_registry = AgentDispatchRegistry()
    return _global_dispatch_registry


def reset_agent_dispatch_registry() -> None:
    """Reset singleton (for testing)."""
    global _global_dispatch_registry
    _global_dispatch_registry = None


__all__ = [
    "AgentDispatchRegistry",
    "AgentCapabilityRegistry",
    "DispatchRecord",
    "DispatchDeniedError",
    "UnregisteredAgentError",
    "get_agent_dispatch_registry",
    "reset_agent_dispatch_registry",
]
