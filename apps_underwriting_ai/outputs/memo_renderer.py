"""
Memo Renderer - Renders decision memo as markdown.
"""

from ..types import DecisionMemo


class MemoRenderer:
    """Renders DecisionMemo as formatted markdown."""

    def render(self, memo: DecisionMemo) -> str:
        """Render memo as markdown string."""
        sections = [
            self._render_header(memo),
            self._render_summary(memo),
            self._render_strengths(memo),
            self._render_risks(memo),
            self._render_conditions(memo),
            self._render_covenants(memo),
            self._render_exceptions(memo),
            self._render_missing(memo),
            self._render_evidence(memo),
            self._render_footer(memo),
        ]

        return "\n\n".join(sections)

    def _render_header(self, memo: DecisionMemo) -> str:
        """Render memo header."""
        decision_emoji = {
            "APPROVE": "✅",
            "APPROVE_WITH_CONDITIONS": "✅",
            "COUNTER_OFFER": "🔄",
            "PEND_FOR_INFORMATION": "⏳",
            "DECLINE": "❌",
            "ESCALATE_TO_HUMAN": "👤",
        }.get(memo.recommended_decision, "❓")

        return f"""# Underwriting Decision Memo

**Request ID:** {memo.request_id}
**Decision:** {decision_emoji} {memo.recommended_decision}
**Confidence:** {memo.confidence_score:.0%}

---
"""

    def _render_summary(self, memo: DecisionMemo) -> str:
        """Render summary section."""
        lines = ["## Summary", ""]

        if memo.recommended_amount:
            lines.append(f"**Recommended Amount:** ${memo.recommended_amount:,.0f}")
        if memo.recommended_term_months:
            lines.append(f"**Recommended Term:** {memo.recommended_term_months} months")
        if memo.pricing_adjustment_bps:
            lines.append(f"**Pricing Adjustment:** +{memo.pricing_adjustment_bps} bps")

        return "\n".join(lines)

    def _render_strengths(self, memo: DecisionMemo) -> str:
        """Render strengths section."""
        if not memo.key_strengths:
            return ""

        lines = ["", "## Key Credit Strengths", ""]
        for strength in memo.key_strengths:
            lines.append(f"- {strength}")

        return "\n".join(lines)

    def _render_risks(self, memo: DecisionMemo) -> str:
        """Render risks section."""
        if not memo.key_risks:
            return ""

        lines = ["", "## Key Credit Risks", ""]
        for risk in memo.key_risks:
            lines.append(f"- {risk}")

        return "\n".join(lines)

    def _render_conditions(self, memo: DecisionMemo) -> str:
        """Render conditions section."""
        if not memo.conditions_precedent:
            return ""

        lines = ["", "## Conditions Precedent", ""]
        for i, condition in enumerate(memo.conditions_precedent, 1):
            lines.append(f"{i}. {condition}")

        return "\n".join(lines)

    def _render_covenants(self, memo: DecisionMemo) -> str:
        """Render covenants section."""
        if not memo.covenants:
            return ""

        lines = ["", "## Ongoing Covenants", ""]
        for i, covenant in enumerate(memo.covenants, 1):
            lines.append(f"{i}. {covenant}")

        return "\n".join(lines)

    def _render_exceptions(self, memo: DecisionMemo) -> str:
        """Render exceptions section."""
        if not memo.policy_exceptions:
            return ""

        lines = ["", "## Policy Exceptions", ""]
        lines.append("The following policy exceptions are noted:")
        lines.append("")
        for exception in memo.policy_exceptions:
            lines.append(f"- ⚠️ {exception}")

        return "\n".join(lines)

    def _render_missing(self, memo: DecisionMemo) -> str:
        """Render missing information section."""
        if not memo.missing_information:
            return ""

        lines = ["", "## Missing Information", ""]
        lines.append("The following information is required to complete this assessment:")
        lines.append("")
        for item in memo.missing_information:
            lines.append(f"- ❓ {item}")

        return "\n".join(lines)

    def _render_evidence(self, memo: DecisionMemo) -> str:
        """Render evidence register section."""
        if not memo.evidence_register:
            return ""

        lines = ["", "## Evidence Register", ""]
        lines.append("| Claim | Evidence Type | Source | Confidence |")
        lines.append("|-------|---------------|--------|------------|")

        for evidence in memo.evidence_register:
            lines.append(
                f"| {evidence.claim_text[:50]}{'...' if len(evidence.claim_text) > 50 else ''} | "
                f"{evidence.evidence_type} | "
                f"{evidence.source_ref} | "
                f"{evidence.confidence:.0%} |",
            )

        return "\n".join(lines)

    def _render_footer(self, memo: DecisionMemo) -> str:
        """Render memo footer."""
        if memo.human_review_reason:
            return f"""

---

**⚠️ Human Review Required:** {memo.human_review_reason}
"""
        return ""
