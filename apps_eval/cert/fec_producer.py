"""apps_eval FEC producer - judge-calibration evidence variant.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W1.P1.

Unlike grounded apps that surface retrieval sources, apps_eval grades the
output of OTHER apps' graders. Its evidence is therefore distinct: it
captures grader-calibration provenance (calibrated rubric id, active judge
versions, taxonomy match counts, self-contradiction check status). The 3
evidence_required rubric dims for apps_eval are grader_calibration,
taxonomy_correctness, no_self_contradiction.

Authority: READ-ONLY. Never mutates run_context. Returns a fresh dict.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_eval.cert.fec_producer"


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    return default


def _safe_list_str(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a FEC-shaped dict from apps_eval's run_context."""
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id"))
    if not route_id:
        rc = ctx.get("route_contract")
        if isinstance(rc, Mapping):
            route_id = _safe_str(rc.get("route_id"))

    calibrated_rubric_id = _safe_str(ctx.get("calibrated_rubric_id"))
    judge_versions = _safe_list_str(ctx.get("judge_versions"))
    taxonomy_match_count = _safe_int(ctx.get("taxonomy_match_count"))
    self_contradiction_checked = bool(ctx.get("self_contradiction_checked"))

    explicit_grounded = ctx.get("grounded")
    if isinstance(explicit_grounded, bool):
        grounded = explicit_grounded
    else:
        grounded = bool(calibrated_rubric_id and judge_versions)

    if grounded:
        sufficiency = "grounded"
    elif calibrated_rubric_id or judge_versions:
        sufficiency = "calibrated_only"
    else:
        sufficiency = "empty"

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": [],
        "template_ids": [],
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
        "judge_calibration": {
            "calibrated_rubric_id": calibrated_rubric_id,
            "judge_versions": judge_versions,
            "taxonomy_match_count": taxonomy_match_count,
            "self_contradiction_checked": self_contradiction_checked,
        },
    }


__all__ = ["produce_fec"]
