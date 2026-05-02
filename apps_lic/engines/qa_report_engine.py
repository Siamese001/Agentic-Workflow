"""HOP8 qa_report — scorecard + compliance annotations.

Consumes the draft, validation report, and evidence bundle; emits a
``qa_report`` dict with a composite quality score and per-dimension
breakdown. The integration stage (HOP9) folds this into the final
``GovernedLicE2ERunRecord``.
"""

from __future__ import annotations

from typing import Any


class QaReportEngine:
    """Composite scorecard over validation + evidence coverage."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        draft = context.get("draft_message") or {}
        report = context.get("validation_report") or {}
        evidence = context.get("evidence_bundle") or {}

        validation_score = 1.0 if report.get("passed") else 0.4
        grounding_score = 1.0 if evidence.get("count", 0) >= 3 else 0.5 if evidence.get("count", 0) > 0 else 0.0
        structural_score = 0.0 if report.get("issues") else 1.0

        composite = round(
            0.4 * validation_score + 0.3 * grounding_score + 0.3 * structural_score,
            3,
        )

        return {
            "qa_report": {
                "composite_score": composite,
                "validation_score": validation_score,
                "grounding_score": grounding_score,
                "structural_score": structural_score,
                "generator": draft.get("generator", "unknown"),
                "evidence_count": int(evidence.get("count", 0)),
                "issues": list(report.get("issues") or []),
            },
        }
