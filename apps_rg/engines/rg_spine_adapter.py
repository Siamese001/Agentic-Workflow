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

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
from apps_shared.utils.determinism_util import canonical_hash, strip_nondeterministic

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


class RgSpineAdapter:
    """
    Canonical RG spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        self._cid_registry = CIDRegistry()
        self._reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=self._cid_registry,
        )
        self._orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=self._cid_registry,
            reentry_loop=self._reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Route a RG intent through the canonical spine.

        Steps:
          1) Strip nondeterministic fields from intent_input.
          2) Derive deterministic CID via canonical hash.
          3) Pre-register CID in CIDRegistry before any HOP stage runs.
          4) Inject cid into intent_input so downstream stages can read it.
          5) Delegate to ExecutionOrchestrator.execute().
          6) Return result dict augmented with cid.

        Args:
            intent_input: Dict with RG slot keys (s0_system, i0_instructional,
                          c0_context, u0_user_prompt, d0_injections).

        Returns:
            Result dict from ExecutionOrchestrator plus ``cid`` key.
        """
        # Step 1: Strip nondeterministic fields from intent_input.
        stripped = strip_nondeterministic(intent_input)

        # Step 2: Derive deterministic CID via canonical hash.
        cid = "rg-" + canonical_hash(stripped)[:16]

        # Step 3: Pre-register CID before any HOP stage runs.
        cycle: ExecutionCycle = self._cid_registry.new_cycle(cid)

        # Step 4: Thread cid into intent_input for downstream visibility.
        enriched = dict(intent_input)
        enriched["_cid"] = cid
        enriched["_cycle_attempt"] = cycle.attempt

        # Step 5: Delegate to orchestrator (it will re-assemble internally).
        result = self._orchestrator.execute(enriched)

        # Step 6: Augment result with cid.
        result["cid"] = cid
        return result
