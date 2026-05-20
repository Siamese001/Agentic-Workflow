"""Whole-run R1A/R1B cache preflight evidence for generation-spine gating."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

CACHE_MISS_RECEIPT_NAME = "whole_run_cache_preflight_miss.json"
CACHE_HIT_RECEIPT_NAME = "whole_run_cache_preflight_hit.json"
CACHE_PREFLIGHT_MANIFEST_NAME = "whole_run_cache_preflight.json"


def _r1a_status(preflight: WholeRunCachePreflightOutcome) -> str:
    if preflight.r1a_hit:
        return "hit"
    return "miss"


def _r1b_status(preflight: WholeRunCachePreflightOutcome) -> str:
    if preflight.r1b_hit:
        return "hit"
    if preflight.r1b_result is None:
        return "skipped"
    outcome = str(preflight.r1b_result.outcome or "")
    if outcome == "r1b_inadmissible_only":
        return "inadmissible_only"
    return "miss"


def build_cache_preflight_evidence(
    preflight: WholeRunCachePreflightOutcome,
    *,
    artifact_dir: Path | None = None,
) -> dict[str, Any]:
    """Shape evidence dict for spine composer and product-proof gate."""
    cache_result = preflight.outcome
    generation_allowed = bool(preflight.generation_required)
    blocked_reason = ""
    if not generation_allowed:
        if preflight.r1a_hit:
            blocked_reason = "r1a_cache_hit"
        elif preflight.r1b_hit:
            blocked_reason = "r1b_cache_hit"
        else:
            blocked_reason = "cache_hit"

    miss_ref = ""
    if artifact_dir is not None and generation_allowed:
        miss_ref = f"artifact://{CACHE_MISS_RECEIPT_NAME}"

    return {
        "cache_preflight_completed": True,
        "r1a_preflight_status": _r1a_status(preflight),
        "r1b_preflight_status": _r1b_status(preflight),
        "cache_result": cache_result,
        "cache_miss_receipt_ref": miss_ref,
        "generation_spine_invocation_allowed": generation_allowed,
        "generation_spine_invocation_blocked_reason": blocked_reason,
        "route_family": "R4_SINGLE_ACTION",
        "whole_run_cache_preflight": preflight.to_dict(),
    }


def write_whole_run_cache_preflight_artifact(
    artifact_dir: Path,
    preflight: WholeRunCachePreflightOutcome,
    evidence: dict[str, Any],
) -> Path:
    """Persist SSOT preflight + evidence fields under the run artifact dir."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = {**evidence, "preflight": preflight.to_dict()}
    path = artifact_dir / CACHE_PREFLIGHT_MANIFEST_NAME
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_cache_miss_receipt(
    artifact_dir: Path,
    preflight: WholeRunCachePreflightOutcome,
    evidence: dict[str, Any],
) -> Path:
    """Write miss receipt when generation spine is invoked (cache miss path)."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / CACHE_MISS_RECEIPT_NAME
    path.write_text(
        json.dumps(
            {
                "cache_result": preflight.outcome,
                "generation_required": True,
                "evidence": evidence,
                "preflight": preflight.to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    evidence["cache_miss_receipt_ref"] = f"artifact://{CACHE_MISS_RECEIPT_NAME}"
    return path


def write_cache_hit_receipt(
    artifact_dir: Path,
    preflight: WholeRunCachePreflightOutcome,
    evidence: dict[str, Any],
) -> Path:
    """Write hit receipt when generation spine must not run."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / CACHE_HIT_RECEIPT_NAME
    path.write_text(
        json.dumps(
            {
                "cache_result": preflight.outcome,
                "generation_required": False,
                "evidence": evidence,
                "preflight": preflight.to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


__all__ = [
    "CACHE_HIT_RECEIPT_NAME",
    "CACHE_MISS_RECEIPT_NAME",
    "CACHE_PREFLIGHT_MANIFEST_NAME",
    "build_cache_preflight_evidence",
    "write_cache_hit_receipt",
    "write_cache_miss_receipt",
    "write_whole_run_cache_preflight_artifact",
]
