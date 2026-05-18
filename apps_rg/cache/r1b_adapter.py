"""R1B semantic cache — ROLE_TARGET_RUN grain (HistoricalIntentRecord + child chunks)."""

from __future__ import annotations

import math
import os
import uuid
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_SIMILARITY_THRESHOLD,
    DURABLE_WRITE_VIA_UWG,
    R1B_NOT_C0_FACT_VECTORS,
)
from apps_rg.cache.r1b_ingest import build_intent_record_complete, chunks_from_output_list
from apps_rg.cache.r1b_post_exit_eligibility import (
    PostExitExitMetadata,
    _tri_bool,
    apply_post_exit_verdict_to_record,
    assess_post_exit_ingestion_eligibility,
    load_post_exit_metadata,
)
from apps_rg.cache.r1b_whole_run_preflight import check_r1b_whole_run_preflight
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root

def _clamp01(value: float) -> float:
    if math.isnan(value):
        return DEFAULT_SIMILARITY_THRESHOLD
    return max(0.0, min(1.0, value))


def _parse_float(env_name: str, default: float) -> float:
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _parse_int_positive(env_name: str, default: int) -> int:
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    try:
        iv = int(float(raw))
    except (TypeError, ValueError):
        return default
    if iv < 0:
        return default
    return iv


def _get_similarity_threshold() -> float:
    return _clamp01(_parse_float("SEMANTIC_CACHE_THRESHOLD", DEFAULT_SIMILARITY_THRESHOLD))


def _get_cache_ttl_seconds() -> int:
    return _parse_int_positive("SEMANTIC_CACHE_TTL_SECONDS", DEFAULT_CACHE_TTL_SECONDS)


def _store_for_runs_dir(runs_dir: str | Path | None) -> R1BSemanticCacheStore:
    if runs_dir:
        return R1BSemanticCacheStore(Path(runs_dir))
    return R1BSemanticCacheStore(default_store_root())


def check_r1b_for_apps_rg(
    *,
    raw_request: dict[str, Any] | None = None,
    runs_dir: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any] | None:
    """Lookup prior ROLE_TARGET_RUN by HistoricalIntentRecord vector (not C0 fact_vectors)."""
    if raw_request is None:
        return None
    if os.environ.get("APPS_RG_R1B_DISABLED", "").strip().lower() in ("1", "true", "yes"):
        return None
    threshold = float(kwargs.get("similarity_threshold") or _get_similarity_threshold())
    store = _store_for_runs_dir(runs_dir)
    return check_r1b_whole_run_preflight(
        raw_request=raw_request,
        runs_dir=runs_dir,
        similarity_threshold=threshold,
        prompt_profile_hash=str(kwargs.get("prompt_profile_hash") or ""),
        gate_profile_hash=str(kwargs.get("gate_profile_hash") or ""),
    )


class AppsRgR1BCacheAdapter:
    """Post-Exit R1B ingest adapter — durable writes via UWG; file store is fixture mirror."""

    durable_write_status: str = DURABLE_WRITE_VIA_UWG

    def __init__(
        self,
        *,
        runs_dir: str | None = None,
        tenant_id: str | None = None,
        similarity_threshold: float | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        self.runs_dir = runs_dir
        self.tenant_id = tenant_id or "default"
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else _get_similarity_threshold()
        )
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else _get_cache_ttl_seconds()
        self._store = _store_for_runs_dir(runs_dir)

    def store_intent_and_output(
        self,
        *,
        intent: dict[str, Any] | Any,
        chunks: list[dict[str, Any]],
        run_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str | None:
        """Write HistoricalIntentRecord + child chunks only after post-Exit eligibility passes."""
        del kwargs
        ctx = run_context or {}
        if not bool(ctx.get("post_exit_ingestion")):
            return None
        if isinstance(intent, dict):
            raw_request = intent
        elif hasattr(intent, "to_cache_key_dict"):
            raw_request = intent.to_cache_key_dict()  # type: ignore[union-attr]
        else:
            raw_request = {}
        record_id = str(ctx.get("record_id") or f"hir_{uuid.uuid4().hex[:16]}")
        ctx = {**ctx, "record_id": record_id}
        meta = {
            "prompt_profile_hash": str(ctx.get("policy_hash") or ctx.get("prompt_profile_hash") or ""),
            "gate_profile_hash": str(ctx.get("blueprint_hash") or ctx.get("gate_profile_hash") or ""),
            "runtime_generation_status": str(ctx.get("runtime_generation_status") or ""),
            "x3_disposition": str(ctx.get("exit_disposition") or ctx.get("x3_disposition") or ""),
            "proof_eligible": ctx.get("proof_eligible"),
        }
        child_chunks = chunks_from_output_list(
            parent_intent_record_id=record_id,
            output_chunks=chunks,
        )
        record = build_intent_record_complete(
            raw_request=raw_request,
            run_context=ctx,
            metadata=meta,
            chunks=child_chunks,
        )
        run_dir = ctx.get("artifact_dir") or ctx.get("run_dir")
        if run_dir:
            exit_meta = load_post_exit_metadata(Path(str(run_dir)))
        else:
            exit_meta = PostExitExitMetadata(
                exit_artifact_present=bool(str(meta.get("x3_disposition") or "").strip()),
                x3_disposition=str(meta.get("x3_disposition") or ""),
                proof_eligible=_tri_bool(meta.get("proof_eligible")),
                runtime_generation_status=str(meta.get("runtime_generation_status") or ""),
                proceed_to_runtime=None,
                exit_pass=None,
                source_run_id=str(ctx.get("run_id") or record_id),
            )
        verdict = assess_post_exit_ingestion_eligibility(record, child_chunks, exit_meta=exit_meta)
        record = apply_post_exit_verdict_to_record(record, verdict)
        run_dir_path = Path(str(run_dir)) if run_dir else None
        if (
            bool(ctx.get("post_exit_ingestion"))
            and run_dir_path
            and (run_dir_path / "x3_disposition.json").is_file()
        ):
            from apps_rg.cache.r1b_uwg_gateway_shim import default_r1b_promotion_gateway
            from apps_rg.cache.r1b_uwg_promotion import (
                build_r1b_promotion_candidate,
                promote_and_project_r1b_cache,
            )

            assessment = {
                **verdict.to_dict(),
                "record": record.to_dict(),
                "chunks": [c.to_dict() for c in child_chunks],
                "exit_metadata": {
                    "source_run_id": exit_meta.source_run_id,
                    "x3_disposition": exit_meta.x3_disposition,
                    "proof_eligible": exit_meta.proof_eligible,
                },
            }
            candidate = build_r1b_promotion_candidate(
                record=record,
                chunks=child_chunks,
                post_exit_eligibility=assessment,
                run_dir=run_dir_path,
            )
            outcome = promote_and_project_r1b_cache(
                candidate=candidate,
                projection_root=self._store.root,
                fixture_store=self._store,
                gateway=default_r1b_promotion_gateway(),
                mirror_fixture_on_blocked=True,
            )
            if outcome.status == "ADMITTED" or outcome.fixture_mirror_written:
                return record.record_id
            return None

        self._store.write_intent(record)
        if not record.cache_admissible:
            return None
        for ch in child_chunks:
            self._store.write_chunk(ch)
        return record.record_id


__all__ = [
    "DEFAULT_CACHE_TTL_SECONDS",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "R1B_NOT_C0_FACT_VECTORS",
    "_get_cache_ttl_seconds",
    "_get_similarity_threshold",
    "AppsRgR1BCacheAdapter",
    "check_r1b_for_apps_rg",
]
