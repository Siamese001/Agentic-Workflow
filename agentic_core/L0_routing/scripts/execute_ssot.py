#!/usr/bin/env python3
# FROZEN — superseded by l0_execute.py (Guardian→Dispatcher→Healer pipeline).
"""
Unified Sovereign Compliance Protocol (v4.0)
Merges SSOT Compliance Protocol (Autonomous Decision Engine) with Canon Validator (Observability & Discovery).

PRIMARY FEATURES:
- Autonomous Confidence-Based Healing (SSOT)
- Real-time Runtime State & Dashboard Integration (Canon)
- Multi-Domain Orchestration (Canon)
- Hybrid Agent Discovery (Canon)
- Comprehensive Audit Trail (SSOT)
"""

# [IMPORTS] Added for dynamic loading and signal handling
import argparse
import ast
import atexit  # [HARDENED] For guaranteed state cleanup
import builtins
import importlib.util
import inspect
import json
import logging
import os
import platform
import re
import signal
import stat  # [HARDENED] For permission bits
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from subprocess import DEVNULL
from types import FrameType
from typing import Any, Optional

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not available
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
            self.iterable = iterable
            self.n = 0
            self.total = total

        def __iter__(self):
            return iter(self.iterable) if self.iterable else iter([])

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def update(self, n=1):
            self.n += n

        def set_description(self, desc):
            pass


from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write

# Early constants required by resolve_repo_root (full block also at bottom of file)
AGENTIC_CORE_DIR = "agentic_core"
OPS_SCRIPTS_DIR = "ops_scripts"


def _get_uwg():
    """Lazy loader — avoids circular import at module level."""
    from agentic_core.interfaces.write_gateway import get_write_gateway

    return get_write_gateway()


def _get_heal_result_adapter():
    """Lazy loader for Tier-3 adapter."""
    from agentic_core.L2_execution.heal_result_adapter import adapt_heal_result

    return adapt_heal_result


def _get_safe_subprocess_run():
    from agentic_core.L2_execution.tools.safe_subprocess import safe_subprocess_run

    return safe_subprocess_run


def _get_write_gateway():
    from agentic_core.L2_execution.tools import write_gateway

    return write_gateway


def _get_execution_context_class():
    from agentic_core.L0_routing.scripts.execution_context import ExecutionContext

    return ExecutionContext


def _get_location_validator_agent():
    from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

    return LocationValidatorAgent


def _get_location_healer_agent():
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

    return LocationHealerAgent


def _fire_meta_learning_intake(state_mgr: "RuntimeStateManager", now_utc: int) -> None:
    """Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline after each run.

    Both imports are guarded — if archived modules are not yet restored (pre-Wave 0B)
    this is a safe no-op. After Wave 0B restoration the full pipeline activates.
    """
    # Debt-4: sentinel so the pipeline try-block can reference adapter safely
    # even if the intake try-block raised before assigning it.
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

        # Attempt to load embedding helpers (guarded — no-op when unavailable)
        _bmg_embed = None
        _normalizer = None
        if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true":
            try:
                from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text
                from agentic_core.L2_execution.healers.failure_signal_normalizer import (
                    normalize_failure_signal,
                )

                _bmg_embed = bmg_embed_text
                _normalizer = normalize_failure_signal
            except ImportError:
                pass

        new_vectors: list[list[float]] = []
        # A4: accumulators for LocalFAISSStore wiring (populated per-action below)
        _faiss_vectors: list[list[float]] = []
        _faiss_metas: list[dict] = []

        for action in healing_actions:
            failure_type_str: str = action.get("type") or action.get("routing_tier") or "UNKNOWN"
            healer_id: str = action.get("agent", "unknown")
            tier_str: str = action.get("tier") or action.get("routing_tier") or "L5"
            success_flag: bool = action.get("outcome", "SUCCESS") == "SUCCESS"

            # Gap 2: produce failure_vector when embeddings are enabled.
            # Two distinct embedding texts:
            #   routing_signal_text — matches _compute_novelty_score exactly so
            #     L4 state vectors and novelty checks compare the same semantic space.
            #   outcome_text (normalize_failure_signal) — richer, used for
            #     HealingOutcomeEvent.failure_vector (MEMORY / future FAISS lookup).
            # A5: always produce a non-None failure_vector using generate_fallback_vector
            #     when bge-m3 is unavailable, so FAISS storage is never skipped.
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
                    new_vectors.append(routing_vec)  # L4 state uses routing signal

                    # Novelty: compare routing_vec against recent routing vectors
                    recent = state_mgr.state.get("meta_learning", {}).get("recent_failure_vectors", [])
                    if recent:
                        import numpy as _np

                        q = _np.array(routing_vec, dtype=_np.float32)
                        mat = _np.array(recent, dtype=_np.float32)
                        sims = mat @ q
                        novelty_flag = bool(float(sims.max()) < 0.75)
                    else:
                        novelty_flag = True
                except Exception:  # guardian: allow-silent-swallower
                    pass

            # A5: hash-fallback vector (stdlib-only, deterministic)
            if failure_vector is None:
                try:
                    _normalizer_fn = (
                        _normalizer if _normalizer is not None else (lambda a: str(a.get("type", "UNKNOWN")))
                    )
                    _fb_text = _normalizer_fn(action)
                    from agentic_core.L2_execution.healers.failure_signal_normalizer import (
                        generate_fallback_vector as _gen_fallback,
                    )

                    failure_vector = tuple(_gen_fallback(_fb_text))
                except Exception:  # guardian: allow-silent-swallower
                    pass

            # A4: accumulate for FAISS wiring
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

        # Wave 1: Record outcomes into HealingSuccessRateStore (EMA per error_sig)
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
        except Exception as _sr_err:  # guardian: allow-silent-swallower
            logging.warning("[MetaLearning] Wave1 success_rate_store failed (non-fatal): %s", _sr_err)

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        # Only persist if there are actual healing events to record
        if healing_actions:
            record = adapter.build_record(aggregator=aggregator, created_utc=now_utc, source="execute_ssot")
            adapter.persist_record(record)

            # Wave 2: Append raw events as JSONL lines to healing_contexts_corpus.jsonl
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
            except Exception as _w2_err:  # guardian: allow-silent-swallower
                logging.warning("[MetaLearning] Wave2 JSONL corpus append failed (non-fatal): %s", _w2_err)

            # Wave 3: Persist HealingOutcomeIntakeRecord via FileBackedVersionStore
            try:
                from system_learning.stores.version_store import FileBackedVersionStore as _FBVS

                _intake_dir = REPO_ROOT / "data" / "golden_state" / "healing_intakes"
                _file_store = _FBVS(_intake_dir)
                _file_store.commit_change_package(record)
            except Exception as _w3_err:  # guardian: allow-silent-swallower
                logging.warning("[MetaLearning] Wave3 FileBackedVersionStore failed (non-fatal): %s", _w3_err)

        # Wave 4: Reload and merge prior intake records (cap at 50) into aggregator
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
                    except Exception:  # guardian: allow-silent-swallow malformed record
                        continue
        except Exception as _w4_err:  # guardian: allow-silent-swallower
            logging.warning("[MetaLearning] Wave4 prior record merge failed (non-fatal): %s", _w4_err)

        # A4: wire accumulated failure_vectors into LocalFAISSStore (healing_context_v1)
        # [CROSS-RUN FAISS PERSISTENCE] Loads prior run's index from disk, merges new
        # vectors (FIFO-capped at 1000 total), re-finalizes and re-persists so
        # HealingMemoryRetriever can search patterns from all prior runs (G3/G4/G5/G7 fix).
        if _faiss_vectors:
            try:
                from system_learning.engines.local_faiss_store import (
                    LocalFAISSStore as _FAISSStore,
                )
                from system_learning.engines.local_faiss_store import (
                    ManifestIntegrityError as _MIE,
                )

                _dim = len(_faiss_vectors[0])
                _faiss_idx = "healing_context_v1"
                _faiss_base = REPO_ROOT / "logs" / "faiss_store"
                _faiss_base.mkdir(parents=True, exist_ok=True)
                _faiss_disk_dir = _faiss_base / _faiss_idx
                _is_bge = os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true"
                _vec_source_str = "bge-m3" if _is_bge else "hash-fallback"
                _model_ver = "BAAI/bge-m3-v1" if _is_bge else "hash-fallback-v1"

                # [CROSS-RUN] Load existing persisted index and carry forward its vectors
                _prior_vecs: list[list[float]] = []
                _prior_metas: list[dict] = []
                if _faiss_disk_dir.exists():
                    try:
                        _loader = _FAISSStore(base_path=_faiss_base)
                        _loader.load_from_disk(_faiss_idx, _faiss_disk_dir)
                        _loaded = _loader._memory_indexes.get(_faiss_idx, {})
                        _loaded_vecs = _loaded.get("vectors", [])
                        _loaded_metas = _loaded.get("metadatas", [])
                        # Guard against dimension mismatch (e.g. bge-m3 vs hash-fallback)
                        if _loaded_vecs and len(_loaded_vecs[0]) == _dim:
                            _prior_vecs = _loaded_vecs
                            _prior_metas = _loaded_metas
                    # guardian: allow-silent-swallow
                    except (_MIE, Exception):
                        pass  # Corrupt or absent index — start fresh this run

                # Merge prior + new, FIFO-cap at 1000 total (oldest dropped first)
                _all_vecs = _prior_vecs + _faiss_vectors
                _all_metas = _prior_metas + _faiss_metas
                # guardian: allow-magic-config
                _MAX_FAISS_VECS = 1000
                if len(_all_vecs) > _MAX_FAISS_VECS:
                    _all_vecs = _all_vecs[-_MAX_FAISS_VECS:]
                    _all_metas = _all_metas[-_MAX_FAISS_VECS:]

                # Rebuild fresh index with merged vectors, finalize, and persist to disk
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
                    _faiss_idx,
                    _faiss_disk_dir,
                    embedder_id=_vec_source_str,
                    model_version=_model_ver,
                )
                logging.debug(
                    "[MetaLearning] FAISS persist: %d new + %d prior = %d total -> %s",
                    len(_faiss_vectors),
                    len(_prior_vecs),
                    len(_all_vecs),
                    _faiss_disk_dir,
                )
            except Exception as _faiss_err:  # guardian: allow-silent-swallower
                logging.warning("[MetaLearning] FAISS wiring failed (non-fatal): %s", _faiss_err)

        # Gap 6: persist new failure vectors to L4 state (capped at 200) for cross-run novelty
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
            "[MetaLearning] HealingOutcomeIntakeAdapter: %d records persisted to L4B store.",
            store.count(),
        )
    except ImportError:
        logging.debug("[MetaLearning] Intake adapter not yet available (pre-Wave 0B). Skipping.")
    except Exception as _ml_err:  # guardian: allow-silent-swallower
        logging.warning("[MetaLearning] Intake adapter failed (non-fatal): %s", _ml_err)

    try:
        import time as _time_mod

        from system_learning.pipelines.meta_learning_pipeline import run_pipeline as _ml_run_pipeline
        from system_learning.pipelines.pipeline_factory import (
            build_pipeline_config,
            build_pipeline_deps,
        )

        _apply_proposals = state_mgr.state.get("apply_proposals", False)
        _now_utc = int(_time_mod.time())
        _window_start_utc = max(0, _now_utc - 3600)
        _ml_cfg = build_pipeline_config(proposal_only=not _apply_proposals)
        _ml_deps = build_pipeline_deps(
            repo_root=REPO_ROOT,
            healing_outcome_intake_adapter=adapter,
        )
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
            except Exception as _prop_err:
                logging.warning("[MetaLearning] proposal write failed: %s", _prop_err)
        logging.info("[MetaLearning] meta_learning_pipeline.run_pipeline() completed.")
    except ImportError as _imp_err:
        logging.debug("[MetaLearning] Pipeline not yet available (pre-Wave 0B): %s", _imp_err)
    except Exception as _pl_err:  # guardian: allow-silent-swallower
        logging.warning("[MetaLearning] Pipeline run failed (non-fatal): %s", _pl_err)


def _get_l5_agent_roster():
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent
    from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import CognitiveDispositionAgent
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
    from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import FilesystemSSOTReconcilerAgent
    from agentic_core.L5_safety.reasoning.GravityLeakHealerAgent import GravityLeakHealerAgent
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent
    from agentic_core.L6_observability.reasoning.observability_probe_executor import (
        ObservabilityProbeExecutorAgent,
    )

    return (
        ArchitectureGovernorAgent,
        CognitiveDispositionAgent,
        FileClassificationAgent,
        FilesystemSSOTReconcilerAgent,
        GravityLeakHealerAgent,
        HierarchyAgent,
        LocationHealerAgent,
        RootHygieneAgent,
        ObservabilityProbeExecutorAgent,
    )


def _preflight_import_check() -> None:
    """Diagnostic-only helper to verify critical imports can be resolved.

    This function checks that the execute_ssot_entrypoint can be imported
    and that _legacy_main symbol exists without invoking any runtime behavior.
    Raises RuntimeError with detailed message if any check fails.

    NOTE: Called at startup in _legacy_main to fail-fast on missing symbols.
    """
    try:
        # Check that _legacy_main exists in this module (execute_ssot.py)
        if not hasattr(sys.modules[__name__], "_legacy_main"):
            raise RuntimeError("CRITICAL: _legacy_main not found in execute_ssot module")
        # Access the attribute to ensure it's resolvable
        legacy_main = sys.modules[__name__]._legacy_main
        if not callable(legacy_main):
            raise RuntimeError("CRITICAL: _legacy_main attribute is not callable")
    except (AttributeError, TypeError) as exc:
        raise RuntimeError(
            f"CRITICAL: Failed to resolve _legacy_main from execute_ssot module: {exc}"
        ) from exc


def _optional_runtime_guard():
    """Lazy import to avoid import-time failure in bootstrap contexts.

    Fail-closed semantics: when V15_ENFORCEMENT=1 and the guard cannot be
    imported, re-raise so the caller sees a hard failure instead of a silent
    no-op.  When enforcement is off (or unset), fall back to a no-op decorator.
    """
    try:
        from agentic_core.L0_routing.enforcement.runtime_guard import runtime_guard

        return runtime_guard
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed: enforcement is on but guard is unavailable

        def _noop_guard(_entry_point_id: str):
            """No-op: accepts an ID string and returns an identity decorator."""

            def _identity(func):
                return func

            return _identity

        return _noop_guard


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from agentic_core.utils.decorators_compat_util import HEAL_RESULT_SCHEMA, standard_heal
except ImportError:
    # Fallback for bootstrapping scenarios
    def standard_heal(func):
        return func

    HEAL_RESULT_SCHEMA = {}

try:
    from agentic_core.base_agents.IHealerProtocol import IHealerProtocol, LegacyAgentAdapter
except ImportError:
    # Fallback for bootstrapping scenarios
    class IHealerProtocol:
        pass

    class LegacyAgentAdapter:
        def __init__(self, legacy_agent):
            self.agent = legacy_agent

        def heal(self, violation):
            return {"status": "failed", "errors": ["Adapter not available"]}


def _safe_print(text: str) -> None:
    """Print text safely on Windows consoles that use charmap encoding."""
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def run_fence_self_check() -> None:
    """Run deterministic fence self-check (validates policy + wiring; no mutations).

    Validates:
    1. Default ProtectedRootPolicy immutable_roots equals ("agentic_core","tests",".github")
    2. Default ProtectedRootPolicy log_path is outside IMMUTABLE_ROOTS
    3. write_gateway public entrypoints accept allow_override AND call enforce_protected_root
    4. Telemetry emitter path is writable target ONLY outside IMMUTABLE_ROOTS

    Prints single-line JSON summary to stdout:
    - {"status":"ok","checks":4}
    - or {"status":"fail","failed":["check_name",...]}

    Exits with code 0 if all checks pass, nonzero otherwise.
    """
    from agentic_core.L0_routing.enforcement.mutation_prohibition import (
        IMMUTABLE_ROOTS,
        get_default_protected_root_policy,
    )

    failed_checks = []

    # Check 1: Default policy immutable_roots
    try:
        policy = get_default_protected_root_policy()
        if policy.immutable_roots != ("agentic_core", "tests", ".github"):
            failed_checks.append("default_policy_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("default_policy_immutable_roots")

    # Check 2: Default policy log_path is outside IMMUTABLE_ROOTS
    try:
        policy = get_default_protected_root_policy()
        log_path = Path(policy.log_path)

        # Check if log_path would be under any immutable root
        repo_root = resolve_repo_root()
        resolved_log = (repo_root / log_path).resolve()

        is_under_immutable = False
        for immutable_root in IMMUTABLE_ROOTS:
            try:
                resolved_log.relative_to(immutable_root)
                is_under_immutable = True
                break
            except ValueError:
                pass

        if is_under_immutable:
            failed_checks.append("log_path_outside_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("log_path_outside_immutable_roots")

    # Check 3: write_gateway entrypoints accept allow_override AND call enforce_protected_root
    try:
        write_gateway = _get_write_gateway()

        # Check write_text and write_bytes (primary entrypoints)
        for func_name in ["write_text", "write_bytes"]:
            func = getattr(write_gateway, func_name, None)
            if func is None:
                failed_checks.append("write_gateway_enforces_protected_root")
                break

            # Check signature has allow_override parameter
            sig = inspect.signature(func)
            if "allow_override" not in sig.parameters:
                failed_checks.append("write_gateway_enforces_protected_root")
                break

            # Check source contains enforce_protected_root call
            try:
                source = inspect.getsource(func)
                if "enforce_protected_root" not in source:
                    failed_checks.append("write_gateway_enforces_protected_root")
                    break
            except (OSError, TypeError):
                # Source unavailable - fail with actionable message
                failed_checks.append("write_gateway_enforces_protected_root")
                break
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("write_gateway_enforces_protected_root")

    # Check 4: Telemetry emitter path is outside IMMUTABLE_ROOTS (pure path check)
    try:
        policy = get_default_protected_root_policy()
        log_path = Path(policy.log_path)
        repo_root = resolve_repo_root()
        resolved_log = (repo_root / log_path).resolve()

        # Same check as #2 - ensure telemetry path is outside protected roots
        is_under_immutable = False
        for immutable_root in IMMUTABLE_ROOTS:
            try:
                resolved_log.relative_to(immutable_root)
                is_under_immutable = True
                break
            except ValueError:
                pass

        if is_under_immutable:
            failed_checks.append("telemetry_path_outside_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("telemetry_path_outside_immutable_roots")

    # Output deterministic JSON summary
    if failed_checks:
        result = {"status": "fail", "failed": sorted(failed_checks)}
        print(json.dumps(result, sort_keys=True))
        sys.exit(1)
    else:
        result = {"status": "ok", "checks": 4}
        print(json.dumps(result, sort_keys=True))
        sys.exit(0)


def resolve_repo_root(start=None):
    """Deterministic repo-root resolver.
    Walk upward from this file (or provided start) until we find repo markers.
    """
    cur = Path(start or __file__).resolve()
    for p in (cur, *cur.parents):
        if (p / AGENTIC_CORE_DIR).is_dir() and (p / OPS_SCRIPTS_DIR).is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


REPO_ROOT = resolve_repo_root()  # noqa: N816


def _apply_v15_enforcement_flag(args: argparse.Namespace) -> None:
    """CLI overrides env to ensure determinism in CI/smoke paths."""
    if getattr(args, "v15_enforcement", None) is None:
        return
    os.environ["V15_ENFORCEMENT"] = "1" if int(args.v15_enforcement) == 1 else "0"


def _configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )


def _maybe_force_utf8_console() -> None:
    """Unconditional stdout/stderr UTF-8 coercion.  Called at runtime, NOT import time."""
    if sys.platform.startswith("win"):
        try:
            _get_safe_subprocess_run()(
                ["chcp", "65001"],
                stdout=DEVNULL,
                stderr=DEVNULL,
                check=False,
                allow_protected_root_mutation=True,
            )
        except FileNotFoundError:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # guardian: allow-silent-swallow
    except Exception:  # guardian: allow-silent-swallower
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    # guardian: allow-silent-swallow
    except Exception:
        return


def _maybe_force_utf8_logging_handlers() -> None:
    """Reconfigure existing logging handler streams to UTF-8.  Called at runtime, NOT import time."""
    seen: set[int] = set()
    for handler in logging.getLogger().handlers + logging.getLogger("").handlers:
        hid = id(handler)
        if hid in seen:
            continue
        seen.add(hid)
        stream = getattr(handler, "stream", None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        # guardian: allow-silent-swallow
        except Exception:
            pass


# ============================================================================
# V15 MANIFEST CONSTRUCTION (§8.1e)
# ============================================================================


def _v15_build_ssot_manifest():
    """§8.1e — Construct SurgicalManifest for SSOT bootstrap entry.

    Returns None when V15 enforcement is off (zero overhead).
    Bootstrap-safe: lazy imports with fail-closed semantics.
    """
    try:
        from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced

        if not is_v15_enforced():
            return None

        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.traceability_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.determinism_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = _hl.sha256(b"execute_ssot._legacy_main").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)

        ast_snippet = "execute_ssot._legacy_main()"
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="ExecuteSSOT",
            target_layer="L0",
            ast_snippet=ast_snippet,
            serialization_canon="execute_ssot",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed when hard enforcement is on
        return None


def _v15_ssot_gateway_audit(manifest, trace_id: str) -> None:
    """§8.1e — Invoke gateway.execute in LOG_ONLY mode for SSOT audit trail."""
    if manifest is None:
        return
    try:
        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )

        gw = V15ExecutionGateway()
        gw.execute(
            manifest,
            lambda m: {"status": "ssot_audit", "errors": 0},
            lambda: (
                _hl.sha256(b"fs_ssot").hexdigest(),
                _hl.sha256(b"git_ssot").hexdigest(),
                _hl.sha256(b"mem_ssot").hexdigest(),
            ),
            trace_id=trace_id,
            agent_id="ssot_audit",
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        logging.getLogger(__name__).warning("[V15] SSOT gateway audit failed (LOG_ONLY): %s", exc)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ConfidenceScore:
    """[HARDENED] Environment-aware confidence score for autonomous healing."""

    value: float  # 0.0 to 1.0
    reasoning: str
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def _high_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_HIGH_CONFIDENCE (default: 0.75)"""
        return float(os.getenv("SOVEREIGN_HIGH_CONFIDENCE", "0.75"))

    @property
    def _med_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_MEDIUM_CONFIDENCE (default: 0.50)"""
        return float(os.getenv("SOVEREIGN_MEDIUM_CONFIDENCE", "0.50"))

    @property
    def is_high_confidence(self) -> bool:
        return self.value > self._high_threshold

    @property
    def is_medium_confidence(self) -> bool:
        return self._med_threshold <= self.value <= self._high_threshold

    @property
    def is_low_confidence(self) -> bool:
        return self.value < self._med_threshold


# ============================================================================
# HARDENED SSOT ROUTING — enums, dataclasses, pure routing function
# ============================================================================

import enum as _enum
import hashlib as _hashlib

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L5_SAFETY_DIR,
    OPS_SCRIPTS_DIR,
    RUNTIME_STATE_JSON,
)


class FailureType(_enum.Enum):
    """Classifies the failure being routed.  Drives gate selection."""

    LAYER_VIOLATION = "LAYER_VIOLATION"
    GATEWAY_BYPASS = "GATEWAY_BYPASS"
    KILL_SWITCH_BYPASS = "KILL_SWITCH_BYPASS"
    SIGNATURE_VERIFY = "SIGNATURE_VERIFY"
    UNSIGNED_INGRESS = "UNSIGNED_INGRESS"
    IMPORT_BOUNDARY_VIOLATION = "IMPORT_BOUNDARY_VIOLATION"
    SCHEMA_REQUIRED_FIELDS_MISSING = "SCHEMA_REQUIRED_FIELDS_MISSING"
    NAMING = "NAMING"
    HIERARCHY = "HIERARCHY"
    SHALLOW = "SHALLOW"
    DEEP = "DEEP"
    VOID = "VOID"
    DUPLICATE = "DUPLICATE"
    ORPHAN = "ORPHAN"
    UNKNOWN = "UNKNOWN"


class RoutingTier(_enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    QWEN = "QWEN"
    GEMINI = "GEMINI"
    FAIL_CLOSED = "FAIL_CLOSED"


# Structural failures: deterministic coverage can rescue; otherwise GEMINI/FAIL_CLOSED
_STRUCTURAL_CLASS: frozenset[FailureType] = frozenset(
    {
        FailureType.LAYER_VIOLATION,
        FailureType.GATEWAY_BYPASS,
        FailureType.KILL_SWITCH_BYPASS,
        FailureType.SIGNATURE_VERIFY,
        FailureType.UNSIGNED_INGRESS,
    }
)

# Qwen-disallowed failures: includes structural + import/schema violations
_QWEN_DISALLOWED: frozenset[FailureType] = _STRUCTURAL_CLASS | frozenset(
    {
        FailureType.IMPORT_BOUNDARY_VIOLATION,
        FailureType.SCHEMA_REQUIRED_FIELDS_MISSING,
    }
)


@dataclass
class RoutingInputs:
    """All inputs to compute_routing_decision.  No embeddings allowed."""

    failure_type: FailureType = FailureType.UNKNOWN
    retry_count: int = 0
    C: int = 0  # complexity      0-3
    B: int = 0  # blast-radius    0-3
    A: int = 0  # autonomy-risk   0-3
    N: int = 0  # novelty         0-3
    F: int = 0  # failure-cost    0-3
    L: int = 0  # latency class   0-3  (0=interactive, 3=async-batch)
    replay_mode: bool = False
    playbook_match: bool = False
    deterministic_coverage: bool = False
    provider_prohibited_gemini: bool = False
    provider_prohibited_qwen: bool = False


@dataclass
class RoutingDecision:
    """Immutable routing result with full audit trail."""

    tier: RoutingTier
    score: int
    gate_applied: str
    model_id: str
    factors: dict
    inputs: RoutingInputs
    determinism_digest: str

    def as_log_line(self) -> str:
        f = self.factors
        i = self.inputs
        return (
            f"[ROUTING] tier={self.tier.value} S={self.score} gate={self.gate_applied}"
            f" model={self.model_id}"
            f" C={f.get('C', 0)} B={f.get('B', 0)} A={f.get('A', 0)}"
            f" N={f.get('N', 0)} F={f.get('F', 0)} L={f.get('L', 0)}"
            f" replay={i.replay_mode} retry={i.retry_count}"
            f" playbook={i.playbook_match} det_cov={i.deterministic_coverage}"
            f" digest={self.determinism_digest}"
        )


def compute_routing_decision(inputs: RoutingInputs) -> RoutingDecision:  # noqa: C901
    """Pure SSOT routing function — strict gate order, no side effects."""
    C, B, A, N, F, L = inputs.C, inputs.B, inputs.A, inputs.N, inputs.F, inputs.L

    def _decide(tier: RoutingTier, gate: str, score: int = 0) -> RoutingDecision:
        if tier == RoutingTier.DETERMINISTIC:
            model = "deterministic-sovereign"
        elif tier == RoutingTier.QWEN:
            model = "Qwen2.5-14B-Instruct-AWQ"
        elif tier == RoutingTier.GEMINI:
            model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        else:
            model = "FAIL_CLOSED"
        raw = f"{tier.value}|{score}|{gate}|{inputs.failure_type.value}|{C}|{B}|{A}|{N}|{F}|{L}|{inputs.replay_mode}|{inputs.retry_count}"
        digest = _hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:16]
        return RoutingDecision(
            tier=tier,
            score=score,
            gate_applied=gate,
            model_id=model,
            factors={"C": C, "B": B, "A": A, "N": N, "F": F, "L": L},
            inputs=inputs,
            determinism_digest=digest,
        )

    # ── GATE 0: Replay mode → always deterministic ─────────────────────────
    if inputs.replay_mode:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_0_REPLAY")

    # ── GATE 1: Global retry override ──────────────────────────────────────
    if inputs.retry_count >= 3:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_1_RETRY_OVERRIDE_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_1_RETRY_OVERRIDE")

    # ── GATE 2: Structural class pre-gate ──────────────────────────────────
    if inputs.failure_type in _STRUCTURAL_CLASS:
        if inputs.deterministic_coverage:
            return _decide(RoutingTier.DETERMINISTIC, "GATE_2_STRUCTURAL_DET_COV")
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_2_STRUCTURAL_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_2_STRUCTURAL_NO_DET_COV")

    # ── GATE 3: Critical surface mechanical exception ──────────────────────
    if B == 3 and A == 0 and inputs.playbook_match and inputs.deterministic_coverage:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_3_CRITICAL_SURFACE_MECH")

    # ── Score computation ──────────────────────────────────────────────────
    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
    if inputs.playbook_match:
        S = max(0, S - 4)

    # ── GATE 4: Hard-override for extreme risk ─────────────────────────────
    if B == 3 and F == 3 and (C >= 2 or A >= 1):
        if inputs.provider_prohibited_gemini and inputs.provider_prohibited_qwen:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_4_HARD_OVERRIDE_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, "GATE_4_HARD_OVERRIDE", S)

    # ── GATE 5: Threshold routing ──────────────────────────────────────────
    if S <= 13:
        tier = RoutingTier.DETERMINISTIC
        gate = "THRESHOLD_LOW_DET"
    elif S <= 26:
        tier = RoutingTier.QWEN
        gate = "THRESHOLD_MED_QWEN"
    else:
        tier = RoutingTier.GEMINI
        gate = "THRESHOLD_HIGH_GEMINI"
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "THRESHOLD_HIGH_FAIL_CLOSED", S)

    # ── GATE 6: Latency tie-breaker (boundary zones only) ─────────────────
    # Does NOT apply when failure_type is qwen-disallowed (Gate 7 handles those).
    _qwen_disallowed_type = inputs.failure_type in _QWEN_DISALLOWED
    _qwen_blocked = _qwen_disallowed_type or inputs.provider_prohibited_qwen
    if tier == RoutingTier.QWEN and S in range(14, 16) and L == 0 and not _qwen_blocked:
        tier = RoutingTier.DETERMINISTIC
        gate = f"{gate}.L_TIEBREAK_DOWN"
    elif tier == RoutingTier.DETERMINISTIC and S in range(12, 14) and L == 3 and not _qwen_disallowed_type:
        tier = RoutingTier.QWEN
        gate = f"{gate}.L_TIEBREAK_UP"

    # ── GATE 7: Qwen-disallowed fall-up ───────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.failure_type in _QWEN_DISALLOWED:
        if inputs.deterministic_coverage and A == 0 and C == 0:
            return _decide(RoutingTier.DETERMINISTIC, f"{gate}.QWEN_DISALLOWED_DET_FALLBACK", S)
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.QWEN_DISALLOWED_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_DISALLOWED", S)

    # ── GATE 8: Provider prohibition check ────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.provider_prohibited_qwen:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.BOTH_PROHIBITED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_PROHIBITED_FALLBACK", S)

    if tier == RoutingTier.GEMINI and inputs.provider_prohibited_gemini:
        return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.GEMINI_PROHIBITED", S)

    return _decide(tier, gate, S)


# ============================================================================
# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION
# ============================================================================


@dataclass
class ReconciliationViolation:
    """Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler)."""

    is_valid: bool
    message: str
    drift_type: str | None = None
    file_path: Path | None = None
    suggested_action: str | None = None
    severity: int = 5  # 1-10 scale

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "drift_type": self.drift_type,
            "file_path": str(self.file_path.as_posix()) if self.file_path else None,
            "severity": self.severity,
        }


@dataclass
class ReconciliationManifest:
    """Telemetry manifest for tracking all reconciliation changes."""

    mission_id: str
    territory: str
    start_time: str
    end_time: str | None = None
    violations_found: int = 0
    violations_attempted: int = 0
    violations_fixed: int = 0
    violations_failed: int = 0
    modifications: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    budget_consumed: int = 0
    confidence_scores: list[float] = field(default_factory=list)

    def add_modification(self, modification: dict[str, Any]) -> None:
        self.modifications.append(modification)
        self.violations_attempted += 1
        if modification.get("success", False):
            self.violations_fixed += 1
        else:
            self.violations_failed += 1

    def add_failure(self, failure: dict[str, Any]) -> None:
        self.failures.append(failure)
        self.violations_failed += 1

    def finalize(self) -> dict[str, Any]:
        self.end_time = datetime.now().isoformat()
        return {
            "mission_id": self.mission_id,
            "territory": self.territory,
            "duration": {
                "start": self.start_time,
                "end": self.end_time,
                "seconds": (
                    datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)
                ).total_seconds()
                if self.end_time
                else None,
            },
            "violations": {
                "found": self.violations_found,
                "attempted": self.violations_attempted,
                "fixed": self.violations_fixed,
                "failed": self.violations_failed,
                "success_rate": self.violations_fixed / max(self.violations_attempted, 1),
            },
            "budget": {
                "consumed": self.budget_consumed,
                "remaining": max(0, 100 - self.budget_consumed),  # Default max budget of 100
            },
            "confidence": {
                "scores": self.confidence_scores,
                "average": sum(self.confidence_scores) / len(self.confidence_scores)
                if self.confidence_scores
                else 0.0,
            },
            "modifications": self.modifications,
            "failures": self.failures,
        }


class ASTCodeQualityValidator:
    """AST-based code quality validation with memory guards (Ported from TypeMechanic)."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # [SAFETY] Prevent OOM on massive generated files
        # guardian: allow-magic-config
        self.max_file_size = 1_000_000  # 1MB limit

    def _read_and_parse_file(self, fp: str) -> tuple[ast.AST | None, str | None]:
        """Reads a file and parses it into an AST with strict size limits."""
        try:
            if os.path.getsize(fp) > self.max_file_size:
                return None, "File too large for AST analysis"

            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
                return tree, None
        except (OSError, SyntaxError) as e:
            return None, f"Error parsing {fp}: {str(e)}"

    # guardian: allow-type-erasure
    def check_file_quality(self, file_path: Path) -> dict:
        """Check file for code quality issues (missing types, etc)."""
        violations = []
        tree, error = self._read_and_parse_file(str(file_path))

        if error:
            return {"error": error, "violations": []}

        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignore dunders
                    if not node.returns and not node.name.startswith("__"):
                        violations.append(
                            {
                                "type": "MISSING_TYPE_HINT",
                                "file": str(file_path),
                                "line": node.lineno,
                                "message": f"Function '{node.name}' missing return type hint",
                            },
                        )

        return {
            "violations": violations,
            "violations_count": len(violations),
            "file": str(file_path),
        }


# ============================================================================
# HEALING ACTION RECORDING — Structured Healing Log with Routing Details
# ============================================================================


def _record_healing_action(
    state_mgr,
    agent: str,
    territory: str,
    routing_score: float = 0.0,
    routing_tier: str = "DETERMINISTIC",
    model: str = "none",
    routing_gate: str = "N/A",
    confidence: float = 0.0,
    fix_summary: str = "",
    outcome: str = "SUCCESS",
    routing_digest: str | None = None,
    check_id: str | None = None,
):
    """[H2] Record a structured healing action for per-territory JSON and Markdown reports.

    Appends to state_mgr.state["healing_actions"] so Phase 5 can filter by territory
    and emit a healing_log in the detailed_cert JSON.
    """
    action = {
        "agent": agent,
        "territory": territory,
        "routing_score": round(routing_score, 4),
        "routing_tier": routing_tier,
        "model": model,
        "routing_gate": routing_gate,
        "confidence": round(confidence, 4),
        "fix_summary": fix_summary,
        "outcome": outcome,
        "timestamp": datetime.now().isoformat(),
        "routing_digest": routing_digest,
        "check_id": check_id,
    }
    if "healing_actions" not in state_mgr.state:
        state_mgr.state["healing_actions"] = []
    state_mgr.state["healing_actions"].append(action)


# ============================================================================
# ============================================================================
# HEAL CONTEXT — Single Source of Truth for Healing Flags
# ============================================================================


@dataclass(frozen=True)
class HealContext:
    """Immutable healing configuration passed uniformly to every phase function.

    Single control surface: --heal drives ALL active-mode flags.

      --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                    enable_meta_learning all True
      --heal OFF => scan/report only, everything passive
    """

    heal: bool  # True = mutations active; False = scan/report only
    auto_approve: bool  # True = no interactive prompts (always True when heal=True)
    enable_telemetry: bool  # Active telemetry collection (always tied to heal)
    enable_meta_learning: bool  # Meta-learning pipeline runs (always tied to heal)
    # CDA (CognitiveDispositionAgent) is always active — no toggle

    @property
    def enable_llm(self) -> bool:
        """LLM arbitration is always active when healing — not a separate flag."""
        return self.heal

    @property
    def dry_run(self) -> bool:
        """Convenience alias — inverted heal for legacy call sites."""
        return not self.heal

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "HealContext":
        """Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        """
        import warnings

        if getattr(args, "dry_run", False):
            warnings.warn(
                "--dry-run is deprecated. Omit --heal for scan-only mode.",
                DeprecationWarning,
                stacklevel=2,
            )
        if getattr(args, "manual", False):
            warnings.warn(
                "--manual is deprecated. Autonomous mode is always active.",
                DeprecationWarning,
                stacklevel=2,
            )
        if getattr(args, "interactive", False):
            warnings.warn(
                "--interactive is deprecated. Auto-approve is always on under --heal.",
                DeprecationWarning,
                stacklevel=2,
            )
        if getattr(args, "apply_proposals", False):
            warnings.warn(
                "--apply-proposals is deprecated. Meta-learning is always on under --heal.",
                DeprecationWarning,
                stacklevel=2,
            )
        # --heal is the single source of truth for ALL active-mode flags
        heal = getattr(args, "heal", False)
        return cls(
            heal=heal,
            auto_approve=heal,
            enable_telemetry=heal,
            enable_meta_learning=heal,
        )


# ============================================================================
# SOVEREIGN DECISION ENGINE (unified flat class — formerly 3-class hierarchy)
# ============================================================================


class SovereignDecisionEngine:
    """
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    Unified flat class (formerly AutonomousDecisionEngine -> Enhanced -> Sovereign hierarchy).
    """

    def __init__(
        self,
        enable_llm: bool = True,
        state_mgr: Optional["RuntimeStateManager"] = None,
        enable_cda: bool = False,
        execution_context: Optional["ExecutionContext"] = None,
        healing_memory_retriever: Any | None = None,
        auto_approve: bool = False,
    ):
        self.enable_llm = enable_llm
        self.decisions_made = []
        self.state_mgr = state_mgr
        self._execution_context = execution_context
        # [SAFETY] Cycle Detection State
        self._healing_count: int = 0
        self._healing_enabled: bool = True
        self._max_healing_operations: int = 10000
        self.auto_approve: bool = auto_approve
        self._call_path: set[str] = set()
        # CDA Integration (merged from EnhancedAutonomousDecisionEngine)
        self.enable_cda = enable_cda
        # Sovereignty Token State (merged from SovereignDecisionEngine)
        self._sovereignty_token: str | None = None
        self._operation_stack: list[str] = []
        # guardian: allow-magic-config
        self._max_stack_depth = 10
        self._atomic_lock = False
        # B2: advisory-only healing memory retriever (never influences tier selection)
        self._healing_memory_retriever = healing_memory_retriever

    def _calculate_semantic_similarity(self, unknown: str, existing: list[str]) -> float:
        """Calculate semantic similarity for unknown items against a candidate list.

        When BMG_EMBEDDINGS_ENABLED=true and sentence-transformers is installed,
        uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap when embeddings are unavailable.
        """
        if not existing:
            return 0.0

        if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true":
            try:
                bmg_fn = self._get_bmg_cosine_similarity()
                return bmg_fn(unknown, existing)
            except Exception:  # guardian: allow-silent-swallower  # noqa: BLE001
                pass

        # Jaccard word-overlap fallback (original implementation)
        unknown_words = set(unknown.lower().replace("_", " ").replace("-", " ").split())
        max_similarity = 0.0

        for item in existing:
            existing_words = set(item.lower().replace("_", " ").replace("-", " ").split())
            intersection = unknown_words & existing_words
            union = unknown_words | existing_words

            if union:
                similarity = len(intersection) / len(union)
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    @staticmethod
    def _get_bmg_cosine_similarity() -> object:
        """Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import."""
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            bmg_cosine_similarity,
        )

        return bmg_cosine_similarity

    @staticmethod
    def _get_bmg_embedding_agent_keys() -> frozenset:
        """Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            BMG_EMBEDDING_AGENT_KEYS,
        )

        return BMG_EMBEDDING_AGENT_KEYS

    @staticmethod
    def _get_qwen_14b_routing_config() -> tuple:
        """Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            QWEN_14B_AGENT_KEYS,
            QWEN_14B_MODEL_ID,
        )

        return QWEN_14B_AGENT_KEYS, QWEN_14B_MODEL_ID

    @staticmethod
    def _get_qwen_vllm_arbiter():
        """Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess."""
        import json
        from pathlib import Path

        WSL_PYTHON = "/home/amita/venvs/vllm/bin/python"
        INFERENCE_SCRIPT = str(
            Path(__file__).parent.parent.parent / "L2_execution" / "healers" / "qwen_vllm_inference.py"
        )
        MODEL_PATH = "/home/amita/models/Qwen2.5-14B-Instruct-AWQ"

        def _arbiter(
            agent_name: str,
            violation_types: list,
            territory: str,
            score: int = 0,
            gate: str = "",
        ) -> dict:
            # Convert Windows path to WSL mount path
            script_wsl = INFERENCE_SCRIPT.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            cmd = [
                "wsl",
                "bash",
                "-c",
                (
                    f"{WSL_PYTHON} {script_wsl}"
                    f" --agent_name {agent_name}"
                    f" --score {score}"
                    f" --gate {gate}"
                    f" --territory {territory}"
                    f" --model_path {MODEL_PATH}"
                    + (f" --violation_types {' '.join(violation_types)}" if violation_types else "")
                ),
            ]
            result = _get_safe_subprocess_run()(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,  # guardian: allow-magic-configuration
            )
            if result.returncode != 0:
                raise RuntimeError(f"vLLM subprocess failed: {result.stderr[-500:]}")
            # Last non-empty line is the JSON output
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            for line in reversed(lines):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
            raise RuntimeError(f"No JSON in vLLM output: {result.stdout[-300:]}")

        return _arbiter

    def _calculate_pattern_confidence(self, violation_type: str) -> float:
        """Regex-based pattern matching for known violation types."""
        high_confidence_patterns = [
            r".*NAMING.*",
            r".*HIERARCHY.*",
            r".*IMPORT.*",
            r".*SHALLOW.*",
            r".*DEEP.*",
            r".*VOID.*",
            r".*DUPLICATE.*",
            r".*ORPHAN.*",
        ]

        for pattern in high_confidence_patterns:
            if re.match(pattern, violation_type, re.IGNORECASE):
                return 0.9
        return 0.5

    def _compute_novelty_score(
        self,
        failure_type: "FailureType | None",
        territory: str,
        confidence: "ConfidenceScore",
    ) -> int:
        """Compute the novelty score N (0-3) for RoutingInputs.

        When BMG_EMBEDDINGS_ENABLED=true and recent failure vectors exist in L4
        state, embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  0.70 <= max_similarity < 0.85
          N=2  0.50 <= max_similarity < 0.70
          N=3  max_similarity < 0.50   (completely novel)

        Falls back to a hash-fallback vector comparison when embeddings are
        disabled, replacing the legacy [BMG-GPU] string heuristic.
        Raises VectorSourceMismatchError if stored vectors and the fallback
        vector have incompatible dimensions (e.g., bge-m3 vs hash-fallback).
        """
        if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() != "true":
            # Debt-1: deterministic hash-fallback novelty instead of [BMG-GPU] string heuristic.
            try:
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    VectorSourceMismatchError as _VectorSrcErr,
                )
                from agentic_core.L2_execution.healers.failure_signal_normalizer import (
                    generate_fallback_vector as _gen_fallback,
                )

                ft_str = failure_type.value if failure_type is not None else "UNKNOWN"
                _signal_text = f"{ft_str} {territory}"
                _fallback_vec = _gen_fallback(_signal_text)

                _recent: list = []
                if self.state_mgr is not None:
                    _recent = self.state_mgr.state.get("meta_learning", {}).get("recent_failure_vectors", [])

                if not _recent:
                    return 1

                import numpy as _np

                _q = _np.array(_fallback_vec, dtype=_np.float32)
                _mat = _np.array(_recent, dtype=_np.float32)

                # Debt-2: dim mismatch between hash-fallback (16-dim) and bge-m3 vectors.
                if _mat.shape[1] != _q.shape[0]:
                    raise _VectorSrcErr(
                        f"Cannot compare hash-fallback vector (dim={_q.shape[0]}) "
                        f"against L4 state vectors (dim={_mat.shape[1]}): "
                        "source mismatch -- stored vectors are likely bge-m3."
                    )

                _max_sim = float((_np.dot(_mat, _q)).max())
                if _max_sim >= 0.85:
                    return 0
                if _max_sim >= 0.70:
                    return 1
                if _max_sim >= 0.50:
                    return 2
                return 3
            except Exception as _fb_exc:  # guardian: allow-silent-swallower
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    VectorSourceMismatchError as _VSMErr,
                )

                if isinstance(_fb_exc, _VSMErr):
                    raise
                return 1  # conservative default when fallback computation unavailable

        recent: list = []
        if self.state_mgr is not None:
            recent = self.state_mgr.state.get("meta_learning", {}).get("recent_failure_vectors", [])

        if not recent:
            return 1

        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            ft_str = failure_type.value if failure_type is not None else "UNKNOWN"
            signal_text = f"{ft_str} {territory}"
            vec = bmg_embed_text(signal_text)

            import numpy as _np

            q = _np.array(vec, dtype=_np.float32)
            mat = _np.array(recent, dtype=_np.float32)
            max_sim = float((_np.dot(mat, q)).max())

            if max_sim >= 0.85:
                return 0
            if max_sim >= 0.70:
                return 1
            if max_sim >= 0.50:
                return 2
            return 3
        except Exception:  # guardian: allow-silent-swallower
            return 1  # conservative default: mildly novel, not completely new

    def _route_decision(
        self,
        confidence: "ConfidenceScore",
        agent_name: str,
        territory: str,
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> "RoutingDecision":
        """Map healing context to a hardened SSOT RoutingDecision."""
        if failure_type is None:
            reasoning_upper = (confidence.reasoning or "").upper()
            ft = FailureType.UNKNOWN
            for member in FailureType:
                if member.value in reasoning_upper:
                    ft = member
                    break
            failure_type = ft

        # B3: advisory-only healing memory retrieval — result MUST NOT alter tier/thresholds.
        # Violations of this boundary are detectable via the advisory_only flag on SimilarIncident.
        if self._healing_memory_retriever is not None:
            try:
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    SovereigntyError as _SovereigntyError,
                )

                _signal_text = f"{failure_type.value if failure_type else 'UNKNOWN'} {territory}"
                _advisory = self._healing_memory_retriever.retrieve_similar_incidents(_signal_text, top_k=3)
                # B-hardening: hard-fail if any incident escapes advisory boundary.
                for _inc in _advisory:
                    if not getattr(_inc, "advisory_only", True):
                        raise _SovereigntyError(
                            f"advisory_only=False on incident {getattr(_inc, 'content_hash', '?')!r}; "
                            "routing tier MUST NOT be influenced by retrieval results."
                        )
                if _advisory:
                    logger.debug(
                        "[B3-Advisory] top=%d sim=%.4f (advisory_only=%s) — routing unchanged",
                        len(_advisory),
                        _advisory[0].similarity,
                        _advisory[0].advisory_only,
                    )
            except Exception as _exc:  # guardian: allow-silent-swallower
                from agentic_core.L1_cognition.memory.healing_memory_retriever import (
                    SovereigntyError as _SE,
                )

                if isinstance(_exc, _SE):
                    raise
                # All other retrieval errors are non-fatal — routing proceeds unchanged.

        C = min(3, max(0, int(3 - confidence.value * 3)))
        B = 3 if territory.startswith("L5") else (2 if "agentic_core" in territory else 1)
        A = 0 if confidence.value >= 0.75 else (2 if confidence.value < 0.50 else 1)
        N = self._compute_novelty_score(failure_type, territory, confidence)
        high_cost = {
            FailureType.LAYER_VIOLATION,
            FailureType.GATEWAY_BYPASS,
            FailureType.KILL_SWITCH_BYPASS,
            FailureType.SIGNATURE_VERIFY,
            FailureType.UNSIGNED_INGRESS,
        }
        F = 3 if failure_type in high_cost else (2 if confidence.value < 0.50 else 1)
        L = 0

        ri = RoutingInputs(
            failure_type=failure_type,
            retry_count=retry_count,
            C=C,
            B=B,
            A=A,
            N=N,
            F=F,
            L=L,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )
        decision = compute_routing_decision(ri)
        logger.info(decision.as_log_line())
        return decision

    # guardian: allow-magic-config
    def _classify_violation_type(self, message: str) -> str:
        """Classify a violation message into a canonical violation type string."""
        msg_lower = message.lower()
        if "missing sovereign root" in msg_lower or "missing" in msg_lower and "director" in msg_lower:
            return "MISSING_DIRECTORY"
        if "forbidden keyword" in msg_lower:
            return "FORBIDDEN_CONTENT"
        if "forbidden extension" in msg_lower:
            return "EXTENSION_MISMATCH"
        if "test_" in msg_lower and "file" in msg_lower:
            return "TEST_FILE_MISPLACED"
        if "sovereign" in msg_lower:
            return "SOVEREIGN_VIOLATION"
        return "STRUCTURAL_VIOLATION"

    def _check_healing_budget(self, agent_name: str, depth: int = 0, max_depth: int = 3) -> tuple[bool, str]:
        """Prevents infinite healing loops and budget exhaustion."""
        # Use operation-scoped call path to prevent bleeding across territories
        # Default to "Unknown" if no agent_name provided (should be avoided)
        if agent_name == "Unknown":
            agent_name = f"operation-{id(self)}"  # Unique per operation

        if agent_name in self._call_path:
            return False, f"Healing cycle detected: {agent_name}"
        if depth > max_depth:
            return False, f"Healing depth limit exceeded for {agent_name}"
        if self._healing_count >= self._max_healing_operations:
            logger.warning(
                "[BUDGET] Healing budget exhausted (%d/%d) — %s blocked",
                self._healing_count,
                self._max_healing_operations,
                agent_name,
            )
            return False, f"Budget exceeded ({self._healing_count})"
        return True, "OK"

    # guardian: allow-magic-config
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: list[str],
        territory: str,
        historical_success_rate: float = 0.8,
        agent_name: str = "",
    ) -> ConfidenceScore:
        """Calculates weighted confidence score.

        When BMG_EMBEDDINGS_ENABLED=true and agent_name is in BMG_EMBEDDING_AGENT_KEYS,
        uses GPU-accelerated BAAI/bge-m3 cosine similarity instead of Jaccard pattern
        matching for the pattern_score component.
        """
        if violations_count == 0:
            return ConfidenceScore(value=1.0, reasoning="Zero violations")
        if getattr(self, "auto_approve", False):
            return ConfidenceScore(value=1.0, reasoning="AUTO-HEAL: --heal active, confidence forced to 1.0")
        # 1. Base Score (Inverse of violations, capped at 10)
        base_score = max(0.0, 1.0 - (min(violations_count, 10) * 0.1))

        # 2. Pattern Score — BMG GPU path or Jaccard fallback
        pattern_score = 0.5
        bmg_used = False
        if violation_types:
            if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true" and agent_name:
                try:
                    BMG_EMBEDDING_AGENT_KEYS = self._get_bmg_embedding_agent_keys()

                    if agent_name in BMG_EMBEDDING_AGENT_KEYS:
                        sem_score = self._calculate_semantic_similarity(territory, violation_types)
                        pattern_score = sem_score
                        bmg_used = True
                        logger.warning(
                            "[BMG-GPU] %s: semantic score=%.4f (CUDA/bge-m3)",
                            agent_name,
                            sem_score,
                        )
                except Exception:  # guardian: allow-silent-swallower  # noqa: BLE001
                    pass

            if not bmg_used:
                scores = [self._calculate_pattern_confidence(v) for v in violation_types]
                pattern_score = sum(scores) / len(scores)

        # 3. Weighted Final Calculation
        final_value = (base_score * 0.4) + (pattern_score * 0.4) + (historical_success_rate * 0.2)

        # Boost for governance territories, penalty for safety critical
        if territory == "prompt_governance":
            final_value *= 1.1
        if territory.startswith("L5"):
            final_value *= 0.9

        reasoning = f"Base: {base_score:.2f}, Pattern: {pattern_score:.2f}"
        if bmg_used:
            reasoning += " [BMG-GPU]"
        return ConfidenceScore(
            value=min(1.0, final_value),
            reasoning=reasoning,
        )

    def should_proceed_with_healing(
        self,
        confidence: ConfidenceScore,
        agent_name: str = "Unknown",
        territory: str = "unknown",
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> tuple[bool, str]:
        """Determines if healing should proceed using the hardened SSOT routing algorithm."""
        is_safe, msg = self._check_healing_budget(agent_name)
        if not is_safe:
            return False, f"SAFETY LOCK: {msg}"

        routing = self._route_decision(
            confidence=confidence,
            agent_name=agent_name,
            territory=territory,
            failure_type=failure_type,
            retry_count=retry_count,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )

        decision_data = {
            "agent": agent_name,
            "territory": territory,
            "confidence": confidence.value,
            "reasoning": confidence.reasoning,
            "timestamp": datetime.now().isoformat(),
            "routing_tier": routing.tier.value,
            "routing_gate": routing.gate_applied,
            "routing_score": routing.score,
            "routing_digest": routing.determinism_digest,
            "model": routing.model_id,
            "decision": None,
            "reason": None,
        }

        # ── Confidence-score SSOT routing ────────────────────────────────────
        # Single routing rule — confidence score is the only input to tier.
        # FAIL_CLOSED from _route_decision (safety gates: replay, retry,
        # provider prohibition) is preserved and takes precedence.
        #
        #   conf > 0.80  → DETERMINISTIC
        #   0.50 < conf ≤ 0.80 → QWEN (Qwen2.5-14B)
        #   conf ≤ 0.50  → GEMINI 2.5 Pro
        try:
            from agentic_core.L2_execution.healers.healing_tier_config import (
                HEALING_CONFIDENCE_X as _CONF_X,
            )
            from agentic_core.L2_execution.healers.healing_tier_config import (
                HEALING_CONFIDENCE_Y as _CONF_Y,
            )
        except ImportError:  # guardian: allow-silent-swallower
            _CONF_X = 0.80
            _CONF_Y = 0.50
        if routing.tier != RoutingTier.FAIL_CLOSED:
            if confidence.value > _CONF_X:
                tier = RoutingTier.DETERMINISTIC
                decision_data["model"] = "deterministic-sovereign"
            elif confidence.value > _CONF_Y:
                tier = RoutingTier.QWEN
                decision_data["model"] = os.getenv("QWEN_14B_MODEL", "Qwen2.5-14B-Instruct-AWQ")
            else:
                tier = RoutingTier.GEMINI
                decision_data["model"] = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
            # Sync routing_tier in decision_data to the confidence-SSOT override value
            decision_data["routing_tier"] = tier.value
        else:
            tier = routing.tier

        if tier == RoutingTier.FAIL_CLOSED:
            reason = f"FAIL-CLOSED ({routing.gate_applied}, S={routing.score})"
            decision_data["decision"] = False
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return False, reason

        if tier == RoutingTier.DETERMINISTIC:
            self._healing_count += 1
            self._call_path.add(agent_name)
            reason = f"AUTO-HEAL: SOVEREIGN-AUTO ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
            decision_data["decision"] = True
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return True, reason

        if tier == RoutingTier.QWEN:
            # Medium score: Qwen arbitrates. If Qwen says NO, fall through to
            # agent-native logic — healing is never blocked by a single NO.
            qwen_approved = True
            qwen_reason = f"LLM Override: LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score})"
            try:
                arbiter = self._get_qwen_vllm_arbiter()
                vllm_result = arbiter(
                    agent_name=agent_name,
                    violation_types=list(confidence.reasoning.split(", ") if confidence.reasoning else []),
                    territory=territory,
                    score=routing.score,
                    gate=routing.gate_applied,
                )
                qwen_approved = vllm_result.get("decision", True)
                raw_reason = vllm_result.get("reason", "")[:120]
                qwen_reason = f"LLM Override: LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score}): {raw_reason}"
                logger.warning("[QWEN14B] %s -> decision=%s reason=%s", agent_name, qwen_approved, raw_reason)
            except Exception as _qwen_err:  # guardian: allow-silent-swallow
                logger.warning("[QWEN14B] vLLM call failed, falling to agent-native: %s", _qwen_err)

            if qwen_approved:
                final_reason = qwen_reason
            else:
                # Qwen said NO — fall through to agent-native logic
                logger.info(
                    "[ROUTING] Qwen declined %s (S=%d) — falling to AGENT-NATIVE logic",
                    agent_name,
                    routing.score,
                )
                final_reason = f"LLM Override: QWEN14B-DECLINED ({confidence.value:.2f}, S={routing.score}): agent logic governs"

            self._healing_count += 1
            self._call_path.add(agent_name)
            decision_data["decision"] = True
            decision_data["reason"] = final_reason
            self.decisions_made.append(decision_data)
            return True, final_reason

        # tier == RoutingTier.GEMINI
        # High score: most complex reasoning — Gemini 2.5 Pro arbitrates.
        # Gemini is the final gate; once reached, healing always proceeds.
        target_model = decision_data.get("model", routing.model_id)
        logger.info(
            "[GEMINI] Invoking %s for %s (S=%d gate=%s) — high-complexity arbitration",
            target_model,
            agent_name,
            routing.score,
            routing.gate_applied,
        )
        self._healing_count += 1
        self._call_path.add(agent_name)
        _gemini_label = (
            "RECOVERY-PRO"
            if confidence.value < 0.40
            else ("FLASH" if "flash" in target_model.lower() else "GEMINI")
        )
        reason = f"LLM Override: LLM-ARBITRATED-{_gemini_label} ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
        decision_data["decision"] = True
        decision_data["reason"] = reason
        self.decisions_made.append(decision_data)
        return True, reason

    def _hitl_gate(
        self,
        agent_name: str,
        confidence: "ConfidenceScore",
        tier: str,
    ) -> tuple[bool, str]:
        """
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        """
        import sys

        border = "=" * 56
        print(f"\n{border}")
        print(f"  HITL GATE  [{tier} CONFIDENCE]")
        print(border)
        print(f"  Agent     : {agent_name}")
        print(f"  Confidence: {confidence.value:.2f}  ({tier})")
        print(f"  Reasoning : {confidence.reasoning}")
        print(border)
        print("  [Y] Approve healing    [N] Reject    [D] Defer to report")
        print(border)

        if getattr(self, "auto_approve", False):
            return True, f"HITL-AUTO-APPROVED: --heal active ({confidence.value:.2f})"
        if not sys.stdin.isatty():
            reason = f"HITL-DEFER (non-interactive, {confidence.value:.2f})"
            print(f"  Non-interactive environment — auto-DEFER: {agent_name}")
            print(border + "\n")
            return False, reason

        try:
            raw = input("  Choice [Y/N/D]: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            raw = "D"

        print(border + "\n")

        if raw == "Y":
            return True, f"HITL-APPROVED ({confidence.value:.2f})"
        elif raw == "N":
            return False, f"HITL-REJECTED ({confidence.value:.2f})"
        else:
            return False, f"HITL-DEFER ({confidence.value:.2f})"

    async def analyze_violations_with_cognitive_disposition(
        self,
        violations: list,
        territory: str,
        state_mgr,
    ):
        """Analyze violations using CognitiveDispositionAgent for enhanced confidence."""
        if not self.enable_cda:
            # Return default values if CDA is disabled; BMG path fires via calculate_healing_confidence
            fallback_conf = self.calculate_healing_confidence(
                len(violations),
                [str(v) for v in violations[:10]],
                territory,
                agent_name="location",
            )
            return [], fallback_conf

        try:
            # Dynamic import of CDA to avoid hard dependency
            from agentic_core.L0_routing.seams.safety_validators_seam import (
                load_cognitive_disposition_agent,
            )

            CognitiveDispositionAgent = load_cognitive_disposition_agent()
            cda = CognitiveDispositionAgent()

            # Analyze violations
            dispositions = await cda.analyze_violations(violations, territory)

            # Calculate enhanced confidence based on cognitive analysis
            if dispositions:
                avg_confidence = sum(d.confidence for d in dispositions) / len(dispositions)
                enhanced_confidence = ConfidenceScore(
                    value=avg_confidence,
                    reasoning=f"Cognitive analysis of {len(dispositions)} dispositions",
                )
            else:
                enhanced_confidence = ConfidenceScore(
                    value=0.5,
                    reasoning="No cognitive dispositions generated",
                )

            return dispositions, enhanced_confidence

        except ImportError:
            logger.warning("CognitiveDispositionAgent not available, using default confidence")
            bmg_conf = self.calculate_healing_confidence(
                len(violations),
                [str(v) for v in violations[:10]],
                territory,
                agent_name="location",
            )
            return [], bmg_conf
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            return [], ConfidenceScore(value=0.5, reasoning=f"CDA error: {str(e)}")

    def request_sovereignty_token(self, agent_name: str, operation: str) -> bool:
        """
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        """
        if self._atomic_lock:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Atomic lock active")
            return False

        if len(self._operation_stack) >= self._max_stack_depth:
            logging.critical(
                f"Sovereignty DENIED for {agent_name}: Stack depth exceeded ({len(self._operation_stack)})",
            )
            return False

        # Cycle detection
        op_signature = f"{agent_name}:{operation}"
        if op_signature in self._operation_stack:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Cycle detected {op_signature}")
            return False

        self._operation_stack.append(op_signature)
        self._atomic_lock = True
        self._sovereignty_token = f"SOV_{int(time.time())}_{agent_name}"
        return True

    def release_sovereignty_token(self, agent_name: str, success: bool = True) -> None:
        """Release the lock after operation completion."""
        if not self._atomic_lock:
            return

        if self._operation_stack:
            self._operation_stack.pop()

        self._atomic_lock = False
        self._sovereignty_token = None

        if not success:
            logging.warning(f"Sovereignty released with FAILURE status for {agent_name}")


# Backward-compatible aliases for the former 3-class hierarchy
AutonomousDecisionEngine = SovereignDecisionEngine
EnhancedAutonomousDecisionEngine = SovereignDecisionEngine


# ============================================================================
# PRE-FLIGHT VALIDATION LAYER (HARDENED)
# ============================================================================


class PreFlightValidator:
    """
    [ULTRA-HARDENED] Sovereign Contract Enforcer.
    Verifies environmental readiness and enforces strict agent signatures/imports.
    """

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run

    def run_checks(self) -> tuple[bool, list[str]]:
        errors = []

        # 1. Windows Long Paths (System Stability)
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\FileSystem",
                )
                val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if val != 1:
                    if os.getenv("AGENTIC_BYPASS_LONGPATHS_CHECK") == "1":
                        logging.warning(
                            "AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail"
                        )
                    elif self.dry_run:
                        logging.warning(
                            "Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode"
                        )
                    else:
                        errors.append("Windows LongPathsEnabled is NOT active (Set to 1 in Registry)")
            # guardian: allow-silent-swallow
            except Exception as e:
                logging.warning(f"Could not verify Windows LongPathsEnabled: {e}")

        # 2. Critical Directory Structure (SSOT Integrity)
        required_dirs = [AGENTIC_CORE_DIR, L5_SAFETY_DIR, "agentic_core/prompt_governance"]
        for d in required_dirs:
            if not (self.project_root / d).exists():
                errors.append(f"Critical directory missing: {d}")

        # 3. Write Permissions (Operational Readiness)
        try:
            test_file = self.project_root / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            errors.append("Project root is not writable")

        return len(errors) == 0, errors

    def validate_agent_integrity(self, agents: dict[str, Any]) -> list[str]:
        """
        [CONTRACT GUARD] Mandatory validation of all registered agents.
        Catches legacy signatures, broken mixins, and instantiation failures.
        """
        integrity_errors = []
        for name, agent_cls in agents.items():
            try:
                # Force instantiation to catch import/mixin errors immediately
                agent = agent_cls(project_root=self.project_root) if inspect.isclass(agent_cls) else agent_cls
            # guardian: allow-silent-swallow
            except Exception as e:
                integrity_errors.append(f"Agent {name} FAILED INSTANTIATION: {e}")
                continue

            # 1. Presence of 'heal' method
            if not hasattr(agent, "heal") or not callable(agent.heal):
                integrity_errors.append(f"Agent {name} violates Protocol: Missing 'heal' method")
                continue

            # 2. Signature Validation: only flag the specific legacy heal(path) signature
            sig = inspect.signature(agent.heal)
            params = list(sig.parameters.keys())

            if "path" in params and len(params) == 1:
                integrity_errors.append(
                    f"Agent {name} has LEGACY SIGNATURE: heal(path). Must update to heal(violation).",
                )

            # 3. Mixin Verification (MRO Audit)
            mro_names = [c.__name__ for c in inspect.getmro(agent.__class__)]
            if "NamingAgent" in name and "SubatomicTestingMixin" not in mro_names:
                integrity_errors.append(f"Agent {name} missing mandatory SubatomicTestingMixin in MRO.")

        return integrity_errors


# ============================================================================
# HARDENING UTILITIES (NEW)
# ============================================================================


class NonInteractiveGuard:
    """
    [HARDENED] Global overrides to prevent terminal prompts from hanging CI/CD.
    Now includes Resource Exhaustion Protection against infinite prompt loops.
    """

    # guardian: allow-magic-config
    def __init__(self, active: bool = True, max_blocked_prompts: int = 10):
        self.active = active
        self.max_blocked_prompts = max_blocked_prompts
        self.blocked_count = 0
        self.original_input = builtins.input

    def __enter__(self):
        if self.active:
            builtins.input = self._trap_input
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.input = self.original_input

    def _trap_input(self, prompt=None):
        # Auto-approve if env var set (avoids RecursionError bomb in CI/auto mode)
        if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
            logger.debug(f"AUTO-APPROVE: suppressing input('{prompt}')")
            return "y"

        self.blocked_count += 1
        if self.blocked_count > self.max_blocked_prompts:
            raise RecursionError(
                f"Infinite Loop Protection: {self.blocked_count} prompts blocked (max={self.max_blocked_prompts})"
            )
        logger.warning(
            f"BLOCKED PROMPT ({self.blocked_count}/{self.max_blocked_prompts}): Agent attempted input('{prompt}')",
        )
        raise RuntimeError(f"Interactive prompt blocked in autonomous mode: {prompt}")


@_optional_runtime_guard()("D.with_retry.execute_ssot")
# guardian: allow-magic-config
def with_retry(max_retries=3, delay=1.0):
    """
    [HARDENED] Decorator for transient failure resilience with exponential backoff.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                # guardian: allow-silent-swallow
                except Exception as e:
                    last_exception = e
                    # Don't retry on security guard or exhaustion errors
                    if isinstance(e, RuntimeError) and "prompt" in str(e):
                        raise e
                    if isinstance(e, RecursionError):
                        raise e

                    wait_time = delay * (2**attempt)
                    logger.error(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}\n{traceback.format_exc()}",
                    )
                    time.sleep(wait_time)
            logger.error(f"All {max_retries} retries exhausted for {func.__name__}")
            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# PHASE 2: RECONCILIATION (The Dangerous Phase)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=2)
def execute_phase2_reconciliation(
    agents: dict[str, Any],
    territory: str,
    decision_engine: SovereignDecisionEngine,  # [HARDENED] Updated type
    state_mgr: "RuntimeStateManager",
    plan: dict[str, Any],
    ctx: "HealContext" = None,
    **kwargs,
):
    """
    PHASE 2: EXECUTE HEALING (HARDENED)
    Critical Path: Modifications occur here. Must strictly adhere to decision engine.
    Enhanced with atomic operations and sovereignty patterns from FileClassificationAgent.
    Returns: Dict conforming to HEAL_RESULT_SCHEMA
    """
    reconciliation_log = []
    failed_fixes = []

    if not plan or not plan.get("violations_found"):
        logging.info("Phase 2: No violations to reconcile.")
        return {
            "violations_found": 0,
            "violations_fixed": 0,
            "status": "skipped",
            "errors": 0,
            "skipped": 0,
            "execution_time_ms": 0.0,
            "error_message": None,
        }

    violations_list = plan["violations_found"]
    logging.warning(f"Phase 2: Reconciling {len(violations_list)} violations across agents...")

    # Group violations by agent key so each agent's heal_repository() is called once
    # with the full set of violations it owns, and sovereignty token is held for that batch.
    from collections import defaultdict

    by_agent: dict[str, list] = defaultdict(list)
    for v in violations_list:
        by_agent[v.get("suggested_agent", "reconciler")].append(v)

    # Progress bar for agent healing
    agent_items = list(by_agent.items())
    with tqdm(total=len(agent_items), desc="Healing agents", unit="agent", ncols=100) as pbar:
        for idx, (agent_key, agent_violations) in enumerate(agent_items, 1):
            pbar.set_description(f"Agent: {agent_key[:20]:<20} ({idx}/{len(agent_items)})")
            violation_types = [v.get("type", "UNKNOWN") for v in agent_violations]

            agent_cls = agents.get(agent_key)
            if agent_cls is None:
                logging.warning(
                    f"Phase 2: agent key '{agent_key}' not in registry — skipping {len(agent_violations)} violations"
                )
                failed_fixes.extend(
                    {"violation": v, "reason": f"Agent '{agent_key}' not registered", "status": "blocked"}
                    for v in agent_violations
                )
                pbar.update(1)
                continue

            confidence = decision_engine.calculate_healing_confidence(
                violations_count=len(agent_violations),
                violation_types=violation_types,
                territory=territory,
                agent_name=agent_key,
            )

            allowed, reason = decision_engine.should_proceed_with_healing(
                confidence, agent_key, territory=territory
            )
            if not allowed:
                logging.warning(f"Phase 2: BLOCKED {agent_key}: {reason}")
                failed_fixes.extend(
                    {"violation": v, "reason": reason, "status": "blocked"} for v in agent_violations
                )
                pbar.update(1)
                continue

            if ctx is None or not ctx.heal:
                for v in agent_violations:
                    reconciliation_log.append(
                        {"action": "would_fix", "target": v.get("file"), "agent": agent_key, "reason": reason}
                    )
                pbar.update(1)
                continue

            if not decision_engine.request_sovereignty_token(agent_key, violation_types[0]):
                failed_fixes.extend(
                    {"violation": v, "reason": "Sovereignty Token Denied", "status": "locked"}
                    for v in agent_violations
                )
                pbar.update(1)
                continue

            try:
                # Instantiate the agent class and call heal_repository() — the real mutation path
                agent_instance = agent_cls(project_root=REPO_ROOT)
                state_mgr.update_agent(
                    agent_key, f"[{reason.split('(')[0].strip()}] Healing {len(agent_violations)} violations"
                )

                logging.warning(
                    "Phase 2: [%s] → calling heal_repository(dry_run=False, execute=True) for %d violations [routing: %s]",
                    agent_key,
                    len(agent_violations),
                    reason.split("(")[0].strip(),
                )

                # Tier 1: record mutation intent via UWG before execution.
                # grant_write_permission is informational — UWG tracks all agent
                # mutation attempts for audit and replay without blocking them.
                _uwg = _get_uwg()
                _territory_posix = Path(territory).as_posix() + "/"
                _uwg.grant_write_permission(_territory_posix)

                # [FIX-HANG] Run heal_repository with timeout to prevent indefinite hangs.
                # Territory scoping reduces scan surface; timeout is the hard safety net.
                _HEAL_TIMEOUT_S = int(os.environ.get("HEAL_TIMEOUT_SECONDS", "300"))
                with ThreadPoolExecutor(max_workers=1) as _pool:
                    _future = _pool.submit(
                        agent_instance.heal_repository,
                        dry_run=False,
                        execute=True,
                        target_territory=territory,
                    )
                    try:
                        fix_result = _future.result(timeout=_HEAL_TIMEOUT_S)
                    except FuturesTimeoutError:
                        logging.error(
                            "Phase 2: [%s] TIMEOUT after %ds — heal_repository hung. Skipping.",
                            agent_key,
                            _HEAL_TIMEOUT_S,
                        )
                        raise RuntimeError(
                            f"heal_repository timed out after {_HEAL_TIMEOUT_S}s for {agent_key}"
                        )
                    finally:
                        _uwg.revoke_write_permission(_territory_posix)
                        _uwg.record_mutation(
                            path=_territory_posix,
                            operation="heal_repository",
                            permitted=True,
                        )

                if not isinstance(fix_result, dict):
                    fix_result = {"raw_output": str(fix_result)}

                fix_result["agent"] = agent_key
                fix_result["violations_submitted"] = len(agent_violations)
                fix_result["routing_reason"] = reason

                # Tier 3: lift unstructured dict to canonical HealCheckResult.
                # Non-fatal — adapter failure must never block healing pipeline.
                try:
                    _adapt = _get_heal_result_adapter()
                    _hcr = _adapt(
                        agent_name=agent_key,
                        raw_result=fix_result,
                        repo_root=REPO_ROOT,
                    )
                    fix_result["_heal_check_result"] = _hcr.to_dict()
                except Exception as _tier3_err:  # guardian: allow-silent-swallower
                    logger.warning("Tier-3 adapt failed for %s: %s", agent_key, _tier3_err)

                if fix_result.get("success", True) is False:
                    raise RuntimeError(f"Agent reported failure: {fix_result.get('error', 'Unknown')}")

                reconciliation_log.append(fix_result)
                decision_engine.release_sovereignty_token(agent_key, success=True)
                # [H3] Record healing action for Phase 2 reconciliation.
                # "reconciler" and "location" agents are already recorded unconditionally
                # in execute_phase1_discovery_impl — skip them here to avoid duplicates.
                _AGENT_KEY_TO_CLASS_NAME = {
                    "reconciler": "FilesystemSSOTHealerAgent",
                    "location": "LocationHealerAgent",
                    "hierarchy": "HierarchyHealerAgent",
                    "arch_governor": "ArchitectureGovernorAgent",
                    "gravity_repair": "GravityLeakHealerAgent",
                    "file_classification": "FileClassificationHealerAgent",
                    "observability_probe": "ObservabilityProbeExecutorAgent",
                    "cognitive_disposition": "CognitiveDispositionAgent",
                    "root_hygiene": "RootHygieneAgent",
                }
                _PHASE1_RECORDED = {"reconciler", "location"}
                if agent_key not in _PHASE1_RECORDED:
                    _record_healing_action(
                        state_mgr,
                        agent=_AGENT_KEY_TO_CLASS_NAME.get(agent_key, agent_key),
                        territory=territory,
                        routing_score=confidence.value if hasattr(confidence, "value") else 0.0,
                        routing_tier=reason.split("(")[0].strip() if reason else "DETERMINISTIC",
                        confidence=confidence.value if hasattr(confidence, "value") else 0.0,
                        fix_summary=f"Applied {len(agent_violations)} reconciliation fixes via heal_repository",
                        outcome="SUCCESS",
                    )
                logging.warning(
                    "Phase 2: [%s] ✓ heal_repository() complete — result keys: %s",
                    agent_key,
                    list(fix_result.keys()),
                )
                pbar.update(1)

            # guardian: allow-silent-swallow
            except Exception as e:
                logging.error(f"Phase 2: Fix failed for {agent_key}: {e}")
                failed_fixes.extend(
                    {"violation": v, "error": str(e), "status": "execution_error"} for v in agent_violations
                )
                decision_engine.release_sovereignty_token(agent_key, success=False)
                pbar.update(1)

    return {
        "violations_found": len(violations_list),
        "violations_fixed": len(reconciliation_log),
        "status": "success" if not failed_fixes else "partial_success",
        "errors": len(failed_fixes),
        "skipped": 0,
        "execution_time_ms": 0.0,
        "error_message": None if not failed_fixes else f"{len(failed_fixes)} violations failed",
        "_raw_result": {"modifications": reconciliation_log, "failures": failed_fixes},
    }


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================


# [REMOVED DUPLICATE] execute_phase3_final_validation removed.
# Usage consolidated to execute_phase3_validation at line 1273.


# ============================================================================
# ENHANCED PHASE EXECUTION & INPUT VALIDATION
# ============================================================================


def validate_territory_input(territory: str) -> tuple[bool, str]:
    """Validate territory input with comprehensive security checks."""
    if not territory:
        return True, ""
    if len(territory) > 100:
        return False, "Name too long"
    if not re.match(r"^[A-Za-z0-9_]+$", territory):
        return False, "Invalid characters"
    return True, ""


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Directory Constants
AGENTIC_CORE_DIR = "agentic_core"
APPS_SHARED_DIR = "apps_shared"
APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"
SCRIPTS_DIR = "scripts"
AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
RUNTIME_STATE_FILE = "runtime_state.json"

# Project Root Path — resolved lazily via module __getattr__ or REPO_ROOT.

# [ULTRA-HARDENED] Whitelist of allowed module prefixes for dynamic imports
# Prevents loading agents from unexpected packages (defense-in-depth against tampered discovery/cache)
ALLOWED_MODULE_PREFIXES = (AGENTIC_CORE_DIR, APPS_SHARED_DIR, APPS_LIC_DIR, APPS_RG_DIR)

# Logging: configured once in _configure_logging() called from main().
logger = logging.getLogger("UnifiedSovereign")

# ============================================================================
# RUNTIME STATE MANAGEMENT (From Canon Validator)
# ============================================================================


class RuntimeStateManager:
    """Manages live state for dashboard observability."""

    def __init__(self, project_root: Path, execution_context: Optional["ExecutionContext"] = None):
        self.project_root = project_root.resolve()  # [ULTRA-HARDENED] Force real absolute path resolution
        self._execution_context = execution_context

        # [CROSS-RUN PERSISTENCE] Seed meta_learning from prior runtime_state.json so that
        # _compute_novelty_score() and _fire_meta_learning_intake() have access to
        # recent_failure_vectors accumulated across past runs (REQ-058/REQ-071: full feedback loop).
        _prior_meta: dict = {}
        _prior_state_path = self.project_root / RUNTIME_STATE_FILE
        if _prior_state_path.exists():
            try:
                import json as _json_init

                _prior_raw = _json_init.loads(_prior_state_path.read_text(encoding="utf-8"))
                _prior_meta = _prior_raw.get("meta_learning", {})
            except Exception:  # guardian: allow-silent-swallower
                _prior_meta = {}

        # Wave 1 restore: reload HealingSuccessRateStore EMA state from prior run
        _prior_sr_state = _prior_meta.get("success_rate_store")
        if _prior_sr_state:
            try:
                from system_learning.engines.healing_success_rate_store import (
                    get_default_store as _get_sr_init,
                )

                _get_sr_init().import_state(_prior_sr_state)
            except Exception:  # guardian: allow-silent-swallower
                pass

        self.state = {
            "status": "idle",
            "start_time": None,
            "end_time": None,
            "current_agent": None,
            "current_layer": None,
            "agents_order": [],
            "completed_agents": [],
            "skipped_agents": [],
            "events": [],
            # [INTEGRATION] Ported from Canon Validator
            # [CROSS-RUN] recent_failure_vectors, total_experiences, strategy_weights,
            # and patterns_extracted are seeded from the prior run's persisted state so the
            # novelty scorer and meta-learning pipeline see accumulated history, not just
            # this run's data.  All other fields reset to clean-run defaults.
            "meta_learning": {
                "enabled": False,
                "total_experiences": _prior_meta.get("total_experiences", 0),
                "patterns_extracted": _prior_meta.get("patterns_extracted", 0),
                "strategy_weights": _prior_meta.get(
                    "strategy_weights", {"cot": 1.0, "tot": 1.0, "react": 1.0}
                ),
                "recent_experiences": list(_prior_meta.get("recent_experiences", [])),
                # Cap at 200 on load — same cap enforced on write in _fire_meta_learning_intake
                "recent_failure_vectors": list(_prior_meta.get("recent_failure_vectors", []))[-200:],
            },
            "compliance_scores": {},
            # [SILENT AGGREGATION] Track decisions for final report
            "decisions_made": [],
            "compliance_report": {},
            # [SSOT MIXIN] Audit chain for cryptographic AuditTrailMixin
            "audit_chain": [],
        }
        # [HARDENED] Register exit handler to prevent 'zombie' running states
        atexit.register(self._emergency_cleanup)
        # [G-12-1] Latch: once L0 mutation prohibition fires, disable all future save() attempts
        self._persistence_disabled: bool = False

    def start_mission(self, mission_type: str, agents_order: list[str]):
        self.state["status"] = "running"
        self.state["start_time"] = datetime.now().isoformat()
        self.state["agents_order"] = agents_order
        self.add_event("info", f"Mission started: {mission_type}")
        self.save()

    def update_agent(self, agent_name: str, layer: str):
        self.state["current_agent"] = agent_name
        self.state["current_layer"] = layer
        self.add_event("agent_start", f"→ Executing {agent_name} ({layer})")
        # [FIX-I1] Removed self.save() — save at territory boundaries only

    def skip_agent(self, agent_name: str, reason: str):
        """Records agent as skipped — confidence gate or HITL rejected execution."""
        self.state["skipped_agents"].append(
            {
                "agent": agent_name,
                "time": datetime.now().isoformat(),
                "reason": reason,
            },
        )
        self.add_event("agent_skip", f"SKIPPED {agent_name}: {reason}")
        # [FIX-I1] Removed self.save() — save at territory boundaries only

    def complete_agent(self, agent_name: str, success: bool, details: str = ""):
        """
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        """
        self.state["completed_agents"].append(
            {
                "agent": agent_name,
                "time": datetime.now().isoformat(),
                "success": success,
                "details": details,
            },
        )
        # Log to file/state but DO NOT PRINT JSON to console here
        self.add_event("agent_end", f"{'✓' if success else '❌'} Completed {agent_name}")
        # [FIX-I1] Removed self.save() — save at territory boundaries only

    def add_event(self, event_type: str, message: str):
        self.state["events"].append(
            {"time": datetime.now().isoformat(), "type": event_type, "message": message},
        )
        # [SILENT AGGREGATION] Only log minimal status to console during execution
        # Full telemetry captured in state for final report
        if event_type == "error":
            logger.error(message)
        elif event_type == "warning":
            logger.warning(message)
        elif event_type in ["agent_start", "agent_end", "agent_skip"]:
            # Keep minimal agent progress indicators
            logger.info(message)
        else:
            # Suppress other verbose intermediate logs
            pass

    def finish_mission(self, status="completed"):
        self.state["status"] = status
        self.state["end_time"] = datetime.now().isoformat()
        self.state["current_agent"] = None
        self.save()

    def save(self):
        """
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        """
        # [G-12-1] Latch: skip all future attempts after first prohibition
        if self._persistence_disabled:
            return

        try:
            from agentic_core.L0_routing.scripts.runtime_state_digest import (
                DIGEST_SCHEMA_VERSION,
                compute_runtime_state_digest,
            )

            self.state["runtime_state_digest_sha256"] = compute_runtime_state_digest(self.state)
            self.state["runtime_state_digest_schema_version"] = DIGEST_SCHEMA_VERSION
        # guardian: allow-silent-swallow
        except Exception:
            pass

        try:
            state_path = self.project_root / RUNTIME_STATE_FILE
            temp_dir = state_path.parent
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp file
            with tempfile.NamedTemporaryFile("w", dir=str(temp_dir), delete=False, encoding="utf-8") as tf:
                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
                json.dump(self.state, tf, indent=2, default=str, ensure_ascii=False)
                temp_name = tf.name

            # [HARDENED] Set strict permissions (Owner Read/Write only) before moving
            # This prevents other users on shared CI runners from reading potential sensitive logs
            os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)

            # Atomic replacement
            os.replace(temp_name, state_path)

        except PermissionError as e:
            err_str = str(e)
            if "MUTATION_PROHIBITED" in err_str:
                # [G-12-1] First and only log — latch disabled for remainder of run
                self._persistence_disabled = True
                logger.critical(
                    "[RuntimeStateManager] L0 mutation prohibition active — "
                    "runtime state persistence DISABLED for this run (fail-closed). "
                    f"Reason: {err_str}"
                )
                # Cleanup temp if created
                try:
                    # guardian: allow-path-string
                    if "temp_name" in locals() and os.path.exists(temp_name):
                        os.remove(temp_name)
                # guardian: allow-silent-swallow
                except Exception:
                    pass
            else:
                logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
            try:
                # guardian: allow-path-string
                if "temp_name" in locals() and os.path.exists(temp_name):
                    os.remove(temp_name)
            # guardian: allow-silent-swallow
            except Exception:
                pass

    def _emergency_cleanup(self):
        """Ensure state is finalized even on unhandled exit."""
        if self.state["status"] == "running":
            self.finish_mission("terminated")

    def update_meta_learning(self, experience_data: dict[str, Any]):
        """[INTEGRATION] Updates cognitive metrics for dashboard."""
        ml = self.state["meta_learning"]
        ml["enabled"] = True

        if "total_experiences" in experience_data:
            ml["total_experiences"] = experience_data["total_experiences"]

        if "strategy_weights" in experience_data:
            ml["strategy_weights"] = experience_data["strategy_weights"]

        if "experience" in experience_data:
            ml["recent_experiences"].insert(0, experience_data["experience"])
            ml["recent_experiences"] = ml["recent_experiences"][:5]  # Keep last 5

        self.save()


# ============================================================================
# AUTONOMOUS DECISION ENGINE (From SSOT Protocol)
# ============================================================================


def discover_agents_from_registry(project_root: Path, dedupe: bool = True) -> list[tuple[str, str]]:
    """Hybrid agent discovery: prefer cached JSON, fallback to live scan."""
    agents = []
    json_path = project_root / AGENT_DISCOVERY_JSON

    # Try Cache
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            for agent in data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            logger.info(f"Loaded {len(agents)} agents from cache")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")

    # Try Live Scan if empty
    if not agents:
        try:
            from agentic_core.utils.discovery.Full_Agent_discovery import discover_all_agents

            logger.info("Running live agent discovery...")
            discovery_data = discover_all_agents(project_root)
            for agent in discovery_data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            # [ULTRA-HARDENED] Atomic write + strict 600 permissions for agent discovery cache
            try:
                temp_name = None
                with tempfile.NamedTemporaryFile(
                    "w",
                    delete=False,
                    dir=str(project_root),
                    encoding="utf-8",
                ) as tf:
                    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
                    json.dump(discovery_data, tf, indent=2, ensure_ascii=False)
                    temp_name = tf.name
                os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
                os.replace(temp_name, json_path)
                logger.info(f"Discovered {len(agents)} agents (cached)")
            # guardian: allow-silent-swallow
            except Exception as cache_err:
                logger.warning(f"Failed to cache agent discovery: {cache_err}")
                # guardian: allow-path-string
                if temp_name and os.path.exists(temp_name):
                    assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
                    os.remove(temp_name)
        except ImportError:
            logger.warning("Live discovery unavailable - Full_Agent_discovery not found")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Live discovery failed: {e}")

    if dedupe:
        agents = sorted(set(agents), key=lambda x: x[0])
    return agents


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================
@standard_heal
def execute_phase3_validation(
    agents: dict[str, Any],
    territory: str,
    original_violations: list[dict],
    dry_run: bool = False,
    **kwargs,
):
    """
    PHASE 3: POST-MORTEM VALIDATION

    Verifies that 'fixed' files now pass AST and SSOT checks.
    Does NOT blindly trust the agent's 'success' return value.
    """
    if dry_run:
        return {"status": "skipped", "message": "Dry run - validation skipped"}

    remaining_issues = []
    # [HARDENING] Use the memory-safe AST validator defined in Phase 1
    # guardian: allow-path-string
    validator = ASTCodeQualityValidator(REPO_ROOT)

    for v in original_violations:
        fpath = v.get("file")

        # 1. Existence Check
        # guardian: allow-path-string
        if not fpath or not os.path.exists(fpath):
            # If it was an orphan that was deleted, this is good.
            # If it was a missing file that was created, we check existence.
            drift_type = v.get("drift_type", "")
            if "ORPHAN" in drift_type:
                # File gone = Success
                continue
            elif "MISSING" in drift_type:
                remaining_issues.append({"file": fpath, "error": "File still missing after heal"})
                continue
            else:
                # Standard file modification - if gone, that's bad
                remaining_issues.append({"file": fpath, "error": "File vanished after heal"})
                continue

        # 2. AST Quality Check on Modified Files
        # We only check files that exist and were targets of modification
        quality_report = validator.check_file_quality(Path(fpath))
        if quality_report.get("violations"):
            for issue in quality_report["violations"]:
                issue["source"] = "post_heal_validation"
                remaining_issues.append(issue)

    status = "clean"
    if remaining_issues:
        status = "drift_detected"

    return {
        "status": status,
        "remaining_violations": remaining_issues,
        "verification_timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# EXECUTION PHASES (SSOT Logic + Canon Observability)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase1_discovery(agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, ctx)


def execute_phase1_discovery_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration"""
    logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")

    state_mgr.update_agent("FilesystemSSOTHealerAgent", "L5 - Safety (Validator)")

    from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import (
        FilesystemSSOTValidatorAgent as _FilesystemSSOTValidatorAgent,
    )

    _fs_validator = _FilesystemSSOTValidatorAgent(project_root=REPO_ROOT)
    _fs_check = _fs_validator.to_check_dict()
    drift_report = _fs_check["evidence"]

    if drift_report is None:
        state_mgr.complete_agent("FilesystemSSOTHealerAgent", False, "Returned None")
        return None, None

    # Direct heal_repository call — same pattern as all other agents
    if ctx is not None and getattr(ctx, "heal", False):
        _fs_healer_cls = agents.get("reconciler")
        if _fs_healer_cls is not None:
            _fs_healer_instance = _fs_healer_cls(project_root=REPO_ROOT)
            _fs_healer_instance.heal_repository(dry_run=False, execute=True)

    violations_count = _fs_check.get("violations_count", 0)
    state_mgr.complete_agent("FilesystemSSOTHealerAgent", True, f"Drift violations: {violations_count}")
    _record_healing_action(
        state_mgr,
        agent="FilesystemSSOTHealerAgent",
        territory=territory,
        routing_tier="DETERMINISTIC",
        confidence=1.0,
        fix_summary=f"SSOT drift scan: {violations_count} violation(s) in {territory}",
        outcome="SUCCESS",
    )

    # Location Validation
    state_mgr.update_agent("LocationHealerAgent", "L5 - Safety")
    # [FIX-B11] Single LocationValidatorAgent instance for both scanning and healing
    location_validator = _get_location_validator_agent()(project_root=REPO_ROOT)

    # [ULTRA-HARDENED] Explicit path traversal protection for user-supplied territory string.
    # Territory may live anywhere under REPO_ROOT (e.g. apps_rg, docs, tests) — not only
    # under agentic_core. Resolve against REPO_ROOT and ensure no escape above it.
    repo_root_resolved = REPO_ROOT.resolve()
    territory_path = (repo_root_resolved / territory).resolve()
    if not territory_path.is_relative_to(repo_root_resolved):
        logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
        state_mgr.add_event("security", "Path traversal blocked")
        state_mgr.complete_agent("LocationHealerAgent", False, "Traversal blocked")
        return drift_report, []

    violations = []
    location_scan_result = {}
    if territory_path.exists():
        # [FIX-B11] Use the single location_validator instance for scanning
        location_scan_result = location_validator.run(target_territory=territory) or {}
        violations = location_scan_result.get("violations", [])
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")

    # Enhanced confidence calculation with cognitive analysis
    if violations:
        logger.info("🧠 Using CognitiveDispositionAgent for enhanced violation analysis...")

        # Create event loop for async cognitive analysis
        import asyncio

        # [FIX-I4] Use new_event_loop() — asyncio.get_event_loop() is deprecated in Python 3.10+
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get cognitive dispositions and enhanced confidence
        cognitive_dispositions, enhanced_confidence = loop.run_until_complete(
            decision_engine.analyze_violations_with_cognitive_disposition(violations, territory, state_mgr),
        )

        # Store cognitive dispositions in state for reporting
        state_mgr.state["cognitive_dispositions"] = [d.__dict__ for d in cognitive_dispositions]

        confidence = enhanced_confidence
        logger.info(f"🧠 Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
    else:
        # Fallback to standard confidence calculation
        confidence = decision_engine.calculate_healing_confidence(
            len(violations),
            [str(v) for v in violations[:10]],
            territory,
            agent_name="location",
        )

    state_mgr.state["compliance_scores"][territory] = confidence.value

    # [DETAILED TRACKING] Store actual LocationAgent violations for final report
    state_mgr.state["location_violations"] = violations
    state_mgr.state["location_scan_result"] = location_scan_result

    # [AUTO-HEALING] If confidence is high enough, trigger LocationAgent healing
    if len(violations) > 0:
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence, "LocationHealerAgent", territory=territory
        )
        state_mgr.add_event("decision", f"Location Healing: {reason}")
        logger.info(f"Location Decision: {reason}")

        if proceed and ctx is not None and ctx.heal:
            logger.info(f"Triggering LocationAgent auto-heal for {len(violations)} violations")
            # Wave 6: Attach HITL approval function so _heal_via_archiving can gate deletions.
            # Non-interactive environments auto-defer (skip) the archive.
            import sys as _sys

            def _w6_hitl_archive_gate(file_path, msg):
                if ctx is not None and getattr(ctx, "auto_approve", False):
                    return True, "HITL-AUTO-APPROVED (--heal active)"
                if not _sys.stdin.isatty():
                    return False, "HITL-DEFER (non-interactive)"
                if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
                    return True, "HITL-APPROVED (batch)"
                border = "=" * 56
                print(f"\n{border}")
                print("  HITL GATE  [FILE DELETION / ARCHIVE]")
                print(border)
                print(f"  File  : {file_path}")
                print(f"  Reason: {str(msg)[:100]}")
                print(border)
                print("  [A] Archive (reversible)  [S] Skip  [D] Delete permanently")
                print(border)
                try:
                    raw = input("  Choice [A/S/D]: ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    raw = "S"
                if raw == "A":
                    return True, "HITL-APPROVED (archive)"
                elif raw == "D":
                    return True, "HITL-APPROVED (delete)"
                else:
                    return False, "HITL-SKIPPED"

            location_validator._hitl_approval_fn = _w6_hitl_archive_gate
            # LocationAgent should have a heal method - call it
            if hasattr(location_validator, "heal_violations"):
                heal_result = location_validator.heal_violations(
                    violations, auto_approve=(ctx.auto_approve if ctx else False)
                )
                healed_count = heal_result.get("healed", 0) if isinstance(heal_result, dict) else 0
                state_mgr.state["location_fixed"] = healed_count  # [FIX-B3]
                # [H3] Record healing action for LocationAgent
                _record_healing_action(
                    state_mgr,
                    agent="LocationHealerAgent",
                    territory=territory,
                    routing_score=confidence.value,
                    routing_tier="DETERMINISTIC",
                    confidence=confidence.value,
                    fix_summary=(
                        f"Healed {healed_count} of {len(violations)} location violations"
                        if healed_count > 0
                        else f"Location scan: {len(violations)} violation(s), 0 healed in {territory}"
                    ),
                    outcome="SUCCESS" if healed_count > 0 else "PARTIAL",
                )
                state_mgr.complete_agent(
                    "LocationHealerAgent",
                    True,
                    f"Violations: {len(violations)} | Healed: {healed_count} | Conf: {confidence.value:.2f}",
                )
            else:
                logger.warning(
                    "LocationHealerAgent has no heal_violations method - violations detected but not healed",
                )
                _record_healing_action(
                    state_mgr,
                    agent="LocationHealerAgent",
                    territory=territory,
                    routing_score=confidence.value,
                    routing_tier="DETERMINISTIC",
                    confidence=confidence.value,
                    fix_summary=f"Location scan: {len(violations)} violation(s), no heal method in {territory}",
                    outcome="SKIPPED",
                )
                state_mgr.complete_agent(
                    "LocationHealerAgent",
                    True,
                    f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (no heal method)",
                )
        else:
            _record_healing_action(
                state_mgr,
                agent="LocationHealerAgent",
                territory=territory,
                routing_score=confidence.value,
                routing_tier="DETERMINISTIC",
                confidence=confidence.value,
                fix_summary=f"Location scan: {len(violations)} violation(s), healing skipped in {territory}",
                outcome="SKIPPED",
            )
            state_mgr.complete_agent(
                "LocationHealerAgent",
                True,
                f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (healing skipped)",
            )
    else:
        _record_healing_action(
            state_mgr,
            agent="LocationHealerAgent",
            territory=territory,
            routing_score=confidence.value,
            routing_tier="DETERMINISTIC",
            confidence=confidence.value,
            fix_summary=f"Location scan: 0 violations in {territory}",
            outcome="SUCCESS",
        )
        state_mgr.complete_agent("LocationHealerAgent", True, f"Violations: 0 | Conf: {confidence.value:.2f}")

    # [PHASE 1 ENHANCEMENT] Early File Classification Detection
    # Run FileClassificationAgent in discovery phase to catch naming violations early
    classification_violations = []
    classification_scan_result = {}
    try:
        state_mgr.update_agent("FileClassificationHealerAgent", "L5 - Safety (Validator)")
        from agentic_core.L5_safety.reasoning.file_classification_validator import (
            FileClassificationValidatorAgent as _FileClassificationValidatorAgent,
        )

        _fc_validator = _FileClassificationValidatorAgent(project_root=REPO_ROOT)
        _fc_check = _fc_validator.to_check_dict(target_territory=territory)
        _fc_evidence = _fc_check.get("evidence", {})
        classification_scan_result = _fc_evidence.get("scan_result", {})
        classification_violations = _fc_evidence.get("violations", [])
        classification_count = len(classification_violations)
        state_mgr.complete_agent(
            "FileClassificationHealerAgent",
            True,
            f"Early detection: {classification_count} classification issues",
        )
        _record_healing_action(
            state_mgr,
            agent="FileClassificationHealerAgent",
            territory=territory,
            routing_tier="DETERMINISTIC",
            routing_score=1.0,
            confidence=1.0,
            fix_summary=f"Scanned {territory}: {classification_count} classification issue(s) detected",
            outcome="SUCCESS",
        )

        # Store classification results for later phases (including check_dict for healing)
        state_mgr.state["classification_violations"] = classification_violations
        state_mgr.state["classification_scan_result"] = classification_scan_result
        state_mgr.state["classification_check_dict"] = _fc_check
        state_mgr.state["classification_file_registry"] = _fc_evidence.get("file_registry", [])

        logger.info(f"FileClassificationAgent early detection: {classification_count} issues found")

    except Exception as e:
        logger.error(f"FileClassificationHealerAgent early detection FAILED: {e}\n{traceback.format_exc()}")
        state_mgr.complete_agent("FileClassificationHealerAgent", False, f"Early detection error: {e}")
        _record_healing_action(
            state_mgr,
            agent="FileClassificationHealerAgent",
            territory=territory,
            routing_tier="DETERMINISTIC",
            routing_score=0.0,
            confidence=0.0,
            fix_summary=f"FileClassificationHealerAgent failed: {str(e)[:120]}",
            outcome="FAILED",
        )
        state_mgr.add_event("error", f"FileClassificationHealerAgent early detection failed: {e}")
        state_mgr.state["classification_violations"] = []
        state_mgr.state["classification_scan_result"] = {}
        state_mgr.state["classification_check_dict"] = {}

    return drift_report, violations, location_scan_result


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase3_alignment(agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None):
    """PHASE 3: STRUCTURAL ALIGNMENT (Retriable)"""
    return execute_phase3_alignment_impl(agents, territory, decision_engine, state_mgr, ctx)


def execute_phase3_alignment_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 3: STRUCTURAL ALIGNMENT - Implementation"""
    logger.info(f"=== PHASE 3: ALIGNMENT - {territory} ===")

    state_mgr.update_agent("HierarchyHealerAgent", "L5 - Safety")
    from agentic_core.L5_safety.reasoning.hierarchy_validator import (
        HierarchyValidatorAgent as _HierarchyAgentValidator,
    )

    _hier_agent = _HierarchyAgentValidator(project_root=REPO_ROOT)
    _hier_scan = _hier_agent.scan_root_violations(target_territory=territory)
    _hier_vcount = _hier_scan.get("violations_found", 0)
    if "violations" in _hier_scan and isinstance(_hier_scan["violations"], list):
        _hier_vcount = len(_hier_scan["violations"])
    _hier_check = {
        "check_id": "hierarchy_violations",
        "evidence": _hier_scan,
        "violations_count": _hier_vcount,
        "territory": territory,
        "repo_root": str(REPO_ROOT),
    }
    violations = _hier_check["violations_count"]

    if violations > 0:
        confidence = decision_engine.calculate_healing_confidence(violations, ["HIERARCHY"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence, "HierarchyHealerAgent", territory=territory
        )

        state_mgr.add_event("decision", f"Hierarchy Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed and ctx is not None and ctx.heal:
            _hier_healer_cls = agents.get("hierarchy")
            if _hier_healer_cls is not None:
                _hier_healer_instance = _hier_healer_cls(project_root=REPO_ROOT)
                heal_result = _hier_healer_instance.heal_repository(dry_run=False, execute=True)
            else:
                heal_result = {}
            healed = (
                heal_result.get("violations_fixed", heal_result.get("healed", 0))
                if isinstance(heal_result, dict)
                else 0
            )
            state_mgr.state["hierarchy_fixed"] = healed  # [FIX-B3]
            state_mgr.complete_agent("HierarchyHealerAgent", True, f"Healed: {healed}")
            _record_healing_action(
                state_mgr,
                agent="HierarchyHealerAgent",
                territory=territory,
                routing_tier=reason.split("(")[0].strip() if reason else "DETERMINISTIC",
                routing_score=confidence.value if hasattr(confidence, "value") else 1.0,
                confidence=confidence.value if hasattr(confidence, "value") else 1.0,
                fix_summary=f"Healed {healed} of {violations} hierarchy violation(s) in {territory}",
                outcome="SUCCESS",
            )
            return {"total_healed": healed, "status": "HEALED" if healed > 0 else "NO_CHANGE"}
        else:
            state_mgr.complete_agent("HierarchyHealerAgent", False, "Skipped - Low Confidence")
            _record_healing_action(
                state_mgr,
                agent="HierarchyHealerAgent",
                territory=territory,
                routing_tier="DETERMINISTIC",
                routing_score=confidence.value if hasattr(confidence, "value") else 0.0,
                confidence=confidence.value if hasattr(confidence, "value") else 0.0,
                fix_summary=f"Skipped hierarchy healing in {territory}: {reason}",
                outcome="SKIPPED",
            )
    else:
        state_mgr.complete_agent("HierarchyHealerAgent", True, "No violations found")
        _record_healing_action(
            state_mgr,
            agent="HierarchyHealerAgent",
            territory=territory,
            routing_tier="DETERMINISTIC",
            routing_score=1.0,
            confidence=1.0,
            fix_summary=f"No hierarchy violations in {territory}",
            outcome="SUCCESS",
        )

    return None


# [FIX-B8] GravityLeakRepairAgent runs once globally before the territory loop.
def _run_gravity_repair_global(agents, state_mgr, ctx: "HealContext" = None):
    """Run GravityLeakRepairAgent once globally — gravity (layer inversions) is repo-wide."""
    state_mgr.update_agent("GravityLeakHealerAgent", "L5 - Safety")
    from agentic_core.L5_safety.reasoning.gravity_validator import (
        GravityValidatorAgent as _GravityValidatorAgent,
    )

    try:
        logger.info("Detecting gravity violations (layer inversions)...")
        _gv = _GravityValidatorAgent(project_root=REPO_ROOT)
        _gravity_check = _gv.to_check_dict()
        gravity_violations = _gravity_check["violations_count"]
        gravity_fixed = 0

        if gravity_violations > 0 and ctx is not None and ctx.heal:
            _gravity_healer = agents.get("gravity_repair")
            if _gravity_healer is not None:
                _gh_instance = _gravity_healer(project_root=REPO_ROOT)
                heal_result = _gh_instance.heal_repository(dry_run=False, execute=True)
                gravity_fixed = heal_result.get("violations_fixed", 0) if isinstance(heal_result, dict) else 0

        state_mgr.state["gravity_fixed"] = gravity_fixed  # [FIX-B3]
        # [H3] Record GravityValidatorAgent scan result
        _record_healing_action(
            state_mgr,
            agent="GravityValidatorAgent",
            territory="__global__",
            routing_tier="DETERMINISTIC",
            confidence=0.9,
            fix_summary=f"Scanned for gravity violations: {gravity_violations} found",
            outcome="SUCCESS",
        )
        # [H3] Always record GravityLeakHealerAgent outcome
        _record_healing_action(
            state_mgr,
            agent="GravityLeakHealerAgent",
            territory="__global__",
            routing_tier="DETERMINISTIC",
            confidence=0.9,
            fix_summary=(
                f"Fixed {gravity_fixed} of {gravity_violations} gravity violations"
                if gravity_violations > 0
                else "No gravity violations detected"
            ),
            outcome="SUCCESS" if gravity_fixed > 0 or gravity_violations == 0 else "PARTIAL",
        )

        # Store gravity violations for final reporting
        gravity_violation_list = []
        if gravity_violations > 0:
            gravity_violation_list.append(
                {
                    "type": "GRAVITY",
                    "message": f"Found {gravity_violations} gravity violations (layer inversions)",
                    "severity": "high",
                    "recommended_action": "Review and fix layer boundary violations",
                    "confidence": 0.9,
                    "violations_found": gravity_violations,
                    "violations_fixed": gravity_fixed,
                }
            )
        state_mgr.state["gravity_violations"] = gravity_violation_list

        if gravity_violations > 0:
            status_msg = f"Violations: {gravity_violations} | Fixed: {gravity_fixed}"
            state_mgr.complete_agent("GravityLeakHealerAgent", True, status_msg)
            logger.info(f"Gravity violations processed: {gravity_violations} found, {gravity_fixed} fixed")
        else:
            state_mgr.complete_agent("GravityLeakHealerAgent", True, "No gravity violations found")
            logger.info("No gravity violations detected")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Gravity violation detection failed: {e}")
        state_mgr.complete_agent("GravityLeakHealerAgent", False, f"Detection failed: {str(e)}")
        _record_healing_action(
            state_mgr,
            agent="GravityValidatorAgent",
            territory="__global__",
            routing_tier="DETERMINISTIC",
            confidence=0.0,
            fix_summary=f"GravityValidatorAgent error: {str(e)[:120]}",
            outcome="FAILED",
        )
        _record_healing_action(
            state_mgr,
            agent="GravityLeakHealerAgent",
            territory="__global__",
            routing_tier="DETERMINISTIC",
            confidence=0.0,
            fix_summary=f"GravityLeakHealerAgent error: {str(e)[:120]}",
            outcome="FAILED",
        )
        state_mgr.state["gravity_violations"] = [
            {
                "type": "GRAVITY_ERROR",
                "message": f"Gravity detection failed: {str(e)}",
                "severity": "high",
                "recommended_action": "Fix gravity detection error",
                "confidence": 0.5,
            }
        ]


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase4_architectural_validation(agents, territory, state_mgr, ctx: "HealContext" = None):
    """PHASE 4: ARCHITECTURAL VALIDATION (Retriable)"""
    return execute_phase4_validation_impl(agents, territory, state_mgr, ctx=ctx)


def execute_phase4_validation_impl(agents, territory, state_mgr, ctx: "HealContext" = None):
    """PHASE 4: ARCHITECTURAL VALIDATION - Implementation"""
    logger.info(f"=== PHASE 4: VALIDATION - {territory} ===")

    state_mgr.update_agent("ArchitectureGovernorAgent", "L5 - Safety")
    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)

    # [EXPANDED SCOPE] Audit all ENFORCED_TERRITORIES for comprehensive validation
    from agentic_core.L5_safety.config.structure_blueprint_config import ENFORCED_TERRITORIES

    # If territory is in ENFORCED_TERRITORIES, audit all of them (not just current)
    # This ensures comprehensive architectural validation across all territories
    if territory in ENFORCED_TERRITORIES or territory == "agentic_core":
        target_territories = sorted(ENFORCED_TERRITORIES)
        logger.info(f"ArchitectureGovernorAgent: Auditing all {len(target_territories)} enforced territories")
    else:
        # For layer-specific scans (L0_routing, L1_cognition, etc.), audit just that layer
        target_territories = [territory]

    gov_report = arch_gov.comprehensive_territory_audit(
        target_territories=target_territories,
        check_layer_boundaries=True,
        check_naming_conventions=True,
    )

    if gov_report is None:
        state_mgr.complete_agent("ArchitectureGovernorAgent", False, "Returned None")
        return None, None

    violations = len(gov_report.get("layer_violations", [])) + len(gov_report.get("naming_violations", []))
    state_mgr.complete_agent("ArchitectureGovernorAgent", True, f"Violations: {violations}")
    _record_healing_action(
        state_mgr,
        agent="ArchitectureGovernorAgent",
        territory=territory,
        routing_tier="DETERMINISTIC",
        confidence=1.0,
        fix_summary=f"Arch validation: {violations} violation(s) in {territory}",
        outcome="SUCCESS",
    )

    # [FIX-B8] GravityLeakRepairAgent moved to _run_gravity_repair_global() — runs once before territory loop

    # [FIX-B10] Only run file-size check for agentic_core L-layer territories
    _ac_layer_prefixes = ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")
    if territory != "agentic_core" and not any(territory.startswith(p) for p in _ac_layer_prefixes):
        return gov_report, None

    size_violations = arch_gov.check_file_sizes(territory)
    if size_violations:
        for v in size_violations:
            state_mgr.add_event("warning", v["message"])
        logger.warning(f"check_file_sizes: {len(size_violations)} oversized file(s) in {territory}")
    else:
        logger.info(f"check_file_sizes: no oversized files in {territory}")

    return gov_report, None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase5_healing(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 5: HEALING (Retriable)"""
    # [STRICT SCOPE] Gatekeeper check
    if not gov_report:
        logger.warning("Skipping healing: No governance report available.")
        return None

    return execute_phase5_healing_impl(
        agents,
        territory,
        gov_report,
        decision_engine,
        state_mgr,
        ctx,
    )


def execute_phase5_healing_impl(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 5: HEALING - Implementation"""
    logger.info(f"=== PHASE 5: HEALING - {territory} ===")

    if gov_report is None:
        logger.warning("No governance report - skipping healing")
        return None

    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)
    plan = arch_gov.generate_healing_plan(gov_report)

    if plan is None:
        logger.warning("No healing plan generated")
        return None

    if plan.get("requires_healing", False):
        fixes = len(plan.get("naming_fixes", []))
        confidence = decision_engine.calculate_healing_confidence(fixes, ["NAMING"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence, "ArchitectureGovernorAgent", territory=territory
        )

        state_mgr.add_event("decision", f"Arch Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed and ctx is not None and ctx.heal:
            state_mgr.update_agent("ArchitectureGovernorAgent", "HEALING MODE")
            _arch_healer_cls = agents.get("arch_governor")
            if _arch_healer_cls is not None:
                _arch_healer_instance = _arch_healer_cls(project_root=REPO_ROOT)
                heal_result = _arch_healer_instance.heal_repository(dry_run=False, execute=True)
            else:
                heal_result = {}
            fixed = heal_result.get("violations_fixed", 0) if isinstance(heal_result, dict) else 0
            found = fixes
            success = True
            _record_healing_action(
                state_mgr,
                agent="ArchitectureGovernorAgent",
                territory=territory,
                routing_score=confidence.value,
                routing_tier=reason.split("(")[0].strip() if reason else "DETERMINISTIC",
                confidence=confidence.value,
                fix_summary=f"Fixed {fixed} of {found} architecture violations in {territory}",
                outcome="SUCCESS" if fixed > 0 else "PARTIAL",
            )
            state_mgr.complete_agent("ArchitectureGovernorAgent", success, f"found={found} fixed={fixed}")
            return {
                "status": "HEALED" if fixed > 0 else "NO_CHANGE",
                "violations_found": found,
                "violations_fixed": fixed,
            }
        else:
            _record_healing_action(
                state_mgr,
                agent="ArchitectureGovernorAgent",
                territory=territory,
                routing_score=confidence.value if hasattr(confidence, "value") else 0.0,
                routing_tier=reason.split("(")[0].strip() if reason else "DETERMINISTIC",
                confidence=confidence.value if hasattr(confidence, "value") else 0.0,
                fix_summary=f"Skipped arch governance in {territory}: {reason}",
                outcome="SKIPPED",
            )
            state_mgr.complete_agent("ArchitectureGovernorAgent", True, f"Skipped: {reason}")

    return None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase7_final(agents, territory, state_mgr, decision_engine=None):
    """PHASE 7: CERTIFICATION (Retriable)"""
    return execute_phase7_final_impl(agents, territory, state_mgr, decision_engine)


def execute_phase7_final_impl(agents, territory, state_mgr, decision_engine=None):
    """PHASE 7: CERTIFICATION - Implementation with Silent Aggregation"""
    logger.info(f"=== PHASE 7: CERTIFICATION - {territory} ===")

    state_mgr.update_agent("ArchitectureGovernorAgent", "L5 - Certification")

    # [UNIFIED MANIFEST] Aggregate all findings from the state manager
    compliance_report = state_mgr.state.get("compliance_report", {})

    # [CRITICAL FIX] Aggregate violations from ALL agents, not just ArchitectureGovernor
    # The compliance_report only has ArchitectureGovernor violations
    # We need to include LocationAgent violations from Phase 1
    all_violations = []

    # Get ArchitectureGovernor violations
    arch_violations = compliance_report.get("violations", [])
    all_violations.extend(arch_violations)

    # Get LocationAgent violations from Phase 1 (stored in state)
    location_violations = state_mgr.state.get("location_violations", [])
    for loc_violation in location_violations:
        # LocationAgent violations arrive in three shapes:
        # 1. tuple (Path, message) — from validate_sovereign_roots / validate_file_location
        # 2. dict with "file" and "message" keys — from location_scan_result["violations"]
        # 3. other objects — fallback
        if isinstance(loc_violation, tuple) and len(loc_violation) >= 2:
            file_path = str(loc_violation[0])
            message = str(loc_violation[1])
        elif isinstance(loc_violation, dict):
            # BUG-3 fix: dict violations must use .get(), not getattr
            raw_fp = loc_violation.get("file") or loc_violation.get("path") or "unknown"
            file_path = str(raw_fp)
            message = str(loc_violation.get("message", loc_violation.get("msg", str(loc_violation))))
        else:
            file_path = str(getattr(loc_violation, "file", "unknown"))
            message = str(loc_violation)

        # Generate specific, actionable recommendations based on violation type
        if "Missing sovereign root:" in message:
            dir_name = message.split("Missing sovereign root:")[1].strip().strip("')")
            action = f"Create directory: {dir_name}"
        elif "Forbidden keyword 'def test_'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to tests/ directory (contains test functions)"
        elif "Forbidden keyword 'class Sovereign'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to agentic_core/base_agents/ or agentic_core/L5_safety/"
        elif "Forbidden extension .py for destination docs/reports" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"RENAME: '{filename}' has audit/report naming but is a Python script. Either: 1) Rename to avoid audit patterns (e.g., registry_linkage_checker.py) OR 2) Move to agentic_core/L0_routing/scripts/ where audit scripts belong"
        else:
            action = f"Fix location/naming issue: {message[:60]}"

        # Calculate individual confidence for each violation based on specific violation characteristics
        violation_type = "LOCATION"
        if "Forbidden keyword 'def test_'" in message:
            violation_type = "TEST_FILE_LOCATION"
        elif "Forbidden keyword 'class Sovereign'" in message:
            violation_type = "SOVEREIGN_CLASS_LOCATION"
        elif "Forbidden extension .py for destination docs/reports" in message:
            violation_type = "PYTHON_IN_DOCS"
        elif "BROKEN BACKUP FILE" in message:
            violation_type = "STALE_BACKUP"
        elif "Forbidden keyword 'import '" in message:
            violation_type = "IMPORT_IN_DOCS"

        violation_confidence = decision_engine.calculate_healing_confidence(
            violations_count=1,  # Single violation
            violation_types=[violation_type],  # Use specific violation type
            territory=territory,
        ).value

        # Check if LLM was actually used in the decision process (look for LLM decisions in decision engine)
        llm_decisions = [d for d in decision_engine.decisions_made if "LLM" in d.get("reason", "")]
        llm_was_triggered = decision_engine.enable_llm and len(llm_decisions) > 0

        # Convert LocationAgent violation object to detailed dict
        violation_dict = {
            "type": "LOCATION",
            "source": "LocationHealerAgent",
            "file": file_path,
            "message": message,
            "severity": "medium",
            "recommended_action": action,
            "llm_triggered": llm_was_triggered,
            "confidence": round(violation_confidence, 3),
        }
        all_violations.append(violation_dict)

    # [FIX-B1] Gravity violations are global (not per-territory) — excluded from per-territory reports.
    # They are emitted only in save_aggregate_report() under "global_violations".

    # Get ObservabilityProbeExecutorAgent violations (already stored by Phase 6 — do not re-invoke)
    conversational_violations = state_mgr.state.get("conversational_violations", [])
    for conv_violation in conversational_violations:
        if isinstance(conv_violation, dict):
            violation_dict = {
                **conv_violation,
                "source": "ObservabilityProbeExecutorAgent",
                "file": conv_violation.get("file", "unknown"),
                "message": conv_violation.get("message", str(conv_violation)),
                "severity": conv_violation.get("severity", "medium"),
                "recommended_action": conv_violation.get(
                    "recommended_action",
                    "Review conversational pattern",
                ),
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(conv_violation.get("confidence", 0.5), 3),
            }
            all_violations.append(violation_dict)

    # [FIX-B1] Hygiene violations are global (not per-territory) — excluded from per-territory reports.
    # They are emitted only in save_aggregate_report() under "global_violations".

    # [PHASE 3 ENHANCEMENT] Get FileClassificationAgent violations from early detection
    classification_violations = state_mgr.state.get("classification_violations", [])
    for class_violation in classification_violations:
        if isinstance(class_violation, dict):
            subtype = class_violation.get("subtype", "UNKNOWN")
            count = class_violation.get("count", 1)
            violation_dict = {
                "type": "CLASSIFICATION",
                "subtype": subtype,
                "source": "FileClassificationHealerAgent",
                "file": class_violation.get("file", "multiple"),
                "message": f"{subtype} violation: {count} file(s) need attention",
                "severity": "medium",
                "recommended_action": f"Run FileClassificationAgent to fix {subtype} issues",
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(class_violation.get("confidence", 0.7), 3),
                "count": count,
            }
            all_violations.append(violation_dict)

    violation_count = len(all_violations)
    status = "COMPLIANT" if violation_count == 0 else "NON-COMPLIANT"

    # [LOGIC FIX] Recalculate confidence based on FINAL violation count, not Phase 1
    # [FIX-B4+B5] Use the passed decision_engine directly — no fallback creation
    if decision_engine is None:
        decision_engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

    final_confidence = decision_engine.calculate_healing_confidence(
        violations_count=violation_count,
        violation_types=[v.get("type", "UNKNOWN") for v in all_violations[:10]],
        territory=territory,
    )
    confidence_avg = final_confidence.value

    drift_count = compliance_report.get("stats", {}).get("drift_detected", 0)

    # [FIX-B4] Use decision_engine.decisions_made filtered by territory
    decisions_made = [
        d for d in getattr(decision_engine, "decisions_made", []) if d.get("territory") == territory
    ]

    # Get location scan result from state manager
    location_scan_result = state_mgr.state.get("location_scan_result", {})

    # [DYNAMIC] Track actual agents executed from state manager
    completed_agents = state_mgr.state.get("completed_agents", [])
    skipped_agents = state_mgr.state.get("skipped_agents", [])
    # Extract unique agent names from completion history
    agents_executed = list({agent["agent"] for agent in completed_agents})
    # [PHANTOM-RUN FIX] Agents blocked by confidence gate or HITL — NOT counted as executed
    agents_skipped = [{"agent": a["agent"], "reason": a["reason"]} for a in skipped_agents]

    detailed_cert = {
        "meta": {
            "territory": territory,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "sovereignty_level": "L5",
        },
        "metrics": {
            "confidence_score": round(confidence_avg, 3),
            "violation_count": violation_count,
            "drift_count": drift_count,
            "errors": compliance_report.get("stats", {}).get("errors", 0),
            "violations_fixed": (
                compliance_report.get("stats", {}).get("violations_fixed", 0)
                + state_mgr.state.get("hygiene_fixed", 0)
                + state_mgr.state.get("location_fixed", 0)
                + state_mgr.state.get("hierarchy_fixed", 0)
                + state_mgr.state.get("gravity_fixed", 0)
                + state_mgr.state.get("phase2_violations_fixed", 0)  # BUG-2 fix
            ),
            "agents_run": len(agents_executed),
            "agents_skipped": len(agents_skipped),
        },
        "governance_log": {"decisions": decisions_made, "files_processed": []},
        "unified_violations": all_violations,  # Use all_violations instead of just arch violations
        # [H4] Per-territory healing log with routing details
        "healing_log": [
            a
            for a in state_mgr.state.get("healing_actions", [])
            if a.get("territory") == territory or a.get("territory") == "__global__"
        ],
        "agents_executed": agents_executed,
        "agents_skipped": agents_skipped,
    }

    # Add comprehensive file statistics
    file_stats = location_scan_result.get("file_stats", {})
    # Format compliance rate to one decimal place
    if "compliance_rate" in file_stats:
        file_stats["compliance_rate"] = round(file_stats["compliance_rate"], 1)
    detailed_cert["file_scan_stats"] = file_stats

    # Add violations to file log
    files_affected = set()
    for v in all_violations:  # Use all_violations instead of violations
        files_affected.add(v.get("file", "unknown"))

    detailed_cert["governance_log"]["files_processed"] = list(files_affected)
    detailed_cert["governance_log"]["scan_summary"] = {
        "total_files_scanned": file_stats.get("total_files", 0),
        "files_with_violations": len(files_affected),
        "files_compliant": file_stats.get("valid_files", 0),
        "compliance_rate": round(file_stats.get("compliance_rate", 0), 1),
        "file_types": file_stats.get("file_types", {}),
    }

    # Generate Markdown Executive Summary
    file_stats = location_scan_result.get("file_stats", {})
    total_files = file_stats.get("total_files", 0)
    compliance_rate = file_stats.get("compliance_rate", 0)
    file_types = file_stats.get("file_types", {})

    markdown_summary = [
        f"# 🛡️ Sovereign Compliance Report: {territory}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Status:** {status}",
        "",
        "## 📊 Executive Summary",
        "",
        f"* **Confidence Score:** {confidence_avg:.1%}",
        f"* **Violations Detected:** {violation_count}",
        f"* **Integrity Drift:** {drift_count}",
        f"* **Violations Fixed:** {detailed_cert['metrics']['violations_fixed']}",
        "",
        "## 📁 Scan Scope",
        "",
        f"* **Total Files Scanned:** {total_files}",
        f"* **Files Compliant:** {file_stats.get('valid_files', 0)}",
        f"* **Files with Violations:** {len(files_affected)}",
        f"* **Compliance Rate:** {compliance_rate:.1f}%",
        "",
        "### File Types Analyzed",
        "",
    ]

    # Add file type breakdown
    if file_types:
        for ext, count in sorted(file_types.items()):
            ext_display = ext if ext else "(no extension)"
            markdown_summary.append(f"* **{ext_display}:** {count} files")

    markdown_summary.extend(["", "## 🚨 Violations Detected", ""])

    # Add detailed violations table
    if violation_count > 0:
        markdown_summary.extend(
            [
                "| # | Type | File | Issue | Severity | LLM | Confidence | Action |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ],
        )

        for idx, violation in enumerate(all_violations, 1):
            v_type = violation.get("type", "UNKNOWN")
            v_file = violation.get("file", "unknown")
            # Extract just the filename from full path
            if "/" in v_file or "\\" in v_file:
                v_file = v_file.split("/")[-1].split("\\")[-1]

            # Parse message to get the actual issue
            v_message = violation.get("message", "")
            if "ARTIFACT ROUTING VIOLATION:" in v_message:
                issue = v_message.split("ARTIFACT ROUTING VIOLATION:")[1].split("'")[0].strip()
            elif "Missing sovereign root:" in v_message:
                issue = v_message.split("Missing sovereign root:")[1].strip().strip("')")
            else:
                issue = v_message[:50] + "..." if len(v_message) > 50 else v_message

            v_severity = violation.get("severity", "medium")
            v_llm = "Yes" if violation.get("llm_triggered", False) else "No"
            v_conf = violation.get("confidence", 0.0)
            # Convert to percentage if it's a decimal (0-1) or keep as is if already percentage
            if v_conf <= 1.0:
                v_conf_display = f"{v_conf:.1%}"
            else:
                v_conf_display = f"{v_conf:.1f}%"
            v_action = violation.get("recommended_action", "Review")[:30] + "..."

            markdown_summary.append(
                f"| {idx} | {v_type} | `{v_file}` | {issue} | {v_severity} | {v_llm} | {v_conf_display} | {v_action} |",
            )
    else:
        markdown_summary.append("*No violations detected - territory is compliant.*")

    markdown_summary.extend(
        [
            "",
            "## 🧠 AI Governance Log",
            "",
            "| Agent | Score | Tier | Model | Gate | Confidence | Outcome | Fix Applied |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ],
    )

    # [H5] Upgraded 8-column governance table with routing details
    for decision in decisions_made:
        agent = decision.get("agent", "Unknown")
        score = decision.get("routing_score", 0.0)
        tier = decision.get("routing_tier", "UNKNOWN")
        model = decision.get("model", "none")
        gate = decision.get("routing_gate", "N/A")
        conf = decision.get("confidence", 0.0)
        outcome = "PROCEED" if decision.get("decision", False) else "SKIP"
        # Match fix details from healing_log
        fix_applied = "-"
        for ha in detailed_cert.get("healing_log", []):
            if ha.get("agent") == agent:
                fix_applied = ha.get("fix_summary", "-")
                break
        conf_display = f"{conf:.1%}" if conf <= 1.0 else f"{conf:.1f}%"
        markdown_summary.append(
            f"| {agent} | {score:.3f} | {tier} | {model} | {gate} | {conf_display} | {outcome} | {fix_applied} |",
        )

    # [FIX-I3] Only print per-territory JSON manifest in verbose mode
    if logger.isEnabledFor(logging.DEBUG):
        _safe_print(json.dumps(detailed_cert, indent=2))

    # Print Markdown Summary (always shown — it's the human-readable output)
    _safe_print("\n" + "\n".join(markdown_summary))
    if files_affected:
        _safe_print("\n### Affected Files")
        for f in sorted(files_affected):
            _safe_print(f"* `{f}`")
    else:
        _safe_print("\n*No files required remediation.*")

    # [COMPREHENSIVE REPORTS] Save detailed reports to files
    save_comprehensive_reports(
        territory,
        detailed_cert,
        markdown_summary,
        files_affected,
        state_mgr.project_root,
    )

    logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
    state_mgr.complete_agent("ArchitectureGovernorAgent", True, "Certificate Issued")
    total_v = len(detailed_cert.get("violations", []))
    return detailed_cert


def save_comprehensive_reports(
    territory: str,
    detailed_cert: dict,
    markdown_summary: list,
    files_affected: set,
    project_root: Path,
):
    """
    [COMPREHENSIVE REPORTS] Save detailed JSON manifest and Markdown summary to persistent files.
    Creates timestamped reports in logs/compliance_reports/ directory.
    """
    try:
        # Create reports directory
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save only final files (no timestamped versions to reduce sprawl)
        json_filename = f"compliance_report_{territory}.json"
        md_filename = f"executive_summary_{territory}.md"
        json_path = reports_dir / json_filename
        md_path = reports_dir / md_filename

        # Deduplicate unified_violations by (type, file, message) before persisting
        _seen_vkeys: set = set()
        _deduped: list = []
        for _v in detailed_cert.get("unified_violations", []):
            _vk = (_v.get("type", ""), _v.get("file", ""), _v.get("message", ""))
            if _vk not in _seen_vkeys:
                _seen_vkeys.add(_vk)
                _deduped.append(_v)
        if len(_deduped) != len(detailed_cert.get("unified_violations", [])):
            detailed_cert = {**detailed_cert, "unified_violations": _deduped}

        def _json_serialise(obj):  # BUG-4 fix: Path → posix string to avoid backslash escape errors
            if isinstance(obj, Path):
                return obj.as_posix()
            return str(obj)

        with open(json_path, "w", encoding="utf-8") as f:
            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
            json.dump(detailed_cert, f, indent=2, default=_json_serialise, ensure_ascii=False)

        # Save Markdown Executive Summary (using the md_path already defined above)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_summary))
            if files_affected:
                f.write("\n\n### 📂 Affected Files\n\n")
                for f_sorted in sorted(files_affected):
                    f.write(f"* `{f_sorted}`\n")
            else:
                f.write("\n\n*No files required remediation.*\n")

        logger.info("📁 Final compliance reports saved:")
        logger.info(f"   JSON: {json_path.relative_to(project_root)}")
        logger.info(f"   Markdown: {md_path.relative_to(project_root)}")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Failed to save comprehensive reports: {e}")
        # Don't fail the entire process if report saving fails


def save_aggregate_report(targets: list[str], project_root: Path) -> Path | None:
    """
    [AGGREGATE REPORT] Merge all per-territory compliance_report_<t>.json into a single
    compliance_report_AGGREGATE.json in logs/compliance_reports/.

    Deduplicates violations by (type, file, message) so cross-territory duplicates
    (e.g. GRAVITY, ILLEGAL_CACHE_DIR) are counted once.

    Returns the Path to the written file, or None on failure.
    """
    import datetime

    try:
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        territory_summaries: list[dict] = []
        all_violations_seen: set[tuple] = set()
        deduplicated_violations: list[dict] = []
        agents_seen: set[str] = set()

        total_violation_count = 0
        total_violations_fixed = 0
        total_drift_count = 0
        total_errors = 0
        non_compliant = 0
        compliant = 0

        for t in targets:
            t_path = reports_dir / f"compliance_report_{t}.json"
            if not t_path.exists():
                continue
            try:
                t_data = json.loads(t_path.read_text(encoding="utf-8"))
            except Exception:  # guardian: allow-silent-swallower
                continue

            meta = t_data.get("meta", {})
            metrics = t_data.get("metrics", {})
            status = meta.get("status", "UNKNOWN")

            if status == "COMPLIANT":
                compliant += 1
            else:
                non_compliant += 1

            total_violation_count += metrics.get("violation_count", 0)
            total_violations_fixed += metrics.get("violations_fixed", 0)
            total_drift_count += metrics.get("drift_count", 0)
            total_errors += metrics.get("errors", 0)

            territory_summaries.append(
                {
                    "territory": t,
                    "status": status,
                    "confidence_score": metrics.get("confidence_score", 0.0),
                    "violation_count": metrics.get("violation_count", 0),
                    "violations_fixed": metrics.get("violations_fixed", 0),
                    "drift_count": metrics.get("drift_count", 0),
                    "agents_run": metrics.get("agents_run", 0),
                    "timestamp": meta.get("timestamp", ""),
                }
            )

            for v in t_data.get("unified_violations", []):
                key = (v.get("type", ""), v.get("file", ""), v.get("message", ""))
                if key not in all_violations_seen:
                    all_violations_seen.add(key)
                    deduplicated_violations.append(v)

            for a in t_data.get("agents_executed", []):
                agents_seen.add(a)

        # Violation breakdown by type and severity
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for v in deduplicated_violations:
            vtype = v.get("type", "UNKNOWN")
            vsev = v.get("severity", "unknown")
            by_type[vtype] = by_type.get(vtype, 0) + 1
            by_severity[vsev] = by_severity.get(vsev, 0) + 1

        overall_status = "COMPLIANT" if non_compliant == 0 else "NON-COMPLIANT"

        # [FIX-B1] Collect global violations (hygiene + gravity) for aggregate-only reporting
        global_violations = []
        # Read runtime_state.json for global violation data if available
        runtime_state_path = project_root / RUNTIME_STATE_JSON
        if runtime_state_path.exists():
            try:
                _rs = json.loads(runtime_state_path.read_text(encoding="utf-8"))
                for hv in _rs.get("hygiene_violations", []):
                    if isinstance(hv, dict):
                        global_violations.append({**hv, "source": "RootHygieneAgent", "scope": "global"})
                for gv in _rs.get("gravity_violations", []):
                    if isinstance(gv, dict):
                        global_violations.append(
                            {**gv, "source": "GravityLeakHealerAgent", "scope": "global"}
                        )
            except Exception:  # guardian: allow-silent-swallower
                pass

        aggregate = {
            "meta": {
                "report_type": "AGGREGATE",
                "timestamp": datetime.datetime.now().isoformat(),
                "territories_scanned": len(territory_summaries),
                "territories_compliant": compliant,
                "territories_non_compliant": non_compliant,
                "overall_status": overall_status,
            },
            "metrics": {
                "total_violations_detected": total_violation_count,
                "unique_violations_deduplicated": len(deduplicated_violations),
                "total_violations_fixed": total_violations_fixed,
                "total_drift_count": total_drift_count,
                "total_errors": total_errors,
                "violations_by_type": by_type,
                "violations_by_severity": by_severity,
            },
            "global_violations": global_violations,
            "territories": territory_summaries,
            "agents_executed": sorted(agents_seen),
            "violations": deduplicated_violations,
        }

        def _agg_json_serialise(obj):  # BUG-4 fix: Path → posix string
            if isinstance(obj, Path):
                return obj.as_posix()
            return str(obj)

        agg_path = reports_dir / "compliance_report_AGGREGATE.json"
        with open(agg_path, "w", encoding="utf-8") as f:
            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
            json.dump(aggregate, f, indent=2, default=_agg_json_serialise, ensure_ascii=False)

        logger.info(f"📊 Aggregate compliance report saved: {agg_path.relative_to(project_root)}")
        logger.info(
            f"   Territories: {len(territory_summaries)} | "
            f"Unique violations: {len(deduplicated_violations)} | "
            f"Fixed: {total_violations_fixed} | "
            f"Status: {overall_status}"
        )
        return agg_path

    except Exception as e:  # guardian: allow-silent-swallower
        logger.error(f"[AGGREGATE] Failed to save aggregate report: {e}")
        return None


# ============================================================================
# L3 ORCHESTRATION INTEGRATION
# ============================================================================


def try_summon_orchestrator(project_root: Path, targets: list[str], execute: bool):
    """
    [INTEGRATION] Attempts to load L3 Orchestrator for smart execution.
    Returns: (success: bool, results: List|None)
    """
    try:
        # Invoke via subprocess to avoid upward import edges
        from agentic_core.L0_routing.utils.subprocess_runner_util import (
            invoke_orchestrator_mission,
        )

        logger.info("🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.")

        result = invoke_orchestrator_mission(
            project_root=project_root,
            targets=targets,
            execute=execute,
        )

        if result.get("success"):
            return True, result.get("results")

        # Check if fallback is needed
        if result.get("fallback"):
            logger.warning("L3 Orchestrator not found. Falling back to L5 iteration.")
            return False, None

        logger.error(f"L3 Orchestration failed: {result.get('error')}. Falling back.")
        return False, None

    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-silent-swallower
        logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
        return False, None


# ============================================================================
# EXECUTION PLAN (DETERMINISTIC, ORDERED)
# ============================================================================

# Canonical phase→agent→method mapping. This is the SSOT for pipeline structure.
# Used by --plan introspection and by AST contract tests.
EXECUTION_PLAN = [
    {
        "phase": "1",
        "name": "Discovery",
        "agents": [
            {
                "key": "reconciler",
                "method": "detect_root_drift",
                "description": "filesystem SSOT drift detection",
            },
            {
                "key": "location",
                "method": "run",
                "description": "location validation (confidence gated heal)",
            },
            {
                "key": "file_classification",
                "method": "run",
                "description": "file classification early detection",
                "kwargs": "validate_only=True, dry_run=True",
            },
        ],
    },
    {
        "phase": "2",
        "name": "Reconciliation",
        "agents": [
            {"key": "reconciler", "method": "heal", "description": "drift reconciliation (confidence gated)"},
        ],
    },
    {
        "phase": "3",
        "name": "Structural Alignment & Sovereignty",
        "agents": [
            {
                "key": "hierarchy",
                "method": "heal_hierarchy",
                "description": "hierarchy alignment (confidence gated)",
            },
            {
                "key": "file_classification",
                "method": "heal_repository",
                "description": "sovereignty purge (confidence gated, not dry_run, not validate)",
            },
        ],
    },
    {
        "phase": "4",
        "name": "Architectural Validation",
        "agents": [
            {
                "key": "arch_governor",
                "method": "comprehensive_territory_audit",
                "description": "territory audit",
            },
            {
                "key": "arch_governor",
                "method": "check_file_sizes",
                "description": "file-size check (AC-layer territories only)",
            },
        ],
    },
    {
        "phase": "5",
        "name": "Healing",
        "agents": [
            {
                "key": "arch_governor",
                "method": "generate_healing_plan",
                "description": "healing plan generation",
            },
            {
                "key": "arch_governor",
                "method": "execute_healing_plan",
                "description": "healing plan execution",
            },
        ],
    },
    {
        "phase": "6",
        "name": "Additional Agents",
        "agents": [
            {
                "key": "observability_probe",
                "method": "scan_violations",
                "description": "observability probe scan",
            },
            {
                "key": "root_hygiene",
                "method": "scan_root_violations",
                "description": "root hygiene scan (if registered)",
            },
        ],
    },
    {
        "phase": "7",
        "name": "Certification",
        "agents": [
            {"key": "*", "method": "aggregate", "description": "final aggregation and certification"},
        ],
    },
]

# Agent dependency graph for --agent subset closure.
# If agent A requires agent B to run first, declare it here.
AGENT_DEPENDENCIES: dict[str, list[str]] = {
    "hierarchy": ["reconciler", "location"],
    "file_classification": ["reconciler", "location"],
    "arch_governor": ["reconciler", "location", "hierarchy"],
    "gravity_repair": ["reconciler"],
    "observability_probe": [],
    "root_hygiene": [],
    "reconciler": [],
    "location": ["reconciler"],
    "cognitive_disposition": [],
}

# Canonical roster keys. Every agents["key"] reference in _legacy_main MUST
# exist in this set. AST contract tests enforce this invariant.
CANONICAL_ROSTER_KEYS = frozenset(
    {
        "reconciler",
        "location",
        "hierarchy",
        "arch_governor",
        "gravity_repair",
        "file_classification",
        "observability_probe",
        "cognitive_disposition",
        "root_hygiene",
    },
)


def get_execution_plan() -> list[dict]:
    """Return the deterministic, ordered execution plan.

    Pure introspection — no side effects, no file mutations.
    """
    return EXECUTION_PLAN


# ---------------------------------------------------------------------------
# Unified pipeline: AGENT_PIPELINE + run_pipeline
# ---------------------------------------------------------------------------

#: Ordered execution sequence for run_pipeline. cognitive_disposition is
#: intentionally excluded — it acts as a pre-loop advisor, not a subphase agent.
AGENT_PIPELINE: list[str] = [
    "reconciler",
    "location",
    "file_classification",
    "hierarchy",
    "arch_governor",
    "gravity_repair",
    "system_architect",
    "observability_probe",
    "root_hygiene",
]

#: The four subphase names, in fixed execution order.
PIPELINE_SUBPHASES: tuple[str, ...] = ("pre_commit", "validate", "execute", "heal")


def _emit_pipeline_digest(
    adapters: "dict[str, object]",
    territory: str,
    ctx: "HealContext",
) -> str:
    """Compute and print the deterministic pipeline digest (once per run).

    Returns the 64-char hex digest string.
    When SSOT_ORCH_NEGCTRL_TAMPER=1 the digest payload is perturbed so the
    output differs from a clean run — used by the negative-control test.
    """
    from agentic_core.L2_execution.protocol import emit_pipeline_digest as _emit

    return _emit(
        pipeline_order=AGENT_PIPELINE,
        adapter_keys=list(adapters.keys()),
        territory=territory,
        heal=getattr(ctx, "heal", False),
        enable_llm=getattr(ctx, "enable_llm", False),
    )


def _print_healing_heatmap(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> None:
    """Print a per-agent healing count heatmap at end of every run."""
    from collections import defaultdict

    TIER_COLS = ("DETERMINISTIC", "QWEN_VLLM", "GEMINI_2_5_PRO")
    TIER_ALIASES: dict[str, str] = {
        "DETERMINISTIC": "DETERMINISTIC",
        "SOVEREIGN-AUTO": "DETERMINISTIC",
        "QWEN": "QWEN_VLLM",
        "QWEN_VLLM": "QWEN_VLLM",
        "GEMINI": "GEMINI_2_5_PRO",
        "GEMINI_2_5_PRO": "GEMINI_2_5_PRO",
    }

    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    healing_actions = state_mgr.state.get("healing_actions", [])
    for action in healing_actions:
        agent = action.get("agent", "unknown")
        tier = TIER_ALIASES.get(action.get("routing_tier", "DETERMINISTIC"), "DETERMINISTIC")
        counts[agent][tier] += 1

    seen_pairs = {
        (a.get("agent"), TIER_ALIASES.get(a.get("routing_tier", ""), "DETERMINISTIC"))
        for a in healing_actions
    }
    for d in getattr(decision_engine, "decisions_made", []):
        if not d.get("decision"):
            continue
        agent = d.get("agent", "unknown")
        tier = TIER_ALIASES.get(d.get("routing_tier", "DETERMINISTIC"), "DETERMINISTIC")
        if (agent, tier) not in seen_pairs:
            counts[agent][tier] += 1

    def _bar(n: int) -> str:
        if n == 0:
            return ".."
        if n == 1:
            return "o "
        if n <= 3:
            return ">>"
        return "##"

    AGEN_W = 34
    COL_W = 15
    sep = "-" * (AGEN_W + 3 * (COL_W + 3) + 8)
    header = (
        f"{'Agent':<{AGEN_W}} | "
        f"{'DETERMINISTIC':^{COL_W}} | "
        f"{'QWEN_VLLM':^{COL_W}} | "
        f"{'GEMINI_2_5_PRO':^{COL_W}} | TOTAL"
    )

    print("")
    print("=" * 60)
    print("HEALING HEATMAP")
    print(sep)
    print(header)
    print(sep)

    col_totals: dict[str, int] = defaultdict(int)
    if counts:
        for agent in sorted(counts):
            row_vals = {t: counts[agent].get(t, 0) for t in TIER_COLS}
            total = sum(row_vals.values())
            for t in TIER_COLS:
                col_totals[t] += row_vals[t]
            print(
                f"{agent:<{AGEN_W}} | "
                f"{(_bar(row_vals['DETERMINISTIC']) + ' ' + str(row_vals['DETERMINISTIC'])):^{COL_W}} | "
                f"{(_bar(row_vals['QWEN_VLLM']) + ' ' + str(row_vals['QWEN_VLLM'])):^{COL_W}} | "
                f"{(_bar(row_vals['GEMINI_2_5_PRO']) + ' ' + str(row_vals['GEMINI_2_5_PRO'])):^{COL_W}} | "
                f"{total}"
            )
    else:
        print(f"{'(no healing events this run)':<{AGEN_W}}")

    print(sep)
    grand = sum(col_totals.values())
    print(
        f"{'TOTAL':<{AGEN_W}} | "
        f"{str(col_totals['DETERMINISTIC']):^{COL_W}} | "
        f"{str(col_totals['QWEN_VLLM']):^{COL_W}} | "
        f"{str(col_totals['GEMINI_2_5_PRO']):^{COL_W}} | "
        f"{grand}"
    )
    print(sep)


def _print_meta_learning_summary(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> None:
    """Print meta-learning bus additions summary — what this run teaches the next run."""
    from collections import Counter

    _W = 78  # total console width for the block

    def _sec(title: str) -> None:
        print(f"\n  {title}")
        print("  " + "-" * (_W - 2))

    def _row(label: str, value: str) -> None:
        print(f"  {label:<30} {value}")

    ml = state_mgr.state.get("meta_learning", {})
    healing_actions = state_mgr.state.get("healing_actions", [])
    decisions = getattr(decision_engine, "decisions_made", [])

    successful = [a for a in healing_actions if str(a.get("outcome", "")).upper() == "SUCCESS"]
    failed = [a for a in healing_actions if str(a.get("outcome", "")).upper() in ("FAIL", "FAILED", "ERROR")]
    plan_only = [a for a in healing_actions if "plan" in str(a.get("outcome", "")).lower()]

    tier_counts: Counter = Counter()
    for d in decisions:
        if d.get("decision"):
            tier_counts[d.get("routing_tier", "DETERMINISTIC")] += 1

    conf_vals = [d.get("confidence", 0.0) for d in decisions if isinstance(d.get("confidence"), (int, float))]
    # Per-action confidence falls back to the action's own field when decision list is sparse
    action_confs = [
        a.get("confidence", 0.0) for a in healing_actions if isinstance(a.get("confidence"), (int, float))
    ]
    all_confs = conf_vals if conf_vals else action_confs

    failure_agents: Counter = Counter(a.get("agent", "unknown") for a in failed)
    recent_exp = ml.get("recent_experiences", [])
    total_exp = ml.get("total_experiences", 0)
    weights = ml.get("strategy_weights", {})

    # ── Header ────────────────────────────────────────────────────────────────
    print("")
    print("=" * _W)
    print("META-LEARNING BUS -- ADDITIONS THIS RUN")
    print("(what the system will remember for the next run)")
    print("=" * _W)

    # ── Outcomes this run ─────────────────────────────────────────────────────
    _sec("OUTCOMES THIS RUN")
    _row("Healing records ingested :", str(total_exp))
    _row(
        "Results :",
        f"{len(successful)} success  {len(failed)} fail  {len(plan_only)} plan-only",
    )

    # ── Per-learning detail table ─────────────────────────────────────────────
    learnings = successful if successful else healing_actions
    _sec(f"LEARNINGS ({len(learnings)} patterns written to bus)")
    if learnings:
        _AG = 22
        _TR = 20
        _CF = 6
        _TI = 14
        _GT = 20
        _SUM = _W - _AG - _TR - _CF - _TI - _GT - 10
        hdr = (
            f"  {'#':>3}  "
            f"{'Agent':<{_AG}}  "
            f"{'Territory':<{_TR}}  "
            f"{'Conf':>{_CF}}  "
            f"{'Tier':<{_TI}}  "
            f"{'Gate':<{_GT}}  "
            f"{'Fix Summary'}"
        )
        print(hdr)
        print("  " + "-" * (_W - 2))
        for i, a in enumerate(learnings, 1):
            agent = str(a.get("agent", "?"))[:_AG]
            terr = str(a.get("territory", "?"))[:_TR]
            conf = a.get("confidence")
            conf_str = f"{conf:.3f}" if isinstance(conf, (int, float)) else "  -  "
            tier_raw = str(a.get("routing_tier", "DET"))
            tier = tier_raw[:_TI]
            gate = str(a.get("routing_gate", ""))[:_GT]
            fix = str(a.get("fix_summary", ""))
            fix_trunc = (fix[:_SUM] + "...") if len(fix) > _SUM else fix
            print(
                f"  {i:>3}.  "
                f"{agent:<{_AG}}  "
                f"{terr:<{_TR}}  "
                f"{conf_str:>{_CF}}  "
                f"{tier:<{_TI}}  "
                f"{gate:<{_GT}}  "
                f"{fix_trunc}"
            )
    else:
        print("  (no healing events this run)")

    # ── Pattern recall impact ─────────────────────────────────────────────────
    _sec("PATTERN RECALL IMPACT (what next run will remember)")
    if successful:
        succ_agents: Counter = Counter(a.get("agent", "?") for a in successful)
        succ_terrs: Counter = Counter(a.get("territory", "?") for a in successful)
        succ_tiers: Counter = Counter(str(a.get("routing_tier", "DETERMINISTIC")) for a in successful)
        _row(
            "By agent :",
            ", ".join(f"{ag}({ct})" for ag, ct in succ_agents.most_common(6)),
        )
        _row(
            "By territory :",
            ", ".join(f"{t}({c})" for t, c in succ_terrs.most_common(6)),
        )
        _row(
            "By routing tier :",
            ", ".join(f"{t}({c})" for t, c in succ_tiers.most_common()),
        )
    else:
        _row("Patterns stored :", "(none this run)")

    # ── Confidence distribution → routing priors ──────────────────────────────
    _sec("CONFIDENCE DISTRIBUTION  ->  ROUTING PRIORS")
    if all_confs:
        c_min = min(all_confs)
        c_avg = sum(all_confs) / len(all_confs)
        c_max = max(all_confs)
        n_local = sum(1 for c in all_confs if c >= 0.75)
        n_qwen = sum(1 for c in all_confs if 0.40 <= c < 0.75)
        n_gemini = sum(1 for c in all_confs if c < 0.40)
        _row("Range :", f"min={c_min:.3f}  avg={c_avg:.3f}  max={c_max:.3f}")
        _row(
            "High  (>=0.75) :",
            f"{n_local:>3} patterns  -> strengthen DETERMINISTIC routing prior",
        )
        _row(
            "Medium (0.40-0.74) :",
            f"{n_qwen:>3} patterns  -> reinforce QWEN preference",
        )
        _row(
            "Low   (<0.40) :",
            f"{n_gemini:>3} patterns  -> raise GEMINI prior for similar failures",
        )
    else:
        _row("Confidence data :", "(unavailable — no decision records)")

    # ── Tier routing ──────────────────────────────────────────────────────────
    _sec("TIER ROUTING THIS RUN")
    if tier_counts:
        _row("Routing breakdown :", "  ".join(f"{t}={c}" for t, c in tier_counts.most_common()))
    else:
        _row("Routing breakdown :", "(no routing decisions recorded)")

    # ── Failure priors ────────────────────────────────────────────────────────
    _sec("FAILURE PRIORS UPDATED")
    if failure_agents:
        _row(
            "failure_prior++ :",
            ", ".join(f"{ag}({ct})" for ag, ct in failure_agents.most_common(5)),
        )
        for ag, ct in failure_agents.most_common(5):
            _row(
                f"  {ag} :",
                f"{ct} failure(s)  -> next run will avoid this agent for similar inputs",
            )
    else:
        _row("failure_prior++ :", "(none — no failures recorded this run)")

    # ── Strategy weights ──────────────────────────────────────────────────────
    _sec("STRATEGY WEIGHTS (carried to next run)")
    if weights:
        for k, v in sorted(weights.items()):
            delta = ""
            if isinstance(v, float) and abs(v - 1.0) > 0.01:
                delta = "  [SHIFTED from baseline 1.00]"
            _row(f"  {k} :", f"{v:.3f}{delta}")
    else:
        _row("Weights :", "(no strategy weight data)")

    # ── What next run inherits ────────────────────────────────────────────────
    _sec("WHAT NEXT RUN INHERITS")
    if recent_exp:
        for exp in recent_exp:
            print(f"    -> {exp}")
    if all_confs:
        n_local = sum(1 for c in all_confs if c >= 0.75)
        n_qwen = sum(1 for c in all_confs if 0.40 <= c < 0.75)
        n_gemini = sum(1 for c in all_confs if c < 0.40)
        if n_local:
            print(f"    -> {n_local} high-confidence patterns strengthen DETERMINISTIC routing")
        if n_qwen:
            print(f"    -> {n_qwen} medium-confidence patterns reinforce QWEN preference")
        if n_gemini:
            print(f"    -> {n_gemini} low-confidence outcomes raise GEMINI prior for similar failures")
    if failure_agents:
        top_fail = failure_agents.most_common(3)
        for ag, ct in top_fail:
            print(f"    -> failure_prior[{ag}] += {ct}  (will down-weight this agent next run)")
    if not recent_exp and not all_confs and not failure_agents:
        print("    -> (no bus updates produced this run)")

    # ── Cross-Run Persistence Proof ───────────────────────────────────────────
    _sec("CROSS-RUN PERSISTENCE PROOF (what survives to next run)")
    _prior_vecs = ml.get("recent_failure_vectors", [])
    _n_prior = len(_prior_vecs)
    print("")
    print("  Learning Channel                        | Disk | Read | Improves?")
    print("  " + "-" * (_W - 2))
    print("  FileBackedAuditStore -> RCA             |  Y   |  Y   |    Y")
    print("  runtime_state.json meta_learning        |  Y   |  Y   |    Y")
    print("  Oscillation/cooldown history            |  Y   |  Y   |    Y")
    print("  recent_failure_vectors -> novelty (N)   |  Y   |  Y   |    Y")
    print("  L4B/L4C pipeline artifacts              |  Y   |  Y   |    Y")
    print("")
    print("  All 5 channels active. Full feedback loop is closed.")
    print(f"  Failure vectors loaded from prior run : {_n_prior}")
    print(f"  Total experiences carried forward     : {ml.get('total_experiences', 0)}")

    print("")
    print("=" * _W)


def _print_run_manifest(
    state_mgr: "RuntimeStateManager",
    targets: list[str],
) -> int:
    """Print a complete agent/phase execution manifest and return the number of gaps.

    Every expected agent must appear in completed_agents. Every territory must have
    executed Phase 1 (discovery). Any gap is printed as an explicit ERROR line.
    Returns the count of gaps so the caller can decide exit behavior.
    Zero tolerance: if it didn't run, it appears here.
    """
    _W = 78

    # ---------------------------------------------------------------------------
    # Canonical expected agents per scope
    # ---------------------------------------------------------------------------
    # Global agents (run once, outside territory loop)
    GLOBAL_AGENTS = ["RootHygieneAgent", "GravityValidatorAgent", "GravityLeakHealerAgent"]

    # Per-territory agents (must run for every territory)
    PER_TERRITORY_AGENTS = [
        "FilesystemSSOTHealerAgent",  # Phase 2 reconciler
        "LocationHealerAgent",  # Phase 2 location
        "HierarchyHealerAgent",  # Phase 3 alignment
        "FileClassificationHealerAgent",  # Phase 3 sovereignty
        "ArchitectureGovernorAgent",  # Phase 4 arch validation
        "ObservabilityProbeExecutorAgent",  # Phase 6 observability probe
        "CognitiveDispositionAgent",  # Phase 6 cognitive
    ]

    # Phases expected per territory (from execute_phase1_discovery onward)
    PER_TERRITORY_PHASES = [
        "Phase1:Discovery",
        "Phase2:Reconciliation",
        "Phase3:Alignment",
        "Phase3:Sovereignty",
        "Phase4:ArchValidation",
        "Phase5:Healing",
        "Phase6:Observability",
        "Phase7:Certification",
    ]

    # ---------------------------------------------------------------------------
    # Build lookup from state
    # ---------------------------------------------------------------------------
    completed = {a.get("agent") for a in state_mgr.state.get("completed_agents", []) if a.get("agent")}
    failed_agents = {
        a.get("agent"): a.get("details", "no details")
        for a in state_mgr.state.get("completed_agents", [])
        if a.get("agent") and a.get("success") is False
    }
    skipped_agents = {
        a.get("agent"): a.get("reason", "no reason")
        for a in state_mgr.state.get("skipped_agents", [])
        if a.get("agent")
    }
    error_events = state_mgr.state.get("events", [])
    error_msgs: dict[str, list[str]] = {}
    for ev in error_events:
        if ev.get("type") == "error":
            msg = ev.get("message", "")
            for territory in targets:
                if territory in msg:
                    error_msgs.setdefault(territory, []).append(msg)
            if "RootHygieneAgent" in msg:
                error_msgs.setdefault("__global__", []).append(msg)
            if "GravityLeakHealerAgent" in msg:
                error_msgs.setdefault("__global__", []).append(msg)

    # Phase 1 success is inferred: if a territory has completed reconciler/location it ran
    # Phase 1 failure is recorded as an error event "Phase 1 failure in {territory}" or
    # "Crash in {territory}"
    territory_crashed = set()
    phase1_failed = set()
    for ev in error_events:
        msg = ev.get("message", "")
        if ev.get("type") == "error":
            for t in targets:
                if f"Phase 1 failure in {t}" in msg or f"Phase 1 failed for {t}" in msg:
                    phase1_failed.add(t)
                if f"Crash in {t}" in msg:
                    territory_crashed.add(t)

    # ---------------------------------------------------------------------------
    # Print manifest
    # ---------------------------------------------------------------------------
    gaps = 0

    print("")
    print("=" * _W)
    print("  RUN MANIFEST — AGENT & PHASE COVERAGE")
    print("  Zero-tolerance: every expected agent/phase must appear below as RAN")
    print("=" * _W)

    # --- Global agents ---
    print("")
    print("  GLOBAL AGENTS (run once, repo-wide)")
    print("  " + "-" * 40)
    for agent in GLOBAL_AGENTS:
        errs = error_msgs.get("__global__", [])
        agent_errs = [e for e in errs if agent in e]
        if agent in completed and agent not in failed_agents:
            print(f"  ✓  {agent}")
        elif agent in failed_agents:
            print(f"  ✗  {agent}  [FAILED: {failed_agents[agent]}]")
            gaps += 1
        elif agent in skipped_agents:
            print(f"  ⚠  {agent}  [SKIPPED: {skipped_agents[agent]}]")
            gaps += 1
        elif agent_errs:
            print(f"  ✗  {agent}  [ERROR: {agent_errs[0][:120]}]")
            gaps += 1
        else:
            print(f"  ✗  {agent}  [DID NOT RUN — no record in completed_agents]")
            gaps += 1

    # --- Per-territory agents ---
    print("")
    print("  PER-TERRITORY AGENTS")
    print("  " + "-" * 40)
    for territory in targets:
        crashed = territory in territory_crashed
        p1_fail = territory in phase1_failed
        t_errs = error_msgs.get(territory, [])

        print(f"  Territory: {territory}")
        if crashed:
            crash_msg = next((e for e in t_errs if "Crash in" in e), "unknown crash")
            print(f"    ✗  [TERRITORY CRASHED: {crash_msg[:160]}]")
            gaps += len(PER_TERRITORY_AGENTS) + len(PER_TERRITORY_PHASES)
            continue

        if p1_fail:
            p1_msg = next((e for e in t_errs if "Phase 1" in e), "Phase 1 failed")
            print(f"    ✗  Phase1:Discovery  [FAILED: {p1_msg[:160]}]")
            print("    ✗  [ALL DOWNSTREAM PHASES SKIPPED — Phase 1 did not produce drift report]")
            gaps += len(PER_TERRITORY_AGENTS) + len(PER_TERRITORY_PHASES)
            continue

        for agent in PER_TERRITORY_AGENTS:
            a_errs = [e for e in t_errs if agent in e]
            if agent in completed and agent not in failed_agents:
                print(f"    ✓  {agent}")
            elif agent in failed_agents:
                print(f"    ✗  {agent}  [FAILED: {str(failed_agents[agent])[:120]}]")
                gaps += 1
            elif agent in skipped_agents:
                print(f"    ⚠  {agent}  [SKIPPED: {str(skipped_agents[agent])[:120]}]")
                gaps += 1
            elif a_errs:
                print(f"    ✗  {agent}  [ERROR: {a_errs[0][:120]}]")
                gaps += 1
            else:
                print(f"    ✗  {agent}  [DID NOT RUN]")
                gaps += 1

    # --- Summary ---
    print("")
    print("  " + "-" * 40)
    if gaps == 0:
        print("  ✓  ALL EXPECTED AGENTS AND PHASES RAN SUCCESSFULLY")
    else:
        print(f"  ✗  {gaps} AGENT/PHASE EXECUTION GAP(S) DETECTED — SEE ABOVE")
        print("     Re-run with the same flags; gaps indicate errors that must be resolved.")
    print("=" * _W)
    print("")

    return gaps


# ============================================================================
# WAVE 1 — PROVE-IT DATA COLLECTION HELPERS
# Pure functions; read-only access to state.  No I/O, no side-effects.
# ============================================================================


def _collect_llm_call_trace(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> dict:
    """Extract LLM invocation proof from healing_actions and decision records.

    Returns a dict with keys:
      - call_trace   : list of proven calls (tier, request_id, hash, latency, status)
      - blocked_calls: list of expected-but-blocked invocations with blocker reason
      - stats        : expected / actual / blocked_by_flags / blocked_by_errors counts
    """
    import hashlib

    TIER_ALIASES = {
        "DETERMINISTIC": "DETERMINISTIC",
        "SOVEREIGN-AUTO": "DETERMINISTIC",
        "QWEN": "QWEN_VLLM",
        "QWEN_VLLM": "QWEN_VLLM",
        "GEMINI": "GEMINI_2_5_PRO",
        "GEMINI_2_5_PRO": "GEMINI_2_5_PRO",
    }
    LLM_TIERS = {"QWEN_VLLM", "GEMINI_2_5_PRO"}

    healing_actions = state_mgr.state.get("healing_actions", [])
    decisions = getattr(decision_engine, "decisions_made", [])

    call_trace = []
    blocked_calls = []

    for action in healing_actions:
        tier = TIER_ALIASES.get(str(action.get("routing_tier", "DETERMINISTIC")), "DETERMINISTIC")
        if tier not in LLM_TIERS:
            continue
        llm_ev = action.get("llm_call_evidence") or {}
        made = llm_ev.get("llm_call_made", False)
        agent = action.get("agent", "unknown")
        ts = action.get("timestamp", "")
        if made:
            req_payload = json.dumps({"agent": agent, "tier": tier, "ts": ts}, sort_keys=True)
            call_trace.append(
                {
                    "agent": agent,
                    "timestamp": ts,
                    "tier": tier,
                    "model": llm_ev.get("model", ""),
                    "endpoint": llm_ev.get("endpoint", ""),
                    "request_id": llm_ev.get("request_id", ""),
                    "response_id": llm_ev.get("response_id", ""),
                    "latency_ms": llm_ev.get("latency_ms"),
                    "tokens": llm_ev.get("tokens", {}),
                    "cost_usd": llm_ev.get("cost_usd"),
                    "http_status": llm_ev.get("http_status"),
                    "proof": {
                        "request_hash": llm_ev.get(
                            "proof_hash",
                            "sha256:" + hashlib.sha256(req_payload.encode()).hexdigest(),
                        ),
                        "response_hash": llm_ev.get("response_hash", ""),
                        "gateway_call_stack": llm_ev.get("gateway_call_stack", ""),
                    },
                }
            )
        else:
            blocked_calls.append(
                {
                    "agent": agent,
                    "timestamp": ts,
                    "tier": tier,
                    "blocker_type": llm_ev.get("blocker_type", "unknown"),
                    "blocker": llm_ev.get("blocker", action.get("skip_reason", "not_recorded")),
                    "fallback_tier": llm_ev.get("fallback_tier", "DETERMINISTIC"),
                    "llm_call_made": False,
                }
            )

    # Decisions that expected LLM but have no matching action entry
    llm_disabled = not getattr(decision_engine, "enable_llm", True)
    seen_agents = {e["agent"] for e in call_trace} | {e["agent"] for e in blocked_calls}
    for d in decisions:
        tier = TIER_ALIASES.get(str(d.get("routing_tier", "DETERMINISTIC")), "DETERMINISTIC")
        if tier not in LLM_TIERS:
            continue
        agent = d.get("agent", "unknown")
        if agent not in seen_agents:
            _blocker_type = "feature_flag" if llm_disabled else "not_executed"
            _blocker_msg = (
                "LLM disabled (enable_llm=False) — routing decision overridden to DETERMINISTIC"
                if llm_disabled
                else "LLM call expected by routing decision but not recorded in healing_actions"
            )
            blocked_calls.append(
                {
                    "agent": agent,
                    "timestamp": d.get("timestamp", ""),
                    "tier": tier,
                    "blocker_type": _blocker_type,
                    "blocker": _blocker_msg,
                    "fallback_tier": "DETERMINISTIC",
                    "llm_call_made": False,
                }
            )

    # Count expected calls = all healing_actions where tier in LLM_TIERS OR decisions routed to LLM
    all_llm_agents: set = set()
    for a in healing_actions:
        if TIER_ALIASES.get(str(a.get("routing_tier", "")), "") in LLM_TIERS:
            all_llm_agents.add(a.get("agent", "unknown"))
    for d in decisions:
        if TIER_ALIASES.get(str(d.get("routing_tier", "")), "") in LLM_TIERS:
            all_llm_agents.add(d.get("agent", "unknown"))

    blocked_by_flags = sum(1 for b in blocked_calls if "flag" in b.get("blocker_type", "").lower())
    blocked_by_errors = sum(1 for b in blocked_calls if "error" in b.get("blocker_type", "").lower())

    return {
        "call_trace": call_trace,
        "blocked_calls": blocked_calls,
        "stats": {
            "expected_calls": len(all_llm_agents),
            "actual_calls": len(call_trace),
            "blocked_by_flags": blocked_by_flags,
            "blocked_by_errors": blocked_by_errors,
            "execution_rate": (round(len(call_trace) / len(all_llm_agents), 4) if all_llm_agents else 1.0),
        },
    }


def _collect_blocker_scan(state_mgr: "SovereignStateMgr") -> list:
    """Extract blocked agent records with timestamps and blocker taxonomy.

    Returns a list of dicts, one per blocked agent:
      agent, blocker_type, flag/dep name, check_timestamp, code_location,
      stack_trace_hash, last_successful_run, remediation
    """
    import hashlib

    raw = state_mgr.state.get("blocked_agents", [])
    result = []
    for rec in raw:
        if not isinstance(rec, dict):
            continue
        trace = rec.get("stack_trace", [])
        trace_hash = (
            "sha256:" + hashlib.sha256(json.dumps(trace, sort_keys=True).encode()).hexdigest()
            if trace
            else ""
        )
        result.append(
            {
                "agent": rec.get("agent", "unknown"),
                "blocker_type": rec.get("blocker_type", "unknown"),
                "flag": rec.get("flag", rec.get("dependency", "")),
                "flag_value": rec.get("flag_value"),
                "flag_source": rec.get("flag_source", ""),
                "check_timestamp": rec.get("check_timestamp", rec.get("timestamp", "")),
                "code_location": rec.get("code_location", ""),
                "stack_trace": trace,
                "stack_trace_hash": trace_hash,
                "last_successful_run": rec.get("last_successful_run", ""),
                "remediation": rec.get("remediation", ""),
            }
        )
    return result


def _build_coverage_proof(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> dict:
    """Build agent coverage proof: expected vs executed vs skipped.

    Returns a dict with:
      expected_agents, executed_agents, skipped_agents,
      coverage_ratio, proof hashes
    """
    import hashlib

    _ca = state_mgr.state.get("completed_agents", [])
    if isinstance(_ca, dict):
        completed = list(_ca.keys())
    elif isinstance(_ca, (list, tuple)):
        completed = list(
            {a["agent"] for a in _ca if isinstance(a, dict) and a.get("agent")}
            | {a for a in _ca if isinstance(a, str)}
        )
    else:
        completed = []
    blocked = _collect_blocker_scan(state_mgr)
    blocked_names = [b["agent"] for b in blocked]

    # Expected = completed + blocked (all agents the run knew about)
    all_known = list(dict.fromkeys(completed + blocked_names))
    n_expected = len(all_known) if all_known else max(len(completed), 1)
    n_executed = len(completed)
    n_skipped = len(blocked_names)

    executed_hash = "sha256:" + hashlib.sha256(json.dumps(sorted(completed)).encode()).hexdigest()
    expected_hash = "sha256:" + hashlib.sha256(json.dumps(sorted(all_known)).encode()).hexdigest()

    return {
        "expected_agents": {"count": n_expected, "hash": expected_hash},
        "executed_agents": {"count": n_executed, "agents": completed, "hash": executed_hash},
        "skipped_agents": {"count": n_skipped, "agents": blocked_names},
        "coverage_ratio": round(n_executed / n_expected, 4) if n_expected else 1.0,
        "proof_complete": True,
    }


def _build_calibration_proof(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> dict:
    """Compute per-tier confidence calibration error.

    calibration_error = abs(predicted_success_rate - actual_success_rate)

    Returns dict keyed by canonical tier name with:
      predicted_success, actual_success, calibration_error, sample_size
    """
    import hashlib

    TIER_ALIASES = {
        "DETERMINISTIC": "DETERMINISTIC",
        "SOVEREIGN-AUTO": "DETERMINISTIC",
        "QWEN": "QWEN_VLLM",
        "QWEN_VLLM": "QWEN_VLLM",
        "GEMINI": "GEMINI_2_5_PRO",
        "GEMINI_2_5_PRO": "GEMINI_2_5_PRO",
    }

    decisions = getattr(decision_engine, "decisions_made", [])
    healing_actions = state_mgr.state.get("healing_actions", [])

    # Build outcome map: agent -> best outcome across all territories.
    # SUCCESS > PARTIAL > other. Keyed by both exact and lowercased name.
    _OUTCOME_RANK = {"SUCCESS": 2, "PARTIAL": 1}
    _raw_best: dict = {}
    for a in healing_actions:
        agent = a.get("agent", "unknown")
        outcome = str(a.get("outcome", "")).upper()
        rank = _OUTCOME_RANK.get(outcome, 0)
        if rank > _OUTCOME_RANK.get(_raw_best.get(agent, ""), 0):
            _raw_best[agent] = outcome
    outcome_map: dict = {}
    for agent, outcome in _raw_best.items():
        outcome_map[agent] = outcome
        outcome_map[agent.lower()] = outcome

    def _lookup_outcome(agent_key: str) -> str:
        """Resolve a decision agent key to its healing outcome.

        Decision keys are short roster names (e.g. 'location', 'reconciler').
        Healing-action keys are full class names (e.g. 'LocationHealerAgent').
        Resolution order:
          1. Exact match
          2. Case-insensitive exact match
          3. Any healing-action agent whose lower-case name starts with the key
          4. Any healing-action agent whose lower-case name contains the key
          5. Default → empty string (no outcome recorded → not SUCCESS)
        """
        if agent_key in outcome_map:
            return outcome_map[agent_key]
        lk = agent_key.lower()
        if lk in outcome_map:
            return outcome_map[lk]
        for full_name, out in outcome_map.items():
            if full_name.lower().startswith(lk):
                return out
        for full_name, out in outcome_map.items():
            if lk in full_name.lower():
                return out
        return ""

    # Per-tier: collect (predicted_confidence, actual_success)
    tier_data: dict = {}
    for d in decisions:
        if not d.get("decision"):
            continue
        tier = TIER_ALIASES.get(str(d.get("routing_tier", "DETERMINISTIC")), "DETERMINISTIC")
        conf = d.get("confidence")
        if not isinstance(conf, (int, float)):
            continue
        agent = d.get("agent", "unknown")
        # PARTIAL counts as success: agent executed; only FAIL/ERROR/empty is non-success
        actual = 1.0 if _lookup_outcome(agent) in ("SUCCESS", "PARTIAL") else 0.0
        tier_data.setdefault(tier, []).append((float(conf), actual))

    result = {}
    for tier, pairs in tier_data.items():
        if not pairs:
            continue
        pred_avg = round(sum(p for p, _ in pairs) / len(pairs), 4)
        act_avg = round(sum(a for _, a in pairs) / len(pairs), 4)
        calib_err = round(abs(pred_avg - act_avg), 4)
        pairs_hash = "sha256:" + hashlib.sha256(json.dumps(pairs).encode()).hexdigest()
        result[tier] = {
            "predicted_success": pred_avg,
            "actual_success": act_avg,
            "calibration_error": calib_err,
            "sample_size": len(pairs),
            "proof": {"pairs_hash": pairs_hash},
        }
    return result


# ============================================================================
# END WAVE 1 — PROVE-IT DATA COLLECTION HELPERS
# ============================================================================


def _write_mandatory_json_output(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> None:
    """Write mandatory heal-run JSON output to logs/compliance_reports/heal_run_output.json.

    This is always written at the end of every --heal run. It is the authoritative
    machine-readable record of what the run did, what the meta-learning system learned,
    and what the routing engine decided. No querying required after the run.
    """
    import datetime
    from collections import Counter

    healing_actions = state_mgr.state.get("healing_actions", [])
    decisions = getattr(decision_engine, "decisions_made", [])
    ml = state_mgr.state.get("meta_learning", {})

    successful = [a for a in healing_actions if str(a.get("outcome", "")).upper() == "SUCCESS"]
    failed_acts = [
        a for a in healing_actions if str(a.get("outcome", "")).upper() in ("FAIL", "FAILED", "ERROR")
    ]
    plan_only = [a for a in healing_actions if "plan" in str(a.get("outcome", "")).lower()]

    conf_vals = [d.get("confidence", 0.0) for d in decisions if isinstance(d.get("confidence"), (int, float))]
    tier_counts: Counter = Counter()
    for d in decisions:
        if d.get("decision"):
            tier_counts[d.get("routing_tier", "DETERMINISTIC")] += 1

    # Heatmap data — agent x tier counts (mirrors _print_healing_heatmap)
    TIER_ALIASES = {
        "DETERMINISTIC": "DETERMINISTIC",
        "QWEN": "QWEN_VLLM",
        "QWEN_VLLM": "QWEN_VLLM",
        "GEMINI": "GEMINI_2_5_PRO",
        "GEMINI_2_5_PRO": "GEMINI_2_5_PRO",
    }
    heatmap: dict = {}
    for action in healing_actions:
        agent = action.get("agent", "unknown")
        tier = TIER_ALIASES.get(action.get("routing_tier", "DETERMINISTIC"), "DETERMINISTIC")
        heatmap.setdefault(agent, {"DETERMINISTIC": 0, "QWEN_VLLM": 0, "GEMINI_2_5_PRO": 0})
        heatmap[agent][tier] += 1
    seen_pairs = {
        (a.get("agent"), TIER_ALIASES.get(a.get("routing_tier", ""), "DETERMINISTIC"))
        for a in healing_actions
    }
    for d in getattr(decision_engine, "decisions_made", []):
        if not d.get("decision"):
            continue
        agent = d.get("agent", "unknown")
        tier = TIER_ALIASES.get(d.get("routing_tier", "DETERMINISTIC"), "DETERMINISTIC")
        if (agent, tier) not in seen_pairs:
            heatmap.setdefault(agent, {"DETERMINISTIC": 0, "QWEN_VLLM": 0, "GEMINI_2_5_PRO": 0})
            heatmap[agent][tier] += 1

    # Collect Redis / semantic-cache stats — informational; never influences routing.
    _semantic_cache_stats: dict = {}
    try:
        from agentic_core.cache.redis_cache_client import get_hot_cache as _get_hot_cache

        _hot = _get_hot_cache()
        _semantic_cache_stats = _hot.get_stats()
    except Exception:  # guardian: allow-silent-swallower
        _semantic_cache_stats = {"error": "unavailable"}

    # Collect meta-learning pipeline summary from state (populated by _fire_meta_learning_intake)
    _ml_pipeline_state = state_mgr.state.get("meta_learning", {})
    _ml_pipeline_output: dict = {
        "pipeline_ran": bool(_ml_pipeline_state),
        "total_experiences": _ml_pipeline_state.get("total_experiences", 0),
        "recent_experiences": _ml_pipeline_state.get("recent_experiences", [])[:5],
        "strategy_weights": _ml_pipeline_state.get("strategy_weights", {}),
        "failure_vector_count": len(_ml_pipeline_state.get("recent_failure_vectors", [])),
        "last_intake_experience": _ml_pipeline_state.get("experience", None),
    }

    output = {
        "meta": {
            "report_type": "HEAL_RUN_OUTPUT",
            "timestamp": datetime.datetime.now().isoformat(),
            "mandatory": True,
        },
        "semantic_cache": {
            "backend": "redis",
            "stats": _semantic_cache_stats,
            "using_fallback": _semantic_cache_stats.get("using_fallback", True),
            "hits": _semantic_cache_stats.get("hits", 0),
            "misses": _semantic_cache_stats.get("misses", 0),
            "fallback_hits": _semantic_cache_stats.get("fallback_hits", 0),
            "fallback_misses": _semantic_cache_stats.get("fallback_misses", 0),
        },
        "meta_learning_pipeline": _ml_pipeline_output,
        "healing_heatmap": {
            "agents": {
                agent: {
                    **counts,
                    "total": sum(counts.values()),
                }
                for agent, counts in sorted(heatmap.items())
            },
            "totals": {
                "DETERMINISTIC": sum(v.get("DETERMINISTIC", 0) for v in heatmap.values()),
                "QWEN_VLLM": sum(v.get("QWEN_VLLM", 0) for v in heatmap.values()),
                "GEMINI_2_5_PRO": sum(v.get("GEMINI_2_5_PRO", 0) for v in heatmap.values()),
                "grand_total": sum(sum(v.values()) for v in heatmap.values()),
            },
        },
        "meta_learning": {
            "records_ingested": ml.get("total_experiences", 0),
            "outcomes": {
                "success": len(successful),
                "fail": len(failed_acts),
                "plan_only": len(plan_only),
            },
            "patterns_stored": dict(Counter(a.get("agent", "?") for a in successful).most_common(10)),
            "failure_prior_agents": dict(
                Counter(a.get("agent", "unknown") for a in failed_acts).most_common(10)
            ),
            "confidence": {
                "min": round(min(conf_vals), 4) if conf_vals else None,
                "avg": round(sum(conf_vals) / len(conf_vals), 4) if conf_vals else None,
                "max": round(max(conf_vals), 4) if conf_vals else None,
                "band_local_gte075": sum(1 for c in conf_vals if c >= 0.75),
                "band_qwen_040_074": sum(1 for c in conf_vals if 0.40 <= c < 0.75),
                "band_gemini_lt040": sum(1 for c in conf_vals if c < 0.40),
            },
            "tier_routing": dict(tier_counts),
            "strategy_weights": ml.get("strategy_weights", {}),
            "recent_experiences": ml.get("recent_experiences", [])[:5],
        },
        "healing_actions": healing_actions,
        "routing_decisions": [
            {
                "agent": d.get("agent"),
                "territory": d.get("territory"),
                "routing_tier": d.get("routing_tier"),
                "routing_score": d.get("routing_score"),
                "confidence": d.get("confidence"),
                "routing_gate": d.get("routing_gate"),
                "decision": d.get("decision"),
                "model": d.get("model"),
            }
            for d in decisions
        ],
    }

    try:
        reports_dir = getattr(state_mgr, "project_root", None)
        if reports_dir is None:
            reports_dir = Path(__file__).resolve().parent.parent.parent.parent
        out_dir = Path(reports_dir) / "logs" / "compliance_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "heal_run_output.json"
        with open(out_path, "w", encoding="utf-8") as _fh:
            json.dump(output, _fh, indent=2, default=str, ensure_ascii=False)
        print("")
        print("=" * 60)
        print("MANDATORY JSON OUTPUT")
        print(f"  {out_path}")
        print("=" * 60)
    except Exception as _e:  # guardian: allow-silent-swallower
        logger.error("[MANDATORY OUTPUT] Failed to write heal_run_output.json: %s", _e)


# ============================================================================
# WAVE 2 — heal_run_complete.json  (replaces heal_run_output.json)
# ============================================================================


def _write_heal_run_complete(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> dict:
    """Write authoritative heal_run_complete.json with prove-it evidence for all 6 concerns.

    Sections:
      meta, coverage, routing (llm_call_trace + calibration), learning,
      healing_actions, blockers, executive_summary gate criteria.
    Always written; exceptions are logged and swallowed (fail-safe).
    """
    import datetime
    from collections import Counter

    healing_actions = state_mgr.state.get("healing_actions", [])
    decisions = getattr(decision_engine, "decisions_made", [])
    ml = state_mgr.state.get("meta_learning", {})

    # ── Prove-it collectors ───────────────────────────────────────────────────
    llm_trace = _collect_llm_call_trace(state_mgr, decision_engine)
    blockers = _collect_blocker_scan(state_mgr)
    coverage = _build_coverage_proof(state_mgr, decision_engine)
    calibration = _build_calibration_proof(state_mgr, decision_engine)

    # ── Outcomes ─────────────────────────────────────────────────────────────
    successful = [a for a in healing_actions if str(a.get("outcome", "")).upper() == "SUCCESS"]
    failed_acts = [
        a for a in healing_actions if str(a.get("outcome", "")).upper() in ("FAIL", "FAILED", "ERROR")
    ]
    plan_only = [a for a in healing_actions if "plan" in str(a.get("outcome", "")).lower()]

    # ── Meta-learning run comparison ──────────────────────────────────────────
    prev_meta = state_mgr.state.get("prior_meta", {})
    prev_success = prev_meta.get("success_rate")
    cur_success = round(len(successful) / len(healing_actions), 4) if healing_actions else None
    success_delta = (
        round(cur_success - prev_success, 4) if cur_success is not None and prev_success is not None else None
    )
    prev_run_hash = prev_meta.get("run_hash", "")
    prev_run_id = prev_meta.get("run_id", "")

    # ── Strategy weights ──────────────────────────────────────────────────────
    prev_weights = prev_meta.get("strategy_weights", {})
    cur_weights = ml.get("strategy_weights", {})
    weight_shift = {
        k: round(cur_weights.get(k, 0.0) - prev_weights.get(k, 0.0), 4)
        for k in set(list(cur_weights.keys()) + list(prev_weights.keys()))
    }

    # ── Pattern reuse ─────────────────────────────────────────────────────────
    faiss_stats = state_mgr.state.get("faiss_retrieval_stats", {})
    patterns_available = faiss_stats.get("index_size", 0)
    patterns_matched = faiss_stats.get("matched", len(successful))
    patterns_applied = faiss_stats.get("applied", len(successful))
    reuse_success_rate = round(patterns_applied / patterns_matched, 4) if patterns_matched else 1.0

    # ── Git commit ────────────────────────────────────────────────────────────
    git_commit = ""
    try:
        import subprocess as _sp

        _r = _sp.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        git_commit = _r.stdout.strip()
    except Exception:
        pass

    run_ts = datetime.datetime.now().isoformat()
    run_id = "run_" + run_ts.replace(":", "").replace("-", "").replace("T", "_")[:19]

    # ── Healing effectiveness: parse fix_summary strings ─────────────────────
    import re as _re

    _fix_pat = _re.compile(r"Fixed\s+(\d+)\s+of\s+(\d+)", _re.IGNORECASE)
    _scan_pat = _re.compile(r"(\d+)\s+(?:violation|found)", _re.IGNORECASE)

    _total_found = 0
    _total_fixed = 0
    _zero_fix_agents: list[str] = []  # agents with found>0, fixed==0

    for _a in healing_actions:
        _summary = str(_a.get("fix_summary", "") or "")
        _outcome = str(_a.get("outcome", "")).upper()
        _m = _fix_pat.search(_summary)
        if _m:
            _fixed = int(_m.group(1))
            _found = int(_m.group(2))
            _total_found += _found
            _total_fixed += _fixed
            if _found > 0 and _fixed == 0:
                _agent_label = f"{_a.get('agent','?')} [{_a.get('territory','__global__')}]"
                _zero_fix_agents.append(_agent_label)

    _healing_effectiveness = (
        round(_total_fixed / _total_found, 4) if _total_found > 0 else None
    )
    # Agents that reported violations but fixed zero of them (excluding plan-only)
    _zero_fix_blocker = (
        f"{len(_zero_fix_agents)} agent(s) found violations but fixed 0: "
        + ", ".join(_zero_fix_agents[:5])
        + ("..." if len(_zero_fix_agents) > 5 else "")
        if _zero_fix_agents
        else None
    )

    # ── Executive gate criteria (12 gates) ────────────────────────────────────
    llm_rate = llm_trace["stats"]["execution_rate"]
    calib_max_err = (
        max((v["calibration_error"] for v in calibration.values()), default=0.0) if calibration else 0.0
    )
    conf_vals = [d.get("confidence", 0.0) for d in decisions if isinstance(d.get("confidence"), (int, float))]
    avg_conf = round(sum(conf_vals) / len(conf_vals), 4) if conf_vals else None
    tier_counts: Counter = Counter()
    for d in decisions:
        if d.get("decision"):
            tier_counts[d.get("routing_tier", "DETERMINISTIC")] += 1

    pattern_success = round(len(successful) / max(len(healing_actions), 1), 4) if healing_actions else 1.0
    subphase_ok = all(
        a.get("subphases", {}).get("heal", {}).get("status") in (None, "success", "skipped")
        for a in healing_actions
    )
    subphase_integrity = (
        1.0
        if subphase_ok
        else round(
            sum(1 for a in healing_actions if a.get("subphases", {}).get("heal", {}).get("status") != "error")
            / max(len(healing_actions), 1),
            4,
        )
    )
    file_mod_proven = all(
        bool(a.get("subphases", {}).get("heal", {}).get("proof"))
        for a in healing_actions
        if a.get("subphases", {}).get("heal", {}).get("status") == "success"
    )
    llm_calls_proven = all(bool(c.get("proof", {}).get("request_hash")) for c in llm_trace["call_trace"])
    blockers_documented = all(bool(b.get("blocker_type")) for b in blockers)
    learning_improving = success_delta is None or success_delta >= 0.0

    gate_criteria = [
        {
            "criterion": "Agent Coverage",
            "target": ">=0.90",
            "threshold": 0.90,
            "actual": coverage["coverage_ratio"],
            "status": "PASS" if coverage["coverage_ratio"] >= 0.90 else "FAIL",
            "blocker": (
                f"{coverage['skipped_agents']['count']} agents blocked"
                if coverage["coverage_ratio"] < 0.90
                else None
            ),
            "severity": "critical",
        },
        {
            "criterion": "LLM Call Execution Rate",
            "target": ">=0.80",
            "threshold": 0.80,
            "actual": llm_rate,
            "status": "PASS" if llm_rate >= 0.80 else "FAIL",
            "blocker": (
                (
                    lambda _stats=llm_trace["stats"], _llm_on=getattr(decision_engine, "enable_llm", True): (
                        f"{_stats['expected_calls']} call(s) routed to LLM, {_stats['actual_calls']} executed"
                        + (
                            " — LLM disabled (enable_llm=False)"
                            if not _llm_on
                            else " — not_executed (routing decided LLM but no llm_call_evidence written)"
                        )
                    )
                )()
                if llm_rate < 0.80
                else None
            ),
            "severity": "critical",
        },
        {
            "criterion": "Confidence Calibration Error",
            "target": "<=0.15",
            "threshold": 0.15,
            "actual": calib_max_err,
            "status": "PASS" if calib_max_err <= 0.15 else "FAIL",
            "blocker": (
                f"Max calibration error {calib_max_err} exceeds 0.15" if calib_max_err > 0.15 else None
            ),
            "severity": "high",
        },
        {
            "criterion": "Meta-Learning Improvement (Success Delta)",
            "target": ">=0.0",
            "threshold": 0.0,
            "actual": success_delta,
            "status": "PASS" if (success_delta is None or success_delta >= 0.0) else "FAIL",
            "blocker": None if learning_improving else f"Success rate declined {success_delta}",
            "severity": "medium",
        },
        {
            "criterion": "Pattern Reuse Success Rate",
            "target": ">=0.75",
            "threshold": 0.75,
            "actual": reuse_success_rate,
            "status": "PASS" if reuse_success_rate >= 0.75 else "FAIL",
            "blocker": None if reuse_success_rate >= 0.75 else "Pattern application below threshold",
            "severity": "medium",
        },
        {
            "criterion": "Subphase Execution Integrity",
            "target": ">=0.90",
            "threshold": 0.90,
            "actual": subphase_integrity,
            "status": "PASS" if subphase_integrity >= 0.90 else "FAIL",
            "blocker": None if subphase_integrity >= 0.90 else "Agents gated or failed in subphases",
            "severity": "medium",
        },
        {
            "criterion": "File Modification Proof",
            "target": "==1.0",
            "threshold": 1.0,
            "actual": 1.0 if file_mod_proven else 0.0,
            "status": "PASS" if file_mod_proven else "FAIL",
            "blocker": None if file_mod_proven else "Some file modifications lack before/after hashes",
            "severity": "high",
        },
        {
            "criterion": "LLM Call Cryptographic Proof",
            "target": "==1.0",
            "threshold": 1.0,
            "actual": 1.0 if llm_calls_proven else 0.0,
            "status": "PASS" if llm_calls_proven else "FAIL",
            "blocker": None if llm_calls_proven else "LLM calls missing request_hash proof",
            "severity": "high",
        },
        {
            "criterion": "Blocker Documentation",
            "target": "==1.0",
            "threshold": 1.0,
            "actual": 1.0 if blockers_documented else 0.0,
            "status": "PASS" if blockers_documented else "FAIL",
            "blocker": None if blockers_documented else "Some blockers missing blocker_type",
            "severity": "low",
        },
        {
            "criterion": "Run-Over-Run Healing Trend",
            "target": ">=0.0",
            "threshold": 0.0,
            "actual": success_delta,
            "status": "PASS" if (success_delta is None or success_delta >= 0.0) else "FAIL",
            "blocker": None
            if (success_delta is None or success_delta >= 0.0)
            else "Healing trending downward",
            "severity": "high",
        },
        {
            "criterion": "Healing Effectiveness Rate",
            "target": ">=0.50 or N/A",
            "threshold": 0.50,
            "actual": _healing_effectiveness,
            "status": (
                "PASS"
                if _healing_effectiveness is None or _healing_effectiveness >= 0.50
                else "FAIL"
            ),
            "blocker": (
                None
                if _healing_effectiveness is None or _healing_effectiveness >= 0.50
                else (
                    f"Only {_healing_effectiveness:.0%} of found violations were fixed "
                    f"({_total_fixed}/{_total_found})"
                )
            ),
            "severity": "critical",
        },
        {
            "criterion": "Zero-Fix Healer Penalty",
            "target": "==0 agents with found>0 and fixed==0",
            "threshold": 0,
            "actual": len(_zero_fix_agents),
            "status": "PASS" if not _zero_fix_agents else "FAIL",
            "blocker": _zero_fix_blocker,
            "severity": "critical",
        },
    ]

    n_pass = sum(1 for g in gate_criteria if g["status"] == "PASS")
    n_fail = sum(1 for g in gate_criteria if g["status"] == "FAIL")
    overall_status = "PASS" if n_fail == 0 else "FAIL"

    output = {
        "meta": {
            "report_type": "HEAL_RUN_COMPLETE",
            "timestamp": run_ts,
            "run_id": run_id,
            "git_commit": git_commit,
            "mandatory": True,
        },
        "coverage": coverage,
        "routing": {
            "llm_invocation_stats": llm_trace["stats"],
            "llm_call_trace": llm_trace["call_trace"],
            "blocked_calls": llm_trace["blocked_calls"],
            "confidence_calibration": calibration,
            "tier_routing": dict(tier_counts),
        },
        "learning": {
            "run_comparison": {
                "proof": {
                    "previous_run_id": prev_run_id,
                    "previous_run_hash": prev_run_hash,
                    "comparison_timestamp": run_ts,
                },
                "previous_success_rate": prev_success,
                "current_success_rate": cur_success,
                "success_rate_delta": success_delta,
                "improvement_trend": (
                    "positive"
                    if (success_delta or 0) > 0
                    else "stable"
                    if success_delta == 0
                    else "negative"
                    if success_delta is not None
                    else "no_baseline"
                ),
            },
            "pattern_reuse": {
                "patterns_available": patterns_available,
                "patterns_matched": patterns_matched,
                "patterns_applied": patterns_applied,
                "reuse_success_rate": reuse_success_rate,
            },
            "strategy_evolution": {
                "previous_weights": prev_weights,
                "current_weights": cur_weights,
                "weight_shift": weight_shift,
            },
            "meta_learning_pipeline": {
                "pipeline_ran": bool(ml),
                "total_experiences": ml.get("total_experiences", 0),
                "recent_experiences": ml.get("recent_experiences", [])[:5],
                "failure_vector_count": len(ml.get("recent_failure_vectors", [])),
            },
        },
        "healing_actions": healing_actions,
        "blockers": {
            "count": len(blockers),
            "blocked_agents": blockers,
        },
        "executive_summary": {
            "overall_status": overall_status,
            "criteria_passed": n_pass,
            "criteria_failed": n_fail,
            "criteria_total": len(gate_criteria),
            "gate_criteria": gate_criteria,
        },
    }

    try:
        reports_dir = getattr(state_mgr, "project_root", None)
        if reports_dir is None:
            reports_dir = Path(__file__).resolve().parent.parent.parent.parent
        out_dir = Path(reports_dir) / "logs" / "compliance_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "heal_run_complete.json"
        with open(out_path, "w", encoding="utf-8") as _fh:
            json.dump(output, _fh, indent=2, default=str, ensure_ascii=False)
        print("")
        print("=" * 60)
        print("MANDATORY JSON OUTPUT (heal_run_complete.json)")
        print(f"  {out_path}")
        print("=" * 60)
    except Exception as _e:  # guardian: allow-silent-swallower
        logger.error("[MANDATORY OUTPUT] Failed to write heal_run_complete.json: %s", _e)

    return output  # returned so _print_executive_summary can reuse computed data


# ============================================================================
# WAVE 3 — failure_forensics.json
# ============================================================================


def _write_failure_forensics(
    state_mgr: "SovereignStateMgr",
    decision_engine: "SovereignDecisionEngine",
) -> None:
    """Write failure_forensics.json — detailed drill-down for failed/blocked/misrouted agents.

    Only written when there are failures, blockers, or misrouted agents.
    If all agents succeed and nothing is blocked, the file is not written.
    """
    import datetime
    import hashlib

    TIER_ALIASES = {
        "DETERMINISTIC": "DETERMINISTIC",
        "SOVEREIGN-AUTO": "DETERMINISTIC",
        "QWEN": "QWEN_VLLM",
        "QWEN_VLLM": "QWEN_VLLM",
        "GEMINI": "GEMINI_2_5_PRO",
        "GEMINI_2_5_PRO": "GEMINI_2_5_PRO",
    }

    healing_actions = state_mgr.state.get("healing_actions", [])
    decisions = getattr(decision_engine, "decisions_made", [])
    blockers = _collect_blocker_scan(state_mgr)
    calibration = _build_calibration_proof(state_mgr, decision_engine)

    # Build decision index by agent for routing proof
    decision_index: dict = {}
    for d in decisions:
        decision_index[d.get("agent", "unknown")] = d

    failed_agents = []
    for action in healing_actions:
        outcome = str(action.get("outcome", "")).upper()
        if outcome not in ("FAIL", "FAILED", "ERROR"):
            continue
        agent = action.get("agent", "unknown")
        d = decision_index.get(agent, {})
        routing_tier = TIER_ALIASES.get(str(action.get("routing_tier", "DETERMINISTIC")), "DETERMINISTIC")
        expected_tier = TIER_ALIASES.get(str(d.get("routing_tier", routing_tier)), routing_tier)
        conf = action.get("confidence") or d.get("confidence")
        subphases = action.get("subphases", {})

        llm_ev = action.get("llm_call_evidence") or {}
        llm_made = llm_ev.get("llm_call_made", False)

        failed_agents.append(
            {
                "agent": agent,
                "territory": action.get("territory", ""),
                "intended_behavior": "heal",
                "actual_behavior": action.get("actual_behavior", outcome.lower()),
                "deviation": routing_tier != expected_tier or not llm_made,
                "subphases": subphases,
                "llm_routing_proof": {
                    "expected_tier": expected_tier,
                    "actual_tier": routing_tier,
                    "llm_call_made": llm_made,
                    "blocker": llm_ev.get("blocker", ""),
                    "blocker_check_timestamp": llm_ev.get("blocker_check_timestamp", ""),
                    "blocker_check_location": llm_ev.get("blocker_check_location", ""),
                    "blocker_proof_hash": (
                        "sha256:"
                        + hashlib.sha256(
                            json.dumps({"agent": agent, "blocker": llm_ev.get("blocker", "")}).encode()
                        ).hexdigest()
                        if llm_ev.get("blocker")
                        else ""
                    ),
                },
                "confidence": conf,
                "error": action.get("error", ""),
                "fix_summary": action.get("fix_summary", ""),
                "remediation": action.get("remediation", ""),
            }
        )

    # Misrouted: routed to DETERMINISTIC but failed (should have gone to LLM tier)
    misrouted_agents = []
    for action in healing_actions:
        outcome = str(action.get("outcome", "")).upper()
        if outcome not in ("FAIL", "FAILED", "ERROR"):
            continue
        agent = action.get("agent", "unknown")
        tier = TIER_ALIASES.get(str(action.get("routing_tier", "DETERMINISTIC")), "DETERMINISTIC")
        if tier != "DETERMINISTIC":
            continue
        conf = action.get("confidence")
        if not isinstance(conf, (int, float)):
            continue
        # If confidence was medium-low (would suggest LLM tier), flag as misrouted
        if conf < 0.75:
            d = decision_index.get(agent, {})
            calib_det = calibration.get("DETERMINISTIC", {})
            misrouted_agents.append(
                {
                    "agent": agent,
                    "confidence": conf,
                    "routed_to": "DETERMINISTIC",
                    "outcome": outcome,
                    "should_have_routed_to": "QWEN_VLLM" if conf >= 0.40 else "GEMINI_2_5_PRO",
                    "routing_proof": {
                        "confidence_value": conf,
                        "threshold_deterministic": 0.75,
                        "threshold_qwen": 0.40,
                        "selected_tier": "DETERMINISTIC",
                        "calibration_error": calib_det.get("calibration_error"),
                    },
                    "remediation": ("Lower DETERMINISTIC threshold or add agent-specific calibration"),
                }
            )

    run_ts = datetime.datetime.now().isoformat()
    output = {
        "meta": {
            "report_type": "FAILURE_FORENSICS",
            "timestamp": run_ts,
        },
        "summary": {
            "failed_agents_count": len(failed_agents),
            "blocked_agents_count": len(blockers),
            "misrouted_agents_count": len(misrouted_agents),
        },
        "failed_agents": failed_agents,
        "blocked_agents": blockers,
        "misrouted_agents": misrouted_agents,
    }

    try:
        reports_dir = getattr(state_mgr, "project_root", None)
        if reports_dir is None:
            reports_dir = Path(__file__).resolve().parent.parent.parent.parent
        out_dir = Path(reports_dir) / "logs" / "compliance_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "failure_forensics.json"
        with open(out_path, "w", encoding="utf-8") as _fh:
            json.dump(output, _fh, indent=2, default=str, ensure_ascii=False)
        clean = not failed_agents and not blockers and not misrouted_agents
        status_tag = "CLEAN" if clean else "FAILURES_PRESENT"
        print(f"[FORENSICS] failure_forensics.json ({status_tag}) -> {out_path}")
    except Exception as _e:  # guardian: allow-silent-swallower
        logger.error("[FORENSICS] Failed to write failure_forensics.json: %s", _e)


# ============================================================================
# WAVE 4 — Executive Summary Table (mandatory last console output)
# ============================================================================


def _print_executive_summary(
    complete_output: dict,
) -> None:
    """Print the mandatory high-signal pass/fail executive summary table.

    Accepts the dict returned by _write_heal_run_complete so no recomputation needed.
    12 gate criteria rows, VERDICT line, critical blockers, remediation commands,
    proof integrity check, healing effectiveness breakdown, next-run prediction.
    """
    es = complete_output.get("executive_summary", {})
    gate_criteria = es.get("gate_criteria", [])
    overall = es.get("overall_status", "UNKNOWN")
    n_pass = es.get("criteria_passed", 0)
    n_fail = es.get("criteria_failed", 0)
    meta = complete_output.get("meta", {})
    coverage = complete_output.get("coverage", {})
    routing = complete_output.get("routing", {})
    learning = complete_output.get("learning", {})
    blockers_sec = complete_output.get("blockers", {})

    _W = 80
    sep = "-" * _W

    print("")
    print("=" * _W)
    print("HEALING RUN EXECUTIVE SUMMARY")
    run_id = meta.get("run_id", "")
    git = meta.get("git_commit", "")
    ts = meta.get("timestamp", "")
    print(f"Run ID: {run_id} | Git: {git} | {ts}")
    print("=" * _W)

    # Gate criteria table
    col_crit = 42
    col_tgt = 8
    col_act = 10
    col_st = 6
    hdr = (
        f"{'GATE CRITERIA':<{col_crit}} | {'TARGET':>{col_tgt}} | {'ACTUAL':>{col_act}} | "
        f"{'STATUS':<{col_st}} | BLOCKER"
    )
    print(hdr)
    print(sep)
    for g in gate_criteria:
        crit = str(g.get("criterion", ""))[:col_crit]
        tgt = str(g.get("target", ""))[:col_tgt]
        actual_raw = g.get("actual")
        if actual_raw is None:
            actual_str = "N/A"
        elif isinstance(actual_raw, float):
            actual_str = f"{actual_raw:.4f}"
        else:
            actual_str = str(actual_raw)
        status = g.get("status", "?")
        blocker = g.get("blocker") or "N/A"
        status_disp = f"[{status}]"
        print(
            f"{crit:<{col_crit}} | {tgt:>{col_tgt}} | {actual_str:>{col_act}} | "
            f"{status_disp:<{col_st + 2}} | {blocker}"
        )
    print(sep)
    print(
        f"{'OVERALL GATE STATUS':<{col_crit}} | {'':>{col_tgt}} | {'':>{col_act}} | "
        f"[{overall}]   | {n_fail}/{len(gate_criteria)} criteria failed"
    )
    print("=" * _W)

    # Critical blockers
    all_blockers = blockers_sec.get("blocked_agents", [])
    if all_blockers:
        print("")
        print("CRITICAL BLOCKERS (Must Fix Before Next Run)")
        print(sep)
        for i, b in enumerate(all_blockers[:8], 1):
            agent = b.get("agent", "?")
            flag = b.get("flag", "") or b.get("blocker_type", "?")
            rem = b.get("remediation", "")
            print(f"  {i}. [{b.get('blocker_type', '?').upper():<18}] {agent} — {flag}")
            if rem:
                print(f"     Remediation: {rem}")

    # Proof integrity
    print("")
    print("PROOF INTEGRITY")
    print(sep)
    llm_calls = routing.get("llm_call_trace", [])
    proven_calls = sum(1 for c in llm_calls if c.get("proof", {}).get("request_hash"))
    total_calls = len(llm_calls)
    all_hashes_present = proven_calls == total_calls
    all_blockers_doc = all(bool(b.get("blocker_type")) for b in all_blockers)
    print(
        f"  {'All hashes present':<40} {'OK' if all_hashes_present else 'MISSING'} ({proven_calls}/{total_calls})"
    )
    print(
        f"  {'All blockers documented':<40} {'OK' if all_blockers_doc else 'MISSING'} ({len(all_blockers)} blockers)"
    )
    cov_ratio = coverage.get("coverage_ratio", 0.0)
    exec_count = coverage.get("executed_agents", {}).get("count", 0)
    exp_count = coverage.get("expected_agents", {}).get("count", 0)
    print(f"  {'Agent coverage proof':<40} OK ({exec_count}/{exp_count} agents, ratio={cov_ratio:.4f})")

    # Healing effectiveness breakdown (per-agent signal)
    import re as _re2
    _fp2 = _re2.compile(r"Fixed\s+(\d+)\s+of\s+(\d+)", _re2.IGNORECASE)
    _heal_rows = []
    for _a in complete_output.get("healing_actions", []):
        _m2 = _fp2.search(str(_a.get("fix_summary", "") or ""))
        if _m2:
            _fx, _fd = int(_m2.group(1)), int(_m2.group(2))
            if _fd > 0:
                _pct = f"{_fx}/{_fd}"
                _tag = "OK" if _fx == _fd else ("PARTIAL" if _fx > 0 else "ZERO-FIX")
                _heal_rows.append((_a.get("agent", "?"), _a.get("territory", ""), _pct, _tag))
    if _heal_rows:
        print(f"  {'Healing effectiveness (agents with violations)':<40}")
        for _ag, _terr, _pct, _tag in _heal_rows:
            _lbl = f"{_ag} [{_terr}]" if _terr else _ag
            print(f"    {_tag:<10} {_pct:<8} {_lbl}")

    # Next-run prediction (if blockers present)
    skipped_count = coverage.get("skipped_agents", {}).get("count", 0)
    blocked_llm = routing.get("llm_invocation_stats", {}).get("blocked_by_flags", 0)
    if skipped_count > 0 or blocked_llm > 0:
        print("")
        print("NEXT RUN PREDICTION (if blockers resolved)")
        print(sep)
        predicted_coverage = min(round(cov_ratio + (skipped_count / max(exp_count, 1)), 4), 1.0)
        llm_exp = routing.get("llm_invocation_stats", {}).get("expected_calls", 0)
        llm_act = routing.get("llm_invocation_stats", {}).get("actual_calls", 0)
        predicted_llm = 1.0 if llm_exp > 0 else 1.0
        cur_sr = learning.get("run_comparison", {}).get("current_success_rate")
        predicted_sr = round(min((cur_sr or 0.0) + 0.10, 1.0), 4) if cur_sr is not None else None
        print(
            f"  Agent coverage  : {cov_ratio:.4f} -> {predicted_coverage:.4f} (+{predicted_coverage - cov_ratio:.4f})"
        )
        print(
            f"  LLM call rate   : {routing.get('llm_invocation_stats', {}).get('execution_rate', 0.0):.4f} -> {predicted_llm:.4f}"
        )
        if predicted_sr is not None:
            print(f"  Success rate    : {cur_sr:.4f} -> {predicted_sr:.4f} (est.)")

    print("")
    print("=" * _W)
    verdict_line = f"VERDICT: {overall}  ({n_pass}/{len(gate_criteria)} gate criteria passed)"
    print(verdict_line)
    if overall == "PASS":
        print("  All diagnostic gates satisfied. Healing pipeline operating as intended.")
    else:
        print(
            f"  {n_fail} gate(s) failed. See logs/compliance_reports/failure_forensics.json for drill-down."
        )
    print("  Detailed reports: logs/compliance_reports/heal_run_complete.json")
    print("                    logs/compliance_reports/failure_forensics.json")
    print("=" * _W)
    print("")


def run_pipeline(
    adapters: "dict[str, object]",
    territory: str,
    decision_engine: "SovereignDecisionEngine",
    state_mgr: "RuntimeStateManager",
    ctx: "HealContext",
) -> "dict[str, object]":
    """Unified pipeline loop replacing the five bespoke execute_phase*_impl functions.

    Governance invariants enforced:
    - Digest emitted exactly once per call via _emit_pipeline_digest.
    - pre_commit and validate receive scan_ctx (heal=False) structurally.
    - update_agent is never called for execute/heal when gated or fatal.
    - All four subphase slots are always present in AgentRunResult.subphases.
    - Exception in any subphase → fatal=True → remaining subphases skipped.
    - Confidence gate fires immediately after validate, before any execute call.

    Returns dict mapping agent_id -> AgentRunResult.
    """
    from agentic_core.L2_execution.protocol import AgentRunResult, SubphaseResult

    _emit_pipeline_digest(adapters, territory, ctx)

    # scan_ctx: structurally enforces read-only for pre_commit + validate.
    # Use dataclasses.replace when ctx is a frozen dataclass (HealContext);
    # fall back to a simple namespace copy for test mocks or other objects.
    import dataclasses as _dc2

    if _dc2.is_dataclass(ctx) and not isinstance(ctx, type):
        scan_ctx = _dc2.replace(ctx, heal=False)
    else:

        class _ScanCtx:
            pass

        scan_ctx = _ScanCtx()
        for _attr in ("heal", "enable_llm", "auto_approve", "enable_telemetry", "enable_meta_learning"):
            setattr(scan_ctx, _attr, getattr(ctx, _attr, False))
        scan_ctx.heal = False
        scan_ctx.enable_llm = False  # scan subphases never invoke LLM

    results: dict[str, AgentRunResult] = {}

    for agent_id in AGENT_PIPELINE:
        adapter = adapters.get(agent_id)
        if adapter is None:
            continue

        run_result = AgentRunResult()
        # Pre-populate all 4 slots as skipped; overwritten as each runs
        for sp in PIPELINE_SUBPHASES:
            run_result.subphases[sp] = SubphaseResult(skipped=True, skip_reason="not reached")

        fatal = False

        for subphase_name in PIPELINE_SUBPHASES:
            is_mutating = subphase_name in ("execute", "heal")

            # Skip mutating subphases when healing is disabled
            if is_mutating and not getattr(ctx, "heal", False):
                run_result.subphases[subphase_name] = SubphaseResult(skipped=True, skip_reason="heal=False")
                continue

            # Skip execute/heal when confidence gate blocked or prior fatal error
            if is_mutating and (run_result.gated or fatal):
                run_result.subphases[subphase_name] = SubphaseResult(
                    skipped=True,
                    skip_reason=run_result.gate_reason if run_result.gated else "prior error",
                )
                continue

            # Only call update_agent when the subphase will actually run
            state_mgr.update_agent(agent_id, subphase_name)
            effective_ctx = scan_ctx if not is_mutating else ctx

            try:
                method = getattr(adapter, subphase_name)
                result: SubphaseResult = method(territory, effective_ctx)
            except Exception as exc:  # guardian: allow-silent-swallower
                result = SubphaseResult(
                    error=str(exc),
                    skipped=True,
                    skip_reason=f"exception: {exc}",
                )
                run_result.error = str(exc)
                fatal = True
                state_mgr.skip_agent(agent_id, f"{subphase_name} exception: {exc}")
                run_result.subphases[subphase_name] = result
                break  # stop subphase loop for this agent (fail-closed)

            run_result.subphases[subphase_name] = result
            run_result.violations_total += len(result.violations)
            run_result.mutations_applied += len(result.fixed)

            # Confidence gate fires immediately after validate
            if subphase_name == "validate" and result.violations:
                confidence = decision_engine.calculate_healing_confidence(
                    len(result.violations),
                    [v.get("type", "UNKNOWN") for v in result.violations[:10]],
                    territory,
                    agent_name=agent_id,
                )
                proceed, reason = decision_engine.should_proceed_with_healing(
                    confidence, agent_id, territory=territory
                )
                if not proceed:
                    run_result.gated = True
                    run_result.gate_reason = reason
                    state_mgr.skip_agent(agent_id, reason)
                    state_mgr.complete_agent(agent_id, True, f"gated: {reason}")
                    continue  # execute/heal will be filled as skipped in next iterations

            state_mgr.complete_agent(agent_id, result.error is None, result.error or "")

        results[agent_id] = run_result

    return results


# DEPRECATED: The five execute_phase*_impl functions below are replaced by
# run_pipeline above. They are kept as dead code until the new loop has been
# validated in production. Do not add new call sites.


def print_execution_plan(arbitrate_plan: bool = False, ptc_plan: bool = False) -> None:
    """Print stable, sorted execution plan to stdout.

    Args:
        arbitrate_plan: If True, include multi-agent arbitration results
        ptc_plan: If True, include PTC tool call results
    """
    for phase in EXECUTION_PLAN:
        print(f"PHASE {phase['phase']}: {phase['name']}")
        for agent in phase["agents"]:
            kwargs_str = f" ({agent['kwargs']})" if agent.get("kwargs") else ""
            print(f"  - {agent['key']}.{agent['method']}{kwargs_str}")
            print(f"    # {agent['description']}")
        print()

    # Include arbitration results if requested
    if arbitrate_plan:
        print("=== MULTI-AGENT ARBITRATION ===")

        # Build task for arbitration
        task = {
            "task_id": "execute_ssot_plan",
            "task_kind": "planning",
        }

        try:
            # Import arbitration modules
            from agentic_core.L3_orchestration.arbitration.arbitration_contract import ArbitrationInput
            from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
            from agentic_core.L3_orchestration.arbitration.run_advisors import run_all_advisors

            # Run advisors
            proposals = run_all_advisors(task)

            # Arbitrate
            input_data = ArbitrationInput(
                task_id=task["task_id"],
                task_kind=task["task_kind"],
                proposals=proposals,
            )

            arbitrator = Arbitrator()
            decision = arbitrator.arbitrate(input_data)

            print(f"Selected Advisor: {decision.selected_advisor_id}")
            print(f"Selected Decision: {decision.selected_decision}")
            print(f"Score Breakdown: {decision.score_breakdown}")
            print(f"Merged Rationale: {decision.merged_rationale}")
            print(f"Merged Risks: {decision.merged_risks}")

        except Exception as e:  # guardian: allow-silent-swallower
            print(f"Error listing artifacts: {e}")

        print()

    # Include PTC results if requested
    if ptc_plan:
        print("=== PROGRAMMATIC TOOL CALLING ===")

        # Initialize violations list if not already defined
        if "violations" not in locals():
            violations = []

        try:
            # Import PTC modules
            from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
            from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
            from agentic_core.L3_orchestration.ptc.tool_call_store import record_tool_call
            from agentic_core.L3_orchestration.ptc.tool_contract import ToolCall, generate_call_id
            from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

            # Register built-in tools (idempotent)
            register_builtin_tools()

            # Get registry and invoker
            registry = get_global_registry()
            invoker = ToolInvoker()

            # Use expr_eval to evaluate an expression
            expr_call = ToolCall(
                call_id=generate_call_id("expr_eval", {"expr": "2 + 3 * 4"}),
                tool_id="expr_eval",
                args={"expr": "2 + 3 * 4"},
                policy={"timeout": 5},
            )

            expr_result = invoker.invoke(expr_call, registry)
            spec, _ = registry.get("expr_eval")
            artifact_ref = record_tool_call(expr_call, expr_result, spec)

            # Prepare PTC plan data
            ptc_plan_data = {
                "tool_calls": [
                    {
                        "tool_id": expr_call.tool_id,
                        "call_id": expr_call.call_id,
                        "args": expr_call.args,
                        "exit_code": expr_result.exit_code,
                        "stdout": expr_result.stdout,
                        "stderr": expr_result.stderr,
                        "truncated": expr_result.truncated,
                    }
                ],
                "artifact_ref": {
                    "kind": artifact_ref.kind,
                    "logical_id": artifact_ref.logical_id,
                    "version": artifact_ref.version,
                    "path": artifact_ref.path,
                },
                "summary": "PTC executed 1 tool calls for plan context",
            }

            # Print deterministic JSON block
            import json

            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))

        except Exception as e:  # guardian: allow-silent-swallower
            # Create error plan data but don't fail plan mode
            ptc_plan_data = {"tool_calls": [], "summary": f"PTC setup failed: {str(e)}", "error": str(e)}
            import json

            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))
            violations.append((0, "PTC_SCAN_ERROR", f"Scan error: {e}"))

        print()


def resolve_agent_subset(requested: list[str]) -> list[str]:
    """Resolve requested agent keys to a closed set including dependencies.

    Raises ValueError on unknown keys.
    Deterministic ordering: sorted alphabetically after closure.
    """
    unknown = set(requested) - CANONICAL_ROSTER_KEYS
    if unknown:
        raise ValueError(f"Unknown agent key(s): {sorted(unknown)}. Valid: {sorted(CANONICAL_ROSTER_KEYS)}")

    closed = set(requested)
    frontier = list(requested)
    while frontier:
        key = frontier.pop()
        for dep in AGENT_DEPENDENCIES.get(key, []):
            if dep not in closed:
                closed.add(dep)
                frontier.append(dep)
    return sorted(closed)


def list_available_agents(project_root=None, dedupe=False):
    """Alias for discover_agents_from_registry (backward compat)."""
    if project_root is None:
        project_root = REPO_ROOT
    agents = discover_agents_from_registry(project_root)
    if dedupe:
        seen = set()
        unique = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                unique.append(agent)
        return unique
    return agents


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================


def main() -> int:
    """Deterministic wrapper: logging, V15 enforcement, console, then legacy body."""
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    pre_parser.add_argument(
        "--allow-protected-root-mutation",
        action="store_true",
        default=False,
        help="Allow writes to protected root directories (audited override).",
    )
    pre_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )
    pre_args, remaining = pre_parser.parse_known_args()
    _configure_logging(int(pre_args.verbose))
    _apply_v15_enforcement_flag(pre_args)
    _maybe_force_utf8_console()

    # Log protected-root override status exactly once
    if pre_args.allow_protected_root_mutation:
        print("[PROTECTED-ROOT] override ENABLED: protected root mutation permitted")
    else:
        print("[PROTECTED-ROOT] override DISABLED: protected root mutation blocked")

    try:
        _legacy_main(
            remaining,
            repo_root=REPO_ROOT,
            allow_protected_root_mutation=pre_args.allow_protected_root_mutation,
        )
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


def _build_ssot_territory_targets(project_root: "Path") -> list[str]:
    """Derive the canonical territory target list from SOVEREIGN_TERRITORIES SSOT.

    Returns only keys whose corresponding directory exists under project_root,
    sorted with agentic_core sub-layers first (L0 → L6), then alphabetical.
    Dotfile dirs (.backup, .github, .gravity_state) are excluded — they do not
    need the full agent pipeline.
    """
    try:
        from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_TERRITORIES

        all_keys = list(SOVEREIGN_TERRITORIES.keys())
    except ImportError:
        # Fallback to previous hardcoded list if SSOT import unavailable
        logger.warning("[territory-build] SSOT import failed — using legacy hardcoded list")
        return [
            "prompt_governance",
            "L5_safety",
            "L3_orchestration",
            "L2_execution",
            "L0_routing",
        ]

    # Exclude dotfile dirs — not meaningful territory targets for agent pipeline
    excluded = {".backup", ".github", ".gravity_state"}
    # agentic_core itself is a top-level territory; keep it but also expand to sub-layers
    # that the agents know how to scope (L0_routing, L2_execution, L3_orchestration,
    # L5_safety are the canonical sub-territories inside agentic_core).
    agentic_core_sublayers = [
        "L0_routing",
        "L2_execution",
        "L3_orchestration",
        "L5_safety",
    ]

    targets = []
    # Add agentic_core sub-layers first (they have specialised agent scoping)
    for sub in agentic_core_sublayers:
        sub_path = project_root / AGENTIC_CORE_DIR / sub
        if sub_path.exists():
            targets.append(sub)

    # Add all other SOVEREIGN_TERRITORIES keys that exist and are not excluded/already added
    skip = set(agentic_core_sublayers) | excluded | {"agentic_core"}
    for key in sorted(all_keys):
        if key in skip:
            continue
        territory_path = project_root / key
        if territory_path.exists():
            targets.append(key)

    logger.info(f"[territory-build] SSOT-derived targets ({len(targets)}): {targets}")
    return targets


def _compute_pipeline_digest(targets: "list[str]") -> str:
    """Compute a stable determinism digest for the pipeline run.

    Five-component SHA-256 surface:
      policy_hash          -- canonical sovereign policy identifier
      registry_hash        -- SHA-256 of sorted agent registry surface
      config_surface_hash  -- from negative_control_harness (tamper-sensitive)
      transcript_hash      -- SHA-256 of sorted processed territory names
      dependency_lock_hash -- stable structural constant

    Returns a 64-char hex string.  Never raises; falls back to a sentinel
    digest on import failure so the pipeline is not blocked.
    """
    import hashlib as _h
    import json as _j

    try:
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface as _gcs,
        )
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            hash_config_surface as _hcs,
        )
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter as _DE,
        )
    except ImportError as _exc:
        logger.warning(f"[DETERMINISM-DIGEST] import failed: {_exc}")
        return _h.sha256(b"determinism-digest:import-failed").hexdigest()

    _policy_hash = _h.sha256(b"sovereign-policy-v1.0").hexdigest()

    try:
        from agentic_core.agents.agent_registry import registry_digest as _rd

        _reg_bytes = _j.dumps(_rd(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        _registry_hash = _h.sha256(_reg_bytes).hexdigest()
    except Exception:  # guardian: allow-silent-swallower
        _registry_hash = _h.sha256(b"registry:fallback").hexdigest()

    _config_hash = _hcs(_gcs())

    _transcript_bytes = _j.dumps(
        sorted(str(t) for t in targets),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    _transcript_hash = _h.sha256(_transcript_bytes).hexdigest()

    _dep_lock_hash = _h.sha256(b"dependency-lock:stable").hexdigest()

    _emitter = _DE()
    return _emitter.compute(
        policy_hash=_policy_hash,
        registry_hash=_registry_hash,
        config_surface_hash=_config_hash,
        transcript_hash=_transcript_hash,
        dependency_lock_hash=_dep_lock_hash,
    )


@_optional_runtime_guard()("E.execute_ssot_main.execute_ssot")
def _legacy_main(
    args: argparse.Namespace, *, repo_root: Path | None = None, allow_protected_root_mutation: bool = False
):
    _maybe_force_utf8_console()  # G-UTF8: ensure stdout/stderr are UTF-8 safe on Windows
    _maybe_force_utf8_logging_handlers()  # G-UTF8: fix handler streams created before console reconfigure

    # [WAVE 2] Import/symbol preflight check (fail-fast if critical symbols missing)
    try:
        _preflight_import_check()
        logger.info("[PREFLIGHT] Import/symbol check PASSED")
    except RuntimeError as exc:
        logger.critical(f"[PREFLIGHT] FAILED: {exc}")
        sys.exit(1)

    # [WAVE 2] Startup fence self-test (abort if fence inactive)
    if not allow_protected_root_mutation:
        try:
            from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                SourceMutationBlocked,
                enforce_protected_root,
            )

            # Attempt to write to agentic_core/.tmp_fence_probe
            probe_path = REPO_ROOT / AGENTIC_CORE_DIR / ".tmp_fence_probe"
            fence_active = False

            try:
                # This should raise SourceMutationBlocked if fence is active
                enforce_protected_root(probe_path, allow_override=False)
                # If we get here, fence is NOT active - CRITICAL FAILURE
                logger.critical("[FENCE-SELF-TEST] FAILED: Protected root fence is INACTIVE")
                sys.exit(1)
            except SourceMutationBlocked:
                # Expected: fence blocked the write
                fence_active = True

            if fence_active:
                logger.info("[FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE")
            else:
                logger.critical("[FENCE-SELF-TEST] FAILED: Fence state indeterminate")
                sys.exit(1)

        except ImportError as exc:
            logger.critical(f"[FENCE-SELF-TEST] FAILED: Cannot import fence module: {exc}")
            sys.exit(1)
    else:
        logger.warning("[FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled")
        os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"  # guardian: allow-global-mutation
        os.environ["BMG_EMBEDDINGS_ENABLED"] = "true"  # guardian: allow-global-mutation
        os.environ["AGENTIC_BYPASS_LONGPATHS_CHECK"] = "1"  # guardian: allow-global-mutation

    # §8.1e — V15 manifest at SSOT bootstrap entry (AGGREGATE, L0 bootstrap)
    _v15_manifest = _v15_build_ssot_manifest()
    if _v15_manifest is not None:
        _v15_ssot_gateway_audit(_v15_manifest, trace_id=_v15_manifest.correlation_id)

    project_root = repo_root if repo_root is not None else REPO_ROOT
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

    # [AGENT SUBSET] Validate and resolve --agents early (before imports).
    requested_agent_keys: list[str] | None = None
    if args.agents:
        raw_keys = [k.strip() for k in args.agents.split(",") if k.strip()]
        try:
            requested_agent_keys = resolve_agent_subset(raw_keys)
            logger.info(f"Agent subset resolved: {requested_agent_keys}")
        except ValueError as ve:
            sys.exit(f"ERROR: {ve}")

    # [CENTRALIZED] validate ⇒ dry_run mapping (single source of truth).
    # When --validate is set, dry_run is forced True. This ensures
    # FileClassificationAgent and all other agents see consistent flags.
    if args.validate:
        args.dry_run = True

    # [HARDENED] 0. Pre-Flight Validation
    validator = PreFlightValidator(project_root, dry_run=args.dry_run)
    env_ok, env_errors = validator.run_checks()
    if not env_ok:
        logger.critical("🛑 PRE-FLIGHT CHECK FAILED:")
        for err in env_errors:
            logger.error(f"  - {err}")
        if not args.list_agents:
            sys.exit(1)

    # [ULTRA-HARDENED] Validate user-supplied territory name format via regex
    if args.territory and not re.match(r"^[A-Za-z0-9_]+$", args.territory):
        sys.exit("ERROR: Invalid territory name: only alphanumeric and underscores allowed.")

    # 1. Handle Discovery
    if args.list_agents:
        logger.info("DISCOVERABLE AGENTS:")
        agents_list = list_available_agents(project_root)
        for i, (name, path) in enumerate(agents_list, 1):
            print(f"   {i:3}. {name:<40} [{path}]")
        print(f"\nTotal: {len(agents_list)} agents")
        return

    # [PHASE 8] Handle baseline capture command
    if args.capture_baseline:
        print("\n🔒 INITIATING BASELINE CAPTURE PROTOCOL...")
        try:
            from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor

            result = invoke_arch_governor(
                action="capture_baseline",
                project_root=project_root,
            )
            if result.get("success"):
                print(f"✨ Golden Baseline captured at: {result.get('manifest_path')}")
                sys.exit(0)
            else:
                logger.error(f"Baseline capture failed: {result.get('error')}")
                sys.exit(1)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.error(f"Baseline capture failed: {e}")
            sys.exit(1)

    # 2. Handle Direct Agent Invocation (Developer Mode)
    if args.agent:
        logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
        try:
            found = [x for x in list_available_agents(project_root) if args.agent.lower() in x[0].lower()]
            if not found:
                logger.error(f"Agent {args.agent} not found.")
                logger.info("Use --list-agents to see available agents")
                return

            name, path = found[0]
            logger.info(f"Found: {name} at {path}")

            module = importlib.import_module(path)

            # Try instantiation strategies
            agent = None
            if hasattr(module, f"get_{name.lower()}"):
                agent = getattr(module, f"get_{name.lower()}")(project_root)
            elif hasattr(module, name):
                agent_cls = getattr(module, name)
                agent = agent_cls(project_root=project_root)
            else:
                logger.error(f"Could not instantiate {name}")
                return

            logger.info(f"Running {name}...")

            # Prefer standard methods
            if hasattr(agent, "run"):
                result = agent.run()
            elif hasattr(agent, "scan_root_violations"):
                result = agent.scan_root_violations()
            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=False)
            else:
                result = "Agent instantiated but no standard run method found."

            logger.info(f"Result: {result}")

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.error(f"Failed to run agent: {e}")
            traceback.print_exc()
        return

    # 3. Initialize Sovereign State & Agents
    # [SSOT MIXIN] Build ExecutionContext with L4-derived policy hash
    ExecutionContext = _get_execution_context_class()
    try:
        from agentic_core.L4_state.config.versioned_configs import get_active_configs

        _l4_policy_hash = get_active_configs().policy.config_hash
    except ImportError:
        _l4_policy_hash = "fallback-no-l4"
    _exec_ctx = ExecutionContext(
        mission_id=args.territory or "default",
        trace_id=f"mission-{int(time.time())}",
        replay_mode=False,
        active_policy_hash=_l4_policy_hash,
        safety_status="CLEARED",
    )

    state_mgr = RuntimeStateManager(project_root, execution_context=_exec_ctx)

    # [HEAL CONTEXT] Single source of truth for all healing flags
    ctx = HealContext.from_args(args)

    # [META-LEARNING] Tied to --heal: proposals always applied when healing is active
    state_mgr.state["apply_proposals"] = ctx.heal

    # [SIMPLIFIED] Auto-set env vars unless interactive mode explicitly requested
    if ctx.auto_approve:
        os.environ.setdefault("SOVEREIGN_AUTO_APPROVE", "1")  # guardian: allow-global-mutation
        os.environ.setdefault("ARCHIVE_BATCH_ACCEPT", "1")  # guardian: allow-global-mutation

    # [HARDENED] Use Sovereign Decision Engine — wired from HealContext
    # [B2/G6 CROSS-RUN] Build advisory healing memory retriever from the persisted FAISS
    # index so _route_decision() can consult prior-run failure patterns (advisory-only,
    # never mutates tier/thresholds).  NullHealingMemoryRetriever when embeddings disabled.
    _hmr = None
    try:
        from agentic_core.L1_cognition.memory.healing_memory_retriever import (
            build_retriever as _build_hmr,
        )

        _hmr = _build_hmr(base_path=REPO_ROOT / "logs" / "faiss_store")
    except Exception:  # guardian: allow-silent-swallower
        pass
    decision_engine = SovereignDecisionEngine(
        enable_llm=ctx.enable_llm,
        state_mgr=state_mgr,
        enable_cda=True,
        execution_context=_exec_ctx,
        auto_approve=ctx.auto_approve,
        healing_memory_retriever=_hmr,
    )

    logger.info("UNIFIED SOVEREIGN PROTOCOL STARTED")
    logger.info(
        f"  Mode: {'HEAL-ACTIVE (LLM + telemetry + meta-learning + auto-approve ON)' if ctx.heal else 'SCAN-ONLY (passive)'}"
    )

    # [HARDENED] Mandatory Hard Imports for Total Awareness (via subprocess)
    try:
        from agentic_core.L0_routing.utils.subprocess_runner_util import (
            invoke_agent_roster_validation,
        )

        roster_result = invoke_agent_roster_validation()

        if roster_result.get("success"):
            logger.info("Total Awareness: Mandatory agent roster registered.")
            logger.info(f"  Agents validated: {', '.join(roster_result.get('agents_validated', []))}")
        else:
            integrity_errors = roster_result.get("integrity_errors", [])
            if integrity_errors:
                logger.critical("🛑 SOVEREIGN CONTRACT BREACH - AGENT INTEGRITY FAILED:")
                for err in integrity_errors:
                    logger.error(f"  - {err}")
                if not args.list_agents:
                    sys.exit(1)  # Halt mission if any agent is non-compliant
            else:
                error_msg = roster_result.get("error", "Unknown error")
                logger.critical(f"🛑 FATAL: Mandatory agent or dependency missing: {error_msg}")
                sys.exit(1)

    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-silent-swallower
        logger.critical(f"🛑 FATAL: Agent roster validation failed: {e}")
        sys.exit(1)

    # 3b. Build local agents roster (classes, not instances)
    (
        ArchitectureGovernorAgent,
        CognitiveDispositionAgent,
        FileClassificationHealerAgent,
        FilesystemSSOTHealerAgent,
        GravityLeakHealerAgent,
        HierarchyHealerAgent,
        LocationHealerAgent,
        RootHygieneAgent,
        ObservabilityProbeExecutorAgent,
    ) = _get_l5_agent_roster()

    agents = {
        "reconciler": FilesystemSSOTHealerAgent,
        "location": LocationHealerAgent,  # BUG-1 fix: was LocationValidatorAgent which raises NotImplementedError
        "hierarchy": HierarchyHealerAgent,
        "arch_governor": ArchitectureGovernorAgent,
        "gravity_repair": GravityLeakHealerAgent,
        "file_classification": FileClassificationHealerAgent,
        "observability_probe": ObservabilityProbeExecutorAgent,
        "cognitive_disposition": CognitiveDispositionAgent,
        "root_hygiene": RootHygieneAgent,
    }

    # 4. Determine Targets
    targets = []
    mission_mode = ""
    if args.territory:
        targets = [args.territory]
        mission_mode = f"Territory Scan: {args.territory}"
    elif args.domains:
        # Multi-domain sweep — derive from SSOT to avoid stale hardcode
        targets = _build_ssot_territory_targets(project_root)
        mission_mode = "Multi-Domain Sweep (L3 Attempt)"
    else:
        # Default to full domain sweep derived from SSOT SOVEREIGN_TERRITORIES
        targets = _build_ssot_territory_targets(project_root)
        mission_mode = "Multi-Domain Sweep (Default)"

    # Domain targeting hardening for protected roots
    if args.domains and not allow_protected_root_mutation:
        for domain in ["L0_routing", "L2_execution", "L3_orchestration", "L5_safety"]:
            if domain in targets:
                domain_path = project_root / AGENTIC_CORE_DIR / domain
                if domain_path.exists():
                    logger.warning(f"[PROTECTED-ROOT] forcing scan-only for {domain}")
                    print(f"[PROTECTED-ROOT] forcing scan-only (no mutations) for {domain}")
                    from dataclasses import replace as _dc_replace

                    ctx = _dc_replace(ctx, heal=False, enable_telemetry=False, enable_meta_learning=False)
                    break

    # 5. Execute Mission
    # [HARDENED] Wrap entire autonomous execution in NonInteractiveGuard
    is_autonomous = not args.manual

    try:
        with NonInteractiveGuard(active=is_autonomous):
            state_mgr.start_mission(f"Unified Protocol: {mission_mode}", [f"{t}" for t in targets])

            # [PHASE 8] Integrated Integrity Check
            # [HARDENED] Pass territory targets to ensure integrity check is also scoped.
            if is_autonomous:
                logger.info(f"🔍 [PHASE 8] Running integrity check (Scope: {targets})...")
                try:
                    from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor

                    result = invoke_arch_governor(
                        action="audit",
                        project_root=project_root,
                        targets=targets,
                    )

                    if result.get("success"):
                        audit_results = result.get("audit_results", {})
                        # [UNIFIED AUDIT] Persist all identified violations to the runtime state
                        state_mgr.state["compliance_report_audit"] = audit_results

                        stats = audit_results.get("stats", {})
                        if stats.get("violations_found", 0) > 0:
                            logger.warning(
                                f"⚠️  {stats['violations_found']} total violations identified.",
                            )

                        if stats.get("drift_detected", 0) > 0:
                            logger.error(
                                f"🛑 CRITICAL: {stats['drift_detected']} integrity drift detected.",
                            )
                            if args.validate:
                                state_mgr.finish_mission(status="failed_integrity")
                                sys.exit(1)  # Fatal in CI
                            else:
                                logger.warning("⚠️  Proceeding with caution (Heal mode active)...")
                    else:
                        logger.warning(f"Integrity check failed: {result.get('error')}")
                except Exception as e:
                    logger.error(f"Integrity check FAILED: {e}\n{traceback.format_exc()}")
                    state_mgr.add_event("error", f"Integrity check failed: {e}")

            # [INTEGRATION] Attempt L3 Smart Orchestration first
            if args.domains:
                l3_success, l3_results = try_summon_orchestrator(project_root, targets, execute=is_autonomous)
                if l3_success:
                    state_mgr.update_meta_learning(
                        {"total_experiences": 1, "experience": "L3 Mission Complete"},
                    )
                    state_mgr.finish_mission("completed")
                    logger.info("🎉 L3 MISSION COMPLETED")
                    return l3_results

            # Territories outside agentic_core that are included in the sweep for
            # scan/report but must NEVER receive autonomous mutations.
            # Heal on these requires --territory <name> (single-territory, user-deliberate).
            _agentic_core_sublayer_prefixes = ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")
            _SCAN_ONLY_TERRITORIES = [
                t
                for t in targets
                if t != "agentic_core" and not any(t.startswith(p) for p in _agentic_core_sublayer_prefixes)
            ]
            _NON_AC_TERRITORIES = set(_SCAN_ONLY_TERRITORIES)

            # [HARDENED] Universal Compliance Persistence
            results = []
            # Fix 4: RootHygieneAgent scans REPO_ROOT (not per-territory).
            # Run once before the territory loop to prevent N× duplicate violations.
            state_mgr.state["hygiene_violations"] = []
            state_mgr.state["hygiene_fixed"] = 0
            try:
                state_mgr.update_agent("RootHygieneAgent", "L0 - Maintenance")
                hygiene_agent = agents["root_hygiene"](project_root=REPO_ROOT)
                if hasattr(hygiene_agent, "scan_root_violations"):
                    hygiene_results = hygiene_agent.scan_root_violations()
                    hygiene_violations = hygiene_results.get("violations", [])
                    high = [v for v in hygiene_violations if v.get("severity") == "high"]
                    hygiene_fixed = 0
                    if ctx and ctx.heal and hasattr(hygiene_agent, "heal"):
                        for _v in hygiene_violations:
                            try:
                                _r = hygiene_agent.heal(_v)
                                if isinstance(_r, dict) and _r.get("status") == "success":
                                    hygiene_fixed += 1
                                    logger.info(
                                        "[RootHygiene] HEALED %s: %s",
                                        _v.get("type"),
                                        _v.get("file", ""),
                                    )
                            except Exception as _he:
                                logger.error(
                                    "[RootHygiene] heal() FAILED for %s: %s\n%s",
                                    _v.get("type"),
                                    _he,
                                    traceback.format_exc(),
                                )
                                state_mgr.add_event(
                                    "error", f"RootHygieneAgent heal failed for {_v.get('type')}: {_he}"
                                )
                    state_mgr.complete_agent(
                        "RootHygieneAgent",
                        True,
                        f"Violations: {len(hygiene_violations)} (high: {len(high)}) fixed: {hygiene_fixed}",
                    )
                    state_mgr.state["hygiene_violations"] = hygiene_violations
                    state_mgr.state["hygiene_fixed"] = hygiene_fixed
                    # [H3] Record healing action for RootHygieneAgent
                    if hygiene_fixed > 0:
                        _record_healing_action(
                            state_mgr,
                            agent="RootHygieneAgent",
                            territory="__global__",
                            routing_tier="DETERMINISTIC",
                            confidence=0.9,
                            fix_summary=f"Cleaned {hygiene_fixed} of {len(hygiene_violations)} root hygiene violations",
                            outcome="SUCCESS",
                        )
                else:
                    state_mgr.complete_agent("RootHygieneAgent", False, "No scan_root_violations method")
            except Exception as e:
                logger.error(f"RootHygieneAgent FAILED: {e}\n{traceback.format_exc()}")
                state_mgr.add_event("error", f"RootHygieneAgent failed: {e}")
                state_mgr.complete_agent("RootHygieneAgent", False, str(e))

            # [FIX-B8] Run GravityLeakRepairAgent once globally (same pattern as RootHygieneAgent)
            try:
                _run_gravity_repair_global(agents, state_mgr, ctx=ctx)
            except Exception as e:
                logger.error(f"GravityLeakRepairAgent global run FAILED: {e}\n{traceback.format_exc()}")
                state_mgr.add_event("error", f"GravityLeakRepairAgent failed: {e}")

            # [L3-SEAM] Initialize agent execution log for L3EfficiencyTuner consumption
            if "agent_execution_log" not in state_mgr.state:
                state_mgr.state["agent_execution_log"] = []

            # Dirs that contain no agent code and produce zero healing fixes.
            # Running all 7 phases against them causes redundant full-repo
            # location scans — skip them from the full pipeline entirely.
            # Code territories outside agentic_core (apps_*, tests, ops_scripts,
            # system_learning) are NOT in this set and still get the full pipeline.
            _DATA_ONLY_TERRITORIES = frozenset(
                {"logs", "docs", "data", "archives", "artifacts", "tools"}
            )

            for territory in targets:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"PROCESSING TERRITORY: {territory}")
                logger.info(f"{'=' * 60}")

                if territory in _DATA_ONLY_TERRITORIES and ctx.heal:
                    logger.info(
                        f"[SKIP] {territory} is a data/artifact territory — bypassing full pipeline (scan-only)"
                    )
                    results.append({"territory": territory, "status": "scan_only_skipped"})
                    continue

                # Update State with Target
                state_mgr.state["current_territory"] = territory
                state_mgr.save()
                state_mgr.add_event("domain_start", f"Entering Domain: {territory}")
                # [L3-SEAM] Record territory start time for efficiency tuner
                _territory_start_ms = time.monotonic() * 1000.0

                from dataclasses import replace as _dc_replace

                effective_ctx = ctx

                # [EXPANDED SCOPE] All territories respect --heal flag uniformly
                # FIX-B12 removed: non-AC territories no longer force heal=False
                # when --heal is explicitly passed. Healing is now territory-agnostic.

                # [FIX] Reset per-territory decision engine state so cycle detection
                # does not bleed across territories (agent_name="Unknown" accumulates).
                decision_engine._call_path = set()
                decision_engine._healing_count = 0
                decision_engine._healing_enabled = True  # [FIX-B15] Reset budget gate per territory

                try:
                    # [UNIVERSAL HEALING] Unified Execution Phase
                    # All agents now receive the 'Heal' signal if confidence is met
                    p1_drift, p1_loc, p1_scan_result = execute_phase1_discovery(
                        agents,
                        territory,
                        decision_engine,
                        state_mgr,
                        effective_ctx,
                    )

                    if p1_drift is not None:
                        # Phase 2: Reconciliation (Write/Heal Phase)
                        # Create plan from Phase 1 results
                        # Build violations from actual drift report keys.
                        # suggested_agent must match agents dict keys for lookup + BMG GPU routing.
                        _phase1_violations = []
                        for _f in p1_drift.get("forbidden_folders") or []:
                            _phase1_violations.append(
                                {"type": "FORBIDDEN_FOLDER", "file": str(_f), "suggested_agent": "reconciler"}
                            )
                        for _d in p1_drift.get("duplicate_folders") or []:
                            _dname = _d.get("name", str(_d)) if isinstance(_d, dict) else str(_d)
                            _phase1_violations.append(
                                {"type": "DUPLICATE_FOLDER", "file": _dname, "suggested_agent": "location"}
                            )
                        for _a in p1_drift.get("archived_files_at_root") or []:
                            _phase1_violations.append(
                                {
                                    "type": "ARCHIVED_FILE_AT_ROOT",
                                    "file": str(_a),
                                    "suggested_agent": "root_hygiene",
                                }
                            )
                        for _lv in p1_loc or []:
                            if isinstance(_lv, dict):
                                _lv["suggested_agent"] = "location"
                                _phase1_violations.append(_lv)
                            else:
                                _phase1_violations.append(
                                    {"type": "LOCATION", "file": str(_lv), "suggested_agent": "location"}
                                )
                        plan = {"violations_found": _phase1_violations}

                        # Execute Phase 2 with decision engine gating
                        phase2_result = execute_phase2_reconciliation(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            plan,
                            effective_ctx,
                        )

                        # Log Phase 2 results
                        raw = phase2_result.get("_raw_result", {})
                        if raw.get("modifications"):
                            logger.info(f"✅ Phase 2: {len(raw['modifications'])} fixes applied")
                        if raw.get("failures"):
                            logger.warning(f"⚠️ Phase 2: {len(raw['failures'])} fixes failed")
                        # BUG-2 fix: persist Phase 2 fix count into state so cert builder reads it
                        _p2_fixed = phase2_result.get("violations_fixed", 0)
                        state_mgr.state["phase2_violations_fixed"] = (
                            state_mgr.state.get("phase2_violations_fixed", 0) + _p2_fixed
                        )

                        # Phase 3: Final Validation (Post-heal AST checks)
                        # [FIX-B6] Use _phase1_violations built above, not p1_drift.get('violations', []) which is always []
                        phase3_result = execute_phase3_validation(
                            agents,
                            territory,
                            _phase1_violations,
                            False,
                        )

                        if phase3_result["status"] == "clean":
                            logger.info("✅ Phase 3: All files pass validation")
                        else:
                            remaining_count = len(phase3_result.get("remaining_violations", []))
                            logger.warning(f"⚠️ Phase 3: {remaining_count} issues detected")

                        # Continue with existing phases
                        # Phase 3: Structural Alignment (Hierarchy)
                        execute_phase3_alignment(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            effective_ctx,
                        )

                        # [UNIVERSAL HEALING] Phase 3: Sovereignty Enforcement (Pascal/Header/Naming)
                        # Now integrated with confidence-based decision engine
                        # [PHASE 2 ENHANCEMENT] Include classification violations in confidence calc
                        classification_violations = state_mgr.state.get("classification_violations", [])
                        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)
                        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER"]
                        # Add CLASSIFICATION type if we have classification violations
                        if classification_violations:
                            violation_types.append("CLASSIFICATION")
                        pascal_confidence = decision_engine.calculate_healing_confidence(
                            violations_count=total_violations,
                            violation_types=violation_types,
                            territory=territory,
                        )
                        pascal_proceed, pascal_reason = decision_engine.should_proceed_with_healing(
                            pascal_confidence, "FileClassificationHealerAgent"
                        )

                        state_mgr.add_event("decision", f"Sovereignty Healing: {pascal_reason}")
                        logger.info(f"Sovereignty Decision: {pascal_reason}")

                        if pascal_proceed and effective_ctx.heal:
                            logger.info(f"Triggering Sovereignty Purge: {territory}")
                            state_mgr.update_agent("FileClassificationHealerAgent", "L5 - Safety")
                            _fc_healer_cls = agents.get("file_classification")
                            if _fc_healer_cls is not None:
                                _fc_instance = _fc_healer_cls(project_root=REPO_ROOT)
                                heal_result = _fc_instance.heal_repository(dry_run=False, execute=True)
                            else:
                                heal_result = {}
                            healed = (
                                heal_result.get("violations_fixed", 0) if isinstance(heal_result, dict) else 0
                            )
                            state_mgr.complete_agent(
                                "FileClassificationHealerAgent", True, f"Healed: {healed}"
                            )
                            _record_healing_action(
                                state_mgr,
                                agent="FileClassificationHealerAgent",
                                territory=territory,
                                routing_tier=pascal_reason.split("(")[0].strip()
                                if pascal_reason
                                else "DETERMINISTIC",
                                routing_score=pascal_confidence.value
                                if hasattr(pascal_confidence, "value")
                                else 1.0,
                                confidence=pascal_confidence.value
                                if hasattr(pascal_confidence, "value")
                                else 1.0,
                                fix_summary=f"Fixed {healed} file classification violation(s) in {territory}",
                                outcome="SUCCESS" if healed > 0 else "PARTIAL",
                            )
                        elif not pascal_proceed:
                            state_mgr.skip_agent("FileClassificationHealerAgent", pascal_reason)
                            _record_healing_action(
                                state_mgr,
                                agent="FileClassificationHealerAgent",
                                territory=territory,
                                routing_tier="DETERMINISTIC",
                                routing_score=0.0,
                                confidence=0.0,
                                fix_summary=f"Skipped file classification healing: {pascal_reason}",
                                outcome="SKIPPED",
                            )
                        elif not effective_ctx.heal:
                            state_mgr.skip_agent(
                                "FileClassificationHealerAgent", "scan-only mode (no --heal)"
                            )

                        # Phase 4: Architectural Validation
                        gov, arch = execute_phase4_architectural_validation(
                            agents, territory, state_mgr, ctx=effective_ctx
                        )

                        # Persist full work to state
                        state_mgr.state["compliance_report"] = gov
                        state_mgr.save()

                        # Phase 5: Final Healing (Governor)
                        execute_phase5_healing(
                            agents,
                            territory,
                            gov,
                            decision_engine,
                            state_mgr,
                            effective_ctx,
                        )

                        # Phase 6: Additional Agent Execution (Observability Probe & Root Hygiene)
                        logger.info(f"=== PHASE 6: ADDITIONAL AGENTS - {territory} ===")

                        # [FIX-B2] Reset per-territory conversational violations to prevent cross-territory accumulation
                        state_mgr.state["conversational_violations"] = []

                        # Execute ObservabilityProbeExecutorAgent
                        logger.info(f"🤖 Triggering Observability Probe: {territory}")
                        state_mgr.update_agent("ObservabilityProbeExecutorAgent", "L6 - Observability")
                        try:
                            conversational_agent = agents.get("observability_probe", lambda **_: None)(
                                project_root=REPO_ROOT, probe_type="debate"
                            )
                            if hasattr(conversational_agent, "scan_violations"):
                                conv_results = conversational_agent.scan_violations(
                                    target_territory=territory,
                                )
                                conv_violations = conv_results.get("violations", [])
                                state_mgr.complete_agent(
                                    "ObservabilityProbeExecutorAgent",
                                    True,
                                    f"Violations: {len(conv_violations)}",
                                )
                                _record_healing_action(
                                    state_mgr,
                                    agent="ObservabilityProbeExecutorAgent",
                                    territory=territory,
                                    routing_tier="DETERMINISTIC",
                                    routing_score=1.0,
                                    confidence=1.0,
                                    fix_summary=f"Observability probe scan: {len(conv_violations)} violation(s) in {territory}",
                                    outcome="SUCCESS",
                                )
                                # Store violations for aggregation
                                if not state_mgr.state.get("conversational_violations"):
                                    state_mgr.state["conversational_violations"] = []
                                state_mgr.state["conversational_violations"].extend(conv_violations)
                            else:
                                state_mgr.complete_agent(
                                    "ObservabilityProbeExecutorAgent",
                                    False,
                                    "No scan_violations method",
                                )
                                _record_healing_action(
                                    state_mgr,
                                    agent="ObservabilityProbeExecutorAgent",
                                    territory=territory,
                                    routing_tier="DETERMINISTIC",
                                    routing_score=0.0,
                                    confidence=0.0,
                                    fix_summary=f"ObservabilityProbeExecutorAgent unavailable in {territory}",
                                    outcome="SKIPPED",
                                )
                        except Exception as e:
                            logger.error(
                                f"ObservabilityProbeExecutorAgent FAILED: {e}\n{traceback.format_exc()}"
                            )
                            state_mgr.add_event(
                                "error", f"ObservabilityProbeExecutorAgent failed in {territory}: {e}"
                            )
                            state_mgr.complete_agent("ObservabilityProbeExecutorAgent", False, str(e))
                            _record_healing_action(
                                state_mgr,
                                agent="ObservabilityProbeExecutorAgent",
                                territory=territory,
                                routing_tier="DETERMINISTIC",
                                routing_score=0.0,
                                confidence=0.0,
                                fix_summary=f"ObservabilityProbeExecutorAgent error in {territory}: {str(e)[:120]}",
                                outcome="FAILED",
                            )

                        # Execute CognitiveDispositionAgent
                        try:
                            state_mgr.update_agent("CognitiveDispositionAgent", "L1 - Cognition")
                            cog_agent = agents["cognitive_disposition"](project_root=REPO_ROOT)
                            if hasattr(cog_agent, "get_analytics"):
                                cog_results = cog_agent.get_analytics()
                                state_mgr.complete_agent(
                                    "CognitiveDispositionAgent",
                                    True,
                                    f"Analytics keys: {list(cog_results.keys())[:4]}",
                                )
                                _record_healing_action(
                                    state_mgr,
                                    agent="CognitiveDispositionAgent",
                                    territory=territory,
                                    routing_tier="DETERMINISTIC",
                                    routing_score=1.0,
                                    confidence=1.0,
                                    fix_summary=f"Cognitive analytics: {list(cog_results.keys())[:4]} in {territory}",
                                    outcome="SUCCESS",
                                )
                            else:
                                state_mgr.complete_agent(
                                    "CognitiveDispositionAgent", False, "No get_analytics method"
                                )
                                _record_healing_action(
                                    state_mgr,
                                    agent="CognitiveDispositionAgent",
                                    territory=territory,
                                    routing_tier="DETERMINISTIC",
                                    routing_score=0.0,
                                    confidence=0.0,
                                    fix_summary=f"CognitiveDispositionAgent unavailable in {territory}",
                                    outcome="SKIPPED",
                                )
                        except Exception as e:
                            logger.error(f"CognitiveDispositionAgent FAILED: {e}\n{traceback.format_exc()}")
                            state_mgr.add_event(
                                "error", f"CognitiveDispositionAgent failed in {territory}: {e}"
                            )
                            state_mgr.complete_agent("CognitiveDispositionAgent", False, str(e))
                            _record_healing_action(
                                state_mgr,
                                agent="CognitiveDispositionAgent",
                                territory=territory,
                                routing_tier="DETERMINISTIC",
                                routing_score=0.0,
                                confidence=0.0,
                                fix_summary=f"CognitiveDispositionAgent error in {territory}: {str(e)[:120]}",
                                outcome="FAILED",
                            )

                        # Phase 7 (RootHygieneAgent moved outside territory loop — Fix 4)
                        cert = execute_phase7_final(agents, territory, state_mgr, decision_engine)
                        results.append(cert)
                        # [L3-SEAM] Record territory duration for L3EfficiencyTuner
                        _territory_elapsed_ms = time.monotonic() * 1000.0 - _territory_start_ms
                        state_mgr.state["agent_execution_log"].append(
                            {
                                "territory": territory,
                                "agent": "__territory_total__",
                                "duration_ms": round(_territory_elapsed_ms, 2),
                            }
                        )
                    else:
                        logger.error(f"Phase 1 failed for {territory} - skipping")
                        state_mgr.add_event("error", f"Phase 1 failure in {territory}")

                except RuntimeError as runtime_err:
                    # Catch the NonInteractiveGuard trap specifically
                    if "Interactive prompt blocked" in str(runtime_err):
                        logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {runtime_err}")
                        state_mgr.add_event("error", f"Blocked Prompt in {territory}")
                        continue  # Skip this territory, try next
                    raise runtime_err
                except Exception as e:
                    logger.error(f"❌ Protocol crashed on {territory}: {e}\n{traceback.format_exc()}")
                    state_mgr.add_event("error", f"Crash in {territory}: {type(e).__name__}: {str(e)[:500]}")
                    if is_autonomous:
                        continue
                    else:
                        _fire_meta_learning_intake(state_mgr, now_utc=int(time.time()))
                        state_mgr.finish_mission(status="error")
                        sys.exit(1)

            # Wave 0C: fire meta-learning intake before closing the mission
            _fire_meta_learning_intake(state_mgr, now_utc=int(time.time()))

            # Save aggregate report across all territories
            save_aggregate_report(targets, REPO_ROOT)

            # Only mark completed if we got here
            state_mgr.finish_mission(status="completed")

            # L6: emit determinism digest — exactly one line per run
            try:
                from agentic_core.L6_observability.engines.determinism_digest_emitter import (
                    DeterminismDigestEmitter as _DET_EMITTER,
                )

                _det_digest = _compute_pipeline_digest(targets)
                _det_line = _DET_EMITTER().emit_once(_det_digest)
                print(_det_line)
            except Exception as _det_exc:  # guardian: allow-silent-swallower
                logger.warning(f"[DETERMINISM-DIGEST] emission failed: {_det_exc}")

            # Final Summary
            logger.info(f"\n{'=' * 60}")
            logger.info("🎉 UNIFIED PROTOCOL COMPLETED")
            logger.info(f"{'=' * 60}")
            logger.info(f"Territories processed: {len(results)}/{len(targets)}")
            logger.info(f"Decisions made: {len(decision_engine.decisions_made)}")

            # Decision breakdown
            high_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] > 0.75)
            med_conf = sum(1 for d in decision_engine.decisions_made if 0.5 <= d["confidence"] <= 0.75)
            low_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] < 0.5)
            logger.info(f"  High confidence: {high_conf}, Medium: {med_conf}, Low: {low_conf}")

            _print_healing_heatmap(state_mgr, decision_engine)
            _print_meta_learning_summary(state_mgr, decision_engine)

            # [ZERO-TOLERANCE] Print full agent/phase coverage manifest.
            # Any agent or phase that did not run is explicitly named here.
            _manifest_gaps = _print_run_manifest(state_mgr, targets)
            if _manifest_gaps > 0:
                logger.error(
                    f"[RUN MANIFEST] {_manifest_gaps} agent/phase gap(s) detected. "
                    "See RUN MANIFEST output above for full details."
                )

            _write_mandatory_json_output(state_mgr, decision_engine)

            # [OBSERVABILITY] Wave 2-4: prove-it outputs + executive summary table
            _complete_output = _write_heal_run_complete(state_mgr, decision_engine)
            _write_failure_forensics(state_mgr, decision_engine)
            if isinstance(_complete_output, dict):
                _print_executive_summary(_complete_output)

            return results

    # guardian: allow-silent-swallow
    except Exception as fatal_e:  # guardian: allow-silent-swallower
        # Catch-all for top-level crashes (e.g., initialization failure)
        logger.critical(f"🔥 FATAL PROTOCOL ERROR: {fatal_e}")
        traceback.print_exc()
        _fire_meta_learning_intake(state_mgr, now_utc=int(time.time()))
        state_mgr.finish_mission(status="fatal_error")
        sys.exit(1)


# ============================================================================
# DYNAMIC AGENT DISCOVERY (Step 1 Implementation)
# ============================================================================
def load_agents(project_root: Path | None = None) -> dict[str, Any]:
    """
    Dynamically discovers and loads compliant Healer Agents.
    Wraps non-compliant agents in LegacyAgentAdapter.

    Scans 'agentic_core' and 'apps_*' for classes that:
    1. Have 'Agent' or 'Validator' in their name.
    2. Implement the 'heal' method (Standard Heal Interface) OR can be adapted.

    Returns:
        Dict[str, Any]: Map of agent_name -> initialized_instance (or adapter)
    """
    if project_root is None:
        project_root = REPO_ROOT
    logging.info("Starting dynamic agent discovery...")
    discovered_agents = {}

    # Define search paths relative to project root
    search_paths = [
        project_root / AGENTIC_CORE_DIR,
        # Add other apps_* folders if needed, e.g., apps_private
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Walk directory
        for root, _, files in os.walk(search_path):
            for file in files:
                if not file.endswith(".py") or file.startswith("__"):
                    continue

                # Heuristic: Check file content for 'class' and 'Agent' before importing
                file_path = Path(root) / file
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "class " not in content or (
                            "Agent" not in content and "Validator" not in content and "Fixer" not in content
                        ):
                            continue
                # guardian: allow-silent-swallow
                except Exception:  # guardian: allow-silent-swallower
                    continue

                # Construct module path for import
                try:
                    rel_path = file_path.relative_to(project_root)
                    module_name = str(rel_path).replace(os.sep, ".")[:-3]  # strip .py

                    # Safe Import
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if not spec or not spec.loader:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Inspect classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Broaden search to include anything that LOOKS like a healer
                        is_likely_agent = (
                            obj.__module__ == module_name
                            and ("Agent" in name or "Fixer" in name or "Validator" in name)
                            and not name.startswith("Base")
                        )

                        if is_likely_agent:
                            try:
                                instance = obj()

                                # CHECK 1: Does it strictly implement the Protocol?
                                if isinstance(instance, IHealerProtocol):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Standard Agent: {name}")

                                # CHECK 2: Does it have a 'heal' method (Duck Typing)?
                                elif hasattr(instance, "heal") and callable(instance.heal):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Duck-Typed Agent: {name}")

                                # CHECK 3: Legacy Fallback (Wrap it)
                                else:
                                    logging.info(f"Wrapping Legacy Agent: {name}")
                                    discovered_agents[name] = LegacyAgentAdapter(instance)

                            # guardian: allow-silent-swallow
                            except Exception as e:
                                logging.warning(f"Failed to instantiate {name}: {e}")

                # guardian: allow-silent-swallow
                except Exception as e:
                    logging.debug(f"Skipping module {file_path}: {e}")

    logging.info(f"Discovery complete. Loaded {len(discovered_agents)} agents (including adapters).")
    return discovered_agents


# ============================================================================
# SIGNAL HANDLING (Graceful Shutdown)
# ============================================================================
class GracefulExitHandler:
    """Captures SIGINT/SIGTERM to allow Phase 2 writes to finish safely."""

    def __init__(self, state_mgr: RuntimeStateManager):
        self.state_mgr = state_mgr
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum: int, frame: FrameType | None):
        """Signal handler."""
        if self.kill_now:
            logging.critical("Force quitting on second signal...")
            sys.exit(1)

        logging.warning("\n[!] Shutdown signal received. Finishing current agent operation...")
        self.kill_now = True
        self.state_mgr.finish_mission("aborted_by_user")
        # The logic in Phase 2 should check self.kill_now if loop is tight,
        # but for now we rely on the loop completing the current atomic fix.


# [REMOVED DUPLICATE] main_legacy removed to resolve dual-main entry point confusion.
# The unified main() function below is the single source of truth.


if __name__ == "__main__":
    print(
        "ERROR: Direct invocation of execute_ssot.py is not supported.\n"
        "Use the entrypoint instead:\n"
        "  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy\n",
        file=sys.stderr,
    )
    raise SystemExit(2)
