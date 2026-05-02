"""EnterpriseUnderwritingRenderer — full-detail rendering for ops review.

Wraps DecisionRenderer with manifest emission (run_summary JSON +
decision Markdown). Mirrors apps_rfp.outputs.enterprise_rfp_renderer.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.types.underwriting_types import UnderwritingResult


class EnterpriseUnderwritingRenderer:
    """Full-detail renderer for ops/audit consumption."""

    def __init__(self, artifact_dir: Path | str = "underwriting_artifacts/") -> None:
        self._dir = Path(artifact_dir)
        self._inner = DecisionRenderer()

    def render_to_disk(self, result: UnderwritingResult) -> dict[str, str]:
        """Render decision Markdown + run-summary JSON to disk.

        Args:
            result: UnderwritingResult to render.

        Returns:
            Dict with keys 'decision_md' and 'run_summary_json' mapping to
            the absolute paths of the emitted files.
        """
        self._dir.mkdir(parents=True, exist_ok=True)
        rid = result.request_id or "unknown"
        md_path = self._dir / f"decision_{rid}.md"
        json_path = self._dir / f"run_summary_{rid}.json"
        md_path.write_text(self._inner.to_markdown(result), encoding="utf-8")
        manifest = {
            "request_id": result.request_id,
            "verdict": result.decision.verdict.value,
            "rationale": result.decision.rationale,
            "evidence_count": len(result.register.records),
            "feature_count": len(result.features.feature_vector),
            "reconciled_count": result.reconciliation.reconciled_count,
            "unresolved_count": result.reconciliation.unresolved_count,
            "trace_id": result.trace_id,
            "gate_violations": list(result.decision.gate_violations),
        }
        json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {
            "decision_md": str(md_path),
            "run_summary_json": str(json_path),
        }
