"""RLHF Optimizer - deterministic DPO-driven threshold adjustments.

Converts DPO feedback into bounded, proposal-only threshold adjustments.
"""

from __future__ import annotations

import json
from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.engines.change_package_impl import ChangePackage


class RLHFOptimizer(Protocol):
    """Protocol for RLHF optimization from DPO feedback."""

    def propose_from_dpo(
        self,
        *,
        dpo_batch_bytes: bytes,
        current_threshold_config_bytes: bytes,
        embedding_context_hash: str | None = None,
    ) -> ChangePackage:
        """Generate proposal-only threshold adjustments from DPO batch.

        Parameters:
            dpo_batch_bytes: Serialized DPOBatch artifact.
            current_threshold_config_bytes: Current threshold configuration.

        Returns:
            ChangePackage with proposal-only adjustments (no activation).
        """
        ...


class DefaultDeterministicRLHFOptimizer:
    """Default deterministic RLHF optimizer.

    Applies bounded adjustments based on APPROVE/REJECT decisions.
    """

    def __init__(
        self,
        *,
        min_threshold: float = 0.1,
        max_threshold: float = 2.0,
        approve_relax_delta: float = 0.1,
        reject_tighten_delta: float = -0.1,
    ):
        """Initialize optimizer with bounded parameters.

        Args:
            min_threshold: Minimum allowed threshold value.
            max_threshold: Maximum allowed threshold value.
            approve_relax_delta: Positive delta for APPROVE decisions.
            reject_tighten_delta: Negative delta for REJECT decisions.
        """
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.approve_relax_delta = approve_relax_delta
        self.reject_tighten_delta = reject_tighten_delta

    def propose_from_dpo(
        self,
        *,
        dpo_batch_bytes: bytes,
        current_threshold_config_bytes: bytes,
        embedding_context_hash: str | None = None,
    ) -> ChangePackage:
        """Generate deterministic threshold adjustments from DPO batch.

        Args:
            dpo_batch_bytes: Serialized DPOBatch artifact.
            current_threshold_config_bytes: Current threshold configuration.

        Returns:
            ChangePackage with proposal-only adjustments.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultDeterministicRLHFOptimizer.propose_from_dpo")

        try:
            dpo_data = json.loads(dpo_batch_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_dpo_batch",),
                timestamp_utc=0,
                embedding_context_hash=embedding_context_hash,
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )
        try:
            current_config = json.loads(current_threshold_config_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_threshold_config",),
                timestamp_utc=0,
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )
        adjustments = {}
        reasons = []
        if "pairs" in dpo_data:
            sorted_pairs = sorted(
                dpo_data["pairs"],
                key=lambda p: (
                    p.get("score", 0.0),
                    p.get("timestamp_utc", 0),
                    p["example_id"]["control_hash"],
                    p["example_id"]["candidate_hash"],
                ),
                reverse=True,
            )
            for pair in sorted_pairs:
                human_decision = pair.get("human_decision", "")
                pair_reasons = pair.get("reasons", [])
                if human_decision == "APPROVE":
                    delta = self.approve_relax_delta
                    reasons.append(f"approve_relax_{delta:.6f}")
                elif human_decision == "REJECT":
                    delta = self.reject_tighten_delta
                    reasons.append(f"reject_tighten_{delta:.6f}")
                else:
                    continue
                for key, value in current_config.items():
                    if isinstance(value, (int, float)):
                        if key not in adjustments:
                            adjustments[key] = 0.0
                        adjustments[key] += delta
                reasons.extend(pair_reasons)
        for key in adjustments:
            adjustments[key] = round(adjustments[key], 6)
        final_config = {}
        for key, value in current_config.items():
            if isinstance(value, (int, float)) and key in adjustments:
                final_config[key] = round(value + adjustments[key], 6)
                final_config[key] = max(self.min_threshold, min(self.max_threshold, final_config[key]))
            else:
                final_config[key] = value
        changes_bytes = json.dumps(final_config, separators=(",", ":"), sort_keys=True).encode("utf-8")
        num_pairs = len(dpo_data.get("pairs", []))
        confidence = min(1.0, num_pairs * 0.1)
        return ChangePackage(
            source="rlhf_optimizer",
            target="threshold_config",
            changes=changes_bytes,
            confidence=confidence,
            reason=tuple(reasons) if reasons else ("no_adjustments",),
            timestamp_utc=0,
            embedding_context_hash=embedding_context_hash,
            authority_sensitivity="MEDIUM",
            target_surface="threshold_config",
        )
