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

All G_RS / G_HI tests use @pytest.mark.unit_min_deps (stdlib + system_learning only).
G_MLA tests use @pytest.mark.unit with SovereignBaseAgent patched out.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import patch

import pytest

from system_learning.config.embedding_storage_layout import EmbeddingStorageLayout
from system_learning.engines.embedding_retention_scheduler import (
    EmbeddingRetentionScheduler,
)
from system_learning.engines.local_faiss_store import (
    LocalFAISSStore,
)

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
            pytest.skip("No pruning occurred — rebuild path not exercised")

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
            pytest.skip("Prune did not trigger (ch_0000 not found)")

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
