"""apps_rg L2 binding adapter — resume_generation execution surface.

Product execution is the signed-authority E1-E5 path. The CPA-only envelope and
package/stub paths remain available only for explicit test and development
postures.

Filename suffix ``_adapter.py`` is exempt from authority MV per phase-a routing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_GOVERNED_PA_L2_EXIT,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_GOVERNED_PA_L2_EXIT
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

APPS_RG_L2_CERT_REF: str = "apps_rg::l2::resume_generation::v1"


@dataclass(frozen=True)
class AppsRGQualityGatePolicy:
    """Minimal policy carrier for extract/evaluate helpers."""

    version: str = "v0"


def extract_apps_rg_quality_gate_policy(_sealed: Any) -> AppsRGQualityGatePolicy:
    """Return a placeholder policy (Exit owns substantive quality gates)."""
    return AppsRGQualityGatePolicy()


def evaluate_apps_rg_l2_quality_precheck(_prompt: CompiledPromptArtifact) -> tuple[bool, str]:
    """No-op precheck hook — detailed gates run inside authorized L2 and Exit."""
    return True, "ok"


def _use_v4_l2_envelope() -> bool:
    if os.environ.get("APPS_RG_L2_DEV_LEGACY_PACKAGE", "").strip() == "1":
        return False
    raw = os.environ.get("APPS_RG_L2_USE_V4_ENVELOPE", "").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _resolve_product_mode(product_mode: bool | None) -> bool:
    """Production defaults to signed authority; pytest preserves explicit legacy tests."""
    if product_mode is not None:
        return bool(product_mode)
    return not bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _stub_sealed_from_prompt(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    l5 = str(getattr(prompt, "l5_certification_ref", "") or "").strip() or APPS_RG_L2_CERT_REF
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
        state_diff_authorized=False,
        is_uwg_write_authority=False,
        l5_certification_ref=l5,
    )


def _legacy_package_driven(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Explicit dev-only compatibility path."""
    return _stub_sealed_from_prompt(prompt)


def _l2_execute_apps_rg_core(
    prompt: CompiledPromptArtifact,
    *,
    route_contract: Any | None = None,
    validated_request: Any | None = None,
    artifact_dir: str | None = None,
    product_mode: bool = False,
    attempt_number: int = 1,
    enable_heal: bool = False,
    max_heal_attempts: int = 3,
    resume_artifact_contract_mode: Any | None = None,
) -> SealedL2Artifact:
    """Execute explicit stub/dev compatibility or the governed v4 path."""
    if os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1":
        return _stub_sealed_from_prompt(prompt)
    if not _use_v4_l2_envelope():
        return _legacy_package_driven(prompt)

    if product_mode:
        from apps_rg.runtime.bindings.l2_authorized_runtime import (
            run_apps_rg_authorized_l2,
        )

        return run_apps_rg_authorized_l2(
            prompt,
            route_contract,
            validated_request,
            artifact_dir=artifact_dir,
            attempt_number=attempt_number,
            enable_heal=enable_heal,
            max_heal_attempts=max_heal_attempts,
            resume_artifact_contract_mode=resume_artifact_contract_mode,
        )

    from apps_rg.runtime.bindings.l2_envelope_adapter import run_apps_rg_l2_envelope

    if (
        route_contract is None
        and validated_request is None
        and artifact_dir is None
        and attempt_number == 1
        and enable_heal is False
        and max_heal_attempts == 3
        and resume_artifact_contract_mode is None
    ):
        out = run_apps_rg_l2_envelope(prompt)
    else:
        out = run_apps_rg_l2_envelope(
            prompt,
            route_contract=route_contract,
            validated_request=validated_request,
            attempt_number=attempt_number,
            enable_heal=enable_heal,
            max_heal_attempts=max_heal_attempts,
            resume_artifact_contract_mode=resume_artifact_contract_mode,
            artifact_dir=artifact_dir,
            product_mode=False,
        )
    if out is None:
        raise ValueError("APPS_RG_L2_V4_ENVELOPE_RETURNED_NONE")
    return out  # type: ignore[return-value]


def l2_execute_apps_rg(
    prompt: CompiledPromptArtifact,
    /,
    *,
    route_contract: Any | None = None,
    validated_request: Any | None = None,
    artifact_dir: str | None = None,
    product_mode: bool | None = None,
    attempt_number: int = 1,
    enable_heal: bool = False,
    max_heal_attempts: int = 3,
    resume_artifact_contract_mode: Any | None = None,
) -> SealedL2Artifact:
    """Execute apps_rg L2.

    Outside tests, product mode is the default and requires the upstream
    ``RouteContract``, ``ValidatedRequest``, and an artifact directory. Missing
    authority is returned as a provider-free sealed rejection.
    """
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            "l2_execute_apps_rg expects a CompiledPromptArtifact; "
            f"got {type(prompt).__name__}"
        )
    resolved_product_mode = _resolve_product_mode(product_mode)
    from apps_rg.runtime.spine.governed_l2_exit_compose import (
        governed_l2_exit_enabled,
        governed_l2_seal_integrated,
    )

    kwargs = dict(
        route_contract=route_contract,
        validated_request=validated_request,
        artifact_dir=artifact_dir,
        product_mode=resolved_product_mode,
        attempt_number=attempt_number,
        enable_heal=enable_heal,
        max_heal_attempts=max_heal_attempts,
        resume_artifact_contract_mode=resume_artifact_contract_mode,
    )
    if governed_l2_exit_enabled() and (
        resolved_product_mode or os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1"
    ):
        return governed_l2_seal_integrated(prompt, **kwargs)
    return _l2_execute_apps_rg_core(prompt, **kwargs)


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "evaluate_apps_rg_l2_quality_precheck",
    "extract_apps_rg_quality_gate_policy",
    "l2_execute_apps_rg",
    "_use_v4_l2_envelope",
]
