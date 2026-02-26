"""
RG Spine Adapter — pure wiring, no business logic.

Forces all RG entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Null-object stubs are provided for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus — these seams are not yet wired for RG and must remain no-ops
until the corresponding phases implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.interfaces.execution import CIDRegistry
from agentic_core.interfaces.spine import (
    AirlockAssembler,
    ExecutionOrchestrator,
    GovernedPayload,
    PathRouter,
    ReEntryLoop,
)
from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

# Default maximum re-entry attempts for the RG spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3

# ---------------------------------------------------------------------------
# Null-object stubs for unimplemented seams
# ---------------------------------------------------------------------------


class _NullD0Engine:
    """Null-object stub for D0 injection engine (not yet wired for RG)."""

    def render_d0(self, d0_injections: str) -> str:
        return d0_injections


@dataclass(frozen=True)
class _RiskResult:
    allow: bool


class _NullRiskGate:
    """Null-object stub for risk gate (not yet wired for RG)."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)


class _NullVigilanceDispatcher:
    """Null-object stub for vigilance dispatcher (not yet wired for RG)."""

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        pass


class _NullMetaBus:
    """Null-object stub for meta-learning bus (not yet wired for RG)."""

    def enqueue(self, *args: Any, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _RgAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the RG slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# RG Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class RgSpineAdapter(BaseSpineAdapter):
    """
    Canonical RG spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    # RG-specific prefix
    _PREFIX: str = "rg-"

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        """Initialize RG spine adapter with dependency wiring."""
        # Create core dependencies
        cid_registry = CIDRegistry()
        reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=cid_registry,
        )
        orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=cid_registry,
            reentry_loop=reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

        # Initialize base adapter with dependencies and RG prefix
        super().__init__(
            cid_registry=cid_registry,
            orchestrator=orchestrator,
            prefix=self._PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )
