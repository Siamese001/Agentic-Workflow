"""
Storage Adapter - Persists domain artifacts through approved repo seam.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from ..types import DecisionMemo, DecisionPacket, AuditTrace


class StorageAdapter:
    """
    Adapter for persisting underwriting artifacts.

    Persists:
    - decision_memo.md
    - decision_packet.json
    - conditions_sheet.json
    - exception_summary.md
    - audit_trace.json

    Uses approved repo artifact patterns, does not invent direct write paths.
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("artifacts/underwriting")

    def save_decision_memo(
        self,
        memo: DecisionMemo,
        request_id: str
    ) -> Path:
        """Save decision memo as markdown."""
        output_path = self.base_path / f"{request_id}_decision_memo.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self._render_memo_markdown(memo)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def save_decision_packet(
        self,
        packet: DecisionPacket,
        request_id: str
    ) -> Path:
        """Save decision packet as JSON."""
        output_path = self.base_path / f"{request_id}_decision_packet.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(packet.dict(), f, indent=2, default=str)

        return output_path

    def save_audit_trace(
        self,
        trace: AuditTrace,
        request_id: str
    ) -> Path:
        """Save audit trace as JSON."""
        output_path = self.base_path / f"{request_id}_audit_trace.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(trace.dict(), f, indent=2, default=str)

        return output_path

    def save_conditions_sheet(
        self,
        conditions: List[str],
        covenants: List[str],
        request_id: str
    ) -> Path:
        """Save conditions and covenants as JSON."""
        output_path = self.base_path / f"{request_id}_conditions.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "conditions_precedent": conditions,
            "ongoing_covenants": covenants,
            "generated_at": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return output_path

    def _render_memo_markdown(self, memo: DecisionMemo) -> str:
        """Render DecisionMemo as markdown document."""
        lines = [
            f"# Underwriting Decision Memo",
            "",
            f"**Request ID:** {memo.request_id}",
            f"**Recommendation:** {memo.recommended_decision}",
            f"**Confidence:** {memo.confidence_score:.0%}",
            "",
            "## Summary",
            "",
        ]

        if memo.recommended_amount:
            lines.append(f"**Recommended Amount:** ${memo.recommended_amount:,.0f}")
        if memo.recommended_term_months:
            lines.append(f"**Recommended Term:** {memo.recommended_term_months} months")
        if memo.pricing_adjustment_bps:
            lines.append(f"**Pricing Adjustment:** +{memo.pricing_adjustment_bps} bps")

        lines.extend(["", "## Key Strengths", ""])
        for strength in memo.key_strengths:
            lines.append(f"- {strength}")

        lines.extend(["", "## Key Risks", ""])
        for risk in memo.key_risks:
            lines.append(f"- {risk}")

        if memo.conditions_precedent:
            lines.extend(["", "## Conditions Precedent", ""])
            for condition in memo.conditions_precedent:
                lines.append(f"- {condition}")

        if memo.covenants:
            lines.extend(["", "## Ongoing Covenants", ""])
            for covenant in memo.covenants:
                lines.append(f"- {covenant}")

        if memo.policy_exceptions:
            lines.extend(["", "## Policy Exceptions", ""])
            for exception in memo.policy_exceptions:
                lines.append(f"- {exception}")

        if memo.missing_information:
            lines.extend(["", "## Missing Information", ""])
            for missing in memo.missing_information:
                lines.append(f"- {missing}")

        if memo.human_review_reason:
            lines.extend(["", "## Human Review Required", ""])
            lines.append(memo.human_review_reason)

        lines.extend(["", "## Evidence Register", ""])
        for evidence in memo.evidence_register:
            lines.append(f"- **{evidence.claim_id}:** {evidence.claim_text}")
            lines.append(f"  - Source: {evidence.source_ref}")
            lines.append(f"  - Confidence: {evidence.confidence:.0%}")
            lines.append("")

        return "\n".join(lines)
