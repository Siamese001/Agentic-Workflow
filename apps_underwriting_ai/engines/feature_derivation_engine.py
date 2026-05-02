"""FeatureDerivationEngine — derives risk features from request + reconciliation.

Skeleton implementation: emits a deterministic feature vector with stable
keys so downstream consumers can pattern-match. Real derivation will pull
from agentic_core feature stores and actuarial pipelines.
"""

from __future__ import annotations

from apps_underwriting_ai.types.underwriting_types import (
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)


class FeatureDerivationEngine:
    """Derives risk features from an underwriting request."""

    def derive_features(
        self,
        request: UnderwritingRequest,
        reconciliation: ReconciliationResult | None = None,
    ) -> RiskFeatures:
        """Derive a deterministic skeleton risk-feature vector.

        Args:
            request: Inbound underwriting request.
            reconciliation: Output of stage 2 (optional).

        Returns:
            RiskFeatures with a deterministic feature vector.
        """
        feature_vector: dict[str, float] = {
            "document_count": float(len(request.documents)),
            "reconciled_count": float(
                reconciliation.reconciled_count if reconciliation else 0
            ),
            "unresolved_count": float(
                reconciliation.unresolved_count if reconciliation else 0
            ),
        }
        return RiskFeatures(
            feature_vector=feature_vector,
            derived_at="",
            notes=("skeleton feature derivation",),
        )
