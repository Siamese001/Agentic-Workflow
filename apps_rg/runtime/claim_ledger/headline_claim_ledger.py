"""Headline-specific claim ledger and text–claim coverage (not executive-summary sentence split)."""
from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    canonical_claim_ledger_hash_sha16,
    normalize_exec_summary_claim_ledger,
    normalize_exec_summary_claim_row,
)

_HEADLINE_SEP = " | "


def normalize_headline_claim_ledger(rows: list[Any]) -> list[dict[str, Any]]:
    return normalize_exec_summary_claim_ledger(rows)


def build_headline_canonical_claim_ledger_v2(
    normalized_rows: list[dict[str, Any]],
    *,
    parse_status: str,
    invalid_reason: str | None = None,
    source_artifact_refs: list[str] | None = None,
) -> dict[str, Any]:
    return build_canonical_claim_ledger_v2_payload(
        normalized_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason,
        source_artifact_refs=source_artifact_refs,
        claim_id_prefix="headline_claim",
    )


def _headline_positioning_segments(headline_line: str) -> tuple[str, str, str] | None:
    hl = (headline_line or "").strip()
    if hl.count(_HEADLINE_SEP) != 3 or not hl.startswith("SVP Engineering | "):
        return None
    parts = [p.strip() for p in hl.split(_HEADLINE_SEP)]
    if len(parts) != 4 or not all(parts) or parts[0] != "SVP Engineering":
        return None
    return parts[1], parts[2], parts[3]


def build_headline_text_claim_coverage(
    headline_line: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Map each X/Y/Z positioning segment to supporting claim_ledger rows (headline seam)."""
    segments = _headline_positioning_segments(headline_line)
    coverage_rows: list[dict[str, Any]] = []
    overall_pass = True

    if not segments:
        return {
            "schema": "headline_text_claim_coverage_v1",
            "overall_pass": False,
            "segments": [],
            "failure_reason": "headline_line_not_four_segment_pipe_shape",
        }

    for idx, segment in enumerate(segments, start=2):
        seg_lower = segment.lower()
        matching: list[dict[str, Any]] = []
        for claim in claim_ledger:
            if not isinstance(claim, dict):
                continue
            claim_text = str(claim.get("claim_text") or "").strip()
            if not claim_text:
                continue
            ct_lower = claim_text.lower()
            if ct_lower == seg_lower:
                matching.append(claim)
                continue
            claim_tokens = [t for t in re.findall(r"[A-Za-z0-9]+", ct_lower) if len(t) > 3]
            seg_tokens = [t for t in re.findall(r"[A-Za-z0-9]+", seg_lower) if len(t) > 3]
            overlap = len(set(claim_tokens) & set(seg_tokens))
            need = max(1, min(2, len(claim_tokens), len(seg_tokens) or 1))
            if claim_tokens and seg_tokens and overlap >= need:
                matching.append(claim)

        row_pass = bool(matching)
        if not row_pass:
            overall_pass = False
        source_ids: set[str] = set()
        for m in matching:
            for fid in m.get("source_fact_ids") or []:
                base = str(fid).split("_metric_")[0]
                if base in allowed_fact_ids or str(fid) in allowed_fact_ids:
                    source_ids.add(str(fid))
        coverage_rows.append(
            {
                "segment_index": idx,
                "segment_text": segment,
                "pass": row_pass,
                "matching_claim_count": len(matching),
                "source_fact_ids": sorted(source_ids),
            }
        )

    return {
        "schema": "headline_text_claim_coverage_v1",
        "overall_pass": overall_pass,
        "segments": coverage_rows,
    }


__all__ = [
    "build_headline_canonical_claim_ledger_v2",
    "build_headline_text_claim_coverage",
    "canonical_claim_ledger_hash_sha16",
    "normalize_headline_claim_ledger",
    "normalize_exec_summary_claim_row",
]
