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

    mock_path = MagicMock()
    mock_path.value = "D"
    orch.assembler = MagicMock()
    orch.assembler.assemble.return_value = MagicMock(d0_injections={})
    orch.path_router = MagicMock()
    orch.path_router.select_path.return_value = mock_path
    orch.d0_engine = MagicMock()
    orch.d0_engine.render_d0.return_value = {}
    orch.risk_gate = MagicMock()
    orch.risk_gate.evaluate.return_value = risk
    orch.cid_registry = MagicMock()
    orch.cid_registry.new_cycle.return_value = "cycle-1"
    orch.reentry_loop = MagicMock()
    orch._L3_PATHS = frozenset()

    return orch


_EO_MOD = "agentic_core.L0_routing.reasoning.execution_orchestrator"
_TRACE_MOD = "agentic_core.runtime.types.execution_trace"
_SCM_MOD = "agentic_core.L4_state.utils.memory.semantic_cache_manager"


def _run_orch_execute(orch, intent_input: dict, env: dict):
    """Run orchestrator.execute() with all infrastructure patches applied."""
    with patch.dict(os.environ, env):
        with patch(f"{_EO_MOD}._emit_signs_execution_trace"):
            with patch(f"{_EO_MOD}._emit_records_execution_trace"):
                with patch(f"{_EO_MOD}.emit_replay_key"):
                    with patch(f"{_EO_MOD}.emit_determinism_digest"):
                        with patch(f"{_EO_MOD}._get_routing_gateway"):
                            with patch(f"{_EO_MOD}.ProposalCommitter"):
                                with patch(f"{_EO_MOD}.create_and_commit_routing_contract"):
                                    with patch(
                                        f"{_TRACE_MOD}.get_active_execution_trace",
                                        return_value=None,
                                    ):
                                        return orch.execute(intent_input)


def test_gate_b_runtime_flag_off_scm_not_called() -> None:
    """Gate B runtime: SEMANTIC_CACHE_D2_ENABLED=0 → SCM.recall() never called on Path D."""
    orch = _minimal_orchestrator()
    mock_scm_instance = MagicMock()

    with patch(f"{_SCM_MOD}.SemanticCacheManager.get_instance", return_value=mock_scm_instance):
        result = _run_orch_execute(orch, {"intent": "test"}, {"SEMANTIC_CACHE_D2_ENABLED": "0"})

    mock_scm_instance.recall.assert_not_called()
    assert result.get("state") == "success", f"expected success state, got {result}"


def test_gate_b_runtime_flag_on_path_d_calls_scm() -> None:
    """Gate B runtime: SEMANTIC_CACHE_D2_ENABLED=1 + Path D → SCM.recall() called; hit short-circuits."""
    orch = _minimal_orchestrator()
    hit_payload = {"answer": "cached", "_metadata": {"namespace": "default"}}
    mock_scm_instance = MagicMock()
    mock_scm_instance.recall.return_value = hit_payload

    with patch(f"{_SCM_MOD}.SemanticCacheManager.get_instance", return_value=mock_scm_instance):
        result = _run_orch_execute(orch, {"intent": "test"}, {"SEMANTIC_CACHE_D2_ENABLED": "1"})

    mock_scm_instance.recall.assert_called_once()
    assert result.get("state") == "d2_cache_hit", f"expected d2_cache_hit, got {result}"
    assert result.get("result") is hit_payload


def test_gate_b_runtime_flag_on_non_d_path_scm_not_called() -> None:
    """Gate B edge: SEMANTIC_CACHE_D2_ENABLED=1 + non-D path → SCM.recall() NOT called."""
    orch = _minimal_orchestrator()
    orch.path_router.select_path.return_value.value = "A"
    mock_scm_instance = MagicMock()

    with patch(f"{_SCM_MOD}.SemanticCacheManager.get_instance", return_value=mock_scm_instance):
        result = _run_orch_execute(orch, {"intent": "test"}, {"SEMANTIC_CACHE_D2_ENABLED": "1"})

    mock_scm_instance.recall.assert_not_called()
    assert result.get("state") == "success", f"expected success for non-D path, got {result}"


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
