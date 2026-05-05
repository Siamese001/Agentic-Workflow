"""QnA Exit FEC Producer — produces FinalEvidenceContract for Exit v6.

W1.2: Registry scaffold. Wraps the existing cert/fec_producer.py with
spine-aware evidence contract production for the live interview path.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.2
"""

from __future__ import annotations

from typing import Any

from apps_qna.cert.fec_producer import produce_fec


def produce_exit_fec(run_context: dict[str, Any]) -> dict[str, Any]:
    """Produce a FinalEvidenceContract for the Exit v6 pipeline.

    Delegates to the existing cert FEC producer, enriched with
    live interview runtime context.

    Args:
        run_context: The runtime context from the spine pipeline.

    Returns:
        A FinalEvidenceContract-shaped dict.
    """
    fec = produce_fec(run_context)

    fec.setdefault("route_id", run_context.get("route_id", ""))
    fec.setdefault("interview_slug", run_context.get("interview_slug", ""))

    return fec


__all__ = ["produce_exit_fec"]
