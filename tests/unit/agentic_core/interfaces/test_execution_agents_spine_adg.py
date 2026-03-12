"""ADG-driven tests for agentic_core/interfaces/execution_agents.py and spine.py — fan_in=2.

Contract tests: re-export shim identity and importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestExecutionAgentsShim:
    def test_importable(self):
        import agentic_core.interfaces.execution_agents as mod
        assert mod is not None

    def test_embedding_sovereign_agent_exported(self):
        from agentic_core.interfaces.execution_agents import EmbeddingSovereignAgent
        assert callable(EmbeddingSovereignAgent)

    def test_redis_sovereign_agent_exported(self):
        from agentic_core.interfaces.execution_agents import RedisSovereignAgent
        assert callable(RedisSovereignAgent)

    def test_embedding_identity_matches_canonical(self):
        from agentic_core.interfaces.execution_agents import EmbeddingSovereignAgent as shim
        from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent as canon
        assert shim is canon

    def test_redis_identity_matches_canonical(self):
        from agentic_core.interfaces.execution_agents import RedisSovereignAgent as shim
        from agentic_core.L2_execution.reasoning.RedisSovereignAgent import RedisSovereignAgent as canon
        assert shim is canon


class TestSpineShim:
    def test_importable(self):
        import agentic_core.interfaces.spine as mod
        assert mod is not None

    def test_airlock_assembler_exported(self):
        from agentic_core.interfaces.spine import AirlockAssembler
        assert callable(AirlockAssembler)

    def test_governed_payload_exported(self):
        from agentic_core.interfaces.spine import GovernedPayload
        assert callable(GovernedPayload)

    def test_path_router_exported(self):
        from agentic_core.interfaces.spine import PathRouter
        assert callable(PathRouter)

    def test_execution_orchestrator_exported(self):
        from agentic_core.interfaces.spine import ExecutionOrchestrator
        assert callable(ExecutionOrchestrator)

    def test_reentry_loop_exported(self):
        from agentic_core.interfaces.spine import ReEntryLoop
        assert callable(ReEntryLoop)

    def test_all_list_matches_exports(self):
        from agentic_core.interfaces.spine import __all__
        for name in ("AirlockAssembler", "GovernedPayload", "PathRouter", "ExecutionOrchestrator", "ReEntryLoop"):
            assert name in __all__
