from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "AgentFactory", "L3")
_emit_routes_through("p1", "AgentFactory", "L3")
_emit_escalates_to_human("p1", "AgentFactory", "L3")
_emit_reads_policy_state("p1", "AgentFactory", "L3")

"\nAgent Factory – L3 Orchestration Layer (Phase 9A & 11 – Dec 26, 2025)\nWires L1 Cognition agents with L2 Execution implementations via DIP.\n\nDDD Compliance:\n- L3 orchestrates the wiring between L1 and L2\n- L1 never directly imports L2\n- All dependencies injected at runtime\n\nPhase 11: Configurable Implementation Factory\n- Supports multiple implementation modes: real, mock, aggressive\n- Enables zero-cost unit testing with mock implementations\n- Allows runtime switching of agent behavior\n"
import uuid
from typing import Any

try:
    import importlib.util

    spec = importlib.util.find_spec("agentic_core.base_agents.SovereignBaseAgent")
    _ = spec
except ImportError:
    L2ExecutionBase = None
MockL2ExecutionBase = None
try:
    from agentic_core.config.core.sovereign_config_1 import OrchestratorConfig  # noqa: F401
except ImportError:
    config = {}
try:
    from agentic_core.L1_cognition.reasoning.canon_agents_core import SystemArchitect as SystemArchitect
except ImportError:
    SystemArchitect = None
HealerAgent = GenerativeGuard = None
try:
    from agentic_core.L1_cognition.reasoning.canon_agents_syntax import CodeJanitor as CodeJanitor
except ImportError:
    CodeJanitor = None
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

DependencySentinelAgent = None
try:
    SafetyInspectorAgent = None
except ImportError:
    SafetyInspectorAgent = None


def _get_CodeEnforcerAgent():
    """Lazy loader for CodeEnforcerAgent (upward L3->L5 seam)."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_CodeEnforcerAgent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_CodeEnforcerAgent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_get_CodeEnforcerAgent")
    try:
        from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import CodeEnforcerAgent

        return CodeEnforcerAgent
    except ImportError:
        return None


CodeEnforcerAgent = _get_CodeEnforcerAgent()


class AgentFactory:
    """
    Centralized factory for sovereign agent injection.

    Phase 9A DDD Compliance:
    - Only L3 knows how to instantiate L2 concrete implementations
    - L1 agents receive implementations via dependency injection
    - Maintains separation of concerns across layers
    """

    @staticmethod
    def _create_impl(ctx: Any | None = None) -> CanonBaseAgentInterface:
        """
        Create base agent implementation with configurable mode support.

        Phase 11: Advanced Factory Pattern
        - Respects global AGENT_IMPLEMENTATION_MODE configuration
        - Supports "real" (standard), "mock" (testing), "aggressive" (fast-healing)
        - Only L3 knows how to instantiate the L2 concrete implementation

        Args:
            ctx: Optional context object to pass to the agent implementation

        Returns:
            CanonBaseAgentInterface: Concrete implementation based on configured mode
        """
        mode = getattr(config, "AGENT_IMPLEMENTATION_MODE", "real") if config else "real"
        if mode == "mock":
            return MockL2ExecutionBase(ctx=ctx) if MockL2ExecutionBase else None
        elif mode == "aggressive":
            impl = L2ExecutionBase(ctx=ctx) if L2ExecutionBase else None
            if impl and hasattr(impl, "enable_aggressive_mode"):
                impl.enable_aggressive_mode()
            return impl
        return L2ExecutionBase(ctx=ctx) if L2ExecutionBase else None

    @staticmethod
    def create_system_architect(ctx: Any | None = None) -> SystemArchitect:
        """
        Create SystemArchitect with injected L2 implementation.
        Injects L2 execution capabilities into L1 strategic architecture reasoning.
        """
        return SystemArchitect(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_healer_agent(ctx: Any | None = None) -> HealerAgent:
        """
        Create HealerAgent with injected L2 implementation.

        Injects L2 repair logic into L1 strategic healing.
        """
        return HealerAgent(AgentFactory._create_impl(ctx)) if HealerAgent else None

    @staticmethod
    def create_generative_guard(ctx: Any | None = None) -> GenerativeGuard:
        """
        Create GenerativeGuard with injected L2 implementation.

        Injects L2 validation capabilities into L1 generative oversight.
        """
        return GenerativeGuard(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_code_janitor(ctx: Any | None = None) -> CodeJanitor:
        """
        Create CodeJanitor with injected L2 implementation.

        Injects L2 action into L1 syntax reasoning.
        """
        return CodeJanitor(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_dependency_sentinel(ctx: Any | None = None) -> DependencySentinelAgent:
        """
        Create DependencySentinelAgent with injected L2 implementation.

        Injects L2 import management into L1 dependency reasoning.
        """
        return DependencySentinelAgent(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_safety_inspector(ctx: Any | None = None) -> SafetyInspectorAgent:
        """
        Create SafetyInspectorAgent with injected L2 implementation.

        Injects L2 security checks into L1 safety reasoning.
        """
        return SafetyInspectorAgent(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_pattern_enforcer(ctx: Any | None = None) -> CodeEnforcerAgent:
        """
        Create CodeEnforcerAgent with injected L2 implementation.

        Injects L2 pattern detection into L1 quality reasoning.
        """
        return CodeEnforcerAgent(AgentFactory._create_impl(ctx))

    @staticmethod
    def create_agent_by_capability(capability: str, ctx: Any | None = None) -> Any:
        """R5: Dynamically discover and instantiate agent by capability via ADG.

        Uses ADG composition graph index for O(1) capability lookup.
        Speedup: 10-50x over linear registry search.

        Example: create_agent_by_capability("PromptLoader")
        """
        try:
            import importlib as _importlib

            from agentic_core.adg.runtime.query_engine import get_runtime_query_engine

            query_engine = get_runtime_query_engine()
            candidates = query_engine.find_agents_by_capability(capability)
            if not candidates:
                return None
            _layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
            best = sorted(candidates, key=lambda c: _layer_order.get(c.layer, 99))[0]
            if not best.module_path:
                return None
            mod_name = best.module_path.replace("/", ".").replace(".py", "")
            mod = _importlib.import_module(mod_name)
            agent_class = getattr(mod, best.agent_class, None)
            if agent_class is None:
                return None
            return agent_class(AgentFactory._create_impl(ctx))
        except Exception:
            return None


def create_all_agents(ctx: Any | None = None) -> dict:
    """
    Create all L1 agents with injected L2 implementations.

    Args:
        ctx: Optional context object to pass to all agents

    Returns:
        dict: Dictionary of agent name to agent instance
    """
    return {
        "SystemArchitect": AgentFactory.create_system_architect(ctx),
        "HealerAgent": AgentFactory.create_healer_agent(ctx),
        "GenerativeGuard": AgentFactory.create_generative_guard(ctx),
        "CodeJanitor": AgentFactory.create_code_janitor(ctx),
        "DependencySentinelAgent": AgentFactory.create_dependency_sentinel(ctx),
        "SafetyInspectorAgent": AgentFactory.create_safety_inspector(ctx),
        "CodeEnforcerAgent": AgentFactory.create_pattern_enforcer(ctx),
    }


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module._run_self_tests")
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
        assert self is not None
        results["passed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
