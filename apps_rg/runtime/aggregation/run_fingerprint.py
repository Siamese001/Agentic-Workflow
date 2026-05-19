"""W1 orchestration run fingerprint from rollup + lane artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.aggregation._digest_utils import canonical_json_sorted, sha256_utf8
from apps_rg.runtime.aggregation.section_sealed_index import build_section_sealed_index
from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS

UNKNOWN = "UNKNOWN"


def _is_blocked_x3(code: str) -> bool:
    u = code.upper()
    if "BLOCK" in u and "REVIEW" not in u:
        return True
    return u.startswith("X3_BLOCK") or "BLOCKED" in u


def _is_review_x3(code: str) -> bool:
    return "REVIEW" in code.upper()


def build_orchestration_fingerprint(
    *,
    rollup_blob: dict[str, Any],
    sealed_index: dict[str, Any],
    base_resume_digest: str,
    rollup_id: str,
) -> dict[str, Any]:
    pointers = sealed_index.get("pointers") or []
    lane_run_ids: dict[str, str] = {}
    lane_artifact_digests: dict[str, str] = {}
    lane_x3_codes: dict[str, str] = {}
    lane_x2_status: dict[str, dict[str, int]] = {}
    jd_digests: set[str] = set()
    briefing_digests: set[str] = set()
    review_lanes: list[str] = []
    blocked_lanes: list[str] = []

    for ptr in pointers:
        if not isinstance(ptr, dict):
            continue
        lane = str(ptr.get("lane") or "")
        if not lane:
            continue
        lane_run_ids[lane] = str(ptr.get("run_id") or "")
        lane_artifact_digests[lane] = str(ptr.get("section_digest") or ptr.get("l2_output_digest") or "")
        code = str(ptr.get("x3_code") or "")
        lane_x3_codes[lane] = code
        lane_x2_status[lane] = {
            "x2_failed": int(ptr.get("x2_failed") or 0),
            "x2_passed": int(ptr.get("x2_passed") or 0),
        }
        jd = ptr.get("jd_digest")
        br = ptr.get("briefing_digest")
        if isinstance(jd, str) and jd.strip() and jd != UNKNOWN:
            jd_digests.add(jd)
        if isinstance(br, str) and br.strip() and br != UNKNOWN:
            briefing_digests.add(br)
        if _is_blocked_x3(code):
            blocked_lanes.append(lane)
        elif _is_review_x3(code):
            review_lanes.append(lane)

    jd_digest_coherent = UNKNOWN if not jd_digests else (next(iter(jd_digests)) if len(jd_digests) == 1 else "MISMATCH")
    briefing_digest_coherent = (
        UNKNOWN if not briefing_digests else (next(iter(briefing_digests)) if len(briefing_digests) == 1 else "MISMATCH")
    )

    run_id_set = {v for v in lane_run_ids.values() if v}
    same_run_coherent = len(run_id_set) <= 1 if run_id_set else False

    def _run_date_prefix(run_id: str) -> str:
        for part in run_id.split("_"):
            if len(part) == 8 and part.isdigit():
                return part
        return ""

    date_prefixes = {_run_date_prefix(rid) for rid in run_id_set}
    date_prefixes.discard("")
    same_date_coherent = len(date_prefixes) <= 1 if date_prefixes else False

    fingerprint_material = {
        "rollup_id": rollup_id,
        "base_resume_digest": base_resume_digest,
        "lane_run_ids": dict(sorted(lane_run_ids.items())),
        "lane_artifact_digests": dict(sorted(lane_artifact_digests.items())),
    }
    orchestration_id = sha256_utf8(canonical_json_sorted(fingerprint_material))[:32]

    return {
        "schema": "apps_rg.orchestration_run_fingerprint.v1",
        "orchestration_id": orchestration_id,
        "rollup_id": rollup_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_resume_digest": base_resume_digest,
        "jd_digest": next(iter(jd_digests)) if len(jd_digests) == 1 else (UNKNOWN if not jd_digests else "MISMATCH"),
        "briefing_digest": next(iter(briefing_digests)) if len(briefing_digests) == 1 else (UNKNOWN if not briefing_digests else "MISMATCH"),
        "jd_digest_coherent": jd_digest_coherent,
        "briefing_digest_coherent": briefing_digest_coherent,
        "lane_run_ids": lane_run_ids,
        "lane_artifact_digests": lane_artifact_digests,
        "lane_x3_codes": lane_x3_codes,
        "lane_x2_status": lane_x2_status,
        "same_run_coherent": same_run_coherent,
        "same_date_prefix_coherent": same_date_coherent,
        "review_lanes": review_lanes,
        "blocked_lanes": blocked_lanes,
        "generated_lane_ids": list(GENERATED_LANE_IDS),
    }


def build_fingerprint_from_rollup(
    *,
    repo: Path,
    rollup_blob: dict[str, Any],
    base_resume_digest: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sealed = build_section_sealed_index(
        repo=repo,
        rollup_blob=rollup_blob,
        base_resume_digest=base_resume_digest,
    )
    fp = build_orchestration_fingerprint(
        rollup_blob=rollup_blob,
        sealed_index=sealed,
        base_resume_digest=base_resume_digest,
        rollup_id=str(rollup_blob.get("rollup_id") or ""),
    )
    return fp, sealed
