"""apps_underwriting_ai HOP pipeline topology.

Declares the 5-stage inner DAG that mirrors the imperative walk in
``UnderwritingEngine.run()`` — initialize evidence → reconcile documents →
derive features → collect evidence → assemble decision packet.

This substrate adoption is **additive**: the existing
``UnderwritingEngine`` remains the primary runtime path (called by the
existing integrations). The shared-substrate entry point documented here
lets future callers drive the same 5 stages via the standard
``HopPipelineExecutor`` surface — for example, to replay a single stage
during incident healing, or to compose apps_underwriting_ai as a
sub-pipeline inside a larger workflow.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-hop-substrate-f7751b.md (Wave 4.1)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="initialize_evidence",
        engine_module="apps_underwriting_ai.engines.hop_initialize_evidence_engine",
        engine_class="HopInitializeEvidenceEngine",
        inputs=("underwriting_request",),
        outputs=("evidence_register",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="reconcile_documents",
        engine_module="apps_underwriting_ai.engines.hop_reconcile_documents_engine",
        engine_class="HopReconcileDocumentsEngine",
        inputs=("underwriting_request",),
        outputs=("reconciliation_result",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="derive_features",
        engine_module="apps_underwriting_ai.engines.hop_derive_features_engine",
        engine_class="HopDeriveFeaturesEngine",
        inputs=("underwriting_request", "reconciliation_result"),
        outputs=("risk_features",),
        required=True,
    ),
    HopStageSpec(
        stage_id=4,
        stage_name="collect_evidence",
        engine_module="apps_underwriting_ai.engines.hop_collect_evidence_engine",
        engine_class="HopCollectEvidenceEngine",
        inputs=("underwriting_request", "evidence_register", "risk_features"),
        outputs=("evidence_collected",),
        required=True,
    ),
    HopStageSpec(
        stage_id=5,
        stage_name="assemble_decision",
        engine_module="apps_underwriting_ai.engines.hop_assemble_decision_engine",
        engine_class="HopAssembleDecisionEngine",
        inputs=(
            "underwriting_request",
            "evidence_register",
            "risk_features",
            "reconciliation_result",
        ),
        outputs=("decision_packet",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_underwriting_ai").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
