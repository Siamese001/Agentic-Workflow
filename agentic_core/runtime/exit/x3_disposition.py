"""Exit X3 Disposition Producer — AG-RGGOV-W6 Core Contract

Exit emits exactly one X3Disposition per request.

Responsibilities:
- Consume SealedL2Artifact from L2 execution
- Evaluate output against rubric
- Emit exactly one X3Disposition

Hard Constraints:
- Core owns all exit disposition
- Exactly one X3Disposition per request
- apps_rg does not emit exit dispositions
- Contract dataclass is defined in runtime/contracts/, imported here
- Exit is NOT L3 — this is a separate core surface
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition


class ExitDispositionEmitter:
    """Exit disposition layer for apps_rg tasks.

    Emits exactly one X3Disposition per request.
    """

    def emit(
        self,
        l2_artifact: SealedL2Artifact,
    ) -> X3Disposition:
        """Evaluate L2 output and emit X3Disposition.

        Args:
            l2_artifact: L2 execution output with generated content

        Returns:
            X3Disposition with final exit status
        """
        # Evaluate the output
        eval_score = self._evaluate_output(l2_artifact)
        eval_threshold_met = eval_score >= 0.7

        # Determine exit status
        exit_status = self._determine_exit_status(l2_artifact, eval_threshold_met)

        # Build final output
        final_output = self._build_final_output(l2_artifact)

        return X3Disposition(
            request_id=l2_artifact.request_id,
            run_id=l2_artifact.run_id,
            app_id=l2_artifact.app_id,
            trace_id=l2_artifact.trace_id,
            exit_status=exit_status,
            outcome_authorized=eval_threshold_met and l2_artifact.state_diff_authorized,
            final_output=final_output,
            output_artifact_path=None,  # Would be set by downstream output assembly
            eval_score=eval_score,
            eval_threshold_met=eval_threshold_met,
            hitl_required=not eval_threshold_met,  # HITL if eval fails
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            disposition_version="W6.0",
            sealed_l2_digest=l2_artifact.compilation_hash,
        )

    def _evaluate_output(self, l2_artifact: SealedL2Artifact) -> float:
        """Evaluate L2 output quality."""
        # Simple heuristic based on content length and status
        if l2_artifact.execution_status != "completed":
            return 0.0

        content_score = min(len(l2_artifact.generated_content) / 1000, 1.0)
        return 0.5 + (content_score * 0.5)  # Score between 0.5 and 1.0

    def _determine_exit_status(
        self, l2_artifact: SealedL2Artifact, threshold_met: bool
    ) -> str:
        """Determine exit status."""
        if l2_artifact.execution_status != "completed":
            return "error"
        if not threshold_met:
            return "abstain"  # Needs HITL review
        return "success"

    def _build_final_output(
        self, l2_artifact: SealedL2Artifact
    ) -> Mapping[str, Any]:
        """Build final output from L2 artifact."""
        return {
            "generated_content": l2_artifact.generated_content,
            "execution_status": l2_artifact.execution_status,
            "execution_duration_ms": l2_artifact.execution_duration_ms,
            "proposed_state_diff": dict(l2_artifact.proposed_state_diff),
        }
