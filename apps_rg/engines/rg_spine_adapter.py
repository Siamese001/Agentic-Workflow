"""
RG Spine Adapter — pure wiring, no business logic.

Forces all RG entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Real implementations are wired for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus via shared adapters. Each adapter falls back to a null stub if
its upstream module cannot be imported, preserving fail-open behaviour.
"""

from __future__ import annotations

from typing import Any

from agentic_core.interfaces.execution import CIDRegistry
from agentic_core.interfaces.spine import (
    AirlockAssembler,
    ExecutionOrchestrator,
    GovernedPayload,
    PathRouter,
    ReEntryLoop,
)
from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningBus
from agentic_core.L2_execution.providers import get_clock
from apps_shared.spine.base_spine_adapter import BaseSpineAdapter
from apps_shared.spine.d0_engine_adapter import D0EngineAdapter
from apps_shared.spine.risk_gate_adapter import RiskGateAdapter
from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

# Default maximum re-entry attempts for the RG spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3


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
        _path_router = PathRouter()
        _clk = get_clock()
        _clk.emit_replay_key(context=f"rg:{self._PREFIX}:init")
        _clk.emit_determinism_digest(inputs={"app": "rg", "prefix": self._PREFIX})
        orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=_path_router,
            d0_engine=D0EngineAdapter(),
            risk_gate=RiskGateAdapter(),
            cid_registry=cid_registry,
            reentry_loop=reentry_loop,
            vigilance_dispatcher=VigilanceDispatcherAdapter(),
            meta_bus=MetaLearningBus(),
        )

        # Initialize base adapter with dependencies and RG prefix
        super().__init__(
            cid_registry=cid_registry,
            orchestrator=orchestrator,
            prefix=self._PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )
