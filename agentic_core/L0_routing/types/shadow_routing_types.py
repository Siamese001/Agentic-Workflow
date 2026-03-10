"""
Phase 9: Shadow Router Types - Non-invasive routing drift detection.

Types for shadow routing decisions that observe L0 routing without affecting
live traffic. All shadow outputs are read-only side-channels.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _get_canonical_json():
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import canonical_json as _cj

    return _cj


canonical_json = _get_canonical_json()


class ShadowRoutingRationale(str, Enum):
    """Shadow routing rationale - independent of live routing rationale."""

    ALIGN_WITH_LIVE = "align_with_live"
    ALTERNATE_PATH_SUGGESTED = "alternate_path_suggested"
    RISK_MITIGATION = "risk_mitigation"
    POLICY_OPTIMIZATION = "policy_optimization"
    FEATURE_DRIFT_DETECTED = "feature_drift_detected"


@dataclass(frozen=True)
class ShadowRoutingDecision:
    """Non-invasive shadow routing decision with drift detection.

    This artifact is produced after the actual routing decision is made
    and cannot affect the live route. It serves as a side-channel for
    detecting routing drift and providing shadow suggestions.
    """

    # Core identification
    trace_id: str

    # Routing comparison
    observed_route: RoutePath  # Actual route chosen by L0
    shadow_route: RoutePath  # Suggested route by shadow classifier

    # Drift metrics
    drift_score: float  # 0.0 = identical, 1.0 = maximum drift

    # Feature fingerprinting (deterministic)
    feature_fingerprint: str  # 64-hex canonical hash of routing features

    # Deterministic timestamp (semantic clock, not wall-clock)
    timestamp: str  # Deterministic, not used in hash inputs

    # Shadow rationale (independent of live routing)
    shadow_rationale: ShadowRoutingRationale

    # Version tracking
    model_version: str = "shadow-router-v1.0"
    ruleset_version: str = "phase9-initial"

    # Optional semantic clock snapshot
    semantic_clock: SemanticClockSnapshot | None = None

    # Feature snapshot (for debugging, not used in hashing)
    feature_snapshot: dict[str, Any] | None = field(default=None, repr=False)

    def compute_canonical_fingerprint(self, features: dict[str, Any]) -> str:
        """Compute deterministic 64-hex fingerprint from routing features.

        Args:
            features: Dictionary of routing features used for classification

        Returns:
            64-character lowercase hex SHA256 digest
        """
        # Use canonical JSON to ensure deterministic serialization
        canonical_features = canonical_json(features)
        return hashlib.sha256(canonical_features.encode("utf-8")).hexdigest()

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for hashing/storage.

        Returns:
            Canonical JSON string representation
        """
        # Create a dict with only hash-relevant fields
        canonical_dict = {
            "trace_id": self.trace_id,
            "observed_route": self.observed_route.value,
            "shadow_route": self.shadow_route.value,
            "drift_score": self.drift_score,
            "feature_fingerprint": self.feature_fingerprint,
            "model_version": self.model_version,
            "ruleset_version": self.ruleset_version,
            "shadow_rationale": self.shadow_rationale.value,
        }

        # Include semantic clock if present
        if self.semantic_clock is not None:
            canonical_dict["semantic_clock"] = self.semantic_clock.to_dict()

        return canonical_json(canonical_dict)


@dataclass(frozen=True)
class ShadowRoutingTelemetry:
    """Telemetry artifact for shadow routing observations.

    Emitted to L6 observability bus and optionally stored in L4.
    """

    trace_id: str
    shadow_decision: ShadowRoutingDecision
    emitted_at: str  # Deterministic timestamp

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for storage/transmission."""
        return canonical_json(
            {
                "trace_id": self.trace_id,
                "shadow_decision": json.loads(self.shadow_decision.to_canonical_json()),
                "emitted_at": self.emitted_at,
            }
        )
