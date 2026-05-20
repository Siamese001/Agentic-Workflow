"""Non-product proof classification stamps — offline rollup, orchestrator, demo harness."""
from __future__ import annotations

from typing import Any, Mapping

# Orchestrator / offline lane rollup (SP-001)
ORCHESTRATOR_PROOF_CLASSIFICATION = "OFFLINE_LANE_ROLLUP_NOT_PRODUCT_SPINE"
ORCHESTRATOR_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "not product runtime",
    "not L7 proof",
    "not Fort Knox proof",
    "not integrated R4",
    "not Exit X3",
)

# Package rollup X3 (SP-003)
PACKAGE_DISPOSITION_CLASSIFICATION = "OFFLINE_PACKAGE_ROLLUP"
PACKAGE_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "package_x3_allow is not exit_x3_allow",
    "package_x3_allow is not spine_x3_allow",
    "package_x3_allow is not product_x3_allow",
    "not integrated R4",
    "not L7 certification",
    "not Fort Knox certification",
)

# Demo harness (SP-002)
DEMO_HARNESS_PROOF_CLASSIFICATION = "DEMO_HARNESS_NOT_RUNTIME_PROOF"
DEMO_HARNESS_ENV = "APPS_RG_ALLOW_DEMO_HARNESS"

# CI harness (SP-005)
CI_LANE_DEV_HARNESS_CLASSIFICATION = "LANE_DEV_HARNESS"

# Section L7 correlation (SP-004)
SECTION_L7_CORRELATION_CLASSIFICATION = "SECTION_RUN_WITH_L7_CORRELATION_REFS_NOT_PRODUCT_PROOF"
SECTION_L7_CORRELATION_CLASSIFICATION_LEGACY = "SECTION_RUN_WITH_INTEGRATED_L7_REFS"

# Product-proof classifications that certification gates may accept (integrated spine only).
PRODUCT_PROOF_CLASSIFICATIONS: frozenset[str] = frozenset(
    {
        "INTEGRATED_R4_PRODUCT_RUNTIME",
        "RELEASE_ELIGIBLE_PROOF",
        "LIVE_RUNTIME_PROOF",
    }
)

# Classifications that must never satisfy L7 / Fort Knox / product certification gates.
NON_PRODUCT_PROOF_CLASSIFICATIONS: frozenset[str] = frozenset(
    {
        ORCHESTRATOR_PROOF_CLASSIFICATION,
        PACKAGE_DISPOSITION_CLASSIFICATION,
        DEMO_HARNESS_PROOF_CLASSIFICATION,
        CI_LANE_DEV_HARNESS_CLASSIFICATION,
        SECTION_L7_CORRELATION_CLASSIFICATION,
        SECTION_L7_CORRELATION_CLASSIFICATION_LEGACY,
        "SECTION_MODULAR_L7_UNTRUSTED_ARTIFACTS_PRESENT",
        "SECTION_DIR_CONTAINS_TRUSTED_L7_REFS",
        "SECTION_MODULAR_UNEXPECTED_99_ARTIFACT",
        "SECTION_MODULAR_L7_BINDING_INCOMPLETE",
    }
)


def orchestrator_non_product_stamp() -> dict[str, Any]:
    return {
        "proof_classification": ORCHESTRATOR_PROOF_CLASSIFICATION,
        "product_certification": "NOT_CLAIMED",
        "l7_certification": "NOT_CLAIMED",
        "fort_knox_certification": "NOT_CLAIMED",
        "integrated_r4_invoked": False,
        "explicit_non_claims": list(ORCHESTRATOR_EXPLICIT_NON_CLAIMS),
    }


def package_rollup_non_product_stamp(*, package_x3_allow: bool) -> dict[str, Any]:
    return {
        "package_disposition_classification": PACKAGE_DISPOSITION_CLASSIFICATION,
        "proof_classification": PACKAGE_DISPOSITION_CLASSIFICATION,
        "package_x3_allow": bool(package_x3_allow),
        "exit_x3_disposition": "NOT_CLAIMED",
        "spine_x3_allow": False,
        "product_x3_allow": False,
        "integrated_r4_invoked": False,
        "agentic_core_how_trace_required_for_product_cert": True,
        "eligible_for_l7_certification": False,
        "product_certification": "NOT_CLAIMED",
        "l7_certification": "NOT_CLAIMED",
        "fort_knox_certification": "NOT_CLAIMED",
        "proof_eligible": False,
        "explicit_non_claims": list(PACKAGE_EXPLICIT_NON_CLAIMS),
    }


def demo_harness_non_product_stamp() -> dict[str, Any]:
    return {
        "proof_classification": DEMO_HARNESS_PROOF_CLASSIFICATION,
        "product_certification": "NOT_CLAIMED",
        "l7_certification": "NOT_CLAIMED",
        "fort_knox_certification": "NOT_CLAIMED",
        "proof_eligible": False,
        "integrated_r4_invoked": False,
        "explicit_non_claims": [
            "demo harness is non-product",
            "use python -m apps_rg --section executive_summary for lane-dev proof",
        ],
    }


def is_eligible_for_product_or_l7_certification(
    payload: Mapping[str, Any] | None,
) -> bool:
    """Return True only when payload explicitly claims integrated product proof."""
    if not payload or not isinstance(payload, Mapping):
        return False
    pc = str(payload.get("proof_classification") or payload.get("package_disposition_classification") or "")
    if pc in NON_PRODUCT_PROOF_CLASSIFICATIONS:
        return False
    if payload.get("integrated_r4_invoked") is False:
        return False
    if payload.get("eligible_for_l7_certification") is False:
        return False
    if str(payload.get("product_certification") or "") == "NOT_CLAIMED":
        return False
    if str(payload.get("l7_certification") or "") == "NOT_CLAIMED":
        return False
    if payload.get("proof_eligible") is False:
        return False
    return pc in PRODUCT_PROOF_CLASSIFICATIONS


def guard_reject_non_product_for_certification(
    payload: Mapping[str, Any] | None,
    *,
    context: str = "",
    run_dir: Any = None,
) -> None:
    """Raise ValueError when offline/package/demo proof is presented for product/L7/Fort Knox certification."""
    if not payload or not isinstance(payload, Mapping):
        return
    from apps_rg.runtime.integrated_product_proof_gate import (
        reject_non_integrated_product_claim,
    )

    if run_dir is not None:
        reject_non_integrated_product_claim(payload, run_dir=run_dir, context=context)
        return
    if is_eligible_for_product_or_l7_certification(payload):
        return
    pc = str(payload.get("proof_classification") or payload.get("package_disposition_classification") or "")
    if (
        pc in NON_PRODUCT_PROOF_CLASSIFICATIONS
        or payload.get("package_x3_allow") is True
        or payload.get("disposition_family") == "resume_package_x3"
        or payload.get("integrated_r4_invoked") is False
    ):
        label = context or "certification gate"
        raise ValueError(
            f"{label}: non-product proof {pc!r} cannot satisfy product/L7/Fort Knox certification"
        )
    if pc in PRODUCT_PROOF_CLASSIFICATIONS:
        label = context or "certification gate"
        raise ValueError(
            f"{label}: product proof classification {pc!r} requires run_dir for integrated-R4 validation"
        )


def assert_not_product_spine_proof(payload: Mapping[str, Any], *, context: str = "") -> None:
    """Alias for guard_reject_non_product_for_certification (tests / gate callers)."""
    guard_reject_non_product_for_certification(payload, context=context)


__all__ = [
    "CI_LANE_DEV_HARNESS_CLASSIFICATION",
    "DEMO_HARNESS_ENV",
    "DEMO_HARNESS_PROOF_CLASSIFICATION",
    "NON_PRODUCT_PROOF_CLASSIFICATIONS",
    "ORCHESTRATOR_PROOF_CLASSIFICATION",
    "PACKAGE_DISPOSITION_CLASSIFICATION",
    "PRODUCT_PROOF_CLASSIFICATIONS",
    "SECTION_L7_CORRELATION_CLASSIFICATION",
    "SECTION_L7_CORRELATION_CLASSIFICATION_LEGACY",
    "assert_not_product_spine_proof",
    "guard_reject_non_product_for_certification",
    "demo_harness_non_product_stamp",
    "is_eligible_for_product_or_l7_certification",
    "orchestrator_non_product_stamp",
    "package_rollup_non_product_stamp",
]
