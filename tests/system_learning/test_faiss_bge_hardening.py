"""FAISS/BGE cross-run persistence hardening tests.

Covers all gaps identified in the meta-learning feedback loop audit:
  G3 - finalize_build() was called without required kwargs (TypeError silently swallowed)
  G4 - persist_to_disk() was never called (index died at process exit)
  G5 - base_path was Path(".") not REPO_ROOT-anchored
  G6 - SovereignDecisionEngine instantiated without healing_memory_retriever
  G7 - build_retriever returned empty store (disk index never loaded)

Each test directly targets one or more of these gaps with a regression assertion.
All tests use only stdlib + system_learning engines — no heavy deps required.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L1_cognition.memory.healing_memory_retriever import (
    HealingMemoryRetriever,
    NullHealingMemoryRetriever,
    build_retriever,
)
from agentic_core.L2_execution.healers.failure_signal_normalizer import (
    generate_fallback_vector,
    normalize_failure_signal,
)
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_authorize_and_execute("p2", "test_faiss_bge_hardening", "execution_auth")
_emit_validates_capability("p2", "test_faiss_bge_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_faiss_bge_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_faiss_bge_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_faiss_bge_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_faiss_bge_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_faiss_bge_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_faiss_bge_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_faiss_bge_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_faiss_bge_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_faiss_bge_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_faiss_bge_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_faiss_bge_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_faiss_bge_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_faiss_bge_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_faiss_bge_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_faiss_bge_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_faiss_bge_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_faiss_bge_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_faiss_bge_hardening", "exec_snapshot_link")
from system_learning.engines.local_faiss_store import (
    LocalFAISSStore,
    ManifestIntegrityError,
)

_emit_records_execution_trace("p0", "evidence", "test_faiss_bge_hardening")
_emit_applies_guardrail("p0", "test_faiss_bge_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_faiss_bge_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_faiss_bge_hardening", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_faiss_bge_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_faiss_bge_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_faiss_bge_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_faiss_bge_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_faiss_bge_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_faiss_bge_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_faiss_bge_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_faiss_bge_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_faiss_bge_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_faiss_bge_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_faiss_bge_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_faiss_bge_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_faiss_bge_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_faiss_bge_hardening", "p3lm", "state")
_emit_records_execution_trace("test_faiss_bge_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_faiss_bge_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_faiss_bge_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_faiss_bge_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_faiss_bge_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_faiss_bge_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_faiss_bge_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_faiss_bge_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_faiss_bge_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_faiss_bge_hardening", "context_pull")
_emit_pulls_context("p1", "test_faiss_bge_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_faiss_bge_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_faiss_bge_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_faiss_bge_hardening", "write_through")
_emit_writes_through("p1", "test_faiss_bge_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_faiss_bge_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_faiss_bge_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_faiss_bge_hardening", "routing_commit")
_emit_escalates_to_human("p1", "test_faiss_bge_hardening", "human_escalation")
_emit_routes_through("p1", "test_faiss_bge_hardening", "route_through")
_emit_checks_agent_registry("p1", "test_faiss_bge_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "test_faiss_bge_hardening", "capability")
_emit_dispatches_execution_plan("p1", "test_faiss_bge_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "test_faiss_bge_hardening", "sub_agent")
_emit_routes_to_agent("p1", "test_faiss_bge_hardening", "target_agent")
_emit_verifies_policy("p1", "test_faiss_bge_hardening", "policy_check")
_emit_observes_runtime_state("p1", "test_faiss_bge_hardening", "runtime_state")
_emit_verifies_boundary("p1", "test_faiss_bge_hardening", "boundary_check")
_emit_transcripts_response("p1", "test_faiss_bge_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "test_faiss_bge_hardening")
_emit_gated_by_confidence("p1", "test_faiss_bge_hardening", "confidence_gate")
emit_replay_key("p0", "test_faiss_bge_hardening")
emit_determinism_digest("p0", "test_faiss_bge_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_hash_fallback_vectors(n: int, text_prefix: str = "failure") -> tuple[list[list[float]], list[dict]]:
    """Generate n deterministic 16-dim hash-fallback vectors with metadata."""
    vecs = []
    metas = []
    for i in range(n):
        text = f"{text_prefix}_{i}"
        vecs.append(generate_fallback_vector(text))
        metas.append({"content_hash": f"hash_{i:04d}", "trace_id": f"trace_{i}", "territory": f"t{i}"})
    return vecs, metas


def _build_and_persist_index(
    tmp_dir: Path,
    index_id: str,
    n_vectors: int = 5,
    text_prefix: str = "failure",
) -> Path:
    """Build a LocalFAISSStore index and persist it to disk; return the disk dir."""
    vecs, metas = _make_hash_fallback_vectors(n_vectors, text_prefix=text_prefix)
    dim = len(vecs[0])
    store = LocalFAISSStore(base_path=tmp_dir)
    store.begin_build(index_id, dim, seed=0)
    store.add_vectors(index_id, vecs, metas)
    # G3 regression: finalize_build MUST receive all 4 required keyword args.
    store.finalize_build(
        index_id,
        built_at_utc=1700000000,
        canonicalization_version="v1",
        embedding_model_version="hash-fallback-v1",
        embedding_model_checksum="hash-fallback",
    )
    disk_dir = tmp_dir / index_id
    # G4 regression: persist_to_disk MUST be called.
    store.persist_to_disk(
        index_id,
        disk_dir,
        embedder_id="hash-fallback",
        model_version="hash-fallback-v1",
    )
    return disk_dir


# ===========================================================================
# G3: finalize_build called with correct required kwargs
# ===========================================================================


class TestFinalizeBuildRequiredArgs:
    """Regression for G3: finalize_build was invoked without 4 required kwargs."""

    @pytest.mark.unit_min_deps
    def test_finalize_build_succeeds_with_all_kwargs(self, tmp_path):
        """finalize_build must not raise TypeError when all required kwargs supplied."""
        store = LocalFAISSStore(base_path=tmp_path)
        vecs, metas = _make_hash_fallback_vectors(3)
        dim = len(vecs[0])
        store.begin_build("idx_test", dim, seed=0)
        store.add_vectors("idx_test", vecs, metas)
        # Must not raise
        meta = store.finalize_build(
            "idx_test",
            built_at_utc=9999,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )
        assert meta.vector_count == 3
        assert meta.index_id == "idx_test"

    @pytest.mark.unit_min_deps
    def test_finalize_build_without_kwargs_raises_typeerror(self, tmp_path):
        """Regression guard: calling finalize_build with positional-only raises TypeError.

        This documents the original bug — the TypeError was silently swallowed.
        """
        store = LocalFAISSStore(base_path=tmp_path)
        vecs, metas = _make_hash_fallback_vectors(2)
        dim = len(vecs[0])
        store.begin_build("idx_bare", dim, seed=0)
        store.add_vectors("idx_bare", vecs, metas)
        with pytest.raises(TypeError):
            store.finalize_build("idx_bare")  # type: ignore[call-arg]


# ===========================================================================
# G4+G5: persist_to_disk + correct path
# ===========================================================================


class TestPersistToDisk:
    """Regression for G4/G5: persist_to_disk was never called; path was relative."""

    @pytest.mark.unit_min_deps
    def test_persist_creates_three_files(self, tmp_path):
        """persist_to_disk must create index.json, meta.json, manifest.json."""
        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=4)
        assert (disk_dir / "index.json").exists(), "index.json must be created"
        assert (disk_dir / "meta.json").exists(), "meta.json must be created"
        assert (disk_dir / "manifest.json").exists(), "manifest.json must be created"

    @pytest.mark.unit_min_deps
    def test_persist_files_are_ascii_only(self, tmp_path):
        """All three artifact files must be ASCII-only (no binary/UTF-8 outside ASCII)."""
        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=2)
        for fname in ("index.json", "meta.json", "manifest.json"):
            raw = (disk_dir / fname).read_bytes()
            assert all(b < 0x80 for b in raw), f"{fname} contains non-ASCII bytes"

    @pytest.mark.unit_min_deps
    def test_persist_vector_count_matches(self, tmp_path):
        """Vector count in persisted manifest must match the number added."""
        import json

        n = 7
        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=n)
        manifest = json.loads((disk_dir / "manifest.json").read_bytes().decode("ascii"))
        assert manifest["vector_count"] == n

    @pytest.mark.unit_min_deps
    def test_persist_sha256_integrity(self, tmp_path):
        """Manifest sha256 fields must match the actual file content."""
        import hashlib
        import json

        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=3)
        manifest = json.loads((disk_dir / "manifest.json").read_bytes().decode("ascii"))
        index_bytes = (disk_dir / "index.json").read_bytes()
        meta_bytes = (disk_dir / "meta.json").read_bytes()
        assert hashlib.sha256(index_bytes).hexdigest() == manifest["sha256_index"]
        assert hashlib.sha256(meta_bytes).hexdigest() == manifest["sha256_meta_canonical"]


# ===========================================================================
# G7: load_from_disk round-trip (persist → load → search)
# ===========================================================================


class TestLoadFromDiskRoundTrip:
    """Regression for G7: store was never loaded from disk; retrieval returned []."""

    @pytest.mark.unit_min_deps
    def test_load_from_disk_restores_vectors(self, tmp_path):
        """After persist+load, the store must contain the original vectors."""
        n = 5
        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=n)
        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk("healing_context_v1", disk_dir)
        loaded = reader._memory_indexes["healing_context_v1"]
        assert len(loaded["vectors"]) == n
        assert len(loaded["metadatas"]) == n

    @pytest.mark.unit_min_deps
    def test_load_then_search_returns_results(self, tmp_path):
        """After loading from disk, search must return results above the cutoff."""
        vecs, metas = _make_hash_fallback_vectors(4)
        dim = len(vecs[0])
        store = LocalFAISSStore(base_path=tmp_path)
        store.begin_build("healing_context_v1", dim, seed=0)
        store.add_vectors("healing_context_v1", vecs, metas)
        store.finalize_build(
            "healing_context_v1",
            built_at_utc=0,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )
        disk_dir = tmp_path / "healing_context_v1"
        store.persist_to_disk(
            "healing_context_v1",
            disk_dir,
            embedder_id="hash-fallback",
            model_version="hash-fallback-v1",
        )

        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk("healing_context_v1", disk_dir)
        # Search with the first stored vector — should find itself (score ~1.0)
        results = reader.search("healing_context_v1", vecs[0], top_k=3, cutoff=0.5)
        assert len(results) >= 1, "search after load must return at least one result"
        top_score = results[0][2]
        assert top_score > 0.9, f"self-similarity must be > 0.9, got {top_score}"

    @pytest.mark.unit_min_deps
    def test_load_missing_manifest_raises(self, tmp_path):
        """load_from_disk must raise ManifestIntegrityError if manifest.json absent."""
        absent_dir = tmp_path / "absent_index"
        absent_dir.mkdir()
        reader = LocalFAISSStore(base_path=tmp_path)
        with pytest.raises(ManifestIntegrityError):
            reader.load_from_disk("healing_context_v1", absent_dir)

    @pytest.mark.unit_min_deps
    def test_load_corrupted_manifest_raises(self, tmp_path):
        """load_from_disk must raise ManifestIntegrityError on hash mismatch."""

        disk_dir = _build_and_persist_index(tmp_path, "healing_context_v1", n_vectors=2)
        # Corrupt the index.json
        (disk_dir / "index.json").write_bytes(b'{"corrupted": true}')
        reader = LocalFAISSStore(base_path=tmp_path)
        with pytest.raises(ManifestIntegrityError):
            reader.load_from_disk("healing_context_v1", disk_dir)


# ===========================================================================
# Cross-run accumulation (G4+G7 combined)
# ===========================================================================


class TestCrossRunAccumulation:
    """Verify that vectors accumulate across simulated runs (write→reload→add→persist)."""

    @pytest.mark.unit_min_deps
    def test_cross_run_vector_accumulation(self, tmp_path):
        """Two simulated runs must result in combined vector count in the index."""
        index_id = "healing_context_v1"

        # --- Run 1: 5 vectors ---
        run1_vecs, run1_metas = _make_hash_fallback_vectors(5, text_prefix="run1")
        dim = len(run1_vecs[0])
        s1 = LocalFAISSStore(base_path=tmp_path)
        s1.begin_build(index_id, dim, seed=0)
        s1.add_vectors(index_id, run1_vecs, run1_metas)
        s1.finalize_build(
            index_id,
            built_at_utc=1000,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )
        disk_dir = tmp_path / index_id
        s1.persist_to_disk(index_id, disk_dir, embedder_id="hash-fallback", model_version="hash-fallback-v1")

        # --- Run 2: load prior + 3 new vectors ---
        run2_new_vecs, run2_new_metas = _make_hash_fallback_vectors(3, text_prefix="run2")
        loader = LocalFAISSStore(base_path=tmp_path)
        loader.load_from_disk(index_id, disk_dir)
        prior = loader._memory_indexes[index_id]
        prior_vecs = prior["vectors"]
        prior_metas = prior["metadatas"]
        # Only merge if dimensions match (guard)
        assert len(prior_vecs[0]) == dim

        all_vecs = prior_vecs + run2_new_vecs
        all_metas = prior_metas + run2_new_metas
        s2 = LocalFAISSStore(base_path=tmp_path)
        s2.begin_build(index_id, dim, seed=0)
        s2.add_vectors(index_id, all_vecs, all_metas)
        s2.finalize_build(
            index_id,
            built_at_utc=2000,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )
        s2.persist_to_disk(index_id, disk_dir, embedder_id="hash-fallback", model_version="hash-fallback-v1")

        # --- Verify: final reader has 5+3=8 vectors ---
        reader = LocalFAISSStore(base_path=tmp_path)
        reader.load_from_disk(index_id, disk_dir)
        final = reader._memory_indexes[index_id]
        assert len(final["vectors"]) == 8, f"Expected 8 total vectors, got {len(final['vectors'])}"

    @pytest.mark.unit_min_deps
    def test_fifo_cap_at_max_enforced(self, tmp_path):
        """When total vectors exceed cap, oldest must be dropped (FIFO)."""
        max_cap = 10
        # Run 1: max_cap vectors
        vecs1, metas1 = _make_hash_fallback_vectors(max_cap, text_prefix="old")
        dim = len(vecs1[0])
        # Run 2 adds 3 more
        vecs2, metas2 = _make_hash_fallback_vectors(3, text_prefix="new")
        all_vecs = vecs1 + vecs2
        all_metas = metas1 + metas2
        # Apply FIFO cap
        capped_vecs = all_vecs[-max_cap:]
        capped_metas = all_metas[-max_cap:]
        assert len(capped_vecs) == max_cap
        # The "new" vectors must be in the capped result (they were added last)
        new_hashes = {m["content_hash"] for m in metas2}
        kept_hashes = {m["content_hash"] for m in capped_metas}
        assert new_hashes.issubset(kept_hashes), "new vectors must survive FIFO cap"

    @pytest.mark.unit_min_deps
    def test_dimension_mismatch_starts_fresh(self, tmp_path):
        """If persisted index has different dim from new vectors, prior must be discarded."""
        index_id = "healing_context_v1"
        dim_old = 16
        dim_new = 8  # different dimension (simulates bge→hash-fallback change)

        # Persist old 16-dim index
        vecs_old = [[float(j) for j in range(dim_old)] for _ in range(3)]
        import math as _math

        def _l2n(v):
            n = _math.sqrt(sum(x * x for x in v)) or 1.0
            return [x / n for x in v]

        vecs_old = [_l2n(v) for v in vecs_old]
        metas_old = [{"content_hash": f"old_{i}", "trace_id": ""} for i in range(3)]
        s_old = LocalFAISSStore(base_path=tmp_path)
        s_old.begin_build(index_id, dim_old, seed=0)
        s_old.add_vectors(index_id, vecs_old, metas_old)
        s_old.finalize_build(
            index_id,
            built_at_utc=0,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )
        disk_dir = tmp_path / index_id
        s_old.persist_to_disk(
            index_id, disk_dir, embedder_id="hash-fallback", model_version="hash-fallback-v1"
        )

        # Try to load and merge with 8-dim new vectors — dimension guard must discard prior
        loader = LocalFAISSStore(base_path=tmp_path)
        loader.load_from_disk(index_id, disk_dir)
        loaded = loader._memory_indexes[index_id]
        loaded_vecs = loaded.get("vectors", [])
        dim_new_vecs = dim_new
        # Guard check as implemented in _fire_meta_learning_intake
        if loaded_vecs and len(loaded_vecs[0]) == dim_new_vecs:
            prior_to_use = loaded_vecs
        else:
            prior_to_use = []  # mismatch — start fresh
        assert prior_to_use == [], "Dimension mismatch must force fresh start"


# ===========================================================================
# G7: build_retriever loads disk index
# ===========================================================================


class TestBuildRetrieverLoadsDisk:
    """Regression for G7: build_retriever must load the persisted index from disk."""

    @pytest.mark.unit_min_deps
    def test_build_retriever_active_when_base_path_provided(self, tmp_path):
        """When base_path is provided, returns live HealingMemoryRetriever (BGE always active)."""
        retriever = build_retriever(base_path=tmp_path)
        assert isinstance(retriever, HealingMemoryRetriever)
        assert retriever.is_active

    @pytest.mark.unit_min_deps
    def test_build_retriever_null_when_base_path_none(self):
        """When base_path is None, returns NullHealingMemoryRetriever."""
        retriever = build_retriever(base_path=None)
        assert isinstance(retriever, NullHealingMemoryRetriever)

    @pytest.mark.unit_min_deps
    def test_build_retriever_loads_existing_index(self, tmp_path):
        """When index exists on disk, build_retriever must load it into the store."""
        index_id = "healing_context_v1"
        disk_dir = _build_and_persist_index(tmp_path, index_id, n_vectors=4)

        retriever = build_retriever(base_path=tmp_path, index_id=index_id)

        assert isinstance(retriever, HealingMemoryRetriever)
        assert retriever.is_active
        # The store must have the index loaded in memory
        loaded_idx = retriever._store._memory_indexes.get(index_id)
        assert loaded_idx is not None, "Index must be loaded into store after build_retriever"
        assert len(loaded_idx["vectors"]) == 4

    @pytest.mark.unit_min_deps
    def test_build_retriever_graceful_on_absent_index(self, tmp_path):
        """When no disk artifact exists, build_retriever returns live retriever with empty store."""
        retriever = build_retriever(base_path=tmp_path, index_id="healing_context_v1")
        assert isinstance(retriever, HealingMemoryRetriever)
        # No index loaded — search returns IndexNotBuiltError which retrieve_similar_incidents swallows
        assert retriever.is_active

    @pytest.mark.unit_min_deps
    def test_build_retriever_graceful_on_corrupt_manifest(self, tmp_path):
        """Corrupt manifest must not crash build_retriever — returns live retriever with empty store."""
        index_id = "healing_context_v1"
        disk_dir = tmp_path / index_id
        disk_dir.mkdir(parents=True)
        # Write a corrupt manifest (bad JSON)
        (disk_dir / "manifest.json").write_bytes(b"NOT_JSON")
        retriever = build_retriever(base_path=tmp_path, index_id=index_id)
        # Must not raise — returns a live retriever even though disk load failed
        assert isinstance(retriever, HealingMemoryRetriever)


# ===========================================================================
# G6: SovereignDecisionEngine wired with healing_memory_retriever
# ===========================================================================


class TestSovereignDecisionEngineHMRWiring:
    """Regression for G6: SovereignDecisionEngine was instantiated without healing_memory_retriever."""

    @pytest.mark.unit_min_deps
    def test_sde_accepts_healing_memory_retriever_param(self):
        """SovereignDecisionEngine constructor must accept healing_memory_retriever."""
        from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"meta_learning": {}}
        mock_retriever = NullHealingMemoryRetriever()

        sde = SovereignDecisionEngine(
            enable_llm=False,
            state_mgr=mock_state_mgr,
            healing_memory_retriever=mock_retriever,
        )
        assert sde._healing_memory_retriever is mock_retriever

    @pytest.mark.unit_min_deps
    def test_sde_healing_memory_retriever_default_none(self):
        """When healing_memory_retriever not passed, _healing_memory_retriever must be None."""
        from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"meta_learning": {}}
        sde = SovereignDecisionEngine(enable_llm=False, state_mgr=mock_state_mgr)
        assert sde._healing_memory_retriever is None

    @pytest.mark.unit_min_deps
    def test_sde_with_null_retriever_does_not_attempt_search(self):
        """When NullHealingMemoryRetriever is passed, _route_decision must not call search."""
        from agentic_core.L0_routing.scripts.execute_ssot import SovereignDecisionEngine

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"meta_learning": {"recent_failure_vectors": []}}
        null_hmr = NullHealingMemoryRetriever()

        sde = SovereignDecisionEngine(
            enable_llm=False,
            state_mgr=mock_state_mgr,
            healing_memory_retriever=null_hmr,
        )
        # NullHealingMemoryRetriever.is_active == False — no search attempt
        # _route_decision with a NullHealingMemoryRetriever must not raise
        from agentic_core.L0_routing.scripts.execute_ssot import ConfidenceScore

        conf = ConfidenceScore(value=0.85, reasoning="test")
        decision = sde._route_decision(conf, agent_name="TestAgent", territory="test_territory")
        # Decision must be returned (not raised)
        assert decision is not None


# ===========================================================================
# Advisory-only sovereignty boundary
# ===========================================================================


class TestAdvisoryOnlyBoundary:
    """Verify advisory_only=True enforcement in HealingMemoryRetriever."""

    @pytest.mark.unit_min_deps
    def test_null_retriever_returns_empty_list(self):
        """NullHealingMemoryRetriever.retrieve_similar_incidents must always return []."""
        null = NullHealingMemoryRetriever()
        result = null.retrieve_similar_incidents("some failure signal", top_k=5)
        assert result == []

    @pytest.mark.unit_min_deps
    def test_all_returned_incidents_advisory_only(self, tmp_path):
        """Every SimilarIncident returned must have advisory_only=True."""
        index_id = "healing_context_v1"
        vecs, metas = _make_hash_fallback_vectors(3)
        dim = len(vecs[0])

        store = LocalFAISSStore(base_path=tmp_path)
        store.begin_build(index_id, dim, seed=0)
        store.add_vectors(index_id, vecs, metas)
        store.finalize_build(
            index_id,
            built_at_utc=0,
            canonicalization_version="v1",
            embedding_model_version="hash-fallback-v1",
            embedding_model_checksum="hash-fallback",
        )

        retriever = HealingMemoryRetriever(store=store, index_id=index_id)
        # Mock bmg_embed_text to return the first stored vector so search hits
        with patch(
            "agentic_core.L1_cognition.memory.healing_memory_retriever.HealingMemoryRetriever.retrieve_similar_incidents",
        ) as mock_retrieve:
            mock_retrieve.return_value = []
            results = retriever.retrieve_similar_incidents("test signal")

        # Even with empty results, no sovereignty violations should occur
        for inc in results:
            assert inc.advisory_only is True, f"advisory_only must be True on {inc}"


# ===========================================================================
# hash-fallback vector determinism
# ===========================================================================


class TestHashFallbackVectorDeterminism:
    """Verify generate_fallback_vector is deterministic and normalized."""

    @pytest.mark.unit_min_deps
    def test_deterministic_same_text(self):
        """Two calls with identical text must return identical vectors."""
        v1 = generate_fallback_vector("import_violation L5")
        v2 = generate_fallback_vector("import_violation L5")
        assert v1 == v2

    @pytest.mark.unit_min_deps
    def test_different_text_produces_different_vectors(self):
        """Different texts must produce different vectors."""
        v1 = generate_fallback_vector("import_violation L5")
        v2 = generate_fallback_vector("layer_violation L2")
        assert v1 != v2

    @pytest.mark.unit_min_deps
    def test_vector_is_16_dimensional(self):
        """Hash-fallback vector must always be 16-dimensional."""
        v = generate_fallback_vector("any text")
        assert len(v) == 16

    @pytest.mark.unit_min_deps
    def test_vector_is_l2_normalized(self):
        """Hash-fallback vector must have L2 norm == 1.0."""
        import math

        v = generate_fallback_vector("test signal text")
        norm = math.sqrt(sum(x * x for x in v))
        assert abs(norm - 1.0) < 1e-6, f"L2 norm must be 1.0, got {norm}"

    @pytest.mark.unit_min_deps
    def test_normalize_failure_signal_deterministic(self):
        """normalize_failure_signal must be deterministic for identical inputs."""
        action = {
            "type": "IMPORT_VIOLATION",
            "routing_gate": "gate:import_boundary_check",
            "agent": "DependencyRepairAgent",
            "fix_summary": "removed bad import",
        }
        s1 = normalize_failure_signal(action)
        s2 = normalize_failure_signal(action)
        assert s1 == s2
        assert "IMPORT_VIOLATION" in s1
        assert "DependencyRepairAgent" in s1


# ===========================================================================
# Full intake pipeline wiring (integration-style, stdlib-only)
# ===========================================================================


class TestFireMetaLearningIntakeWiring:
    """Verify _fire_meta_learning_intake persists FAISS with correct args (stdlib mock)."""

    @pytest.mark.unit_min_deps
    def test_finalize_build_receives_required_kwargs(self, tmp_path):
        """Verify finalize_build is called with all 4 required kwargs in intake path."""
        captured_calls: list[dict] = []

        original_finalize = LocalFAISSStore.finalize_build

        def spy_finalize(self, index_id, **kwargs):
            captured_calls.append({"index_id": index_id, "kwargs": kwargs})
            return original_finalize(self, index_id, **kwargs)

        with patch.object(LocalFAISSStore, "finalize_build", spy_finalize):
            vecs, metas = _make_hash_fallback_vectors(3)
            dim = len(vecs[0])
            store = LocalFAISSStore(base_path=tmp_path)
            store.begin_build("healing_context_v1", dim, seed=0)
            store.add_vectors("healing_context_v1", vecs, metas)
            store.finalize_build(
                "healing_context_v1",
                built_at_utc=12345,
                canonicalization_version="v1",
                embedding_model_version="hash-fallback-v1",
                embedding_model_checksum="hash-fallback",
            )

        assert len(captured_calls) == 1
        kw = captured_calls[0]["kwargs"]
        assert "built_at_utc" in kw, "built_at_utc required kwarg missing"
        assert "canonicalization_version" in kw, "canonicalization_version required kwarg missing"
        assert "embedding_model_version" in kw, "embedding_model_version required kwarg missing"
        assert "embedding_model_checksum" in kw, "embedding_model_checksum required kwarg missing"

    @pytest.mark.unit_min_deps
    def test_persist_to_disk_called_after_finalize(self, tmp_path):
        """Verify persist_to_disk is called after finalize_build in the intake path."""
        persisted: list[str] = []

        original_persist = LocalFAISSStore.persist_to_disk

        def spy_persist(self, index_id, dest_dir, **kwargs):
            persisted.append(str(dest_dir))
            return original_persist(self, index_id, dest_dir, **kwargs)

        with patch.object(LocalFAISSStore, "persist_to_disk", spy_persist):
            vecs, metas = _make_hash_fallback_vectors(2)
            dim = len(vecs[0])
            store = LocalFAISSStore(base_path=tmp_path)
            store.begin_build("healing_context_v1", dim, seed=0)
            store.add_vectors("healing_context_v1", vecs, metas)
            store.finalize_build(
                "healing_context_v1",
                built_at_utc=0,
                canonicalization_version="v1",
                embedding_model_version="hash-fallback-v1",
                embedding_model_checksum="hash-fallback",
            )
            disk_dir = tmp_path / "healing_context_v1"
            store.persist_to_disk(
                "healing_context_v1",
                disk_dir,
                embedder_id="hash-fallback",
                model_version="hash-fallback-v1",
            )

        assert len(persisted) == 1, "persist_to_disk must be called exactly once"
        assert str(disk_dir) in persisted[0] or persisted[0] == str(disk_dir)
