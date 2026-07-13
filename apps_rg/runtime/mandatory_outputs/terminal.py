"""Terminal-state projection for mandatory-output closeout.

Mandatory reporting is post-boundary.  It may block pipeline completion and
request observability repair, but it may not revoke a product authorization
already closed by Exit -> UWG.
"""

from __future__ import annotations

from typing import Any, Mapping


def apply_mandatory_closeout_state(
    document: Mapping[str, Any],
    gate: Mapping[str, Any],
    *,
    failure_code: str,
) -> dict[str, Any]:
    result = dict(document)
    summary = dict(result.get("result_summary") or {})
    upstream_fault = str(summary.get("fault") or "")
    upstream_completion_fault = str(summary.get("completion_fault") or "")
    gate_passed = gate.get("pass") is True
    product_authorized = bool(
        summary.get("product_authorized", summary.get("outcome_authorized", False))
    )
    summary["product_authorized"] = product_authorized
    summary["outcome_authorized"] = product_authorized
    final_pipeline_complete = bool(
        gate_passed and summary.get("pipeline_complete") is True
    )
    summary["pipeline_complete"] = final_pipeline_complete
    summary["observability_repair_required"] = bool(
        product_authorized and not final_pipeline_complete
    )
    if not gate_passed:
        summary["completion_status"] = "BLOCKED"
        summary["completion_fault"] = failure_code
        summary["mandatory_output_upstream_fault"] = upstream_fault
        summary["mandatory_output_upstream_completion_fault"] = upstream_completion_fault
    result["result_summary"] = summary
    result["mandatory_output_hard_stop"] = dict(gate)
    return result


__all__ = ["apply_mandatory_closeout_state"]
