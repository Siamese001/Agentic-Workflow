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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def _get_canonical_json():
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import canonical_json as _cj
    return _cj
canonical_json = _get_canonical_json()

class ShadowRoutingRationale(str, Enum):
    """Shadow routing rationale - independent of live routing rationale."""
    ALIGN_WITH_LIVE = 'align_with_live'
    ALTERNATE_PATH_SUGGESTED = 'alternate_path_suggested'
    RISK_MITIGATION = 'risk_mitigation'
    POLICY_OPTIMIZATION = 'policy_optimization'
    FEATURE_DRIFT_DETECTED = 'feature_drift_detected'

@dataclass(frozen=True)
class ShadowRoutingDecision:
    """Non-invasive shadow routing decision with drift detection.

    This artifact is produced after the actual routing decision is made
    and cannot affect the live route. It serves as a side-channel for
    detecting routing drift and providing shadow suggestions.
    """
    trace_id: str
    observed_route: RoutePath
    shadow_route: RoutePath
    drift_score: float
    feature_fingerprint: str
    timestamp: str
    shadow_rationale: ShadowRoutingRationale
    model_version: str = 'shadow-router-v1.0'
    ruleset_version: str = 'phase9-initial'
    semantic_clock: SemanticClockSnapshot | None = None
    feature_snapshot: dict[str, Any] | None = field(default=None, repr=False)

    def compute_canonical_fingerprint(self, features: dict[str, Any]) -> str:
        """Compute deterministic 64-hex fingerprint from routing features.

        Args:
            features: Dictionary of routing features used for classification

        Returns:
            64-character lowercase hex SHA256 digest
        """
        canonical_features = canonical_json(features)
        return hashlib.sha256(canonical_features.encode('utf-8')).hexdigest()

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for hashing/storage.

        Returns:
            Canonical JSON string representation
        """
        canonical_dict = {'trace_id': self.trace_id, 'observed_route': self.observed_route.value, 'shadow_route': self.shadow_route.value, 'drift_score': self.drift_score, 'feature_fingerprint': self.feature_fingerprint, 'model_version': self.model_version, 'ruleset_version': self.ruleset_version, 'shadow_rationale': self.shadow_rationale.value}
        if self.semantic_clock is not None:
            canonical_dict['semantic_clock'] = self.semantic_clock.to_dict()
        return canonical_json(canonical_dict)

@dataclass(frozen=True)
class ShadowRoutingTelemetry:
    """Telemetry artifact for shadow routing observations.

    Emitted to L6 observability bus and optionally stored in L4.
    """
    trace_id: str
    shadow_decision: ShadowRoutingDecision
    emitted_at: str

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for storage/transmission."""
        return canonical_json({'trace_id': self.trace_id, 'shadow_decision': json.loads(self.shadow_decision.to_canonical_json()), 'emitted_at': self.emitted_at})
