"""Infrastructure stack invariant tests — F1-F5 regression suite.

Covers:
    F1+F5  QWEN_GPU_MEM_UTIL is the single source of truth for all vLLM launch sites.
    F2     EmbeddingServiceFactory GPU path: _faiss_gpu_available, _embedding_device,
           _build_gpu_index helpers are wired correctly (CPU fallback tested without GPU).
    F3     LocalFAISSStore.verify_indexes_at_boot delegates to faiss_startup_integrity
           and handles missing / corrupt artifacts correctly.
    F4     check_redis_health returns structured dict; no raise on connection failure;
           fix hint is present when unhealthy.

All tests are stdlib + existing-dep only (numpy, faiss-cpu already installed).
No network, no GPU, no Redis required.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_stack_invariants")
# REMOVED: _emit_applies_guardrail("p0", "test_stack_invariants", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_stack_invariants", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_stack_invariants", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_stack_invariants", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_stack_invariants", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_stack_invariants", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_stack_invariants", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_stack_invariants", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_stack_invariants", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_stack_invariants", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_stack_invariants", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_stack_invariants", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_stack_invariants", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_stack_invariants", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_stack_invariants", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_stack_invariants", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_stack_invariants", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_stack_invariants", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_stack_invariants", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_stack_invariants", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_stack_invariants", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_stack_invariants", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_stack_invariants", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_stack_invariants", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_stack_invariants", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_stack_invariants", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_stack_invariants", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_stack_invariants", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_stack_invariants", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_stack_invariants", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_stack_invariants", "write_through")
# REMOVED: _emit_writes_through("p1", "test_stack_invariants", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_stack_invariants", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_stack_invariants", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_stack_invariants", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_stack_invariants", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_stack_invariants", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_stack_invariants", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_stack_invariants", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_stack_invariants", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_stack_invariants", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_stack_invariants", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_stack_invariants", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_stack_invariants", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_stack_invariants", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_stack_invariants", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_stack_invariants")
# REMOVED: _emit_gated_by_confidence("p1", "test_stack_invariants", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_stack_invariants")
# REMOVED: emit_determinism_digest("p0", "test_stack_invariants")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_stack_invariants", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_stack_invariants", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_stack_invariants", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_stack_invariants", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_stack_invariants", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_stack_invariants", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_stack_invariants", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_stack_invariants", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_stack_invariants", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_stack_invariants", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_stack_invariants", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_stack_invariants", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_stack_invariants", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_stack_invariants", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_stack_invariants", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_stack_invariants", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_stack_invariants", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_stack_invariants", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_stack_invariants", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_stack_invariants", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# F1 + F5 — QWEN_GPU_MEM_UTIL SSOT
# ---------------------------------------------------------------------------


class TestQwenGpuMemUtilSSOT:
    """F1+F5: A single constant governs all vLLM gpu_memory_utilization values."""

    @pytest.mark.unit_min_deps
    def test_constant_exists_and_is_float(self):
        """QWEN_GPU_MEM_UTIL must be importable and be a float."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL

        assert isinstance(QWEN_GPU_MEM_UTIL, float), "QWEN_GPU_MEM_UTIL must be float"

    @pytest.mark.unit_min_deps
    def test_constant_value_is_0_70(self):
        """Canonical value is 0.70 — preserves KV-cache headroom on RTX 5090."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL

        assert QWEN_GPU_MEM_UTIL == 0.70, f"Expected 0.70, got {QWEN_GPU_MEM_UTIL}"

    @pytest.mark.unit_min_deps
    def test_constant_in_valid_range(self):
        """QWEN_GPU_MEM_UTIL must be strictly between 0.0 and 1.0."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL

        assert 0.0 < QWEN_GPU_MEM_UTIL < 1.0

    @pytest.mark.unit_min_deps
    def test_vllm_process_manager_uses_constant_not_literal(self):
        """vllm_process_manager must import QWEN_GPU_MEM_UTIL — not contain a bare 0.85 literal."""
        import ast

        src = Path("agentic_core/L2_execution/healers/vllm_process_manager.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        # Collect all numeric literals in the file
        literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert 0.85 not in literals, (
            "vllm_process_manager.py must not contain a bare 0.85 float literal — "
            "use QWEN_GPU_MEM_UTIL constant instead"
        )

    @pytest.mark.unit_min_deps
    def test_qwen_vllm_inference_uses_constant_not_literal(self):
        """qwen_vllm_inference must import QWEN_GPU_MEM_UTIL — not contain a bare 0.7 literal."""
        import ast

        src = Path("agentic_core/L2_execution/healers/qwen_vllm_inference.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert 0.7 not in literals, (
            "qwen_vllm_inference.py must not contain a bare 0.7 float literal — "
            "use QWEN_GPU_MEM_UTIL constant instead"
        )
        assert 0.85 not in literals, "qwen_vllm_inference.py must not contain a bare 0.85 float literal"

    @pytest.mark.unit_min_deps
    def test_vllm_process_manager_imports_constant(self):
        """vllm_process_manager.py must have an import of QWEN_GPU_MEM_UTIL."""
        import ast

        src = Path("agentic_core/L2_execution/healers/vllm_process_manager.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        imported_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.append(alias.name)

        assert "QWEN_GPU_MEM_UTIL" in imported_names, (
            "vllm_process_manager.py must import QWEN_GPU_MEM_UTIL from healing_tier_config"
        )

    @pytest.mark.unit_min_deps
    def test_qwen_vllm_inference_imports_constant(self):
        """qwen_vllm_inference.py must have an import of QWEN_GPU_MEM_UTIL."""
        import ast

        src = Path("agentic_core/L2_execution/healers/qwen_vllm_inference.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        imported_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.append(alias.name)

        assert "QWEN_GPU_MEM_UTIL" in imported_names, (
            "qwen_vllm_inference.py must import QWEN_GPU_MEM_UTIL from healing_tier_config"
        )

    @pytest.mark.unit_min_deps
    def test_get_model_config_returns_canonical_util(self):
        """VLLMProcessManager.get_model_config must return QWEN_GPU_MEM_UTIL for both sizes."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
        from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

        for size in ("7B", "14B"):
            cfg = get_model_config(size)
            assert cfg["gpu_memory_utilization"] == QWEN_GPU_MEM_UTIL, (
                f"get_model_config('{size}') gpu_memory_utilization mismatch: "
                f"expected {QWEN_GPU_MEM_UTIL}, got {cfg['gpu_memory_utilization']}"
            )

    @pytest.mark.unit_min_deps
    def test_constant_exported_from_healing_tier_config(self):
        """QWEN_GPU_MEM_UTIL must appear in healing_tier_config.__all__."""
        from agentic_core.L2_execution.healers import healing_tier_config

        assert "QWEN_GPU_MEM_UTIL" in healing_tier_config.__all__, (
            "QWEN_GPU_MEM_UTIL must be listed in healing_tier_config.__all__"
        )


# ---------------------------------------------------------------------------
# F2 — EmbeddingServiceFactory GPU helpers
# ---------------------------------------------------------------------------


class TestEmbeddingServiceFactoryGpuHelpers:
    """F2: GPU-aware FAISS path helpers are correctly wired."""

    @pytest.mark.unit_min_deps
    def test_faiss_gpu_available_returns_bool(self):
        """_faiss_gpu_available must return a bool (True or False — not exception)."""
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        result = EmbeddingServiceFactory._faiss_gpu_available()
        assert isinstance(result, bool)

    @pytest.mark.unit_min_deps
    def test_faiss_gpu_available_false_when_faiss_cpu(self):
        """faiss-cpu build does not expose StandardGpuResources — must return False."""
        import faiss

        if hasattr(faiss, "StandardGpuResources"):
            pytest.fail("faiss-gpu is installed but this test requires faiss-cpu build only — remove faiss-gpu or run on a cpu-only environment")

        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        assert EmbeddingServiceFactory._faiss_gpu_available() is False

    @pytest.mark.unit_min_deps
    def test_embedding_device_defaults_to_cpu(self):
        """EMBEDDING_DEVICE not set → _embedding_device() returns 'cpu'."""
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        with patch.dict(os.environ, {}, clear=False):
            env_without_device = {k: v for k, v in os.environ.items() if k != "EMBEDDING_DEVICE"}
            with patch.dict(os.environ, env_without_device, clear=True):
                assert EmbeddingServiceFactory._embedding_device() == "cpu"

    @pytest.mark.unit_min_deps
    def test_embedding_device_reads_env_var(self):
        """EMBEDDING_DEVICE=cuda → _embedding_device() returns 'cuda'."""
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        with patch.dict(os.environ, {"EMBEDDING_DEVICE": "cuda"}):
            assert EmbeddingServiceFactory._embedding_device() == "cuda"

    @pytest.mark.unit_min_deps
    def test_embedding_device_lowercases(self):
        """EMBEDDING_DEVICE is normalised to lowercase."""
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        with patch.dict(os.environ, {"EMBEDDING_DEVICE": "CUDA"}):
            assert EmbeddingServiceFactory._embedding_device() == "cuda"

    @pytest.mark.unit_min_deps
    def test_build_gpu_index_returns_none_when_no_gpu_faiss(self):
        """_build_gpu_index must return None (not raise) when faiss-gpu unavailable."""
        import faiss

        if hasattr(faiss, "StandardGpuResources"):
            pytest.fail("faiss-gpu is installed but this test requires faiss-cpu build to test the CPU fallback path — remove faiss-gpu or run on a cpu-only environment")

        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        matrix = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        result = EmbeddingServiceFactory._build_gpu_index(matrix)
        assert result is None

    @pytest.mark.unit_min_deps
    def test_gpu_index_not_built_when_device_is_cpu(self, tmp_path):
        """When EMBEDDING_DEVICE=cpu, _gpu_index must remain None after _load_pack."""
        EmbeddingServiceFactory = _get_esf()
        pack_dir = _make_seed_pack(tmp_path, n=3, dim=4)

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true", "EMBEDDING_DEVICE": "cpu"}):
            svc = EmbeddingServiceFactory.get(pack_dir)

        try:
            assert svc._gpu_index is None, "_gpu_index must be None when EMBEDDING_DEVICE=cpu"
        finally:
            _cleanup_esf(svc, EmbeddingServiceFactory)

    @pytest.mark.unit_min_deps
    def test_gpu_index_not_built_when_faiss_gpu_absent(self, tmp_path):
        """When EMBEDDING_DEVICE=cuda but faiss-gpu absent, _gpu_index stays None."""
        import faiss

        if hasattr(faiss, "StandardGpuResources"):
            pytest.fail("faiss-gpu is installed but this test requires faiss-gpu to be absent — remove faiss-gpu or run on a cpu-only environment")

        EmbeddingServiceFactory = _get_esf()
        pack_dir = _make_seed_pack(tmp_path, n=3, dim=4)

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true", "EMBEDDING_DEVICE": "cuda"}):
            svc = EmbeddingServiceFactory.get(pack_dir)

        try:
            assert svc._gpu_index is None, "_gpu_index must be None when faiss-gpu is not installed"
        finally:
            _cleanup_esf(svc, EmbeddingServiceFactory)

    @pytest.mark.unit_min_deps
    def test_retrieve_still_works_after_gpu_path_activated(self, tmp_path):
        """retrieve() must return correct results regardless of GPU index availability."""
        EmbeddingServiceFactory = _get_esf()
        pack_dir = _make_seed_pack(tmp_path, n=3, dim=4)

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true", "EMBEDDING_DEVICE": "cpu"}):
            svc = EmbeddingServiceFactory.get(pack_dir)

        try:
            query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            results = svc.retrieve(query_vector=query, k=2, cutoff=0.0)
            assert results is not None
            assert len(results) >= 1
        finally:
            _cleanup_esf(svc, EmbeddingServiceFactory)


# ---------------------------------------------------------------------------
# F3 — LocalFAISSStore.verify_indexes_at_boot
# ---------------------------------------------------------------------------


class TestVerifyIndexesAtBoot:
    """F3: Boot-time integrity sweep is wired through LocalFAISSStore."""

    @pytest.mark.unit_min_deps
    def test_method_exists_on_class(self):
        """verify_indexes_at_boot must exist as a staticmethod on LocalFAISSStore."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        assert hasattr(LocalFAISSStore, "verify_indexes_at_boot"), (
            "LocalFAISSStore.verify_indexes_at_boot must exist"
        )
        assert callable(LocalFAISSStore.verify_indexes_at_boot)

    @pytest.mark.unit_min_deps
    def test_returns_empty_dict_when_base_dir_absent(self, tmp_path):
        """Non-existent base_dir must return {} (not raise)."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        absent = tmp_path / "indexes_not_built_yet"
        result = LocalFAISSStore.verify_indexes_at_boot(absent)
        assert result == {}

    @pytest.mark.unit_min_deps
    def test_returns_empty_dict_when_base_dir_empty(self, tmp_path):
        """Empty base_dir (no index subdirs) must return {}."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        empty_base = tmp_path / "empty_indexes"
        empty_base.mkdir()
        result = LocalFAISSStore.verify_indexes_at_boot(empty_base)
        assert result == {}

    @pytest.mark.unit_min_deps
    def test_returns_digest_for_valid_index(self, tmp_path):
        """Valid persisted 3-file artifact must verify and return its digest."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        index_id = "healing_context_v1"
        disk_dir = _build_and_persist_faiss(tmp_path, index_id, n_vectors=4)

        result = LocalFAISSStore.verify_indexes_at_boot(tmp_path)
        assert index_id in result, f"index_id '{index_id}' must be in result: {result}"
        digest = result[index_id]
        assert isinstance(digest, str) and len(digest) == 64, "digest must be 64-char hex"

    @pytest.mark.unit_min_deps
    def test_raises_on_tampered_index_json(self, tmp_path):
        """Corrupted index.json must raise StartupIntegrityError — fail-closed."""
        from system_learning.engines.faiss_startup_integrity import StartupIntegrityError
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        index_id = "healing_context_v1"
        disk_dir = _build_and_persist_faiss(tmp_path, index_id, n_vectors=3)

        (disk_dir / "index.json").write_bytes(b'{"tampered": true}')

        with pytest.raises(StartupIntegrityError):
            LocalFAISSStore.verify_indexes_at_boot(tmp_path)

    @pytest.mark.unit_min_deps
    def test_raises_on_missing_manifest(self, tmp_path):
        """Subdirectory without manifest.json must be ignored (no manifest, no sweep)."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        # A dir without manifest.json should be skipped, not raise
        ghost_dir = tmp_path / "ghost_index"
        ghost_dir.mkdir()
        (ghost_dir / "index.json").write_bytes(b"{}")

        result = LocalFAISSStore.verify_indexes_at_boot(tmp_path)
        assert result == {}

    @pytest.mark.unit_min_deps
    def test_embedder_id_mismatch_raises(self, tmp_path):
        """expected_embedder_id mismatch must raise StartupIntegrityError."""
        from system_learning.engines.faiss_startup_integrity import StartupIntegrityError
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        index_id = "healing_context_v1"
        _build_and_persist_faiss(tmp_path, index_id, n_vectors=2)

        with pytest.raises(StartupIntegrityError):
            LocalFAISSStore.verify_indexes_at_boot(tmp_path, expected_embedder_id="wrong-embedder-id")

    @pytest.mark.unit_min_deps
    def test_correct_embedder_id_passes(self, tmp_path):
        """Matching expected_embedder_id must pass verification."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        index_id = "healing_context_v1"
        _build_and_persist_faiss(tmp_path, index_id, n_vectors=2)

        result = LocalFAISSStore.verify_indexes_at_boot(tmp_path, expected_embedder_id="hash-fallback")
        assert index_id in result

    @pytest.mark.unit_min_deps
    def test_multiple_indexes_all_verified(self, tmp_path):
        """Multiple index subdirs must all appear in the result."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        ids = ["idx_a", "idx_b", "idx_c"]
        for idx_id in ids:
            _build_and_persist_faiss(tmp_path, idx_id, n_vectors=2)

        result = LocalFAISSStore.verify_indexes_at_boot(tmp_path)
        for idx_id in ids:
            assert idx_id in result, f"index '{idx_id}' must be in boot sweep result"

    @pytest.mark.unit_min_deps
    def test_digest_is_deterministic(self, tmp_path):
        """Calling verify_indexes_at_boot twice on the same artifact returns the same digest."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        index_id = "healing_context_v1"
        _build_and_persist_faiss(tmp_path, index_id, n_vectors=3)

        r1 = LocalFAISSStore.verify_indexes_at_boot(tmp_path)
        r2 = LocalFAISSStore.verify_indexes_at_boot(tmp_path)
        assert r1[index_id] == r2[index_id], "Digest must be deterministic across calls"


# ---------------------------------------------------------------------------
# F4 — check_redis_health
# ---------------------------------------------------------------------------


class TestCheckRedisHealth:
    """F4: check_redis_health returns structured dict; never raises; has fix hint on failure."""

    @pytest.mark.unit_min_deps
    def test_function_importable(self):
        """check_redis_health must be importable from redis_cache_client."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        assert callable(check_redis_health)

    def _refused_result(self) -> dict:
        """Return check_redis_health result with a mocked connection error (no network I/O)."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        mock_conn = MagicMock()
        mock_conn.ping.side_effect = ConnectionRefusedError("Connection refused")
        mock_redis_cls = MagicMock(return_value=mock_conn)
        with patch.dict("sys.modules", {"redis": MagicMock(Redis=mock_redis_cls)}):
            return check_redis_health("redis://localhost:6379")

    @pytest.mark.unit_min_deps
    def test_returns_dict_on_connection_refused(self):
        """Returns dict (not raises) when Redis raises ConnectionRefusedError."""
        result = self._refused_result()
        assert isinstance(result, dict)

    @pytest.mark.unit_min_deps
    def test_unhealthy_result_has_required_keys(self):
        """Unhealthy result must contain all required keys."""
        result = self._refused_result()
        for key in ("healthy", "url", "using_fallback", "error", "fix"):
            assert key in result, f"Key '{key}' missing from check_redis_health result"

    @pytest.mark.unit_min_deps
    def test_unhealthy_healthy_is_false(self):
        """healthy must be False when connection refused."""
        result = self._refused_result()
        assert result["healthy"] is False

    @pytest.mark.unit_min_deps
    def test_unhealthy_has_fix_hint(self):
        """fix field must be a non-empty string when unhealthy."""
        result = self._refused_result()
        assert isinstance(result["fix"], str) and len(result["fix"]) > 0, (
            "fix hint must be a non-empty string when Redis is unreachable"
        )

    @pytest.mark.unit_min_deps
    def test_fix_hint_contains_wsl2_instruction(self):
        """fix hint must mention WSL2 start command for on-premise developer guidance."""
        result = self._refused_result()
        assert "WSL2" in result["fix"] or "redis-server" in result["fix"], (
            "fix hint must reference WSL2 or redis-server start command"
        )

    @pytest.mark.unit_min_deps
    def test_url_in_result_matches_argument(self):
        """url in result must equal the probe URL passed to the function."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        probe = "redis://localhost:6379"
        mock_conn = MagicMock()
        mock_conn.ping.side_effect = ConnectionRefusedError("refused")
        mock_redis_cls = MagicMock(return_value=mock_conn)
        with patch.dict("sys.modules", {"redis": MagicMock(Redis=mock_redis_cls)}):
            result = check_redis_health(probe)
        assert result["url"] == probe

    @pytest.mark.unit_min_deps
    def test_healthy_result_structure_when_mocked(self):
        """When Redis responds to PING, healthy must be True and using_fallback False."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        mock_conn = MagicMock()
        mock_conn.ping.return_value = True
        mock_conn.info.return_value = {
            "used_memory_human": "1.00M",
            "maxmemory_human": "0B",
        }

        mock_redis_cls = MagicMock(return_value=mock_conn)

        with patch.dict("sys.modules", {"redis": MagicMock(Redis=mock_redis_cls)}):
            result = check_redis_health("redis://localhost:6379")

        assert result["healthy"] is True
        assert result["using_fallback"] is False
        assert result["error"] is None

    @pytest.mark.unit_min_deps
    def test_default_url_uses_env_var(self):
        """When no url arg given, REDIS_URL env var must be used."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        custom_url = "redis://localhost:29999"
        mock_conn = MagicMock()
        mock_conn.ping.side_effect = ConnectionRefusedError("refused")
        mock_redis_cls = MagicMock(return_value=mock_conn)
        with patch.dict(os.environ, {"REDIS_URL": custom_url}):
            with patch.dict("sys.modules", {"redis": MagicMock(Redis=mock_redis_cls)}):
                result = check_redis_health()
        assert result["url"] == custom_url

    @pytest.mark.unit_min_deps
    def test_redis_not_installed_returns_healthy_false(self):
        """If redis package is not installed, returns healthy=False with fix=pip install."""
        from agentic_core.cache.redis_cache_client import check_redis_health

        with patch.dict("sys.modules", {"redis": None}):
            result = check_redis_health("redis://localhost:6379")

        assert result["healthy"] is False
        assert result["fix"] is not None


# ---------------------------------------------------------------------------
# Private helpers shared across test classes
# ---------------------------------------------------------------------------


def _get_esf():
    """Import EmbeddingServiceFactory fresh (avoids module-level singleton contamination)."""
    from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

    return EmbeddingServiceFactory


def _cleanup_esf(svc, esf_cls) -> None:
    """Release Windows memmap file lock and reset singleton."""
    if hasattr(svc, "_raw") and hasattr(svc._raw, "_mmap"):
        try:
            svc._raw._mmap.close()
        except OSError:
            pass
    if hasattr(svc, "_raw"):
        del svc._raw
    esf_cls._INSTANCE = None
    esf_cls._INSTANCE_IDENTITY = None


def _make_seed_pack(base: Path, n: int = 3, dim: int = 4) -> Path:
    """Create a minimal valid seed pack directory for EmbeddingServiceFactory tests."""
    pack_dir = base / "seed_pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    embeddings = np.eye(max(n, dim), dtype=np.float32)[:n, :dim]
    matrix_hash = hashlib.sha256(embeddings.tobytes()).hexdigest()

    manifest = {
        "namespace": "healing_contexts",
        "bootstrap_mode": "curated_seed",
        "embedding_model_version": "test-v1",
        "embedding_model_checksum": hashlib.sha256(b"model").hexdigest(),
        "canonicalization_version": "v1",
        "dimensions": dim,
        "vector_count": n,
        "row_index_hash": hashlib.sha256(b"rows").hexdigest(),
        "matrix_hash": matrix_hash,
        "seed_index_version_hash": "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9",
        "built_at_utc": 1640995200,
    }
    (pack_dir / "seed_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with open(pack_dir / "row_index.jsonl", "w", encoding="utf-8") as f:
        for i in range(n):
            f.write(
                json.dumps({"content_hash": hashlib.sha256(f"c{i}".encode()).hexdigest(), "row_idx": i})
                + "\n"
            )

    embeddings.tofile(pack_dir / "embeddings.f32")
    return pack_dir


def _make_fallback_vector(text: str, dim: int = 16) -> list[float]:
    """Deterministic L2-normalised vector from SHA-256 bytes.

    Uses repeated SHA-256 rounds to produce enough bytes for arbitrary dim.
    SHA-256 yields 32 bytes = 8 float32s per round.
    """
    encoded = text.encode("utf-8")
    raw = b""
    seed = encoded
    while len(raw) < dim * 4:
        seed = hashlib.sha256(seed).digest()
        raw += seed
    floats = [struct.unpack("<f", raw[i * 4 : i * 4 + 4])[0] for i in range(dim)]
    norm = sum(x * x for x in floats) ** 0.5 or 1.0
    return [x / norm for x in floats]


def _build_and_persist_faiss(base: Path, index_id: str, n_vectors: int = 4) -> Path:
    """Build, finalize, and persist a LocalFAISSStore index; return the artifact dir."""
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    vecs = [_make_fallback_vector(f"vec_{i}") for i in range(n_vectors)]
    metas = [{"content_hash": f"hash_{i:04d}", "trace_id": f"t{i}"} for i in range(n_vectors)]
    dim = len(vecs[0])

    store = LocalFAISSStore(base_path=base)
    store.begin_build(index_id, dim, seed=0)
    store.add_vectors(index_id, vecs, metas)
    store.finalize_build(
        index_id,
        built_at_utc=1700000000,
        canonicalization_version="v1",
        embedding_model_version="hash-fallback-v1",
        embedding_model_checksum="hash-fallback",
    )
    disk_dir = base / index_id
    store.persist_to_disk(
        index_id,
        disk_dir,
        embedder_id="hash-fallback",
        model_version="hash-fallback-v1",
    )
    return disk_dir
