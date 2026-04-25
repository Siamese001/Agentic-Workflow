"""V7 6B.S2E Eval Record Signer.

Seals an immutable ``CompletedEvalRecord`` from outcome + trajectory +
governance evals + human calibration. 6C may not consume any eval that
has not been signed here.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6B S2E "EVAL RECORD SEAL".
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Mapping

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CompletedEvalRecord:
    """Immutable, content-addressed eval record per v7 S2E."""

    eval_record_id: str
    trace_id: str
    run_id: str
    rubric_hash: str
    grader_version: str
    evidence_snapshot_hash: str
    outcome_eval_ref: str
    trajectory_eval_ref: str
    governance_eval_ref: str
    calibration_ref: str
    score_bundle: Mapping[str, float]
    uncertainty_markers: tuple[str, ...]
    reviewer_overrides: tuple[str, ...]
    signed_at: float


def _stable_hash(payload: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 hex digest for ``payload``."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class EvalRecordSigner:
    """Seal the per-run eval bundle into an immutable record."""

    def seal(
        self,
        *,
        trace_id: str,
        run_id: str,
        rubric_hash: str,
        grader_version: str,
        evidence_snapshot_hash: str,
        outcome_eval_ref: str,
        trajectory_eval_ref: str,
        governance_eval_ref: str,
        calibration_ref: str,
        score_bundle: Mapping[str, float],
        uncertainty_markers: tuple[str, ...] = (),
        reviewer_overrides: tuple[str, ...] = (),
        signed_at: float | None = None,
    ) -> CompletedEvalRecord:
        """Produce a sealed :class:`CompletedEvalRecord`.

        ``eval_record_id`` is a content-addressed hash of the full payload
        (excluding ``signed_at``), so the same inputs always produce the
        same id — necessary for replay and dedup.
        """
        ts = signed_at if signed_at is not None else time.time()
        payload = {
            "trace_id": trace_id,
            "run_id": run_id,
            "rubric_hash": rubric_hash,
            "grader_version": grader_version,
            "evidence_snapshot_hash": evidence_snapshot_hash,
            "outcome_eval_ref": outcome_eval_ref,
            "trajectory_eval_ref": trajectory_eval_ref,
            "governance_eval_ref": governance_eval_ref,
            "calibration_ref": calibration_ref,
            "score_bundle": dict(score_bundle),
            "uncertainty_markers": list(uncertainty_markers),
            "reviewer_overrides": list(reviewer_overrides),
        }
        eval_id = _stable_hash(payload)
        return CompletedEvalRecord(
            eval_record_id=eval_id,
            trace_id=trace_id,
            run_id=run_id,
            rubric_hash=rubric_hash,
            grader_version=grader_version,
            evidence_snapshot_hash=evidence_snapshot_hash,
            outcome_eval_ref=outcome_eval_ref,
            trajectory_eval_ref=trajectory_eval_ref,
            governance_eval_ref=governance_eval_ref,
            calibration_ref=calibration_ref,
            score_bundle=dict(score_bundle),
            uncertainty_markers=tuple(uncertainty_markers),
            reviewer_overrides=tuple(reviewer_overrides),
            signed_at=ts,
        )


__all__ = ["CompletedEvalRecord", "EvalRecordSigner"]
