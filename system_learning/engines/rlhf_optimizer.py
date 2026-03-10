"""RLHF Optimizer - deterministic DPO-driven threshold adjustments.

Converts DPO feedback into bounded, proposal-only threshold adjustments.
"""

from __future__ import annotations

import json
from typing import Protocol

from system_learning.engines.change_package_impl import ChangePackage


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        # Parse DPO batch
        try:
            dpo_data = json.loads(dpo_batch_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Return empty proposal for malformed DPO batch
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_dpo_batch",),
                timestamp_utc=0,  # Will be set by caller
                embedding_context_hash=embedding_context_hash,
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )

        # Parse current threshold config
        try:
            current_config = json.loads(current_threshold_config_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Return empty proposal for malformed config
            return ChangePackage(
                source="rlhf_optimizer",
                target="threshold_config",
                changes=b"{}",
                confidence=0.0,
                reason=("malformed_threshold_config",),
                timestamp_utc=0,  # Will be set by caller
                authority_sensitivity="MEDIUM",
                target_surface="threshold_config",
            )

        # Process DPO pairs in deterministic order
        adjustments = {}
        reasons = []

        if "pairs" in dpo_data:
            # Sort pairs by control_hash, then candidate_hash for determinism
            # Stable sort by score (desc), timestamp (asc), and then hashes
            sorted_pairs = sorted(
                dpo_data["pairs"],
                key=lambda p: (
                    p.get("score", 0.0),
                    p.get("timestamp_utc", 0),
                    p["example_id"]["control_hash"],
                    p["example_id"]["candidate_hash"],
                ),
                reverse=True,  # Sort by score descending
            )

            for pair in sorted_pairs:
                human_decision = pair.get("human_decision", "")
                pair_reasons = pair.get("reasons", [])

                # Apply deterministic adjustment based on decision
                if human_decision == "APPROVE":
                    delta = self.approve_relax_delta
                    reasons.append(f"approve_relax_{delta:.6f}")
                elif human_decision == "REJECT":
                    delta = self.reject_tighten_delta
                    reasons.append(f"reject_tighten_{delta:.6f}")
                else:
                    continue  # Skip invalid decisions

                # Apply delta to all threshold values (simplified approach)
                for key, value in current_config.items():
                    if isinstance(value, (int, float)):
                        # Initialize accumulator if needed
                        if key not in adjustments:
                            adjustments[key] = 0.0

                        # Apply delta
                        adjustments[key] += delta

                # Add pair-specific reasons
                reasons.extend(pair_reasons)

        # Round all adjustments to 6 decimal places for determinism
        for key in adjustments:
            adjustments[key] = round(adjustments[key], 6)

        # Create final adjusted config
        final_config = {}
        for key, value in current_config.items():
            if isinstance(value, (int, float)) and key in adjustments:
                final_config[key] = round(value + adjustments[key], 6)
                # Final clamp
                final_config[key] = max(self.min_threshold, min(self.max_threshold, final_config[key]))
            else:
                final_config[key] = value

        # Create proposal
        changes_bytes = json.dumps(final_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Calculate confidence based on number of pairs processed
        num_pairs = len(dpo_data.get("pairs", []))
        confidence = min(1.0, num_pairs * 0.1)  # Simple confidence model

        return ChangePackage(
            source="rlhf_optimizer",
            target="threshold_config",
            changes=changes_bytes,
            confidence=confidence,
            reason=tuple(reasons) if reasons else ("no_adjustments",),
            timestamp_utc=0,  # Will be set by caller
            embedding_context_hash=embedding_context_hash,
            authority_sensitivity="MEDIUM",
            target_surface="threshold_config",
        )
