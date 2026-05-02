"""HOP4 collect_evidence — wraps EvidenceRegisterEngine.collect_* methods."""

from __future__ import annotations

from typing import Any


class HopCollectEvidenceEngine:
    """Adapter for stage 4 — evidence collection across financial, credit,
    collateral, relationship, and policy dimensions.
    """

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_underwriting_ai.engines.evidence_register_engine import (
            EvidenceRegisterEngine,
        )

        request = context.get("underwriting_request")
        register = context.get("evidence_register")
        features = context.get("risk_features")
        if request is None or register is None:
            return {"evidence_collected": False, "evidence_skipped": True}

        engine = EvidenceRegisterEngine()
        engine.collect_financial_evidence(register, request)
        engine.collect_credit_evidence(register, request)
        engine.collect_collateral_evidence(register, request)
        engine.collect_relationship_evidence(register, request)
        if features is not None and hasattr(features, "policy"):
            engine.collect_policy_evidence(
                register,
                request,
                getattr(features.policy, "policy_exception_count", 0),
            )

        return {
            "evidence_collected": True,
            "evidence_register": register,
        }
