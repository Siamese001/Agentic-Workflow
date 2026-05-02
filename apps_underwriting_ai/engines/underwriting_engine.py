"""UnderwritingEngine — primary imperative entrypoint.

Walks the 5-stage HOP pipeline imperatively, aggregating outputs into a
single :class:`UnderwritingResult`. Mirrors the pattern used by
``apps_rfp.engines.rfp_engine`` and similar pipeline-style apps.

The shared-substrate alternative (``UnderwritingHopOrchestrator``) walks
the same 5 stages declaratively via ``HopPipelineExecutor``; both are
supported and produce equivalent results.
"""

from __future__ import annotations

from typing import Any

from apps_underwriting_ai.engines.decision_packet_assembler import (
    DecisionPacketAssembler,
)
from apps_underwriting_ai.engines.document_reconciliation_engine import (
    DocumentReconciliationEngine,
)
from apps_underwriting_ai.engines.evidence_register_engine import (
    EvidenceRegisterEngine,
)
from apps_underwriting_ai.engines.feature_derivation_engine import (
    FeatureDerivationEngine,
)
from apps_underwriting_ai.types.underwriting_types import (
    UnderwritingRequest,
    UnderwritingResult,
)


class UnderwritingEngine:
    """Imperative driver for the 5-stage underwriting pipeline.

    Invokes each backing engine in order, threading state through the
    pipeline. Equivalent to driving the same stage registry declaratively
    via :class:`UnderwritingHopOrchestrator`.
    """

    def run(
        self,
        request: UnderwritingRequest,
        *,
        trace_id: str = "",
        **_: Any,
    ) -> UnderwritingResult:
        """Execute the underwriting pipeline imperatively.

        Args:
            request: Inbound underwriting request.
            trace_id: Optional trace identifier for provenance.

        Returns:
            UnderwritingResult aggregating all stage outputs.
        """
        evidence_engine = EvidenceRegisterEngine()

        # Stage 1 — initialize evidence register
        register = evidence_engine.initialize(request.request_id)

        # Stage 2 — reconcile documents
        reconciliation = DocumentReconciliationEngine().reconcile(request)

        # Stage 3 — derive features
        features = FeatureDerivationEngine().derive_features(request, reconciliation)

        # Stage 4 — collect evidence across the 5 dimensions
        register = evidence_engine.collect_financial_evidence(register, request)
        register = evidence_engine.collect_credit_evidence(register, request)
        register = evidence_engine.collect_collateral_evidence(register, request)
        register = evidence_engine.collect_relationship_evidence(register, request)
        register = evidence_engine.collect_policy_evidence(register, request, 0)

        # Stage 5 — assemble decision
        decision = DecisionPacketAssembler().assemble(
            request=request,
            register=register,
            features=features,
            reconciliation=reconciliation,
        )

        return UnderwritingResult(
            request_id=request.request_id,
            decision=decision,
            register=register,
            features=features,
            reconciliation=reconciliation,
            trace_id=trace_id,
        )
