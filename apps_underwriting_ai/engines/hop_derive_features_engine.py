"""HOP3 derive_features — wraps FeatureDerivationEngine.derive_features."""

from __future__ import annotations

from typing import Any


class HopDeriveFeaturesEngine:
    """Adapter for stage 3 — risk feature derivation."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_underwriting_ai.engines.feature_derivation_engine import (
            FeatureDerivationEngine,
        )

        request = context.get("underwriting_request")
        reconciliation = context.get("reconciliation_result")
        if request is None:
            return {"risk_features": None, "feature_derivation_skipped": True}

        engine = FeatureDerivationEngine()
        features = engine.derive_features(request, reconciliation)

        return {"risk_features": features}
