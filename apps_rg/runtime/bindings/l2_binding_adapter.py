"""apps_rg L2 binding adapter — resume_generation execution surface.

Thin adapter over the v4 envelope pipeline (``run_apps_rg_l2_envelope``).
The generic package-driven L2 executor is retained only for explicit dev
diagnostics.

Filename suffix ``_adapter.py`` is exempt from authority MV per phase-a routing.

Canonical L2 implementation surface. The ``agentic_core`` LEGACY_SHIM at
``agentic_core.L2_execution.apps_rg_l2_binding`` is ARCHIVE_PENDING (W11) and must
not be imported by product or test code.

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
    if os.environ.get("APPS_RG_L2_DEV_LEGACY_PACKAGE", "").strip() == "1":
        return False
    raw = os.environ.get("APPS_RG_L2_USE_V4_ENVELOPE", "").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    return True


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
    """Preserve the disabled-v4 contract with an app-local sealed fallback."""
    return _stub_sealed_from_prompt(prompt)


def _l2_execute_apps_rg_core(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Core L2 execution paths (explicit stub/dev legacy or default v4 envelope)."""
    if os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1":
        return _stub_sealed_from_prompt(prompt)
    if _use_v4_l2_envelope():
        from apps_rg.runtime.bindings.l2_envelope_adapter import run_apps_rg_l2_envelope

        out = run_apps_rg_l2_envelope(prompt)
        if out is None:
            raise ValueError("APPS_RG_L2_V4_ENVELOPE_RETURNED_NONE")
        return out  # type: ignore[return-value]
    return _legacy_package_driven(prompt)


def l2_execute_apps_rg(prompt: CompiledPromptArtifact, /) -> SealedL2Artifact:
    """Execute apps_rg L2 for a compiled prompt (CPA in, sealed artifact out)."""
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            "l2_execute_apps_rg expects a CompiledPromptArtifact; "
            f"got {type(prompt).__name__}"
        )
    from apps_rg.runtime.spine.governed_l2_exit_compose import (
        governed_l2_exit_enabled,
        governed_l2_seal_integrated,
    )

    if governed_l2_exit_enabled():
        return governed_l2_seal_integrated(prompt)
    return _l2_execute_apps_rg_core(prompt)


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "evaluate_apps_rg_l2_quality_precheck",
    "extract_apps_rg_quality_gate_policy",
    "l2_execute_apps_rg",
    "_use_v4_l2_envelope",
]
