"""Minimal canonical claim ledger v2 for executive_summary (claim-support proof only)."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


_REF_BLOCK = {
    "selected_fact_plan_path": "selected_fact_plan.json",
    "text_claim_coverage_path": "text_claim_coverage.json",
}


def _short_row_hash(claim_text: str, source_fact_ids: list[str]) -> str:
    payload = json.dumps(
        {"claim_text": claim_text, "ids": sorted(str(x) for x in source_fact_ids)},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:8]


def make_lane_claim_id(prefix: str, ordinal: int, claim_text: str, source_fact_ids: list[str]) -> str:
    return f"{prefix}_{ordinal}_{_short_row_hash(claim_text, source_fact_ids)}"


def make_exec_summary_claim_id(ordinal: int, claim_text: str, source_fact_ids: list[str]) -> str:
    return make_lane_claim_id("exec_summary_claim", ordinal, claim_text, source_fact_ids)


def normalize_exec_summary_claim_row(row: Any) -> dict[str, Any]:
    """Map provider drift: claim_text wins; else claim -> claim_text. Preserve source_fact_ids list."""
    if not isinstance(row, dict):
        return {"claim_text": "", "source_fact_ids": []}
    text = str(row.get("claim_text") or "").strip()
    if not text and row.get("claim") is not None:
        text = str(row.get("claim") or "").strip()
    raw_ids = row.get("source_fact_ids")
    if raw_ids is None:
        ids: list[str] = []
    elif isinstance(raw_ids, list):
        ids = [str(x) for x in raw_ids]
    else:
        ids = [str(raw_ids)]
    return {"claim_text": text, "source_fact_ids": ids}


def normalize_exec_summary_claim_ledger(rows: list[Any]) -> list[dict[str, Any]]:
    return [normalize_exec_summary_claim_row(r) for r in rows]


def build_canonical_claim_ledger_v2_document(
    normalized_rows: list[dict[str, Any]],
    *,
    claim_id_prefix: str = "exec_summary_claim",
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    for i, row in enumerate(normalized_rows, start=1):
        ct = str(row.get("claim_text") or "")
        ids = list(row.get("source_fact_ids") or [])
        claims.append(
            {
                "claim_id": make_lane_claim_id(claim_id_prefix, i, ct, ids),
                "claim_text": ct,
                "source_fact_ids": ids,
            }
        )
    return {
        "schema": "canonical_claim_ledger_v2",
        "claims": claims,
        "refs": dict(_REF_BLOCK),
    }


def classify_ledger_parse_state(
    parsed: dict[str, Any] | None,
    *,
    parse_error: str,
    raw_output: str,
    lane_profile: str = "executive_summary",
) -> tuple[str, str]:
    """Return (parse_status, invalid_reason) for canonical_claim_ledger_v2 envelope."""
    if parsed is not None:
        if lane_profile in ("unify_bullets", "ibm_bullets"):
            bl = parsed.get("bullets")
            if not isinstance(bl, list):
                return "SCHEMA_INVALID", "bullets must be an array for bullets lane output"
            if "claim_ledger" not in parsed:
                return "SCHEMA_INVALID", "claim_ledger key is required for bullets lane output"
            cl_ub = parsed.get("claim_ledger")
            if not isinstance(cl_ub, list):
                return "SCHEMA_INVALID", "claim_ledger must be an array for bullets lane output"
            sfp_ub = parsed.get("selected_fact_plan")
            if sfp_ub is not None and not isinstance(sfp_ub, dict):
                return "SCHEMA_INVALID", "selected_fact_plan must be an object or omitted"
            return "OK", ""

        if lane_profile in ("unify_narrative", "ibm_narrative"):
            ns = parsed.get("narrative_sentence")
            if ns is not None and not isinstance(ns, str):
                return "SCHEMA_INVALID", "narrative_sentence must be a string when present"
            cl_n = parsed.get("claim_ledger")
            if cl_n is not None and not isinstance(cl_n, list):
                return "SCHEMA_INVALID", "claim_ledger must be a list or omitted"
            sfp_n = parsed.get("selected_fact_plan")
            if sfp_n is not None and not isinstance(sfp_n, dict):
                return "SCHEMA_INVALID", "selected_fact_plan must be an object or omitted"
            return "OK", ""

        if lane_profile == "headline":
            hl = parsed.get("headline_line")
            if hl is not None and not isinstance(hl, str):
                return "SCHEMA_INVALID", "headline_line must be a string when present"
            cl_h = parsed.get("claim_ledger")
            if cl_h is not None and not isinstance(cl_h, list):
                return "SCHEMA_INVALID", "claim_ledger must be a list or omitted"
            sfp_h = parsed.get("selected_fact_plan")
            if sfp_h is not None and not isinstance(sfp_h, dict):
                return "SCHEMA_INVALID", "selected_fact_plan must be an object or omitted"
            return "OK", ""

        if lane_profile in ("competencies", "professional_competencies"):
            comps = parsed.get("competencies")
            if comps is not None and not isinstance(comps, list):
                return "SCHEMA_INVALID", "competencies must be an array when present"
            cl_c = parsed.get("claim_ledger")
            if cl_c is not None and not isinstance(cl_c, list):
                return "SCHEMA_INVALID", "claim_ledger must be a list or omitted"
            sfp_c = parsed.get("selected_fact_plan")
            if sfp_c is not None and not isinstance(sfp_c, dict):
                return "SCHEMA_INVALID", "selected_fact_plan must be an object or omitted"
            return "OK", ""

        if not isinstance(parsed.get("resume_display_text"), str):
            return "SCHEMA_INVALID", "resume_display_text must be a string when present"
        cl = parsed.get("claim_ledger")
        if cl is not None and not isinstance(cl, list):
            return "SCHEMA_INVALID", "claim_ledger must be a list or omitted"
        sfp = parsed.get("selected_fact_plan")
        if sfp is not None and not isinstance(sfp, dict):
            return "SCHEMA_INVALID", "selected_fact_plan must be an object or omitted"
        return "OK", ""

    err = (parse_error or "").strip() or "parse failed"
    err_l = err.lower()
    text = raw_output.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    truncated_hint = (
        not text.endswith("}")
        or "unterminated string" in err_l
        or ("expecting" in err_l and "delimiter" in err_l)
        or "expecting value" in err_l
    )
    if truncated_hint:
        return "TRUNCATED_JSON", err
    return "INVALID_JSON", err


def build_canonical_claim_ledger_v2_payload(
    normalized_rows: list[dict[str, Any]],
    *,
    parse_status: str,
    invalid_reason: str | None = None,
    source_artifact_refs: list[str] | None = None,
    claim_id_prefix: str = "exec_summary_claim",
) -> dict[str, Any]:
    """Build on-disk canonical_claim_ledger_v2.json body (OK + degraded paths).

    Non-OK statuses use empty ``claims[]`` per section-pipeline contract.
    """
    if parse_status == "OK":
        doc = build_canonical_claim_ledger_v2_document(
            normalized_rows,
            claim_id_prefix=claim_id_prefix,
        )
        doc["parse_status"] = "OK"
        return doc
    return {
        "schema": "canonical_claim_ledger_v2",
        "claims": [],
        "parse_status": parse_status,
        "invalid_reason": invalid_reason or "",
        "source_artifact_refs": list(source_artifact_refs or ("provider_response.json",)),
        "refs": dict(_REF_BLOCK),
    }


def canonical_claim_ledger_hash_sha16(claims: list[dict[str, Any]]) -> str:
    """SHA-256[:16] over canonical claims (X3 / receipts)."""
    blob = json.dumps(claims, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
