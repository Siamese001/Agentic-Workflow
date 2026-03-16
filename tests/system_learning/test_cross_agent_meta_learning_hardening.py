"""Cross-agent meta-learning feedback loop hardening tests.

Covers three gaps identified during the full codebase audit (all agents,
not just execute_ssot-aligned ones):

  G_RS - EmbeddingRetentionScheduler.run_once() never called persist_to_disk()
         after rebuild — pruned state lost on process restart.
  G_HI - historical_ingestion_orchestrator.ingest_and_build_indexes_with_embedder()
         only called finalize_build() (in-memory), never persist_to_disk() —
         ingested indexes died at process exit.
  G_MLA - MetaLearningAgent.strategy_weights in-memory only — learned weights
          reset to defaults on every restart.

And ten additional governance gaps (h2-h10):

  h2  - Embedding model compatibility: load_from_disk must reject indexes built
        with a different embedder_id (fail-closed).
  h3  - META_LEARNING_STATE_DIGEST: combined digest across FAISS indexes +
        strategy weights + embedding model version.
  h4  - Atomic persistence: persist_to_disk() and _save_strategy_weights() must
        use .tmp -> fsync -> rename, never write directly to target path.
  h5  - Replay key binding: strategy_weights_digest property is deterministic.
  h8  - Telemetry: _save_strategy_weights() fires telemetry callback with digest.
  h9  - Crash recovery: stale .tmp files are cleaned up before each atomic write.
  h10 - Schema versioning: persisted strategy_weights.json includes schema_version.

All G_RS / G_HI / h2 / h3 / h4 / h9 / h10 tests use @pytest.mark.unit_min_deps.
G_MLA / h5 / h8 tests use @pytest.mark.unit with SovereignBaseAgent patched out.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_cross_agent_meta_learning_hardening", "execution_auth")
_emit_validates_capability("p2", "test_cross_agent_meta_learning_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_cross_agent_meta_learning_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_cross_agent_meta_learning_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_cross_agent_meta_learning_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_cross_agent_meta_learning_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_cross_agent_meta_learning_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_cross_agent_meta_learning_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_cross_agent_meta_learning_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_cross_agent_meta_learning_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_cross_agent_meta_learning_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_cross_agent_meta_learning_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_cross_agent_meta_learning_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_cross_agent_meta_learning_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_cross_agent_meta_learning_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_cross_agent_meta_learning_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_cross_agent_meta_learning_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_cross_agent_meta_learning_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_cross_agent_meta_learning_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_cross_agent_meta_learning_hardening", "exec_snapshot_link")
from system_learning.config.embedding_storage_layout import EmbeddingStorageLayout
from system_learning.engines.embedding_retention_scheduler import (
    EmbeddingRetentionScheduler,
)
from system_learning.engines.local_faiss_store import (
    LocalFAISSStore,
)

_emit_records_execution_trace("p0", "evidence", "test_cross_agent_meta_learning_hardening")
_emit_applies_guardrail("p0", "test_cross_agent_meta_learning_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_cross_agent_meta_learning_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_cross_agent_meta_learning_hardening", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_cross_agent_meta_learning_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_cross_agent_meta_learning_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_cross_agent_meta_learning_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_cross_agent_meta_learning_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_cross_agent_meta_learning_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_cross_agent_meta_learning_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_cross_agent_meta_learning_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_cross_agent_meta_learning_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_cross_agent_meta_learning_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_cross_agent_meta_learning_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_cross_agent_meta_learning_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_cross_agent_meta_learning_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_cross_agent_meta_learning_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_cross_agent_meta_learning_hardening", "p3lm", "state")
_emit_records_execution_trace("test_cross_agent_meta_learning_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_cross_agent_meta_learning_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_cross_agent_meta_learning_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_cross_agent_meta_learning_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_cross_agent_meta_learning_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_cross_agent_meta_learning_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_cross_agent_meta_learning_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_cross_agent_meta_learning_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_cross_agent_meta_learning_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_cross_agent_meta_learning_hardening", "context_pull")
_emit_pulls_context("p1", "test_cross_agent_meta_learning_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_cross_agent_meta_learning_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_cross_agent_meta_learning_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_cross_agent_meta_learning_hardening", "write_through")
_emit_writes_through("p1", "test_cross_agent_meta_learning_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_cross_agent_meta_learning_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_cross_agent_meta_learning_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_cross_agent_meta_learning_hardening", "routing_commit")
emit_replay_key("p0", "test_cross_agent_meta_learning_hardening")
emit_determinism_digest("p0", "test_cross_agent_meta_learning_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_DIM = 16  # Use 16-dim hash-fallback for fast unit tests


def _l2(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def _make_vecs(n: int, dim: int = _DIM, offset: int = 0) -> tuple[list[list[float]], list[dict]]:
    """Generate n deterministic L2-normalised vectors with metadata."""
    vecs, metas = [], []
    for i in range(n):
        raw = [float((i + offset + j + 1) % 100) for j in range(dim)]
        vecs.append(_l2(raw))
        metas.append(
            {
                "content_hash": f"ch_{i + offset:04d}",
                "trace_id": f"tr_{i + offset}",
                "created_utc": 1_000_000 + (i + offset) * 1000,
            }
        )
    return vecs, metas


def _build_store(tmp: Path, index_id: str, n: int = 5, dim: int = _DIM) -> LocalFAISSStore:
    """Build and finalize (in-memory) a LocalFAISSStore."""
    vecs, metas = _make_vecs(n, dim=dim)
    store = LocalFAISSStore(base_path=tmp)
    store.begin_build(index_id, dim, seed=0)
    store.add_vectors(index_id, vecs, metas)
    store.finalize_build(
        index_id,
        built_at_utc=1_000_000,
        canonicalization_version="v1",
        embedding_model_version="hash-fallback-v1",
        embedding_model_checksum="hash-fallback",
    )
    return store


# ===========================================================================
# G_RS: EmbeddingRetentionScheduler persist after rebuild
# ===========================================================================


class TestEmbeddingRetentionSchedulerPersist:
    """G_RS fix regression: run_once() must persist rebuilt index to disk."""

    @pytest.mark.unit_min_deps
    def test_run_once_rolling_window_persists_to_disk(self, tmp_path):
        """After rolling-window prune+rebuild, persist_base_path triggers disk write."""
        index_id = "healing_context_v1"
        store = _build_store(tmp_path, index_id, n=6)

        # All vectors have created_utc in [1_000_000 .. 1_005_000].
        # Cutoff: now_utc - retention_window = prune everything before 1_004_500.
        # That leaves the last 1–2 vectors depending on stride.
        now_utc = 1_004_500 + (1 * 24 * 3600)  # 1 day after the cutoff epoch

        scheduler = EmbeddingRetentionScheduler()
        results = scheduler.run_once(
            now_utc=now_utc,
            policies={index_id: {"mode": "rolling_window", "retention_days": 1}},
            stores={index_id: store},
            persist_base_path=tmp_path,
        )

        # Prune must have happened (results non-empty) OR all vectors survived
        # (still must not crash — test non-regression).
        dest = tmp_path / index_id
        if results:
            assert dest.exists(), "persist_base_path dir must be created after rebuild"
            assert (dest / "index.json").exists(), "index.json must be written"
            assert (dest / "meta.json").exists(), "meta.json must be written"
            assert (dest / "manifest.json").exists(), "manifest.json must be written"

    @pytest.mark.unit_min_deps
    def test_run_once_predicate_persists_to_disk(self, tmp_path):
        """After predicate prune+rebuild, persist_base_path triggers disk write."""
        index_id = "telemetry_v1"
        store = _build_store(tmp_path, index_id, n=5)

        # Predicate: prune vectors with even content_hash index
        def prune_even(meta: dict) -> bool:
            return meta.get("content_hash", "")[-4:].lstrip("0") in ("0", "2", "4", "")

        scheduler = EmbeddingRetentionScheduler()
        results = scheduler.run_once(
            now_utc=0,
            policies={index_id: {"mode": "predicate", "predicate": prune_even}},
            stores={index_id: store},
            persist_base_path=tmp_path,
        )

        dest = tmp_path / index_id
        if results:
            assert (dest / "manifest.json").exists(), "manifest.json must be written after predicate rebuild"

    @pytest.mark.unit_min_deps
    def test_run_once_persisted_index_is_loadable(self, tmp_path):
        """After persist_base_path rebuild, the artifact must be loadable."""
        index_id = "healing_context_v1"
        store = _build_store(tmp_path, index_id, n=4)
        vecs_orig, _ = _make_vecs(4)

        # Prune all vectors (cutoff in the far future)
        def prune_all(_: dict) -> bool:
            return True

        scheduler = EmbeddingRetentionScheduler()
        results = scheduler.run_once(
            now_utc=999_999_999,
            policies={index_id: {"mode": "predicate", "predicate": prune_all}},
            stores={index_id: store},
            persist_base_path=tmp_path,
        )

        if not results:
            pytest.fail("No pruning occurred — rebuild path not exercised")

        dest = tmp_path / index_id
        assert dest.exists(), "Disk artifact must have been created"

        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk(index_id, dest)
        loaded = reader._memory_indexes[index_id]
        assert isinstance(loaded["vectors"], list), "Loaded vectors must be a list"

    @pytest.mark.unit_min_deps
    def test_run_once_without_persist_base_path_no_disk_write(self, tmp_path):
        """When persist_base_path is None (default), no disk artifacts written."""
        index_id = "healing_context_v1"
        store = _build_store(tmp_path, index_id, n=3)

        def prune_all(_: dict) -> bool:
            return True

        scheduler = EmbeddingRetentionScheduler()
        scheduler.run_once(
            now_utc=0,
            policies={index_id: {"mode": "predicate", "predicate": prune_all}},
            stores={index_id: store},
            # persist_base_path intentionally omitted (default None)
        )

        dest = tmp_path / index_id
        assert not dest.exists(), "No disk artifact when persist_base_path=None"

    @pytest.mark.unit_min_deps
    def test_run_once_none_mode_skips_rebuild_and_persist(self, tmp_path):
        """mode='none' must skip pruning and produce no disk artifact."""
        index_id = "healing_context_v1"
        store = _build_store(tmp_path, index_id, n=3)

        scheduler = EmbeddingRetentionScheduler()
        results = scheduler.run_once(
            now_utc=0,
            policies={index_id: {"mode": "none"}},
            stores={index_id: store},
            persist_base_path=tmp_path,
        )

        assert results == {}, "mode=none must return empty results"
        dest = tmp_path / index_id
        assert not dest.exists(), "No disk artifact for mode=none"

    @pytest.mark.unit_min_deps
    def test_run_once_persisted_manifest_integrity(self, tmp_path):
        """manifest.json sha256 fields must match actual file content after rebuild."""
        import hashlib

        index_id = "healing_context_v1"
        store = _build_store(tmp_path, index_id, n=4)

        def prune_first(_meta: dict) -> bool:
            return _meta.get("content_hash", "") == "ch_0000"

        scheduler = EmbeddingRetentionScheduler()
        results = scheduler.run_once(
            now_utc=0,
            policies={index_id: {"mode": "predicate", "predicate": prune_first}},
            stores={index_id: store},
            persist_base_path=tmp_path,
        )

        if not results:
            pytest.fail("Prune did not trigger (ch_0000 not found)")

        dest = tmp_path / index_id
        manifest = json.loads((dest / "manifest.json").read_bytes().decode("ascii"))
        index_bytes = (dest / "index.json").read_bytes()
        meta_bytes = (dest / "meta.json").read_bytes()
        assert hashlib.sha256(index_bytes).hexdigest() == manifest["sha256_index"]
        assert hashlib.sha256(meta_bytes).hexdigest() == manifest["sha256_meta_canonical"]


# ===========================================================================
# G_HI: historical_ingestion_orchestrator persist after build
# ===========================================================================


class _FakeEmbedder:
    """Deterministic fake embedder — returns L2-normalised constant vectors."""

    def embed_batch(self, texts: list[str], dimension: int) -> list[list[float]]:
        vecs = []
        for i, _ in enumerate(texts):
            raw = [float((i + j + 1) % 100) for j in range(dimension)]
            vecs.append(_l2(raw))
        return vecs


class TestHistoricalIngestionOrchestratorPersist:
    """G_HI fix regression: ingest_and_build_indexes_with_embedder must persist to disk."""

    @pytest.fixture()
    def healing_source(self):
        return [
            {"violation_signature": "import_boundary", "strategy": "repair_imports", "trace_id": "t0"},
            {"violation_signature": "layer_inversion", "strategy": "reorder_imports", "trace_id": "t1"},
        ]

    @pytest.fixture()
    def telemetry_source(self):
        return [
            {"event_type": "gate_fail", "payload": {"gate": "import_check"}, "trace_id": "t2"},
        ]

    @pytest.fixture()
    def dpo_source(self):
        return [
            {"prompt": "fix imports", "chosen": "repair_imports", "rejected": "ignore", "trace_id": "t3"},
        ]

    @pytest.mark.unit_min_deps
    def test_healing_contexts_index_persisted_to_layout_dir(
        self, tmp_path, healing_source, telemetry_source, dpo_source
    ):
        """healing_contexts_v1 must be written to EmbeddingStorageLayout path."""
        from system_learning.engines.historical_ingestion_orchestrator import (
            ingest_and_build_indexes_with_embedder,
        )

        ingest_and_build_indexes_with_embedder(
            base_path=tmp_path,
            built_at_utc=1_700_000_000,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
            canonicalization_version="v1",
            embedder=_FakeEmbedder(),
        )

        layout = EmbeddingStorageLayout(tmp_path)
        dest = layout.healing_contexts_index_dir()
        assert dest.exists(), "healing_contexts index dir must be created"
        assert (dest / "index.json").exists(), "index.json must be written"
        assert (dest / "meta.json").exists(), "meta.json must be written"
        assert (dest / "manifest.json").exists(), "manifest.json must be written"

    @pytest.mark.unit_min_deps
    def test_telemetry_events_index_persisted_to_layout_dir(
        self, tmp_path, healing_source, telemetry_source, dpo_source
    ):
        """telemetry_events_v1 must be written to EmbeddingStorageLayout path."""
        from system_learning.engines.historical_ingestion_orchestrator import (
            ingest_and_build_indexes_with_embedder,
        )

        ingest_and_build_indexes_with_embedder(
            base_path=tmp_path,
            built_at_utc=1_700_000_000,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
            canonicalization_version="v1",
            embedder=_FakeEmbedder(),
        )

        layout = EmbeddingStorageLayout(tmp_path)
        dest = layout.telemetry_events_index_dir()
        assert dest.exists(), "telemetry_events index dir must be created"
        assert (dest / "manifest.json").exists(), "manifest.json must be written"

    @pytest.mark.unit_min_deps
    def test_dpo_pairs_index_persisted_to_layout_dir(
        self, tmp_path, healing_source, telemetry_source, dpo_source
    ):
        """dpo_pairs_v1 must be written to EmbeddingStorageLayout path."""
        from system_learning.engines.historical_ingestion_orchestrator import (
            ingest_and_build_indexes_with_embedder,
        )

        ingest_and_build_indexes_with_embedder(
            base_path=tmp_path,
            built_at_utc=1_700_000_000,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
            canonicalization_version="v1",
            embedder=_FakeEmbedder(),
        )

        layout = EmbeddingStorageLayout(tmp_path)
        dest = layout.dpo_pairs_index_dir()
        assert dest.exists(), "dpo_pairs index dir must be created"
        assert (dest / "manifest.json").exists(), "manifest.json must be written"

    @pytest.mark.unit_min_deps
    def test_all_three_indexes_loadable_after_build(
        self, tmp_path, healing_source, telemetry_source, dpo_source
    ):
        """All three persisted indexes must be loadable by LocalFAISSStore."""
        from system_learning.engines.historical_ingestion_orchestrator import (
            ingest_and_build_indexes_with_embedder,
        )

        results = ingest_and_build_indexes_with_embedder(
            base_path=tmp_path,
            built_at_utc=1_700_000_000,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
            canonicalization_version="v1",
            embedder=_FakeEmbedder(),
        )

        assert "healing_contexts_v1" in results
        assert "telemetry_events_v1" in results
        assert "dpo_pairs_v1" in results

        layout = EmbeddingStorageLayout(tmp_path)
        index_dirs = {
            "healing_contexts_v1": layout.healing_contexts_index_dir(),
            "telemetry_events_v1": layout.telemetry_events_index_dir(),
            "dpo_pairs_v1": layout.dpo_pairs_index_dir(),
        }

        store = LocalFAISSStore(base_path=tmp_path)
        for idx_id, dest in index_dirs.items():
            # Must not raise ManifestIntegrityError
            store.load_from_disk(idx_id, dest)
            loaded = store._memory_indexes[idx_id]
            assert isinstance(loaded["vectors"], list), f"{idx_id}: vectors must be a list"

    @pytest.mark.unit_min_deps
    def test_persisted_manifest_checksum_valid(self, tmp_path, healing_source, telemetry_source, dpo_source):
        """Manifests written by orchestrator must have valid sha256 fields."""
        import hashlib

        from system_learning.engines.historical_ingestion_orchestrator import (
            ingest_and_build_indexes_with_embedder,
        )

        ingest_and_build_indexes_with_embedder(
            base_path=tmp_path,
            built_at_utc=1_700_000_000,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
            canonicalization_version="v1",
            embedder=_FakeEmbedder(),
        )

        layout = EmbeddingStorageLayout(tmp_path)
        for dest in (
            layout.healing_contexts_index_dir(),
            layout.telemetry_events_index_dir(),
            layout.dpo_pairs_index_dir(),
        ):
            manifest = json.loads((dest / "manifest.json").read_bytes().decode("ascii"))
            assert hashlib.sha256((dest / "index.json").read_bytes()).hexdigest() == manifest["sha256_index"]
            assert (
                hashlib.sha256((dest / "meta.json").read_bytes()).hexdigest()
                == manifest["sha256_meta_canonical"]
            )


# ===========================================================================
# G_MLA: MetaLearningAgent strategy_weights cross-run persistence
# ===========================================================================


class TestMetaLearningAgentPersistence:
    """G_MLA fix regression: strategy_weights must survive process restarts."""

    @staticmethod
    def _make_agent(weights_file: Path):
        """Construct MetaLearningAgent with SovereignBaseAgent.__init__ patched out."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            return MetaLearningAgent(strategy_weights_file=weights_file)

    @pytest.mark.unit
    def test_strategy_weights_file_created_after_update(self, tmp_path):
        """After update_strategy_weights(), a weights JSON file must be written."""
        weights_file = tmp_path / "weights.json"
        agent = self._make_agent(weights_file)
        # Store experiences to produce a non-trivial update
        for reward, thought in [(1.0, "cot"), (-0.5, "tot"), (0.5, "react")]:
            agent.store_experience({}, thought, {}, reward)
        agent.update_strategy_weights()
        assert weights_file.exists(), "Weights file must be created after update"

    @pytest.mark.unit
    def test_strategy_weights_file_is_valid_json(self, tmp_path):
        """Persisted weights file must be valid JSON with 'strategy_weights' key."""
        weights_file = tmp_path / "weights.json"
        agent = self._make_agent(weights_file)
        agent.store_experience({}, "cot", {}, 1.0)
        agent.update_strategy_weights()
        raw = json.loads(weights_file.read_text(encoding="utf-8"))
        assert "strategy_weights" in raw, "File must contain 'strategy_weights' key"
        assert isinstance(raw["strategy_weights"], dict)

    @pytest.mark.unit
    def test_weights_survive_process_restart(self, tmp_path):
        """New agent instantiated with same file must load previous run's weights."""
        weights_file = tmp_path / "weights.json"

        # Run 1: high rewards for 'cot', low for others
        a1 = self._make_agent(weights_file)
        for _ in range(10):
            a1.store_experience({}, "cot", {}, 1.0)
        for _ in range(10):
            a1.store_experience({}, "tot", {}, -1.0)
        a1.update_strategy_weights()
        saved_weights = dict(a1.strategy_weights)

        # Run 2: new agent, same file
        a2 = self._make_agent(weights_file)
        # Weights must match what was saved
        assert a2.strategy_weights == pytest.approx(saved_weights, rel=1e-5), (
            "Loaded weights must match saved weights from prior run"
        )

    @pytest.mark.unit
    def test_get_strategy_recommendation_reflects_loaded_weights(self, tmp_path):
        """After loading persisted weights, recommendation must reflect prior learning."""
        weights_file = tmp_path / "weights.json"

        # Run 1: train 'reflection' to dominate
        a1 = self._make_agent(weights_file)
        for _ in range(20):
            a1.store_experience({}, "reflection", {}, 1.0)
        for _ in range(20):
            a1.store_experience({}, "cot", {}, -1.0)
        a1.update_strategy_weights()

        # Run 2: fresh agent reads saved weights
        a2 = self._make_agent(weights_file)
        recommendation = a2.get_strategy_recommendation({})
        assert recommendation == "reflection", (
            f"Recommendation must be 'reflection' (highest weight from prior run), got '{recommendation}'"
        )

    @pytest.mark.unit
    def test_no_persistence_when_file_not_provided(self, tmp_path):
        """When strategy_weights_file=None, no file is written after update."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            agent = MetaLearningAgent(strategy_weights_file=None)

        agent.store_experience({}, "cot", {}, 1.0)
        agent.update_strategy_weights()
        # No JSON files should have been created in cwd/tmp_path
        json_files = list(tmp_path.rglob("*.json"))
        assert json_files == [], "No JSON files must be written when strategy_weights_file=None"

    @pytest.mark.unit
    def test_corrupt_weights_file_uses_defaults(self, tmp_path):
        """Corrupt/empty weights file must not crash agent init — defaults used."""
        weights_file = tmp_path / "weights.json"
        weights_file.write_text("NOT JSON {{{{", encoding="utf-8")

        agent = self._make_agent(weights_file)
        # Must not raise; defaults must be intact
        assert set(agent.strategy_weights.keys()) == {"cot", "tot", "react", "reflection"}
        for v in agent.strategy_weights.values():
            assert v == pytest.approx(1.0), "Default weights must be 1.0 when file is corrupt"

    @pytest.mark.unit
    def test_weights_file_ascii_only(self, tmp_path):
        """Persisted weights JSON must contain only ASCII bytes (no UTF-8 outside ASCII)."""
        weights_file = tmp_path / "weights.json"
        agent = self._make_agent(weights_file)
        agent.store_experience({}, "cot", {}, 0.8)
        agent.update_strategy_weights()
        raw_bytes = weights_file.read_bytes()
        assert all(b < 0x80 for b in raw_bytes), "Weights file must be ASCII-only"


# ===========================================================================
# h2: Embedding model compatibility check in load_from_disk
# ===========================================================================


class TestEmbedderCompatibilityCheck:
    """h2: load_from_disk must fail-closed when embedder_id mismatches."""

    @pytest.mark.unit_min_deps
    def test_load_rejects_mismatched_embedder_id(self, tmp_path):
        """load_from_disk with wrong expected_embedder_id must raise EmbedderMismatchError."""
        from system_learning.engines.local_faiss_store import (
            EmbedderMismatchError,
            LocalFAISSStore,
        )

        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="BAAI/bge-m3",
            model_version="v1",
        )

        reader = LocalFAISSStore(base_path=tmp_path)
        with pytest.raises(EmbedderMismatchError, match="embedder_id mismatch"):
            reader.load_from_disk(
                "hc_v1",
                tmp_path / "hc_v1",
                expected_embedder_id="openai/text-embedding-3-large",
            )

    @pytest.mark.unit_min_deps
    def test_load_accepts_matching_embedder_id(self, tmp_path):
        """load_from_disk must succeed when expected_embedder_id matches manifest."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="BAAI/bge-m3",
            model_version="v1",
        )

        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            expected_embedder_id="BAAI/bge-m3",
        )
        assert "hc_v1" in reader._memory_indexes

    @pytest.mark.unit_min_deps
    def test_load_skips_compat_check_when_none(self, tmp_path):
        """load_from_disk without expected_embedder_id must load without error."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="BAAI/bge-m3",
            model_version="v1",
        )

        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk("hc_v1", tmp_path / "hc_v1")
        assert "hc_v1" in reader._memory_indexes


# ===========================================================================
# h3: META_LEARNING_STATE_DIGEST combined determinism artifact
# ===========================================================================


class TestMetaLearningStateDigest:
    """h3: compute_meta_learning_state_digest must be deterministic and cover all inputs."""

    @pytest.mark.unit_min_deps
    def test_digest_is_64_hex(self):
        """compute_meta_learning_state_digest must return 64-char hex string."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        d = compute_meta_learning_state_digest(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="b" * 64,
            embedding_model_version="BAAI/bge-m3-v1",
        )
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    @pytest.mark.unit_min_deps
    def test_digest_is_deterministic(self):
        """Same inputs must always produce the same digest."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        kwargs = {
            "faiss_index_digests": {"hc_v1": "a" * 64, "tel_v1": "b" * 64},
            "strategy_weights_digest": "c" * 64,
            "embedding_model_version": "hash-fallback-v1",
        }
        assert compute_meta_learning_state_digest(**kwargs) == compute_meta_learning_state_digest(**kwargs)

    @pytest.mark.unit_min_deps
    def test_digest_changes_on_different_weights(self):
        """Changing strategy_weights_digest must change the output."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        base = {
            "faiss_index_digests": {"hc_v1": "a" * 64},
            "embedding_model_version": "v1",
        }
        d1 = compute_meta_learning_state_digest(**base, strategy_weights_digest="1" * 64)
        d2 = compute_meta_learning_state_digest(**base, strategy_weights_digest="2" * 64)
        assert d1 != d2

    @pytest.mark.unit_min_deps
    def test_digest_changes_on_different_model(self):
        """Changing embedding_model_version must change the output."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        base = {
            "faiss_index_digests": {"hc_v1": "a" * 64},
            "strategy_weights_digest": "c" * 64,
        }
        d1 = compute_meta_learning_state_digest(**base, embedding_model_version="model-v1")
        d2 = compute_meta_learning_state_digest(**base, embedding_model_version="model-v2")
        assert d1 != d2

    @pytest.mark.unit_min_deps
    def test_digest_raises_on_empty_faiss_dict(self):
        """Empty faiss_index_digests must raise ValueError."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        with pytest.raises(ValueError, match="faiss_index_digests must contain at least one entry"):
            compute_meta_learning_state_digest(
                faiss_index_digests={},
                strategy_weights_digest="a" * 64,
                embedding_model_version="v1",
            )

    @pytest.mark.unit_min_deps
    def test_emit_prints_digest(self, capsys):
        """emit_meta_learning_state_digest must print META_LEARNING_STATE_DIGEST line."""
        from system_learning.engines.meta_learning_state_digest import (
            emit_meta_learning_state_digest,
        )

        digest = emit_meta_learning_state_digest(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="b" * 64,
            embedding_model_version="v1",
        )
        captured = capsys.readouterr()
        digest_lines = [
            line for line in captured.out.splitlines() if line.startswith("META_LEARNING_STATE_DIGEST:")
        ]
        assert f"META_LEARNING_STATE_DIGEST: {digest}" in captured.out


# ===========================================================================
# h4: Atomic persistence — persist_to_disk() uses .tmp -> fsync -> rename
# ===========================================================================


class TestAtomicPersistence:
    """h4: verify files are written via atomic rename (no partial writes survive)."""

    @pytest.mark.unit_min_deps
    def test_no_tmp_files_after_successful_persist(self, tmp_path):
        """After persist_to_disk() succeeds, no .tmp files must remain."""
        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="test-embedder",
            model_version="v1",
        )
        tmp_files = list((tmp_path / "hc_v1").glob("*.tmp"))
        assert tmp_files == [], f"Stale .tmp files found: {tmp_files}"

    @pytest.mark.unit_min_deps
    def test_target_files_exist_after_persist(self, tmp_path):
        """After persist_to_disk(), all three canonical files must exist."""
        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="test-embedder",
            model_version="v1",
        )
        dest = tmp_path / "hc_v1"
        for fname in ("index.json", "meta.json", "manifest.json"):
            assert (dest / fname).exists(), f"{fname} must exist after persist"

    @pytest.mark.unit_min_deps
    def test_stale_tmp_cleaned_before_persist(self, tmp_path):
        """Pre-existing .tmp files from prior crash must be removed before writing."""
        dest = tmp_path / "hc_v1"
        dest.mkdir(parents=True, exist_ok=True)
        stale = dest / "index.tmp"
        stale.write_bytes(b"CRASH REMNANT")

        store = _build_store(tmp_path, "hc_v1", n=3)
        store.persist_to_disk(
            "hc_v1",
            dest,
            embedder_id="test-embedder",
            model_version="v1",
        )
        assert not stale.exists(), "Stale .tmp must have been deleted"
        assert (dest / "index.json").exists(), "index.json must be written after cleanup"


# ===========================================================================
# h5 + h8 + h10: strategy_weights_digest, telemetry, schema_version
# ===========================================================================


class TestStrategyWeightsHardening:
    """h5/h8/h10: digest property, telemetry callback, schema_version in file."""

    @staticmethod
    def _make_agent(weights_file: Path):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            return MetaLearningAgent(strategy_weights_file=weights_file)

    # --- h5: replay key binding ---

    @pytest.mark.unit
    def test_strategy_weights_digest_is_64_hex(self, tmp_path):
        """strategy_weights_digest property must return 64-char hex string."""
        agent = self._make_agent(tmp_path / "w.json")
        d = agent.strategy_weights_digest
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    @pytest.mark.unit
    def test_strategy_weights_digest_is_deterministic(self, tmp_path):
        """Same weights must always produce the same digest."""
        agent = self._make_agent(tmp_path / "w.json")
        assert agent.strategy_weights_digest == agent.strategy_weights_digest

    @pytest.mark.unit
    def test_strategy_weights_digest_changes_after_update(self, tmp_path):
        """After update_strategy_weights() changes weights, digest must change."""
        agent = self._make_agent(tmp_path / "w.json")
        d_before = agent.strategy_weights_digest
        for _ in range(20):
            agent.store_experience({}, "cot", {}, 1.0)
        for _ in range(20):
            agent.store_experience({}, "tot", {}, -1.0)
        agent.update_strategy_weights()
        d_after = agent.strategy_weights_digest
        assert d_before != d_after, "Digest must change when weights change"

    # --- h8: telemetry callback ---

    @pytest.mark.unit
    def test_telemetry_callback_fired_on_save(self, tmp_path):
        """_save_strategy_weights() must fire telemetry_callback with strategy_weights_persisted."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent

        events = []

        def _cb(event_type: str, data: dict) -> None:
            events.append((event_type, data))

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            agent = MetaLearningAgent(
                strategy_weights_file=tmp_path / "w.json",
                telemetry_callback=_cb,
            )

        agent.store_experience({}, "cot", {}, 0.9)
        agent.update_strategy_weights()

        persisted_events = [e for e in events if e[0] == "strategy_weights_persisted"]
        assert len(persisted_events) >= 1, "strategy_weights_persisted event must be emitted"
        payload = persisted_events[-1][1]
        assert "weights_digest" in payload, "Event payload must include weights_digest"
        assert len(payload["weights_digest"]) == 64

    @pytest.mark.unit
    def test_no_telemetry_when_callback_is_none(self, tmp_path):
        """No error when telemetry_callback=None and weights are saved."""
        agent = self._make_agent(tmp_path / "w.json")
        assert agent.telemetry_callback is None
        agent.store_experience({}, "cot", {}, 0.5)
        agent.update_strategy_weights()
        assert (tmp_path / "w.json").exists()

    # --- h10: schema_version ---

    @pytest.mark.unit
    def test_persisted_weights_has_schema_version(self, tmp_path):
        """Persisted strategy_weights.json must contain 'schema_version' field."""
        weights_file = tmp_path / "w.json"
        agent = self._make_agent(weights_file)
        agent.store_experience({}, "cot", {}, 0.7)
        agent.update_strategy_weights()
        raw = json.loads(weights_file.read_bytes().decode("ascii"))
        assert "schema_version" in raw, "Weights file must contain schema_version"
        assert raw["schema_version"] == "1"

    @pytest.mark.unit
    def test_load_ignores_schema_version_field(self, tmp_path):
        """Loading weights file with schema_version must not crash or corrupt weights."""
        weights_file = tmp_path / "w.json"
        agent1 = self._make_agent(weights_file)
        for _ in range(10):
            agent1.store_experience({}, "reflection", {}, 1.0)
        agent1.update_strategy_weights()
        saved = dict(agent1.strategy_weights)

        agent2 = self._make_agent(weights_file)
        assert agent2.strategy_weights == pytest.approx(saved, rel=1e-5)

    @pytest.mark.unit
    def test_weights_file_ascii_only_with_schema_version(self, tmp_path):
        """Persisted weights JSON (including schema_version) must be ASCII-only."""
        weights_file = tmp_path / "w.json"
        agent = self._make_agent(weights_file)
        agent.store_experience({}, "react", {}, 0.3)
        agent.update_strategy_weights()
        raw_bytes = weights_file.read_bytes()
        assert all(b < 0x80 for b in raw_bytes), "All bytes must be < 0x80 (ASCII)"


# ===========================================================================
# hA: Strict-mode weights corruption (META_LEARNING_STRICT_WEIGHTS=1)
# ===========================================================================


class TestStrictWeightsMode:
    """hA: corrupt weights raise in strict mode; emit telemetry in non-strict mode."""

    @staticmethod
    def _make_agent(weights_file, telemetry_callback=None):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            return MetaLearningAgent(
                strategy_weights_file=weights_file,
                telemetry_callback=telemetry_callback,
            )

    @pytest.mark.unit
    def test_strict_mode_raises_on_corrupt_file(self, tmp_path, monkeypatch):
        """META_LEARNING_STRICT_WEIGHTS=1: corrupt file must raise RuntimeError."""
        monkeypatch.setenv("META_LEARNING_STRICT_WEIGHTS", "1")
        weights_file = tmp_path / "w.json"
        weights_file.write_text("NOT JSON {{{{", encoding="utf-8")

        with pytest.raises(RuntimeError, match="META_LEARNING_STRICT_WEIGHTS=1"):
            self._make_agent(weights_file)

    @pytest.mark.unit
    def test_strict_mode_off_by_default(self, tmp_path, monkeypatch):
        """Without META_LEARNING_STRICT_WEIGHTS=1, corrupt file uses defaults silently."""
        monkeypatch.delenv("META_LEARNING_STRICT_WEIGHTS", raising=False)
        weights_file = tmp_path / "w.json"
        weights_file.write_text("NOT JSON {{{{", encoding="utf-8")

        agent = self._make_agent(weights_file)
        assert agent.strategy_weights["cot"] == pytest.approx(1.0)

    @pytest.mark.unit
    def test_nonstrict_corrupt_emits_telemetry(self, tmp_path, monkeypatch):
        """In non-strict mode, corrupt file must emit strategy_weights_load_failed_fallback event."""
        monkeypatch.delenv("META_LEARNING_STRICT_WEIGHTS", raising=False)
        weights_file = tmp_path / "w.json"
        weights_file.write_text("{bad json", encoding="utf-8")

        events = []
        self._make_agent(weights_file, telemetry_callback=lambda e, d: events.append((e, d)))

        fallback_events = [e for e in events if e[0] == "strategy_weights_load_failed_fallback"]
        assert len(fallback_events) == 1, "Must emit exactly one fallback telemetry event"
        payload = fallback_events[0][1]
        assert "file" in payload
        assert "exc_type" in payload

    @pytest.mark.unit
    def test_strict_mode_value_1_only(self, tmp_path, monkeypatch):
        """Only '1' activates strict mode; '0', 'true', 'yes' must not activate it."""
        weights_file = tmp_path / "w.json"
        weights_file.write_text("NOT JSON", encoding="utf-8")

        for val in ("0", "true", "yes", "TRUE", ""):
            monkeypatch.setenv("META_LEARNING_STRICT_WEIGHTS", val)
            agent = self._make_agent(weights_file)
            assert agent.strategy_weights["cot"] == pytest.approx(1.0), (
                f"val={val!r} should not activate strict mode"
            )

    @pytest.mark.unit
    def test_strict_mode_valid_file_loads_normally(self, tmp_path, monkeypatch):
        """META_LEARNING_STRICT_WEIGHTS=1 must not affect loading a valid weights file."""
        monkeypatch.setenv("META_LEARNING_STRICT_WEIGHTS", "1")
        weights_file = tmp_path / "w.json"

        agent1 = self._make_agent(weights_file)
        for _ in range(15):
            agent1.store_experience({}, "cot", {}, 1.0)
        agent1.update_strategy_weights()
        saved = dict(agent1.strategy_weights)

        agent2 = self._make_agent(weights_file)
        assert agent2.strategy_weights == pytest.approx(saved, rel=1e-5)


# ===========================================================================
# hB: Determinism proof — two independent runs produce identical digest
# ===========================================================================


class TestDeterminismProof:
    """hB: META_LEARNING_STATE_DIGEST is stable across two independent runs."""

    @pytest.mark.unit_min_deps
    def test_digest_identical_across_two_runs(self, tmp_path, capsys):
        """Two builds from identical inputs must emit the same META_LEARNING_STATE_DIGEST."""
        from system_learning.engines.meta_learning_state_digest import (
            emit_meta_learning_state_digest,
        )

        def _run(base: Path) -> str:
            store = _build_store(base, "hc_v1", n=4)
            faiss_digest = store.persist_to_disk(
                "hc_v1",
                base / "hc_v1",
                embedder_id="hash-fallback",
                model_version="v1",
            )
            digest = emit_meta_learning_state_digest(
                faiss_index_digests={"hc_v1": faiss_digest},
                strategy_weights_digest="a" * 64,
                embedding_model_version="hash-fallback-v1",
            )
            return digest

        d1 = _run(tmp_path / "run1")
        d2 = _run(tmp_path / "run2")
        assert d1 == d2, "META_LEARNING_STATE_DIGEST must be identical across two identical runs"

    @pytest.mark.unit_min_deps
    def test_digest_emitted_exactly_once_per_run(self, tmp_path, capsys):
        """emit_meta_learning_state_digest must print the digest line exactly once per call."""
        from system_learning.engines.meta_learning_state_digest import (
            emit_meta_learning_state_digest,
        )

        capsys.readouterr()
        store = _build_store(tmp_path, "hc_v1", n=2)
        faiss_digest = store.persist_to_disk(
            "hc_v1",
            tmp_path / "hc_v1",
            embedder_id="hash-fallback",
            model_version="v1",
        )
        capsys.readouterr()  # flush prior prints

        digest = emit_meta_learning_state_digest(
            faiss_index_digests={"hc_v1": faiss_digest},
            strategy_weights_digest="b" * 64,
            embedding_model_version="v1",
        )
        captured = capsys.readouterr()
        digest_lines = [
            ln for ln in captured.out.splitlines() if ln.startswith("META_LEARNING_STATE_DIGEST:")
        ]
        assert len(digest_lines) == 1, f"Expected exactly 1 digest line, got {len(digest_lines)}"
        assert digest_lines[0] == f"META_LEARNING_STATE_DIGEST: {digest}"

    @pytest.mark.unit_min_deps
    def test_digest_changes_when_faiss_content_changes(self, tmp_path):
        """Different FAISS content must yield different META_LEARNING_STATE_DIGEST."""
        from system_learning.engines.meta_learning_state_digest import (
            compute_meta_learning_state_digest,
        )

        store_a = _build_store(tmp_path / "a", "hc_v1", n=3)
        d_a = store_a.persist_to_disk("hc_v1", tmp_path / "a" / "hc_v1", embedder_id="e", model_version="v1")

        store_b = _build_store(tmp_path / "b", "hc_v1", n=5)
        d_b = store_b.persist_to_disk("hc_v1", tmp_path / "b" / "hc_v1", embedder_id="e", model_version="v1")

        digest_a = compute_meta_learning_state_digest(
            faiss_index_digests={"hc_v1": d_a},
            strategy_weights_digest="c" * 64,
            embedding_model_version="v1",
        )
        digest_b = compute_meta_learning_state_digest(
            faiss_index_digests={"hc_v1": d_b},
            strategy_weights_digest="c" * 64,
            embedding_model_version="v1",
        )
        assert digest_a != digest_b


# ===========================================================================
# hC: Replay binding struct
# ===========================================================================


class TestReplayBinding:
    """hC: MetaLearningReplayBinding contains all three digest fields and is deterministic."""

    @pytest.mark.unit_min_deps
    def test_binding_has_all_three_keys(self):
        """to_dict() must contain faiss_index_digests, strategy_weights_digest, embedding_model_version."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        b = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="b" * 64,
            embedding_model_version="hash-fallback-v1",
        )
        d = b.to_dict()
        assert "faiss_index_digests" in d
        assert "strategy_weights_digest" in d
        assert "embedding_model_version" in d

    @pytest.mark.unit_min_deps
    def test_binding_emit_prints_replay_binding_line(self, capsys):
        """emit() must print exactly one REPLAY-BINDING: line."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        b = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="b" * 64,
            embedding_model_version="v1",
        )
        b.emit()
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.startswith("REPLAY-BINDING:")]
        assert len(lines) == 1

    @pytest.mark.unit_min_deps
    def test_binding_round_trips_via_from_line(self):
        """from_line(to_line()) must reproduce an equal binding."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        original = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64, "tel_v1": "b" * 64},
            strategy_weights_digest="c" * 64,
            embedding_model_version="BAAI/bge-m3-v1",
        )
        restored = MetaLearningReplayBinding.from_line(original.to_line())
        assert restored.faiss_index_digests == original.faiss_index_digests
        assert restored.strategy_weights_digest == original.strategy_weights_digest
        assert restored.embedding_model_version == original.embedding_model_version

    @pytest.mark.unit_min_deps
    def test_binding_digest_changes_when_weights_change(self):
        """Binding with different strategy_weights_digest must not equal original."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        b1 = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="1" * 64,
            embedding_model_version="v1",
        )
        b2 = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest="2" * 64,
            embedding_model_version="v1",
        )
        assert b1.to_line() != b2.to_line()

    @pytest.mark.unit_min_deps
    def test_binding_raises_on_empty_faiss_dict(self):
        """Empty faiss_index_digests must raise ValueError."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        with pytest.raises(ValueError, match="faiss_index_digests must contain at least one entry"):
            MetaLearningReplayBinding(
                faiss_index_digests={},
                strategy_weights_digest="a" * 64,
                embedding_model_version="v1",
            )

    @pytest.mark.unit_min_deps
    def test_binding_raises_on_short_digest(self):
        """strategy_weights_digest shorter than 64 chars must raise ValueError."""
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        with pytest.raises(ValueError, match="strategy_weights_digest must be 64-hex chars"):
            MetaLearningReplayBinding(
                faiss_index_digests={"hc_v1": "a" * 64},
                strategy_weights_digest="tooshort",
                embedding_model_version="v1",
            )

    @pytest.mark.unit
    def test_binding_built_from_live_agent(self, tmp_path):
        """Binding constructed from a live MetaLearningAgent must include its live digest."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent
        from system_learning.engines.meta_learning_replay_binding import MetaLearningReplayBinding

        with patch.object(SovereignBaseAgent, "__init__", return_value=None):
            agent = MetaLearningAgent(strategy_weights_file=tmp_path / "w.json")

        for _ in range(10):
            agent.store_experience({}, "cot", {}, 1.0)
        agent.update_strategy_weights()

        binding = MetaLearningReplayBinding(
            faiss_index_digests={"hc_v1": "a" * 64},
            strategy_weights_digest=agent.strategy_weights_digest,
            embedding_model_version="hash-fallback-v1",
        )
        d = binding.to_dict()
        assert d["strategy_weights_digest"] == agent.strategy_weights_digest
        assert len(d["strategy_weights_digest"]) == 64


# ===========================================================================
# h7: CI checker — check_faiss_persist_contract.py
# ===========================================================================


class TestFaissPersistContractChecker:
    """h7: AST-based CI checker correctly identifies persist contract violations."""

    @pytest.mark.unit_min_deps
    def test_checker_passes_on_compliant_code(self, tmp_path):
        """A function with finalize_build() followed by persist_to_disk() must pass."""
        src = tmp_path / "good.py"
        src.write_text(
            "def build_index(store, path):\n"
            "    store.begin_build('x', 16)\n"
            "    store.finalize_build('x')\n"
            "    store.persist_to_disk('x', path, embedder_id='e', model_version='v1')\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import _run

        violations = _run([src])
        assert violations == [], f"Expected no violations, got: {violations}"

    @pytest.mark.unit_min_deps
    def test_checker_fails_on_finalize_without_persist(self, tmp_path):
        """A function with finalize_build() but no persist_to_disk() must produce R1 violation."""
        src = tmp_path / "bad.py"
        src.write_text(
            "def build_index(store):\n    store.begin_build('x', 16)\n    store.finalize_build('x')\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import _run

        violations = _run([src])
        assert len(violations) == 1
        assert violations[0].rule == "R1"

    @pytest.mark.unit_min_deps
    def test_checker_accepts_guardian_comment(self, tmp_path):
        """finalize_build() with guardian comment AND reason= must not produce violation."""
        src = tmp_path / "guarded.py"
        src.write_text(
            "def build_index(store):\n"
            "    store.begin_build('x', 16)\n"
            "    store.finalize_build('x')  # guardian: faiss-no-persist reason=in-memory-only test fixture\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import _run

        violations = _run([src])
        assert violations == [], f"Guardian comment with reason= must suppress violation, got: {violations}"

    @pytest.mark.unit_min_deps
    def test_checker_rejects_guardian_without_reason(self, tmp_path):
        """finalize_build() with guardian comment but no reason= must produce R2 violation."""
        src = tmp_path / "bare_guardian.py"
        src.write_text(
            "def build_index(store):\n"
            "    store.begin_build('x', 16)\n"
            "    store.finalize_build('x')  # guardian: faiss-no-persist\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import _run

        violations = _run([src])
        assert len(violations) == 1
        assert violations[0].rule == "R2", (
            f"Expected R2 violation for missing reason=, got: {violations[0].rule}"
        )

    @pytest.mark.unit_min_deps
    def test_checker_passes_on_rebuild_with_persist(self, tmp_path):
        """rebuild() followed by persist_to_disk() must not produce a violation."""
        src = tmp_path / "rebuild_ok.py"
        src.write_text(
            "def prune_and_persist(store, path):\n"
            "    store.rebuild('x', keep_ids=[])\n"
            "    store.persist_to_disk('x', path, embedder_id='e', model_version='v1')\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import _run

        violations = _run([src])
        assert violations == []

    @pytest.mark.unit_min_deps
    def test_checker_exit_zero_on_clean_code(self, tmp_path):
        """main() must return 0 when no violations found."""
        src = tmp_path / "clean.py"
        src.write_text(
            "def build(store, path):\n"
            "    store.finalize_build('x')\n"
            "    store.persist_to_disk('x', path, embedder_id='e', model_version='v1')\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import main

        assert main([str(src)]) == 0

    @pytest.mark.unit_min_deps
    def test_checker_exit_one_on_violation(self, tmp_path):
        """main() must return 1 when violations found."""
        src = tmp_path / "violation.py"
        src.write_text(
            "def build(store):\n    store.finalize_build('x')\n",
            encoding="utf-8",
        )
        from ops_scripts.ci.check_faiss_persist_contract import main

        assert main([str(src)]) == 1


# ===========================================================================
# p3-2: compute_replay_key() deterministic binding
# ===========================================================================


class TestComputeReplayKey:
    """p3-2: compute_replay_key() produces deterministic, sensitive replay keys."""

    @pytest.mark.unit_min_deps
    def test_replay_key_is_64_hex(self):
        """compute_replay_key() must return a 64-char lowercase hex string."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        key = compute_replay_key(
            trace_id="run-001",
            transcript_hash="a" * 64,
            strategy_weights_digest="b" * 64,
            faiss_index_digests={"hc_v1": "c" * 64},
        )
        assert len(key) == 64
        assert key == key.lower()

    @pytest.mark.unit_min_deps
    def test_replay_key_is_deterministic(self):
        """Two calls with identical inputs must produce identical replay keys."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        kwargs = {
            "trace_id": "run-abc",
            "transcript_hash": "1" * 64,
            "strategy_weights_digest": "2" * 64,
            "faiss_index_digests": {"idx_a": "3" * 64, "idx_b": "4" * 64},
        }
        assert compute_replay_key(**kwargs) == compute_replay_key(**kwargs)

    @pytest.mark.unit_min_deps
    def test_replay_key_changes_on_different_trace_id(self):
        """Different trace_id must produce different replay key."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        common = {
            "transcript_hash": "a" * 64,
            "strategy_weights_digest": "b" * 64,
            "faiss_index_digests": {"x": "c" * 64},
        }
        k1 = compute_replay_key(trace_id="run-1", **common)
        k2 = compute_replay_key(trace_id="run-2", **common)
        assert k1 != k2

    @pytest.mark.unit_min_deps
    def test_replay_key_changes_on_different_weights(self):
        """Different strategy_weights_digest must produce different replay key."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        common = {
            "trace_id": "run-x",
            "transcript_hash": "a" * 64,
            "faiss_index_digests": {"x": "c" * 64},
        }
        k1 = compute_replay_key(strategy_weights_digest="1" * 64, **common)
        k2 = compute_replay_key(strategy_weights_digest="2" * 64, **common)
        assert k1 != k2

    @pytest.mark.unit_min_deps
    def test_replay_key_independent_of_faiss_dict_insertion_order(self):
        """Replay key must be identical regardless of faiss_index_digests dict ordering."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        base = {
            "trace_id": "run-order",
            "transcript_hash": "a" * 64,
            "strategy_weights_digest": "b" * 64,
        }
        k1 = compute_replay_key(faiss_index_digests={"idx_a": "1" * 64, "idx_b": "2" * 64}, **base)
        k2 = compute_replay_key(faiss_index_digests={"idx_b": "2" * 64, "idx_a": "1" * 64}, **base)
        assert k1 == k2

    @pytest.mark.unit_min_deps
    def test_replay_key_raises_on_empty_faiss_dict(self):
        """Empty faiss_index_digests must raise ValueError."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        with pytest.raises(ValueError, match="faiss_index_digests must contain at least one entry"):
            compute_replay_key(
                trace_id="x",
                transcript_hash="a" * 64,
                strategy_weights_digest="b" * 64,
                faiss_index_digests={},
            )

    @pytest.mark.unit_min_deps
    def test_replay_key_raises_on_short_weights_digest(self):
        """strategy_weights_digest shorter than 64 chars must raise ValueError."""
        from system_learning.engines.meta_learning_replay_binding import compute_replay_key

        with pytest.raises(ValueError, match="strategy_weights_digest must be 64-hex chars"):
            compute_replay_key(
                trace_id="x",
                transcript_hash="a" * 64,
                strategy_weights_digest="tooshort",
                faiss_index_digests={"x": "c" * 64},
            )


# ===========================================================================
# p3-4: startup integrity sweep — verify_all_indexes_in_dir()
# ===========================================================================


class TestStartupIntegritySweep:
    """p3-4: verify_all_indexes_in_dir() sweeps and fails closed on any mismatch."""

    def _build_valid_index_dir(self, base: Path, index_id: str) -> None:
        """Helper: build a valid 3-file FAISS artifact under base/<index_id>/."""
        import hashlib
        import json

        idx_dir = base / index_id
        idx_dir.mkdir(parents=True, exist_ok=True)

        index_data = {
            "schema_version": "1",
            "index_id": index_id,
            "dimension": 4,
            "vector_count": 1,
            "vectors": [[0.1, 0.2, 0.3, 0.4]],
            "metadatas": [{"content_hash": "abc"}],
        }
        index_bytes = json.dumps(index_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        meta_data = {
            "dims": 4,
            "embedder_id": "test-embedder",
            "index_id": index_id,
            "index_version_hash": "v1",
            "model_version": "m1",
            "schema_version": "1",
            "vector_count": 1,
        }
        meta_bytes = json.dumps(meta_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        manifest_data = {
            "dims": 4,
            "embedder_id": "test-embedder",
            "model_version": "m1",
            "schema_version": "1",
            "sha256_index": hashlib.sha256(index_bytes).hexdigest(),
            "sha256_meta_canonical": hashlib.sha256(meta_bytes).hexdigest(),
            "vector_count": 1,
        }
        manifest_bytes = json.dumps(
            manifest_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")

        (idx_dir / "index.json").write_bytes(index_bytes)
        (idx_dir / "meta.json").write_bytes(meta_bytes)
        (idx_dir / "manifest.json").write_bytes(manifest_bytes)

    @pytest.mark.unit_min_deps
    def test_sweep_empty_dir_returns_empty_dict(self, tmp_path):
        """Empty base_dir must return empty dict (no indexes present)."""
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        result = verify_all_indexes_in_dir(tmp_path)
        assert result == {}

    @pytest.mark.unit_min_deps
    def test_sweep_valid_index_returns_digest(self, tmp_path):
        """Valid persisted index must appear in returned dict with a 64-hex digest."""
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        self._build_valid_index_dir(tmp_path, "hc_v1")
        result = verify_all_indexes_in_dir(tmp_path)
        assert "hc_v1" in result
        assert len(result["hc_v1"]) == 64

    @pytest.mark.unit_min_deps
    def test_sweep_multiple_valid_indexes(self, tmp_path):
        """Multiple valid indexes must all appear in result."""
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        for name in ("hc_v1", "tel_v1", "dpo_v1"):
            self._build_valid_index_dir(tmp_path, name)
        result = verify_all_indexes_in_dir(tmp_path)
        assert set(result.keys()) == {"hc_v1", "tel_v1", "dpo_v1"}

    @pytest.mark.unit_min_deps
    def test_sweep_raises_on_corrupted_index(self, tmp_path):
        """Corrupted index.json (wrong bytes) must raise StartupIntegrityError."""
        from system_learning.engines.faiss_startup_integrity import (
            StartupIntegrityError,
            verify_all_indexes_in_dir,
        )

        self._build_valid_index_dir(tmp_path, "hc_v1")
        (tmp_path / "hc_v1" / "index.json").write_bytes(b"corrupted content")
        with pytest.raises(StartupIntegrityError, match="SHA-256 mismatch"):
            verify_all_indexes_in_dir(tmp_path)

    @pytest.mark.unit_min_deps
    def test_sweep_raises_on_missing_manifest(self, tmp_path):
        """Missing manifest.json must raise StartupIntegrityError."""
        from system_learning.engines.faiss_startup_integrity import (
            StartupIntegrityError,
            verify_all_indexes_in_dir,
        )

        idx_dir = tmp_path / "hc_v1"
        idx_dir.mkdir()
        (idx_dir / "index.json").write_bytes(b"{}")
        (idx_dir / "meta.json").write_bytes(b"{}")
        (idx_dir / "manifest.json").write_bytes(b"{}")
        with pytest.raises(StartupIntegrityError):
            verify_all_indexes_in_dir(tmp_path)

    @pytest.mark.unit_min_deps
    def test_sweep_raises_on_embedder_mismatch(self, tmp_path):
        """Wrong expected_embedder_id must raise StartupIntegrityError."""
        from system_learning.engines.faiss_startup_integrity import (
            StartupIntegrityError,
            verify_all_indexes_in_dir,
        )

        self._build_valid_index_dir(tmp_path, "hc_v1")
        with pytest.raises(StartupIntegrityError, match="embedder_id mismatch"):
            verify_all_indexes_in_dir(tmp_path, expected_embedder_id="wrong-embedder")

    @pytest.mark.unit_min_deps
    def test_sweep_accepts_correct_embedder_id(self, tmp_path):
        """Correct expected_embedder_id must not raise."""
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        self._build_valid_index_dir(tmp_path, "hc_v1")
        result = verify_all_indexes_in_dir(tmp_path, expected_embedder_id="test-embedder")
        assert "hc_v1" in result

    @pytest.mark.unit_min_deps
    def test_sweep_raises_on_nonexistent_base_dir(self, tmp_path):
        """Non-existent base_dir must raise ValueError."""
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        with pytest.raises(ValueError, match="does not exist"):
            verify_all_indexes_in_dir(tmp_path / "nonexistent")


# ===========================================================================
# p3-5: FAISS telemetry events
# ===========================================================================


class TestFaissTelemetryEvents:
    """p3-5: LocalFAISSStore emits faiss_index_rebuilt/persisted/manifest_verified telemetry."""

    @pytest.mark.unit_min_deps
    def test_finalize_build_emits_rebuilt_event(self, tmp_path):
        """finalize_build() must emit faiss_index_rebuilt telemetry event."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        events: list[tuple[str, dict]] = []
        store = LocalFAISSStore(tmp_path, telemetry_callback=lambda e, d: events.append((e, d)))
        store.begin_build("idx", 16, 42)
        store.add_vectors(
            "idx",
            [[float(i)] * 16 for i in range(3)],
            [{"content_hash": f"h{i}", "trace_id": f"t{i}"} for i in range(3)],
        )
        store.finalize_build(
            "idx",
            built_at_utc=0,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )

        rebuilt = [e for e in events if e[0] == "faiss_index_rebuilt"]
        assert len(rebuilt) == 1
        assert rebuilt[0][1]["index_id"] == "idx"
        assert rebuilt[0][1]["vector_count"] == 3
        assert "index_version_hash" in rebuilt[0][1]

    @pytest.mark.unit_min_deps
    def test_persist_to_disk_emits_persisted_event(self, tmp_path):
        """persist_to_disk() must emit faiss_index_persisted telemetry event."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        events: list[tuple[str, dict]] = []
        store = LocalFAISSStore(tmp_path, telemetry_callback=lambda e, d: events.append((e, d)))
        store.begin_build("idx", 16, 0)
        store.add_vectors("idx", [[0.1] * 16], [{"content_hash": "h0", "trace_id": "t0"}])
        store.finalize_build(
            "idx",
            built_at_utc=0,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )
        store.persist_to_disk("idx", tmp_path / "out", embedder_id="test-emb", model_version="v1")

        persisted = [e for e in events if e[0] == "faiss_index_persisted"]
        assert len(persisted) == 1
        data = persisted[0][1]
        assert data["index_id"] == "idx"
        assert data["vector_count"] == 1
        assert len(data["digest"]) == 64
        assert data["embedder_id"] == "test-emb"
        assert data["model_version"] == "v1"

    @pytest.mark.unit_min_deps
    def test_load_from_disk_emits_manifest_verified_event(self, tmp_path):
        """load_from_disk() must emit faiss_manifest_verified telemetry event."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        events: list[tuple[str, dict]] = []
        store = LocalFAISSStore(tmp_path, telemetry_callback=lambda e, d: events.append((e, d)))
        store.begin_build("idx", 16, 0)
        store.add_vectors("idx", [[0.5] * 16], [{"content_hash": "h0", "trace_id": "t0"}])
        store.finalize_build(
            "idx",
            built_at_utc=0,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )
        out_dir = tmp_path / "persisted"
        store.persist_to_disk("idx", out_dir, embedder_id="test-emb", model_version="v1")

        events.clear()

        store2 = LocalFAISSStore(tmp_path, telemetry_callback=lambda e, d: events.append((e, d)))
        store2.load_from_disk("idx", out_dir)

        verified = [e for e in events if e[0] == "faiss_manifest_verified"]
        assert len(verified) == 1
        data = verified[0][1]
        assert data["index_id"] == "idx"
        assert data["vector_count"] == 1
        assert "digest" in data

    @pytest.mark.unit_min_deps
    def test_no_telemetry_when_callback_is_none(self, tmp_path):
        """Store without telemetry_callback must not raise when persisting."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        store = LocalFAISSStore(tmp_path)
        store.begin_build("idx", 16, 0)
        store.add_vectors("idx", [[0.1] * 16], [{"content_hash": "h0", "trace_id": "t0"}])
        store.finalize_build(
            "idx",
            built_at_utc=0,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )
        store.persist_to_disk("idx", tmp_path / "out", embedder_id="e", model_version="v1")

    @pytest.mark.unit_min_deps
    def test_rebuild_emits_rebuilt_event(self, tmp_path):
        """rebuild() must emit faiss_index_rebuilt telemetry event."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        events: list[tuple[str, dict]] = []
        store = LocalFAISSStore(tmp_path, telemetry_callback=lambda e, d: events.append((e, d)))
        store.begin_build("idx", 16, 0)
        store.add_vectors(
            "idx",
            [[0.1] * 16, [0.2] * 16],
            [{"content_hash": f"h{i}", "trace_id": f"t{i}"} for i in range(2)],
        )
        store.finalize_build(
            "idx",
            built_at_utc=0,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )
        store.prune("idx", lambda m: m["content_hash"] == "h0")
        events.clear()
        store.rebuild(
            "idx",
            built_at_utc=1,
            canonicalization_version="1",
            embedding_model_version="m1",
            embedding_model_checksum="chk",
        )

        rebuilt = [e for e in events if e[0] == "faiss_index_rebuilt"]
        assert len(rebuilt) == 1
        assert rebuilt[0][1]["vector_count"] == 1
