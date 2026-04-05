"""
Validation Report Renderer — Renders validation results.

SVP Standards:
- Deterministic output
- Full evidence capture
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_lic.types import ValidationResult

_log = logging.getLogger(__name__)


class ValidationReportRenderer:
    """Renderer for validation reports."""

    def render_json(self, result: ValidationResult) -> str:
        """Render validation as formatted JSON."""
        return json.dumps(
            {
                "passed": result.passed,
                "reasons": list(result.reasons),
                "attempts": result.attempts,
                "qa_result": result.qa_result,
            },
            indent=2,
            default=str,
        )

    def render_markdown(self, result: ValidationResult) -> str:
        """Render validation as Markdown report."""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        lines = [
            "# Validation Report",
            "",
            f"**Status:** {status}",
            f"**Attempts:** {result.attempts}",
            "",
        ]

        if result.reasons:
            lines.extend(["## Issues", ""])
            for reason in result.reasons:
                lines.append(f"- {reason}")
            lines.append("")

        if result.qa_result:
            lines.extend(
                [
                    "## QA Result",
                    "",
                    f"```json\n{json.dumps(result.qa_result, indent=2, default=str)}\n```",
                    "",
                ]
            )

        return "\n".join(lines)

    def render_compact(self, result: ValidationResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "passed": result.passed,
            "issues_count": len(result.reasons),
            "attempts": result.attempts,
        }
