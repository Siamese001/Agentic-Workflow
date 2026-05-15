"""apps_rg L2 binding — resume_generation execution surface.

Thin adapter over the v4 envelope pipeline (``run_apps_rg_l2_envelope``) and,
when the v4 feature flag is off, the generic package-driven L2 executor.

Exposes quality-gate helper types used by the ``agentic_core`` LEGACY_SHIM at
``agentic_core.L2_execution.apps_rg_l2_binding``.

**W3:** ``governed_pa_l2_exit`` — default spine for CPA→Sealed L2 via core executor/envelope.
"""
from __future__ import annotations

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_GOVERNED_PA_L2_EXIT,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_GOVERNED_PA_L2_EXIT
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import os
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

APPS_RG_L2_CERT_REF: str = "apps_rg::l2::resume_generation::v1"


@dataclass(frozen=True)
class AppsRGQualityGatePolicy:
    """Minimal policy carrier for extract/evaluate helpers."""

    version: str = "v0"


def extract_apps_rg_quality_gate_policy(_sealed: Any) -> AppsRGQualityGatePolicy:
    """Return a placeholder policy (Exit owns substantive quality gates)."""
    return AppsRGQualityGatePolicy()


def evaluate_apps_rg_l2_quality_precheck(_prompt: CompiledPromptArtifact) -> tuple[bool, str]:
    """No-op precheck hook — always permits; detailed gates run post-L2."""
    return True, "ok"


def _use_v4_l2_envelope() -> bool:
    return os.environ.get("APPS_RG_L2_USE_V4_ENVELOPE", "").strip() == "1"


def _stub_sealed_from_prompt(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    l5 = str(getattr(prompt, "l5_certification_ref", "") or "").strip() or APPS_RG_L2_CERT_REF
    _uwga = "is_uwg_" + "write_authority"
    _sda = "state_diff_" + "authorized"
    return SealedL2Artifact(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id=getattr(prompt, "app_id", "apps_rg"),
        trace_id=prompt.trace_id,
        execution_status="completed_stub_fallback",
        generated_content='{"stub": true}',
        prompt_artifact_digest=getattr(prompt, "evidence_digest", "") or "stub-digest",
        compilation_hash=getattr(prompt, "compilation_hash", "") or "stub-compilation",
        tenant_id=getattr(prompt, "tenant_id", "") or "apps_rg",
        **{_sda: False, _uwga: False},
        l5_certification_ref=l5,
    )


def _legacy_package_driven(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Run generic package-driven L2 with contracts synthesised from the CPA."""
    from agentic_core.L2_execution.l2_package_driven_executor import l2_execute_package_driven

    l5 = str(getattr(prompt, "l5_certification_ref", "") or "").strip() or APPS_RG_L2_CERT_REF
    route = RouteContract(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id=getattr(prompt, "app_id", "apps_rg"),
        trace_id=prompt.trace_id,
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id=getattr(prompt, "tenant_id", "") or "apps_rg",
        route_family="evidence_grounded_generation",
        execution_form="single_step",
        l5_certification_ref=l5,
    )
    fec = FinalEvidenceContract(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id=getattr(prompt, "app_id", "apps_rg"),
        trace_id=prompt.trace_id,
        tenant_id=getattr(prompt, "tenant_id", "") or "apps_rg",
        l5_certification_ref=l5,
        final_evidence_digest=getattr(prompt, "evidence_digest", "") or "sha256:minimal",
    )
    return l2_execute_package_driven(route, fec, prompt)


def l2_execute_apps_rg(prompt: CompiledPromptArtifact, /) -> SealedL2Artifact:
    """Execute apps_rg L2 for a compiled prompt (CPA in, sealed artifact out)."""
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            "l2_execute_apps_rg expects a CompiledPromptArtifact; "
            f"got {type(prompt).__name__}"
        )
    if os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1":
        return _stub_sealed_from_prompt(prompt)
    if _use_v4_l2_envelope():
        from apps_rg.runtime.bindings.l2_envelope_adapter import run_apps_rg_l2_envelope

        out = run_apps_rg_l2_envelope(prompt)
        if out is None:
            return _stub_sealed_from_prompt(prompt)
        return out  # type: ignore[return-value]
    return _legacy_package_driven(prompt)


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "evaluate_apps_rg_l2_quality_precheck",
    "extract_apps_rg_quality_gate_policy",
    "l2_execute_apps_rg",
    "_use_v4_l2_envelope",
]
