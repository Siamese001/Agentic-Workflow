"""
_ssot_meta_learning.py — Meta-learning intake pipeline for execute_ssot.

Extracted from execute_ssot.py to reduce file size and improve cohesion.
All public symbols are re-exported from execute_ssot.py for backward compat.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _fire_meta_learning_intake(state_mgr: "object", now_utc: int, repo_root: Path) -> None:
    """Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline after each run.

    Both imports are guarded — if archived modules are not yet restored (pre-Wave 0B)
    this is a safe no-op. After Wave 0B restoration the full pipeline activates.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_fire_meta_learning_intake", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_fire_meta_learning_intake", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_fire_meta_learning_intake")
    REPO_ROOT = repo_root
    adapter = None
    try:
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        healing_actions = state_mgr.state.get("healing_actions", [])
        aggregator = HealingOutcomeAggregator(window_size=max(len(healing_actions), 1))
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text
            from agentic_core.L2_execution.healers.failure_signal_normalizer import normalize_failure_signal

            _bmg_embed = bmg_embed_text
            _normalizer = normalize_failure_signal
        except ImportError as e:
            raise ImportError(
                "BGE embeddings are required for meta-learning. Install sentence-transformers: pip install sentence-transformers"
            ) from e
        new_vectors: list[list[float]] = []
        _faiss_vectors: list[list[float]] = []
        _faiss_metas: list[dict] = []
        _bge_per_agent: dict[str, int] = {}
        _bge_arch_counts: dict[str, int] = {
            "meta_learning_embed": 0,
            "routing_novelty": 0,
            "semantic_cache": 0,
        }
        for action in healing_actions:
            failure_type_str: str = action.get("type") or action.get("routing_tier") or "UNKNOWN"
            healer_id: str = action.get("agent", "unknown")
            tier_str: str = action.get("tier") or action.get("routing_tier") or "L5"
            success_flag: bool = action.get("outcome", "SUCCESS") == "SUCCESS"
            failure_vector: tuple[float, ...] | None = None
            novelty_flag: bool = False
            _vec_source = "hash-fallback"
            territory_str: str = action.get("territory", "unknown")
            if _bmg_embed is not None and _normalizer is not None:
                try:
                    routing_signal_text = f"{failure_type_str} {territory_str}"
                    outcome_text = _normalizer(action)
                    routing_vec = _bmg_embed(routing_signal_text)
                    outcome_vec = _bmg_embed(outcome_text)
                    failure_vector = tuple(outcome_vec)
                    _vec_source = "bge-m3"
                    new_vectors.append(routing_vec)
                    _bge_per_agent[healer_id] = _bge_per_agent.get(healer_id, 0) + 2
                    _bge_arch_counts["meta_learning_embed"] += 2
                    recent = state_mgr.state.get("meta_learning", {}).get("recent_failure_vectors", [])
                    if recent:
                        import numpy as _np

                        q = _np.array(routing_vec, dtype=_np.float32)
                        mat = _np.array(recent, dtype=_np.float32)
                        sims = mat @ q
                        novelty_flag = bool(float(sims.max()) < 0.75)
                    else:
                        novelty_flag = True
                except (ValueError, AttributeError, ImportError) as e:
                    logging.debug(f"Novelty detection failed, using default: {e}")
                    novelty_flag = True
            if failure_vector is None:
                try:
                    _normalizer_fn = (
                        _normalizer if _normalizer is not None else lambda a: str(a.get("type", "UNKNOWN"))
                    )
                    _fb_text = _normalizer_fn(action)
                    from agentic_core.L2_execution.healers.failure_signal_normalizer import (
                        generate_fallback_vector as _gen_fallback,
                    )

                    failure_vector = tuple(_gen_fallback(_fb_text))
                except (ImportError, ValueError, AttributeError) as e:
                    logging.debug(f"Fallback vector generation failed: {e}")
            if failure_vector is not None:
                _faiss_vectors.append(list(failure_vector))
                _faiss_metas.append(
                    {
                        "content_hash": action.get("routing_digest") or "",
                        "trace_id": action.get("trace_id") or "",
                        "territory": territory_str,
                        "outcome": action.get("outcome", "UNKNOWN"),
                        "vector_source": _vec_source,
                    }
                )
            aggregator.ingest(
                HealingOutcomeEvent(
                    healer_id=healer_id,
                    tier=tier_str,
                    failure_type=failure_type_str,
                    success=success_flag,
                    timestamp_utc=now_utc,
                    routing_digest=action.get("routing_digest"),
                    confidence_score=action.get("confidence"),
                    failure_vector=failure_vector,
                    novelty_flag=novelty_flag,
                    cluster_id=action.get("cluster_id"),
                    files_touched=tuple(action.get("files_touched") or []),
                )
            )
        _routing_decisions = state_mgr.state.get("routing_decisions", []) if state_mgr is not None else []
        for _dec in _routing_decisions:
            _dagent = _dec.get("agent", "unknown")
            _bge_per_agent[_dagent] = _bge_per_agent.get(_dagent, 0) + 1
            _bge_arch_counts["routing_novelty"] += 1
        try:
            from agentic_core.cache.redis_cache_client import get_hot_cache as _ghc_bge

            _hc_bge = _ghc_bge()
            _cs = _hc_bge.get_stats()
            _bge_arch_counts["semantic_cache"] = _cs.get(
                "embed_calls", _cs.get("hits", 0) + _cs.get("misses", 0)
            )
        except (ImportError, AttributeError, KeyError):
            pass
        state_mgr.state.setdefault("meta_learning", {})["bge_per_agent"] = _bge_per_agent
        state_mgr.state["meta_learning"]["bge_arch_counts"] = _bge_arch_counts
        state_mgr.state["meta_learning"]["bge_model"] = "BAAI/bge-m3-v1"
        try:
            from system_learning.engines.healing_success_rate_store import get_default_store as _get_sr_store

            _sr_store = _get_sr_store()
            for _action in healing_actions:
                _sig = (
                    _action.get("routing_digest")
                    or f"{_action.get('agent', 'unknown')}:{_action.get('type', 'UNKNOWN')}"
                )
                _sr_store.record_outcome(_sig, _action.get("outcome", "SUCCESS") == "SUCCESS")
            state_mgr.state.setdefault("meta_learning", {})["success_rate_store"] = _sr_store.export_state()
        except (ImportError, AttributeError, KeyError) as _sr_err:
            logging.warning("[MetaLearning] Wave1 success_rate_store failed (non-fatal): %s", _sr_err)
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        if healing_actions:
            record = adapter.build_record(aggregator=aggregator, created_utc=now_utc, source="execute_ssot")
            adapter.persist_record(record)
            try:
                import json as _json_w2

                _corpus_path = REPO_ROOT / "data" / "corpus" / "healing_contexts_corpus.jsonl"
                _new_lines = []
                for _action in healing_actions:
                    _new_lines.append(
                        _json_w2.dumps(
                            {
                                "schema_version": 1,
                                "content_hash": _action.get("routing_digest", ""),
                                "trace_id": _action.get("trace_id", ""),
                                "namespace": "healing_contexts",
                                "created_utc": now_utc,
                                "healer_id": _action.get("agent", "unknown"),
                                "tier": _action.get("routing_tier") or _action.get("tier", "L5"),
                                "failure_type": _action.get("type", "UNKNOWN"),
                                "territory": _action.get("territory", "unknown"),
                                "outcome": _action.get("outcome", "UNKNOWN"),
                                "fix_summary": _action.get("fix_summary", ""),
                            },
                            separators=(",", ":"),
                            sort_keys=True,
                        )
                    )
                with open(_corpus_path, "a", encoding="utf-8") as _cf:
                    _cf.write("\n".join(_new_lines) + "\n")
            except (OSError, TypeError) as _w2_err:
                logging.warning("[MetaLearning] Wave2 JSONL corpus append failed (non-fatal): %s", _w2_err)
            try:
                from system_learning.stores.version_store import FileBackedVersionStore as _FBVS

                _intake_dir = REPO_ROOT / "data" / "golden_state" / "healing_intakes"
                _file_store = _FBVS(_intake_dir)
                _file_store.commit_change_package(record)
            except (ImportError, AttributeError, OSError) as _w3_err:
                logging.warning("[MetaLearning] Wave3 FileBackedVersionStore failed (non-fatal): %s", _w3_err)
        try:
            import json as _json_w4

            from system_learning.stores.version_store import FileBackedVersionStore as _FBVS4
            from system_learning.types.healing_outcome_types import HealingOutcomeEvent as _HOE4

            _intake_dir4 = REPO_ROOT / "data" / "golden_state" / "healing_intakes"
            _idx_path4 = _intake_dir4 / "_index.json"
            if _idx_path4.exists():
                _idx4 = _json_w4.loads(_idx_path4.read_text(encoding="utf-8"))
                _file_store4 = _FBVS4(_intake_dir4)
                _prior_vids = sorted(_idx4.keys())[-50:]
                for _vid in _prior_vids:
                    _raw4 = _file_store4.get(_vid)
                    if not _raw4:
                        continue
                    try:
                        _rec4 = _json_w4.loads(_raw4.decode("utf-8"))
                        for _s in _rec4.get("snapshot", []):
                            _hid4 = _s.get("healer_id", "unknown")
                            _tier4 = _s.get("tier", "L5")
                            _ftype4 = _s.get("failure_type", "UNKNOWN")
                            for _ in range(int(_s.get("success_count", 0))):
                                aggregator.ingest(
                                    _HOE4(
                                        healer_id=_hid4,
                                        tier=_tier4,
                                        failure_type=_ftype4,
                                        success=True,
                                        timestamp_utc=now_utc,
                                    )
                                )
                            for _ in range(int(_s.get("failure_count", 0))):
                                aggregator.ingest(
                                    _HOE4(
                                        healer_id=_hid4,
                                        tier=_tier4,
                                        failure_type=_ftype4,
                                        success=False,
                                        timestamp_utc=now_utc,
                                    )
                                )
                    except (KeyError, ValueError, TypeError):
                        continue
        except (ImportError, AttributeError, OSError) as _w4_err:
            logging.warning("[MetaLearning] Wave4 prior record merge failed (non-fatal): %s", _w4_err)
        if _faiss_vectors:
            try:
                from system_learning.engines.local_faiss_store import LocalFAISSStore as _FAISSStore
                from system_learning.engines.local_faiss_store import ManifestIntegrityError as _MIE

                _dim = len(_faiss_vectors[0])
                _faiss_idx = "healing_context_v1"
                _faiss_base = REPO_ROOT / "logs" / "faiss_store"
                _faiss_base.mkdir(parents=True, exist_ok=True)
                _faiss_disk_dir = _faiss_base / _faiss_idx
                _vec_source_str = "bge-m3"
                _model_ver = "BAAI/bge-m3-v1"
                _prior_vecs: list[list[float]] = []
                _prior_metas: list[dict] = []
                if _faiss_disk_dir.exists():
                    try:
                        _loader = _FAISSStore(base_path=_faiss_base)
                        _loader.load_from_disk(_faiss_idx, _faiss_disk_dir)
                        _loaded = _loader._memory_indexes.get(_faiss_idx, {})
                        _loaded_vecs = _loaded.get("vectors", [])
                        _loaded_metas = _loaded.get("metadatas", [])
                        if _loaded_vecs and len(_loaded_vecs[0]) == _dim:
                            _prior_vecs = _loaded_vecs
                            _prior_metas = _loaded_metas
                    # guardian: allow-silent-swallow
                    except (_MIE, Exception):
                        pass
                _all_vecs = _prior_vecs + _faiss_vectors
                _all_metas = _prior_metas + _faiss_metas
                _MAX_FAISS_VECS = 1000
                if len(_all_vecs) > _MAX_FAISS_VECS:
                    _all_vecs = _all_vecs[-_MAX_FAISS_VECS:]
                    _all_metas = _all_metas[-_MAX_FAISS_VECS:]
                _faiss_writer = _FAISSStore(base_path=_faiss_base)
                _faiss_writer.begin_build(_faiss_idx, _dim, seed=0)
                _faiss_writer.add_vectors(_faiss_idx, _all_vecs, _all_metas)
                _faiss_writer.finalize_build(
                    _faiss_idx,
                    built_at_utc=now_utc,
                    canonicalization_version="v1",
                    embedding_model_version=_model_ver,
                    embedding_model_checksum=_vec_source_str,
                )
                _faiss_writer.persist_to_disk(
                    _faiss_idx, _faiss_disk_dir, embedder_id=_vec_source_str, model_version=_model_ver
                )
                logging.debug(
                    "[MetaLearning] FAISS persist: %d new + %d prior = %d total -> %s",
                    len(_faiss_vectors),
                    len(_prior_vecs),
                    len(_all_vecs),
                    _faiss_disk_dir,
                )
            except (ImportError, AttributeError, OSError, ValueError) as _faiss_err:
                logging.warning("[MetaLearning] FAISS wiring failed (non-fatal): %s", _faiss_err)
        if new_vectors:
            ml_state = state_mgr.state.setdefault("meta_learning", {})
            existing_vecs: list = ml_state.get("recent_failure_vectors", [])
            merged = existing_vecs + new_vectors
            ml_state["recent_failure_vectors"] = merged[-200:]
        state_mgr.update_meta_learning(
            {
                "meta_learning_schema": 1,
                "total_experiences": store.count(),
                "experience": f"intake: {store.count()} healing records persisted",
            }
        )
        logging.info(
            "[MetaLearning] HealingOutcomeIntakeAdapter: %d records persisted to L4B store.", store.count()
        )
    except ImportError:
        logging.debug("[MetaLearning] Intake adapter not yet available (pre-Wave 0B). Skipping.")
    except (AttributeError, TypeError, OSError) as _ml_err:
        logging.warning("[MetaLearning] Intake adapter failed (non-fatal): %s", _ml_err)
    try:
        import time as _time_mod

        from system_learning.pipelines.meta_learning_pipeline import run_pipeline as _ml_run_pipeline
        from system_learning.pipelines.pipeline_factory import build_pipeline_config, build_pipeline_deps

        _apply_proposals = state_mgr.state.get("apply_proposals", False)
        _now_utc = int(_time_mod.time())
        _window_start_utc = max(0, _now_utc - 3600)
        _ml_cfg = build_pipeline_config(proposal_only=not _apply_proposals)
        _ml_deps = build_pipeline_deps(repo_root=REPO_ROOT, healing_outcome_intake_adapter=adapter)
        _ml_proposals = _ml_run_pipeline(
            now_utc=_now_utc,
            window_start_utc=_window_start_utc,
            window_end_utc=_now_utc,
            cfg=_ml_cfg,
            deps=_ml_deps,
        )
        if _ml_proposals:
            _prop_path = REPO_ROOT / "logs" / "proposals" / "threshold_proposals.jsonl"
            _prop_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                import json as _json_prop

                with open(_prop_path, "a", encoding="utf-8") as _pf:
                    for _p in _ml_proposals:
                        _pf.write(
                            _json_prop.dumps(
                                {
                                    "schema_version": 1,
                                    "created_utc": _now_utc,
                                    "payload": _p.canonical_bytes().decode("utf-8", errors="replace"),
                                },
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                            + "\n"
                        )
            except (OSError, TypeError) as _prop_err:
                logging.warning("[MetaLearning] proposal write failed: %s", _prop_err)
        logging.info("[MetaLearning] meta_learning_pipeline.run_pipeline() completed.")
    except ImportError as _imp_err:
        logging.debug("[MetaLearning] Pipeline not yet available (pre-Wave 0B): %s", _imp_err)
    except (AttributeError, TypeError, ValueError) as _pl_err:
        logging.warning("[MetaLearning] Pipeline run failed (non-fatal): %s", _pl_err)
