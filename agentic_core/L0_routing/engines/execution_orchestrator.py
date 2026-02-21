"""
L0→L2 Execution Orchestrator - Deterministic Layer Binding

Binds Assembly Stage, PathRouter, D0InjectionEngine, ConfCalibRiskGate,
CIDRegistry, ReEntryLoop, MetaLearningBus, and VigilanceDispatcher.
Remains deterministic, side-effect minimal, uses injected seams only.
"""

from typing import Any


class ExecutionOrchestrator:
    """
    Deterministic execution orchestrator binding all layers.

    Uses injected seams only, no direct dependencies.
    No wall-clock usage, no side effects beyond injected functions.
    """

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
        """
        self.assembler = assembler
        self.path_router = path_router
        self.d0_engine = d0_engine
        self.risk_gate = risk_gate
        self.cid_registry = cid_registry
        self.reentry_loop = reentry_loop
        self.vigilance_dispatcher = vigilance_dispatcher
        self.meta_bus = meta_bus

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
        7) Return structured result dict

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

        # 7) Return successful execution state
        return {"path": path, "risk": risk, "cycle": cycle, "state": "success"}
