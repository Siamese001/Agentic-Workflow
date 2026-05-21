"""W8 — strict post-Exit ingestion eligibility for R1B ROLE_TARGET_RUN records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_compatibility import CompatibilityVerdict, assess_intent_record_admissibility
from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
    NON_ADMISSIBLE_RUNTIME_STATUSES,
    X3_FINISH_ALLOWED,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk

POST_EXIT_INGESTION_PHASE = "post_exit_only"
REQUIRED_EXIT_ARTIFACT = "x3_disposition.json"


@dataclass(frozen=True)
class PostExitExitMetadata:
    """Exit-cleared metadata required before any R1B durable file write."""

    exit_artifact_present: bool
    x3_disposition: str
    proof_eligible: bool | None
    runtime_generation_status: str
    proceed_to_runtime: bool | None
    exit_pass: bool | None
    source_run_id: str
    run_dir: str = ""

    @property
    def exit_metadata_present(self) -> bool:
        return self.exit_artifact_present and bool(str(self.x3_disposition or "").strip())


@dataclass
class PostExitIngestionVerdict:
    admissible: bool
    non_admissible_reason: str
    checks: dict[str, bool] = field(default_factory=dict)
    exit_metadata: PostExitExitMetadata | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "admissible": self.admissible,
            "cache_admissible": self.admissible,
            "non_admissible_reason": self.non_admissible_reason,
            "checks": dict(self.checks),
            "ingestion_phase": POST_EXIT_INGESTION_PHASE,
            "exit_metadata_present": bool(self.exit_metadata and self.exit_metadata.exit_metadata_present),
        }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return raw if isinstance(raw, dict) else None


def _tri_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("true", "1", "yes"):
        return True
    if text in ("false", "0", "no"):
        return False
    return None


def load_post_exit_metadata(run_dir: Path) -> PostExitExitMetadata:
    """Load Exit disposition from completed run artifacts (fail-closed when missing)."""
    manifest = _read_json(run_dir / "run_manifest.json") or {}
    x3_doc = _read_json(run_dir / REQUIRED_EXIT_ARTIFACT) or {}
    x3_code = str(x3_doc.get("x3_code") or x3_doc.get("disposition") or "").strip().upper()
    proof = _tri_bool(x3_doc.get("proof_eligible"))
    if proof is None:
        proof = _tri_bool(manifest.get("proof_eligible"))
    runtime = str(
        x3_doc.get("runtime_generation_status")
        or manifest.get("runtime_generation_status")
        or ""
    ).strip()
    return PostExitExitMetadata(
        exit_artifact_present=(run_dir / REQUIRED_EXIT_ARTIFACT).is_file(),
        x3_disposition=x3_code,
        proof_eligible=proof,
        runtime_generation_status=runtime,
        proceed_to_runtime=_tri_bool(x3_doc.get("proceed_to_runtime")),
        exit_pass=_tri_bool(x3_doc.get("pass")),
        source_run_id=str(manifest.get("run_id") or run_dir.name),
        run_dir=str(run_dir),
    )


def assess_post_exit_ingestion_eligibility(
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    *,
    exit_meta: PostExitExitMetadata,
) -> PostExitIngestionVerdict:
    """Fail-closed gate: only Exit-cleared, proof-eligible, non-mock runs may be cache_admissible."""
    checks: dict[str, bool] = {}

    checks["post_exit_phase_only"] = True
    checks["exit_metadata_present"] = exit_meta.exit_metadata_present
    checks["exit_artifact_on_disk"] = exit_meta.exit_artifact_present
    checks["role_target_run_grain"] = record.cache_grain == CACHE_GRAIN_ROLE_TARGET_RUN

    x3 = str(record.x3_disposition or exit_meta.x3_disposition or "").strip().upper()
    checks["x3_disposition_present"] = bool(x3)
    checks["x3_allows_finish"] = x3 in X3_FINISH_ALLOWED
    if exit_meta.proceed_to_runtime is False:
        checks["exit_proceed_to_runtime"] = False
    else:
        checks["exit_proceed_to_runtime"] = True

    if exit_meta.proof_eligible is None:
        checks["proof_eligible_explicit"] = False
        checks["proof_eligible"] = False
    else:
        checks["proof_eligible_explicit"] = True
        checks["proof_eligible"] = bool(exit_meta.proof_eligible) and bool(record.proof_eligible)

    runtime = str(exit_meta.runtime_generation_status or "").strip()
    if not runtime:
        checks["runtime_status_present"] = False
        checks["not_mock_runtime"] = False
    else:
        checks["runtime_status_present"] = True
        checks["not_mock_runtime"] = runtime not in NON_ADMISSIBLE_RUNTIME_STATUSES

    from apps_rg.cache.r1b_semantic_chunk_builder import (
        INGEST_PROFILE_INTEGRATED_WHOLE_RUN,
        detect_ingest_profile,
    )

    manifest_path = Path(exit_meta.run_dir) / "run_manifest.json"
    manifest = _read_json(manifest_path) or {}
    ingest_profile = detect_ingest_profile(Path(exit_meta.run_dir), manifest)
    require_final_resume = ingest_profile == INGEST_PROFILE_INTEGRATED_WHOLE_RUN

    base = assess_intent_record_admissibility(
        record,
        chunks=chunks,
        runtime_generation_status=runtime,
        require_final_resume=require_final_resume,
    )
    checks.update(base.checks)
    checks["chunks_not_independent_lookup_identities"] = all(
        not ch.to_dict().get("independent_cache_identity", True) for ch in chunks
    )
    checks["no_c0_fact_vector_chunks"] = all(
        "fact_vectors" not in str(ch.chunk_type or "").lower() for ch in chunks
    )

    failed = [k for k, v in checks.items() if not v]
    if not exit_meta.exit_metadata_present:
        reason = "missing_exit_x3_disposition"
    elif failed:
        reason = "; ".join(failed)
    else:
        reason = ""

    return PostExitIngestionVerdict(
        admissible=not failed and exit_meta.exit_metadata_present,
        non_admissible_reason=reason,
        checks=checks,
        exit_metadata=exit_meta,
    )


def apply_post_exit_verdict_to_record(
    record: HistoricalIntentRecord,
    verdict: PostExitIngestionVerdict,
) -> HistoricalIntentRecord:
    from dataclasses import replace

    return replace(
        record,
        cache_admissible=verdict.admissible,
        non_admissible_reason="" if verdict.admissible else verdict.non_admissible_reason,
    )


__all__ = [
    "POST_EXIT_INGESTION_PHASE",
    "REQUIRED_EXIT_ARTIFACT",
    "PostExitExitMetadata",
    "PostExitIngestionVerdict",
    "_tri_bool",
    "apply_post_exit_verdict_to_record",
    "assess_post_exit_ingestion_eligibility",
    "load_post_exit_metadata",
]
