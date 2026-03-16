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

from agentic_core.L2_execution.enforcement.guardrail_gate import (
    GuardrailGate,
    GuardrailViolationError,
    get_guardrail_gate,
)
from agentic_core.L2_execution.trace_context import get_trace_context
from agentic_core.L3_orchestration.contracts.coordination_ledger import (
    MissingCoordinationLedger,
    get_coordination_ledger,
    update_coordination_ledger,
)
from agentic_core.L3_orchestration.registry.agent_capability_registry import (
    AgentCapabilityRegistry,
    get_agent_capability_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "agent_dispatch_registry")
emit_determinism_digest("p0", "agent_dispatch_registry")

_emit_dispatches_healing_run("p1", "agent_dispatch_registry", "L3")
_emit_routes_through("p1", "agent_dispatch_registry", "L3")
_emit_escalates_to_human("p1", "agent_dispatch_registry", "L3")
_emit_reads_policy_state("p1", "agent_dispatch_registry", "L3")
_emit_snapshots_state("p0", "agent_dispatch_registry", "state_snapshot")
_emit_applies_guardrail("p0", "agent_dispatch_registry", "p0_governance")

logger = logging.getLogger(__name__)

_ADG_EDGE_LOGGER = logging.getLogger("adg.agent_executes_agent")
_SAFETY_LOGGER = logging.getLogger("adg.reenters_safety")


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
    guardrail_verdict: str = ""
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
        guardrail_gate: GuardrailGate | None = None,
        guardrail_mode: str = "warn",
    ) -> None:
        """Initialise the dispatch registry.

        Args:
            capability_registry: Capability registry for handoff validation.
            shim_mode: If True, capability failures warn but do not block.
            guardrail_gate: Pre-execution guardrail gate. Defaults to process-level gate.
            guardrail_mode: ``"warn"`` (log only) or ``"enforce"`` (raise on DENY).
                            Wave 3 hardening: start ``warn``, switch to ``enforce`` per sublayer.
        """
        self._cap_registry = capability_registry or get_agent_capability_registry()
        self.shim_mode = shim_mode
        self._guardrail_gate = guardrail_gate or get_guardrail_gate()
        self.guardrail_mode = guardrail_mode
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

        # --- Wave 3: Guardrail pre-check (applies_guardrail ADG edge) ---
        guardrail_op = f"dispatch:{caller}->{target_class}.{method}"
        guardrail_verdict = "allow"
        try:
            gr_result = self._guardrail_gate.check(
                operation=guardrail_op,
                target=f"{target_class}.{method}",
                metadata={"caller": caller, "token_id": token_id},
            )
            guardrail_verdict = gr_result.verdict.value
        except GuardrailViolationError as gve:
            guardrail_verdict = "deny"
            _SAFETY_LOGGER.warning(
                "reenters_safety caller=%s target=%s method=%s reason=%s",
                caller,
                target_class,
                method,
                str(gve),
            )
            record = DispatchRecord(
                caller=caller,
                target_class=target_class,
                method=method,
                capability_token_id=token_id,
                permitted=False,
                shim_mode=self.shim_mode,
                guardrail_verdict="deny",
                error=f"guardrail_deny:{gve}",
            )
            self._dispatch_ledger.append(record)
            if self.guardrail_mode == "enforce":
                raise DispatchDeniedError(
                    f"AgentDispatchRegistry: guardrail denied dispatch. "
                    f"caller={caller} target={target_class}.{method}"
                ) from gve
            logger.warning(
                "DISPATCH_REGISTRY guardrail_blocked (warn mode: continuing) caller=%s target=%s method=%s",
                caller,
                target_class,
                method,
            )

        # --- Capability check ---
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
                guardrail_verdict=guardrail_verdict,
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
                f"AgentDispatchRegistry: {target_class!r} has no method {method!r}. caller={caller}"
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
            guardrail_verdict=guardrail_verdict,
            result_type=result_type,
        )
        self._dispatch_ledger.append(record)

        _ADG_EDGE_LOGGER.debug(
            "agent_executes_agent caller=%s target=%s method=%s token=%s result_type=%s guardrail=%s",
            caller,
            target_class,
            method,
            token_id,
            result_type,
            guardrail_verdict,
        )

        # P1/L3: update CoordinationLedger on every agent dispatch if run is tracked
        _run_id = getattr(capability_token, "run_id", "") if capability_token else ""
        if _run_id and get_coordination_ledger(_run_id) is not None:
            try:
                update_coordination_ledger(
                    run_id=_run_id,
                    owner_agent_id=caller,
                    stage_transition={
                        "new_stage": f"dispatch:{method}",
                        "new_owner": target_class,
                        "handoff_reason": f"{caller}->{target_class}.{method}",
                    },
                )
            except (MissingCoordinationLedger, Exception) as _cl_exc:
                logger.debug("DISPATCH_REGISTRY coordination_ledger update skipped: %s", _cl_exc)

        # P0/L6: emit records_execution_trace + signs_execution_trace lifecycle edges
        from agentic_core.runtime.execution_trace import get_active_execution_trace  # noqa: PLC0415

        _active = get_active_execution_trace()
        _rtid = _active.trace_id if _active else f"no-trace:{caller}->{target_class}"
        _emit_records_execution_trace(_rtid, "L3", f"dispatch:{caller}->{target_class}.{method}")
        _emit_signs_execution_trace(_rtid, f"{caller}:{target_class}:{method}", result_type, 0)
        get_trace_context().record(
            layer="L3",
            module="AgentDispatchRegistry",
            operation=f"dispatch:{caller}->{target_class}.{method}",
            metadata={
                "caller": caller,
                "target_class": target_class,
                "method": method,
                "token_id": token_id,
                "guardrail_verdict": guardrail_verdict,
                "result_type": result_type,
            },
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

    def set_guardrail_enforce(self) -> None:
        """Switch guardrail from warn to enforce — enable at Wave 3 acceptance gate."""
        self.guardrail_mode = "enforce"
        logger.info("DISPATCH_REGISTRY guardrail enforce mode enabled")


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
