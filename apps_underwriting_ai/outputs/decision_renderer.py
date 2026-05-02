"""DecisionRenderer — renders DecisionPacket to text/JSON formats."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    UnderwritingResult,
)


class DecisionRenderer:
    """Renders underwriting decisions to text/JSON output formats."""

    def to_json(self, result: UnderwritingResult, *, indent: int = 2) -> str:
        """Render the result as JSON.

        Args:
            result: UnderwritingResult to render.
            indent: JSON indent level.

        Returns:
            JSON string.
        """
        payload = self._to_dict(result)
        return json.dumps(payload, indent=indent, default=str)

    def to_markdown(self, result: UnderwritingResult) -> str:
        """Render the result as Markdown."""
        d = result.decision
        evidence_lines = (
            [f"- {ref}" for ref in d.evidence_refs]
            if d.evidence_refs
            else ["- _none_"]
        )
        feature_lines = (
            [f"- `{k}`: {v}" for k, v in sorted(d.feature_summary.items())]
            if d.feature_summary
            else ["- _none_"]
        )
        lines = [
            f"# Underwriting Decision — {result.request_id}",
            "",
            f"**Verdict:** {d.verdict.value}",
            f"**Rationale:** {d.rationale}",
            "",
            "## Evidence",
            *evidence_lines,
            "",
            "## Feature Summary",
            *feature_lines,
            "",
            "## Reconciliation",
            f"- reconciled: {result.reconciliation.reconciled_count}",
            f"- unresolved: {result.reconciliation.unresolved_count}",
            "",
            f"**Trace ID:** `{result.trace_id or 'n/a'}`",
        ]
        return "\n".join(lines) + "\n"

    def _to_dict(self, result: UnderwritingResult) -> dict[str, Any]:
        d = result.decision
        return {
            "request_id": result.request_id,
            "decision": {
                "verdict": d.verdict.value,
                "rationale": d.rationale,
                "evidence_refs": list(d.evidence_refs),
                "feature_summary": dict(d.feature_summary),
                "gate_violations": list(d.gate_violations),
            },
            "register": {
                "request_id": result.register.request_id,
                "record_count": len(result.register.records),
            },
            "features": {
                "feature_vector": dict(result.features.feature_vector),
            },
            "reconciliation": asdict(result.reconciliation),
            "trace_id": result.trace_id,
        }
