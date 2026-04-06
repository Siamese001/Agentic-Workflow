"""
Exception Renderer - Renders exception summary as markdown.
"""

from ..reasoning.exception_summarizer import ExceptionSummary


class ExceptionRenderer:
    """Renders exception and escalation summary."""

    def render(self, summary: ExceptionSummary) -> str:
        """Render exception summary as markdown."""
        if not summary.has_exceptions and not summary.escalation_required:
            return ""

        lines = [
            "# Exception Summary",
            "",
        ]

        # Exception details
        if summary.exception_details:
            lines.extend(
                [
                    "## Policy Exceptions",
                    "",
                ],
            )
            for detail in summary.exception_details:
                severity = detail.get("severity", "moderate")
                emoji = "🔴" if severity == "high" else "🟡" if severity == "moderate" else "🟢"
                lines.append(f"{emoji} **{detail['type']}**: {detail['description']}")

                mitigants = detail.get("mitigants", [])
                if mitigants:
                    lines.append(f"   - Mitigants: {', '.join(mitigants)}")
                lines.append("")

        # Escalation reasons
        if summary.escalation_reasons:
            lines.extend(
                [
                    "",
                    "## Escalation Required",
                    "",
                    "This request requires human review due to:",
                    "",
                ],
            )
            for reason in summary.escalation_reasons:
                lines.append(f"- ⚠️ {reason}")

        # Recommended approver
        if summary.recommended_approver:
            lines.extend(
                [
                    "",
                    f"**Recommended Approval Authority:** {summary.recommended_approver}",
                ],
            )

        return "\n".join(lines)
