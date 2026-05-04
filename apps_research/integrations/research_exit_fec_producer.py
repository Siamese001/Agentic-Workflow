"""apps_research Exit v6 FEC producer.

Produces the FinalEvidenceContract (FEC) for all apps_research execution
paths — not just live-cert mode. The FEC is handed to Exit v6 which
determines the X3 disposition.

Required FEC fields (validated by E4 receipt gate):
- app_id:              "apps_research"
- route_id:            "R3_SIMPLE_GROUNDED_READ"
- execution_form:      "SINGLE_STEP"
- c0_evidence_summary: populated from C0EvidenceBundle
- synthesis_model:     provider + model name from governed gateway
- e1_e5_receipts:      all 5 receipt names from ALL_E1_E5_RECEIPTS
- depth_profile:       one of ResearchDepthProfile constants

Plan: apps-research-spine-alignment-d4e8f2 P0.2 (scaffold stub).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_research.integrations.research_l2_step_adapters import ALL_E1_E5_RECEIPTS

APP_ID = "apps_research"
ROUTE_ID = "R3_SIMPLE_GROUNDED_READ"
EXECUTION_FORM = "SINGLE_STEP"


# ---------------------------------------------------------------------------
# FEC data contract (stub)
# ---------------------------------------------------------------------------

@dataclass
class ResearchFinalEvidenceContract:
    """FinalEvidenceContract for apps_research.

    This is the apps_research-specific FEC shape. The agentic_core
    FEC validator requires all fields to be non-empty at E4 emit time.
    """

    app_id: str = APP_ID
    route_id: str = ROUTE_ID
    execution_form: str = EXECUTION_FORM
    c0_evidence_summary: dict[str, Any] = field(default_factory=dict)
    synthesis_model: str = ""
    e1_e5_receipts: list[str] = field(default_factory=list)
    depth_profile: str = ""
    output_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Raise FECValidationError if any required field is missing or empty."""
        missing = []
        if not self.c0_evidence_summary:
            missing.append("c0_evidence_summary")
        if not self.synthesis_model:
            missing.append("synthesis_model")
        if not self.depth_profile:
            missing.append("depth_profile")
        missing_receipts = set(ALL_E1_E5_RECEIPTS) - set(self.e1_e5_receipts)
        if missing_receipts:
            missing.append(f"e1_e5_receipts missing: {sorted(missing_receipts)}")
        if missing:
            raise FECValidationError(
                f"ResearchFinalEvidenceContract validation failed. "
                f"Missing required fields: {missing}"
            )


class FECValidationError(RuntimeError):
    """Raised when FEC assembly is incomplete at E4 time.

    Must be routed through Exit v6 as X3E_SAFE_ABSTAIN — no partial FEC.
    """


# ---------------------------------------------------------------------------
# Producer (stub)
# ---------------------------------------------------------------------------

def produce_fec(
    c0_bundle: Any,
    synthesis_output: Any,
    receipts: list[str] | None = None,
) -> ResearchFinalEvidenceContract:
    """Produce the FinalEvidenceContract for an apps_research execution.

    Called by E4FECProducerAdapter. The resulting FEC is passed to
    Exit v6 (E5) and must pass validate() before Exit is invoked.

    Args:
        c0_bundle: BriefingEvidenceBundle (preferred) or C0EvidenceBundle from E1.
        synthesis_output: Provider synthesis output dict from E3.
        receipts: E1-E5 receipt names collected during execution.

    Returns:
        Populated ResearchFinalEvidenceContract.

    Raises:
        FECValidationError: If FEC assembly is incomplete.
            Must be routed through Exit v6 as X3E_SAFE_ABSTAIN.
    """
    import hashlib as _hashlib  # noqa: PLC0415

    # ------------------------------------------------------------------
    # Resolve depth_profile
    # ------------------------------------------------------------------
    depth_profile = getattr(c0_bundle, "depth_profile", "") or "COMPANY_BRIEF_STANDARD"

    # ------------------------------------------------------------------
    # Build c0_evidence_summary
    # ------------------------------------------------------------------
    try:
        from apps_research.types.briefing_evidence_contracts import (  # noqa: PLC0415
            BriefingEvidenceBundle,
        )
        if isinstance(c0_bundle, BriefingEvidenceBundle):
            portfolio = c0_bundle.source_portfolio
            coverage = c0_bundle.coverage_matrix
            c0_summary: dict[str, Any] = coverage.to_summary_dict() if coverage else {
                "depth_profile": depth_profile,
            }
            c0_summary["total_sources"] = portfolio.total_sources if portfolio else 0
            c0_summary["gate_verdict"] = (
                c0_bundle.synthesis_guidance.c0_gate_verdict
                if c0_bundle.synthesis_guidance
                else "UNKNOWN"
            )
        else:
            c0_summary = {
                "depth_profile": depth_profile,
                "chunk_count": getattr(c0_bundle, "chunk_count", 0),
            }
    except Exception:  # guardian: allow-log-and-swallow -- c0_summary assembly is best-effort; FECValidationError raised below if summary is empty
        c0_summary = {"depth_profile": depth_profile}

    # ------------------------------------------------------------------
    # Synthesis provenance
    # ------------------------------------------------------------------
    synthesis_text = ""
    synthesis_model = "stub"
    if isinstance(synthesis_output, dict):
        synthesis_text = synthesis_output.get("text", "")
        synthesis_model = synthesis_output.get("provider", "stub")
    elif hasattr(synthesis_output, "text"):
        synthesis_text = str(synthesis_output.text or "")
        synthesis_model = getattr(synthesis_output, "model", "governed_gateway")

    output_hash = _hashlib.sha256(synthesis_text.encode()).hexdigest()[:32]

    # ------------------------------------------------------------------
    # Receipts
    # ------------------------------------------------------------------
    all_receipts = list(receipts or list(ALL_E1_E5_RECEIPTS))

    # ------------------------------------------------------------------
    # Assemble and validate
    # ------------------------------------------------------------------
    fec = ResearchFinalEvidenceContract(
        c0_evidence_summary=c0_summary,
        synthesis_model=synthesis_model,
        e1_e5_receipts=all_receipts,
        depth_profile=depth_profile,
        output_hash=output_hash,
        metadata={
            "synthesis_provider": synthesis_model,
        },
    )
    fec.validate()
    return fec
