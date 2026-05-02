"""HOP6 validation — factual + structural checks on the draft message.

Produces a ``validation_report`` dict with ``passed`` (bool) and
``issues`` (list). The gate_decision stage (HOP7) consumes this report.

Scaffold implementation — deeper checks (cross-reference against evidence
bundle, numeric consistency, compliance-keyword scan) land in a follow-up
plan that adds real domain logic.
"""

from __future__ import annotations

from typing import Any


class ValidationEngine:
    """Lightweight structural + evidence-coverage validation."""

    MIN_BODY_LENGTH = 20
    MAX_BODY_LENGTH = 4000

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        draft = context.get("draft_message") or {}
        evidence = context.get("evidence_bundle") or {}

        issues: list[str] = []
        body = str(draft.get("body", ""))

        if len(body) < self.MIN_BODY_LENGTH:
            issues.append(f"body_too_short (<{self.MIN_BODY_LENGTH} chars)")
        if len(body) > self.MAX_BODY_LENGTH:
            issues.append(f"body_too_long (>{self.MAX_BODY_LENGTH} chars)")
        if not body.strip():
            issues.append("empty_body")

        evidence_count = int(evidence.get("count", 0))
        # Non-fatal advisory when evidence bundle is empty — generation was
        # allowed to run, but qa_report will reflect the ungrounded state.
        grounded = evidence_count > 0

        return {
            "validation_report": {
                "passed": len(issues) == 0,
                "issues": issues,
                "grounded": grounded,
                "evidence_count": evidence_count,
                "body_length": len(body),
            },
        }
