"""Executive-summary judge certification helpers.

These helpers keep executive_summary-specific proof rules out of generic X3
dispatch code. A generic ``X3_REVIEW_JUDGE_SOFT_FAIL`` may remain a review
surface for other lanes, but executive_summary publish/certification requires
all required model-backed judges to pass.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXECUTIVE_SUMMARY_SECTION_ID = "executive_summary"
EXECUTIVE_SUMMARY_JUDGE_REVIEW_X3 = "X3_REVIEW_JUDGE_SOFT_FAIL"

_NON_CERTIFIED_PUBLISH_DISPOSITIONS = frozenset(
    {
        "best_effort",
        "judge_certification_required",
    }
)


def executive_summary_x3_requires_failure(x3_doc: dict[str, Any]) -> bool:
    """Return true when an executive-summary X3 mirror is not judge-certified."""
    pub = str(x3_doc.get("publish_disposition") or "").strip()
    if pub in _NON_CERTIFIED_PUBLISH_DISPOSITIONS:
        return True
    if pub and pub != "certified":
        return True
    blocking = x3_doc.get("blocking_judge_ids") or []
    if isinstance(blocking, list) and blocking:
        return True
    if x3_doc.get("x1d_certified") is False and (
        pub
        or "judge_certified" in x3_doc
        or "proof_eligible_allow_requires" in x3_doc
    ):
        return True
    if x3_doc.get("judge_certified") is False and pub:
        return True
    return False


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-silent-swallow -- optional artifact probe
        return {}
    return doc if isinstance(doc, dict) else {}


def executive_summary_certification_block(run_root: Path) -> dict[str, Any]:
    """Inspect a whole-run artifact root for non-certified executive summary output."""
    lane_dir = Path(run_root) / "lanes" / EXECUTIVE_SUMMARY_SECTION_ID
    if not lane_dir.is_dir():
        return {"blocked": False}

    x3_doc = _read_json(lane_dir / "x3_disposition.json")
    publish_doc = _read_json(lane_dir / "publish_disposition.json")
    merged = dict(x3_doc)
    merged.update(publish_doc)

    if not executive_summary_x3_requires_failure(merged):
        return {"blocked": False}

    blocking = merged.get("blocking_judge_ids") or []
    return {
        "blocked": True,
        "section_id": EXECUTIVE_SUMMARY_SECTION_ID,
        "x3_disposition": EXECUTIVE_SUMMARY_JUDGE_REVIEW_X3,
        "original_x3_disposition": str(merged.get("x3_code") or ""),
        "publish_disposition": str(merged.get("publish_disposition") or ""),
        "x1d_certified": bool(merged.get("x1d_certified")),
        "blocking_judge_ids": list(blocking) if isinstance(blocking, list) else [],
        "reason": "executive_summary_required_judge_not_certified",
    }


__all__ = [
    "EXECUTIVE_SUMMARY_JUDGE_REVIEW_X3",
    "EXECUTIVE_SUMMARY_SECTION_ID",
    "executive_summary_certification_block",
    "executive_summary_x3_requires_failure",
]
