"""Judge score variance receipt when dual panels grade the same judge_packet_hash."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

JUDGE_SCORE_VARIANCE_THRESHOLD = 0.3
RECEIPT_SCHEMA = "executive_summary_judge_score_variance_v1"


def _coerce_score(judge: dict[str, Any]) -> float | None:
    raw = judge.get("score")
    if raw is None:
        raw = judge.get("normalized_score")
        if raw is not None:
            try:
                return float(raw) * 5.0
            except (TypeError, ValueError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
                return None
    try:
        return float(raw)
    except (TypeError, ValueError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def _model_backed_judges(judges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in judges:
        if not isinstance(row, dict):
            continue
        if row.get("provider_blocked") or str(row.get("evaluator_mode") or "") != "MODEL_BACKED":
            continue
        pk = str(row.get("provider_key") or "").strip()
        if pk:
            out[pk] = row
    return out


def build_judge_score_variance_receipt(
    *,
    prior_judges: list[dict[str, Any]],
    refreshed_judges: list[dict[str, Any]],
    judge_packet_hash: str,
) -> dict[str, Any]:
    """Compare model-backed scores across two panels on the same packet hash."""
    packet_hash = str(judge_packet_hash or "").strip()
    prior_by_key = _model_backed_judges(prior_judges)
    refreshed_by_key = _model_backed_judges(refreshed_judges)
    comparisons: list[dict[str, Any]] = []
    flagged: list[str] = []

    for pk, after_row in refreshed_by_key.items():
        before_row = prior_by_key.get(pk)
        if not before_row:
            continue
        before_hash = str(
            before_row.get("judge_packet_hash") or before_row.get("input_hash") or ""
        ).strip()
        after_hash = str(
            after_row.get("judge_packet_hash") or after_row.get("input_hash") or ""
        ).strip()
        if packet_hash and before_hash and before_hash != packet_hash:
            continue
        if packet_hash and after_hash and after_hash != packet_hash:
            continue
        before_score = _coerce_score(before_row)
        after_score = _coerce_score(after_row)
        if before_score is None or after_score is None:
            continue
        delta = round(after_score - before_score, 4)
        abs_delta = round(abs(delta), 4)
        entry = {
            "provider_key": pk,
            "score_before": before_score,
            "score_after": after_score,
            "score_delta": delta,
            "abs_score_delta": abs_delta,
            "variance_flagged": abs_delta >= JUDGE_SCORE_VARIANCE_THRESHOLD,
        }
        comparisons.append(entry)
        if entry["variance_flagged"]:
            flagged.append(pk)

    return {
        "schema": RECEIPT_SCHEMA,
        "judge_packet_hash": packet_hash,
        "variance_threshold": JUDGE_SCORE_VARIANCE_THRESHOLD,
        "dual_panel": bool(prior_judges) and bool(comparisons),
        "comparisons": comparisons,
        "flagged_provider_keys": sorted(flagged),
        "any_variance_flagged": bool(flagged),
    }


def write_judge_score_variance_receipt(
    artifact_dir: Path,
    receipt: dict[str, Any],
) -> str:
    path = artifact_dir / "judge_score_variance_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, ensure_ascii=False)
    return str(path)


def emit_judge_score_variance_if_dual_panel(
    *,
    artifact_dir: Path,
    prior_judges: list[dict[str, Any]],
    refreshed_judges: list[dict[str, Any]],
    judge_packet_hash: str,
) -> dict[str, Any] | None:
    """Persist variance receipt when a second panel follows a non-empty first panel."""
    if not prior_judges:
        return None
    receipt = build_judge_score_variance_receipt(
        prior_judges=prior_judges,
        refreshed_judges=refreshed_judges,
        judge_packet_hash=judge_packet_hash,
    )
    if not receipt.get("comparisons"):
        return None
    receipt["artifact_path"] = write_judge_score_variance_receipt(artifact_dir, receipt)
    return receipt
