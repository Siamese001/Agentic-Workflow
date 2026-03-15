"""
SSOT Hallucination Detection Mixin — Advisory-Only Violation Analysis.

Provides hallucination detection that:
  - Advisory only — must not mutate violation payload
  - Replay uses deterministic result (same inputs → same output)
  - Policy-hash-scoped detection context

Layer: L6 Observer
Authority: Advisory only. No mutation. No L4 writes. No routing influence.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_logger = logging.getLogger("SSOTHallucinationDetection")


class SSOTHallucinationDetectionMixin:
    """Advisory hallucination detection for healing outputs.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Detection results are advisory — they never mutate the violation payload.
    Under replay mode, results are deterministic (derived from input hash).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_detections: list[dict[str, Any]] = []

    def detect_hallucination(
        self, agent_output: str, expected_format: str | None = None, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analyze an agent output for potential hallucination.

        This is ADVISORY ONLY — the result does not mutate any payload.

        Parameters
        ----------
        agent_output : str
            The output to analyze.
        expected_format : str | None
            Expected output format description.
        context : dict | None
            Additional context for analysis.

        Returns
        -------
        dict
            Detection result with confidence and flags.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTHallucinationDetectionMixin.detect_hallucination")

        policy_hash = getattr(self, "active_policy_hash", "unknown")
        is_replay = getattr(self, "is_replay_mode", False)
        if is_replay:
            det_hash = hashlib.sha256(f"{agent_output}|{policy_hash}".encode()).hexdigest()
            confidence = int(det_hash[:8], 16) % 100 / 100.0
        else:
            confidence = self._compute_hallucination_score(agent_output, expected_format)
        result = {
            "confidence": confidence,
            "is_suspicious": confidence > 0.7,
            "policy_hash": policy_hash,
            "replay_mode": is_replay,
            "output_length": len(agent_output),
            "context": context or {},
        }
        self._ssot_detections.append(result)
        if result["is_suspicious"]:
            _logger.warning("[SSOTHallucination] Suspicious output detected (confidence=%.2f)", confidence)
        return result

    @property
    def detection_history(self) -> list[dict[str, Any]]:
        """All detection results."""
        return list(self._ssot_detections)

    @staticmethod
    def _compute_hallucination_score(output: str, expected_format: str | None) -> float:
        """Compute a basic hallucination score.

        Heuristic checks:
        - Empty output → high suspicion
        - Very short output → moderate suspicion
        - Format mismatch → elevated suspicion
        """
        if not output or not output.strip():
            return 0.95
        score = 0.1
        if len(output.strip()) < 10:
            score += 0.3
        if expected_format:
            if expected_format.lower() == "json":
                if not (output.strip().startswith("{") or output.strip().startswith("[")):
                    score += 0.4
            elif expected_format.lower() == "python":
                if "def " not in output and "class " not in output and ("import " not in output):
                    score += 0.3
        return min(score, 1.0)
