"""P2 tests: D2 feature-flag / kill-switch / fail-closed behaviour.

SEMANTIC_CACHE_D2_ENABLED controls two gates:
    Gate A — SemanticCacheManager._init_gptcache()   (L2 initialisation)
    Gate B — ExecutionOrchestrator.execute()          (D2 recall hot path)

Default "0" = fail-closed (production-safe).
Set "1"     = enabled     (non-production opt-in).
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Gate A: SemanticCacheManager._init_gptcache()
# ---------------------------------------------------------------------------


def _make_scm_fresh():
    """Return a new (uninitialised) SemanticCacheManager bypassing the singleton."""
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    return object.__new__(SemanticCacheManager)


def test_gate_a_flag_off_gptcache_disabled() -> None:
    """Flag=0 (default): _init_gptcache() must leave gptcache_enabled=False."""
    scm = _make_scm_fresh()
    scm.gptcache_enabled = False
    scm.similarity_threshold = 0.98
    with patch.dict(os.environ, {"SEMANTIC_CACHE_D2_ENABLED": "0"}):
        result = scm._init_gptcache()
    assert scm.gptcache_enabled is False
    assert isinstance(result, ValueError)


def test_gate_a_flag_unset_gptcache_disabled() -> None:
    """Flag absent (default): _init_gptcache() must leave gptcache_enabled=False."""
    scm = _make_scm_fresh()
    scm.gptcache_enabled = False
    scm.similarity_threshold = 0.98
    env = {k: v for k, v in os.environ.items() if k != "SEMANTIC_CACHE_D2_ENABLED"}
    with patch.dict(os.environ, env, clear=True):
        result = scm._init_gptcache()
    assert scm.gptcache_enabled is False
    assert isinstance(result, ValueError)


def test_gate_a_flag_on_attempts_init() -> None:
    """Flag=1: _init_gptcache() must attempt real initialisation."""
    from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient

    scm = _make_scm_fresh()
    scm.gptcache_enabled = False
    scm.similarity_threshold = 0.98

    mock_client = MagicMock(spec=NativePersistentCacheClient)
    mock_client._cache = "real"  # not "mock" — simulate ChromaDB present

    with patch.dict(os.environ, {"SEMANTIC_CACHE_D2_ENABLED": "1"}):
        with patch(
            "agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient",
            return_value=mock_client,
        ):
            with patch(
                "agentic_core.L4_state.utils.memory.semantic_cache_manager._get_model_id",
                return_value="bge-m3-v1",
            ):
                result = scm._init_gptcache()

    assert scm.gptcache_enabled is True
    assert result is None


# ---------------------------------------------------------------------------
# Gate B: ExecutionOrchestrator.execute() D2 gate
# ---------------------------------------------------------------------------


def _minimal_orchestrator():
    """Return the smallest usable ExecutionOrchestrator (deps mocked out)."""
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

    orch = object.__new__(ExecutionOrchestrator)

    risk = MagicMock()
    risk.allow = True

    orch.routing_engine = MagicMock()
    orch.d0_engine = MagicMock()
    orch.d0_engine.render_d0.return_value = {}
    orch.risk_gate = MagicMock()
    orch.risk_gate.evaluate.return_value = risk
    orch.cid_registry = MagicMock()
    orch.cid_registry.new_cycle.return_value = "cycle-1"
    orch.reentry_loop = MagicMock()
    orch._L3_PATHS = frozenset()

    return orch


def test_gate_b_flag_off_skipped_in_source() -> None:
    """Flag=0 (default): orchestrator execute() source must guard D2 gate on SEMANTIC_CACHE_D2_ENABLED."""
    import inspect
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

    src = inspect.getsource(ExecutionOrchestrator.execute)
    assert "SEMANTIC_CACHE_D2_ENABLED" in src, "Gate B: flag var missing from orchestrator execute()"
    assert '== "1"' in src, "Gate B: flag must check for explicit '1' — fail-closed default"


def test_gate_b_flag_on_d2_path_in_source() -> None:
    """Flag=1 path: orchestrator must call SemanticCacheManager.recall() when gate passes."""
    import inspect
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

    src = inspect.getsource(ExecutionOrchestrator.execute)
    assert "SemanticCacheManager" in src, "Gate B: SCM import missing from execute()"
    assert ".recall(" in src, "Gate B: recall() call missing from execute()"
    assert "flow_class" in src, "Gate B: flow_class not threaded to recall()"
    assert "replay_mode" in src, "Gate B: replay_mode not threaded to recall()"


def test_gate_b_hit_short_circuits_in_source() -> None:
    """Cache hit must short-circuit to d2_cache_hit state."""
    import inspect
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

    src = inspect.getsource(ExecutionOrchestrator.execute)
    assert "d2_cache_hit" in src, "Gate B: d2_cache_hit short-circuit state missing"


def test_kill_switch_env_var_documented_in_source() -> None:
    """SEMANTIC_CACHE_D2_ENABLED must appear in both SCM and orchestrator source."""
    import inspect
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    scm_src = inspect.getsource(SemanticCacheManager._init_gptcache)
    orch_src = inspect.getsource(ExecutionOrchestrator.execute)

    assert "SEMANTIC_CACHE_D2_ENABLED" in scm_src, "Kill-switch var missing from SCM _init_gptcache()"
    assert "SEMANTIC_CACHE_D2_ENABLED" in orch_src, (
        "Kill-switch var missing from ExecutionOrchestrator.execute()"
    )
