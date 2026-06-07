"""e2_agent_gate — decorator adapter wrapping agent methods with the E2 gate.

Plan: `docs/archive/windsurf/legacy-tree/plans/l2-execute-v2-agent-conformance-c8e4f1.md` §W4.
Closes gap G-V6 (no agent-level E2 gate decorator).

This module is a thin ADDITIVE adapter that lets any agent method opt into
the L2 Execute v2 §E2 Work Order Check without modifying the method's call
signature. The decorator:

1. Extracts or constructs a :class:`ToolContract` from the method's kwargs
   (looks for an explicit ``tool_contract`` kwarg; if absent, returns the
   method's native behavior untouched — FULLY OPT-IN)
2. Calls :func:`evaluate_work_order` (W4 of plan b7c4e2, landed 2026-04-23)
3. On approved verdict: invokes the wrapped method and returns its result
4. On ``ConfirmBeforeExecute``: wraps the exception with the agent + method
   identity and re-raises. Does NOT swallow.
5. On ``E2RejectedBeforeExecute``: re-raises with agent + method identity.

No call-site migration is required by this plan — the decorator is landed
as a reusable primitive. Future plans can apply ``@e2_agent_gate`` to
specific agent methods when those methods should go through the gate.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

from agentic_core.L2_execution.enforcement.e2_validate_before_execute import (
    ConfirmBeforeExecute,
    E2RejectedBeforeExecute,
    E2Verdict,
    evaluate_work_order,
)
from agentic_core.L2_execution.types.execution_tool_contract import ToolContract

__all__ = [
    "AgentGateConfirmRequired",
    "AgentGateRejected",
    "e2_agent_gate",
    "extract_contract",
]

_F = TypeVar("_F", bound=Callable[..., Any])


class AgentGateConfirmRequired(Exception):
    """Raised when an agent-wrapped method's E2 gate requires HITL confirmation.

    Wraps :class:`ConfirmBeforeExecute` with the agent + method identity so
    upstream HITL routers can present actionable context to the approver.
    """

    def __init__(self, agent: str, method: str, verdict: E2Verdict) -> None:
        super().__init__(
            f"e2_agent_gate confirm_required agent={agent} method={method} "
            f"tool={verdict.tool_name} trace_id={verdict.trace_id} "
            f"reason={verdict.reason!r}"
        )
        self.agent = agent
        self.method = method
        self.verdict = verdict


class AgentGateRejected(Exception):
    """Raised when an agent-wrapped method's E2 gate hard-rejects the call."""

    def __init__(self, agent: str, method: str, verdict: E2Verdict) -> None:
        super().__init__(
            f"e2_agent_gate rejected agent={agent} method={method} "
            f"tool={verdict.tool_name} trace_id={verdict.trace_id} "
            f"reason={verdict.reason!r}"
        )
        self.agent = agent
        self.method = method
        self.verdict = verdict


_CONTRACT_KWARGS: tuple[str, ...] = ("tool_contract", "contract", "e2_contract")


def extract_contract(args: tuple[Any, ...], kwargs: dict[str, Any]) -> ToolContract | None:
    """Pull a ToolContract out of *args* / *kwargs* if present.

    Lookup order:
      1. Explicit kwargs: ``tool_contract``, ``contract``, ``e2_contract``
      2. Any positional argument that is a :class:`ToolContract` instance

    Returns ``None`` when no contract is attached — signals "no E2 gate for
    this call; fall through to native method".
    """
    for key in _CONTRACT_KWARGS:
        val = kwargs.get(key)
        if isinstance(val, ToolContract):
            return val
    for a in args:
        if isinstance(a, ToolContract):
            return a
    return None


def e2_agent_gate(method: _F) -> _F:
    """Decorator: run L2 Execute v2 §E2 gate before invoking *method*.

    Usage::

        class MyAgent(SovereignBaseAgent):
            @e2_agent_gate
            def do_work(self, payload, *, tool_contract: ToolContract):
                ...

    Semantics:
      * When the call includes a :class:`ToolContract` (positional or kwargs
        ``tool_contract`` / ``contract`` / ``e2_contract``), the gate runs
        and must emit ``decision="approved"`` before the method executes.
      * When the call does NOT include a contract, the method runs
        unchanged — this is the opt-in path. A future plan can remove the
        fallback once all call sites thread a contract.
      * ``ConfirmBeforeExecute`` and ``E2RejectedBeforeExecute`` are
        intercepted, wrapped with agent + method identity, and re-raised as
        :class:`AgentGateConfirmRequired` / :class:`AgentGateRejected`.
        They are NEVER swallowed.

    The wrapped method may also annotate its return dict with the verdict
    via ``_attach_verdict_to_result`` (left to downstream plans to compose).
    """

    @functools.wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        contract = extract_contract(args, kwargs)
        if contract is None:
            # Opt-in path: no contract → no gate. Preserve native behavior.
            return method(self, *args, **kwargs)
        agent_name = type(self).__name__
        method_name = method.__name__
        try:
            verdict = evaluate_work_order(contract)
        except ConfirmBeforeExecute as exc:
            raise AgentGateConfirmRequired(agent_name, method_name, exc.verdict) from exc
        except E2RejectedBeforeExecute as exc:
            raise AgentGateRejected(agent_name, method_name, exc.verdict) from exc
        # decision == "approved" path — record a breadcrumb in kwargs so the
        # method can include it in seal evidence if desired.
        kwargs.setdefault("_e2_verdict", verdict.to_dict())
        return method(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
