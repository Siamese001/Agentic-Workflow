"""Minimal canonical claim ledger v2 for executive_summary (claim-support proof only)."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def _short_row_hash(claim_text: str, source_fact_ids: list[str]) -> str:
    payload = json.dumps(
        {"claim_text": claim_text, "ids": sorted(str(x) for x in source_fact_ids)},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:8]


def make_exec_summary_claim_id(ordinal: int, claim_text: str, source_fact_ids: list[str]) -> str:
    return f"exec_summary_claim_{ordinal}_{_short_row_hash(claim_text, source_fact_ids)}"


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
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    for i, row in enumerate(normalized_rows, start=1):
        ct = str(row.get("claim_text") or "")
        ids = list(row.get("source_fact_ids") or [])
        claims.append(
            {
                "claim_id": make_exec_summary_claim_id(i, ct, ids),
                "claim_text": ct,
                "source_fact_ids": ids,
            }
        )
    return {
        "schema": "canonical_claim_ledger_v2",
        "claims": claims,
        "refs": {
            "selected_fact_plan_path": "selected_fact_plan.json",
            "text_claim_coverage_path": "text_claim_coverage.json",
        },
    }


def canonical_claim_ledger_hash_sha16(claims: list[dict[str, Any]]) -> str:
    """SHA-256[:16] over canonical claims (X3 / receipts)."""
    blob = json.dumps(claims, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
