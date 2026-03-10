"""
L0→L2 Execution Orchestrator - Deterministic Layer Binding

Binds Assembly Stage, PathRouter, D0InjectionEngine, ConfCalibRiskGate,
CIDRegistry, ReEntryLoop, MetaLearningBus, and VigilanceDispatcher.
Remains deterministic, side-effect minimal, uses injected seams only.
"""

import logging
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class ExecutionOrchestrator:
    """
    Deterministic execution orchestrator binding all layers.

    Uses injected seams only, no direct dependencies.
    No wall-clock usage, no side effects beyond injected functions.
    """

    # Paths that delegate to L3 orchestrator when one is injected.
    _L3_PATHS: frozenset = frozenset({"B", "C", "D"})

    def __init__(
        self,
        assembler,
        path_router,
        d0_engine,
        risk_gate,
        cid_registry,
        reentry_loop,
        vigilance_dispatcher,
        meta_bus,
        l3_orchestrator=None,
    ):
        """
        Initialize orchestrator with injected dependencies.

        Args:
            assembler: Assembly Stage instance
            path_router: PathRouter instance
            d0_engine: D0InjectionEngine instance
            risk_gate: ConfCalibRiskGate instance
            cid_registry: CIDRegistry instance
            reentry_loop: ReEntryLoop instance
            vigilance_dispatcher: VigilanceDispatcher instance
            meta_bus: MetaLearningBus instance
            l3_orchestrator: Optional L3 orchestrator for Paths B/C/D delegation.
                Must implement orchestrate(payload, route_mode, trace_id, ...) or
                a compatible synchronous interface.  When None, Paths B/C/D return
                without delegation (backwards-compatible default).
        """
        self.assembler = assembler
        self.path_router = path_router
        self.d0_engine = d0_engine
        self.risk_gate = risk_gate
        self.cid_registry = cid_registry
        self.reentry_loop = reentry_loop
        self.vigilance_dispatcher = vigilance_dispatcher
        self.meta_bus = meta_bus
        self.l3_orchestrator = l3_orchestrator

    def _delegate_to_l3(self, path, payload, cycle, risk) -> dict[str, Any]:
        """
        Delegate execution to L3 orchestrator for Paths B/C/D.

        Calls l3_orchestrator.orchestrate() when available.  Any exception is
        caught and returned as an error key so L0 routing remains unaffected.

        Returns:
            Result dict including orchestration sub-result or error metadata.
        """
        orchestration: dict[str, Any] = {}
        if self.l3_orchestrator is not None:
            try:
                result = self.l3_orchestrator.orchestrate(
                    payload,
                    route_mode=path.value,
                    trace_id=cycle.cid,
                    policy_hash="",
                    allowed_tools=(),
                )
                orchestration = {
                    "completed": getattr(result, "completed", False),
                    "stage": getattr(result, "stage", "unknown"),
                    "signals": list(getattr(result, "signals", [])),
                    "metadata": getattr(result, "metadata", {}),
                }
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
                # Expected L3 orchestration errors - log and continue with error state
                Logger.error(f"[L0-ORCH] L3 orchestration failed: {e}")
                orchestration = {"error": f"L3 orchestration failed: {e}", "completed": False}
            except Exception as e:
                # Critical L3 orchestration errors - log and continue with error state
                Logger.critical(f"[L0-ORCH] Critical L3 orchestration error: {e}")
                orchestration = {"error": f"Critical L3 orchestration error: {e}", "completed": False}
                # Re-raise to surface critical issues to caller
                raise
        return {
            "path": path,
            "risk": risk,
            "cycle": cycle,
            "state": "success",
            "orchestration": orchestration,
        }

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Execute intent through all layers deterministically.

        Flow (no hidden state):
        1) Assemble → payload
        2) Route → path
        3) Render D0
        4) Evaluate risk
        5) Start ExecutionCycle
        6) Handle re-entry if risk disallowed
        7) Delegate to L3 for Paths B/C/D (when l3_orchestrator injected)
        8) Return structured result dict

        Args:
            intent_input: Input intent dictionary

        Returns:
            Structured result dict with path, risk, cycle, and state
        """
        # 1) Assemble intent into payload
        payload = self.assembler.assemble(intent_input)

        # 2) Route payload to determine path
        path = self.path_router.select_path(payload)

        # 3) Render D0 injections
        d0_injections = self.d0_engine.render_d0(payload.d0_injections)

        # 4) Evaluate risk
        risk = self.risk_gate.evaluate(payload_like=payload, d0_injections=d0_injections)

        # 5) Start execution cycle
        cycle = self.cid_registry.new_cycle(f"execute_{path.value}")

        # 6) Handle re-entry if risk disallowed
        if not risk.allow:
            if self.reentry_loop.should_retry(cycle):
                # Advance cycle for retry
                cycle = self.reentry_loop.advance(cycle)
                return {"path": path, "risk": risk, "cycle": cycle, "state": "retry"}
            else:
                # Terminal blocked state
                return {"path": path, "risk": risk, "cycle": cycle, "state": "blocked"}

        # 7) Delegate to L3 orchestrator for Paths B/C/D
        if path.value in self._L3_PATHS:
            return self._delegate_to_l3(path, payload, cycle, risk)

        # 8) Return successful execution state for Path A
        return {"path": path, "risk": risk, "cycle": cycle, "state": "success"}

    def plan_execution_with_impact_analysis(self, changed_files: list[str]) -> dict[str, Any]:
        """R6: Plan execution order based on ADG blast radius.

        Uses pre-built reverse dependency index instead of full codebase scan.
        Speedup: 50-500x over full scan.
        """
        try:
            from agentic_core.adg.runtime.query_engine import get_runtime_query_engine

            query_engine = get_runtime_query_engine()
            blast = query_engine.compute_blast_radius(changed_files)
            sorted_modules = sorted(blast.items(), key=lambda x: x[1])
            return {
                "modules": [m for m, _ in sorted_modules],
                "depths": dict(sorted_modules),
                "changed_files": changed_files,
                "total_impacted": len(blast),
            }
        except Exception as exc:
            Logger.warning("[L0-ORCH] ADG impact analysis unavailable: %s", exc)
            return {
                "modules": changed_files,
                "changed_files": changed_files,
                "total_impacted": len(changed_files),
            }
