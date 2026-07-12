"""R1B semantic cache adapter with X3C and transactional L4 enforcement."""

from __future__ import annotations

import math
import os
import uuid
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_commit_authority import (
    assess_r1b_commit_authority_from_run_dir,
)
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
from apps_rg.cache.r1b_strict_gateway import get_r1b_strict_gateway
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
        value = int(float(raw))
    except (TypeError, ValueError):
        return default
    return default if value < 0 else value


def _get_similarity_threshold() -> float:
    return _clamp01(
        _parse_float("SEMANTIC_CACHE_THRESHOLD", DEFAULT_SIMILARITY_THRESHOLD)
    )


def _get_cache_ttl_seconds() -> int:
    return _parse_int_positive(
        "SEMANTIC_CACHE_TTL_SECONDS", DEFAULT_CACHE_TTL_SECONDS
    )


def _store_root_for_runs_dir(runs_dir: str | Path | None) -> Path:
    return Path(runs_dir).resolve() if runs_dir else default_store_root().resolve()


def _fixture_mirror_enabled_for_tests(*, explicit_private_flag: bool) -> bool:
    enabled = os.environ.get(
        "APPS_RG_R1B_ALLOW_FIXTURE_FALLBACK_FOR_TESTS", ""
    ).strip().lower() in {"1", "true", "yes", "on"}
    return bool(explicit_private_flag and enabled)


def check_r1b_for_apps_rg(
    *,
    raw_request: dict[str, Any] | None = None,
    runs_dir: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any] | None:
    """Read only the admitted derived projection; fixture mirrors are not truth."""

    if raw_request is None:
        return None
    if os.environ.get("APPS_RG_R1B_DISABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        return None
    return check_r1b_whole_run_preflight(
        raw_request=raw_request,
        runs_dir=runs_dir,
        similarity_threshold=float(
            kwargs.get("similarity_threshold") or _get_similarity_threshold()
        ),
        prompt_profile_hash=str(kwargs.get("prompt_profile_hash") or ""),
        gate_profile_hash=str(kwargs.get("gate_profile_hash") or ""),
    )


class AppsRgR1BCacheAdapter:
    """Post-Exit R1B adapter; product writes use transactional UWG only."""

    durable_write_status = DURABLE_WRITE_VIA_UWG

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
            similarity_threshold
            if similarity_threshold is not None
            else _get_similarity_threshold()
        )
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else _get_cache_ttl_seconds()
        )
        self._store_root = _store_root_for_runs_dir(runs_dir)

    def _fixture_store(self) -> R1BSemanticCacheStore:
        return R1BSemanticCacheStore(self._store_root)

    def store_intent_and_output(
        self,
        *,
        intent: dict[str, Any] | Any,
        chunks: list[dict[str, Any]],
        run_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str | None:
        """Commit and project only when the run carries literal X3C authority."""

        write_fixture_mirror = _fixture_mirror_enabled_for_tests(
            explicit_private_flag=bool(
                kwargs.pop("_write_fixture_mirror_for_tests", False)
            )
        )
        ctx = dict(run_context or {})
        if not bool(ctx.get("post_exit_ingestion")):
            return None
        raw_request = (
            dict(intent)
            if isinstance(intent, dict)
            else intent.to_cache_key_dict()
            if hasattr(intent, "to_cache_key_dict")
            else {}
        )
        record_id = str(ctx.get("record_id") or f"hir_{uuid.uuid4().hex[:16]}")
        ctx["record_id"] = record_id
        metadata = {
            "prompt_profile_hash": str(
                ctx.get("policy_hash") or ctx.get("prompt_profile_hash") or ""
            ),
            "gate_profile_hash": str(
                ctx.get("blueprint_hash") or ctx.get("gate_profile_hash") or ""
            ),
            "runtime_generation_status": str(
                ctx.get("runtime_generation_status") or ""
            ),
            "x3_disposition": str(
                ctx.get("exit_disposition") or ctx.get("x3_disposition") or ""
            ),
            "proof_eligible": ctx.get("proof_eligible"),
        }
        child_chunks = chunks_from_output_list(
            parent_intent_record_id=record_id,
            output_chunks=chunks,
        )
        record = build_intent_record_complete(
            raw_request=raw_request,
            run_context=ctx,
            metadata=metadata,
            chunks=child_chunks,
        )
        run_dir_value = ctx.get("artifact_dir") or ctx.get("run_dir")
        run_dir = Path(str(run_dir_value)).resolve() if run_dir_value else None
        if run_dir is not None:
            exit_meta = load_post_exit_metadata(run_dir)
        else:
            exit_meta = PostExitExitMetadata(
                exit_artifact_present=bool(metadata["x3_disposition"]),
                x3_disposition=metadata["x3_disposition"],
                proof_eligible=_tri_bool(metadata["proof_eligible"]),
                runtime_generation_status=metadata["runtime_generation_status"],
                proceed_to_runtime=None,
                exit_pass=None,
                source_run_id=str(ctx.get("run_id") or record_id),
            )
        verdict = assess_post_exit_ingestion_eligibility(
            record, child_chunks, exit_meta=exit_meta
        )
        record = apply_post_exit_verdict_to_record(record, verdict)

        if run_dir is not None and (run_dir / "x3_disposition.json").is_file():
            authority = assess_r1b_commit_authority_from_run_dir(run_dir)
            if not authority.authorized or not record.cache_admissible:
                return None
            assessment = {
                **verdict.to_dict(),
                "record": record.to_dict(),
                "chunks": [row.to_dict() for row in child_chunks],
                "exit_metadata": {
                    "source_run_id": exit_meta.source_run_id,
                    "x3_disposition": exit_meta.x3_disposition,
                    "proof_eligible": exit_meta.proof_eligible,
                    "x3_commit_authorized": True,
                    "x3_commit_authority_reason": "",
                },
            }
            from apps_rg.cache.r1b_transactional_promotion import (
                promote_r1b_transactionally,
            )
            from apps_rg.cache.r1b_uwg_promotion import (
                build_r1b_promotion_candidate,
            )

            candidate = build_r1b_promotion_candidate(
                record=record,
                chunks=child_chunks,
                post_exit_eligibility=assessment,
                run_dir=run_dir,
                tenant_id=self.tenant_id,
            )
            result = promote_r1b_transactionally(
                candidate=candidate,
                projection_root=self._store_root,
                artifact_dir=run_dir,
                section_id=str(ctx.get("section_id") or "integrated_whole_run"),
                run_id=str(ctx.get("run_id") or exit_meta.source_run_id),
                raw_request=raw_request,
                gateway=get_r1b_strict_gateway(),
            )
            if not result.complete:
                return None
            if write_fixture_mirror:
                store = self._fixture_store()
                store.write_intent(record)
                for row in child_chunks:
                    store.write_chunk(row)
            return record.record_id

        if not write_fixture_mirror:
            return None
        store = self._fixture_store()
        store.write_intent(record)
        if not record.cache_admissible:
            return None
        for row in child_chunks:
            store.write_chunk(row)
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
