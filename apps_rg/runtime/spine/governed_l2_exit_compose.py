"""Governed L2 + Exit compose — integrated spine (W6).

Section lanes: ``section_l2_spine_receipt`` + ``exit_artifacts`` (lane receipts).
Integrated: ``l2_execute_apps_rg`` → ``exit_finalize_apps_rg`` + ``ExitEvalPipeline``
→ canonical ``RuntimeExhaustBundle`` (L6 handoff boundary).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

GOVERNED_L2_EXIT_MODE_INTEGRATED = "integrated_spine_l2_exit"
GOVERNED_EXIT_SPINE_MARKER = "governed_l2_exit:v1"


def governed_l2_exit_enabled() -> bool:
    if os.environ.get("APPS_RG_GOVERNED_L2_EXIT_SKIP", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return True


def _stamp_sealed_governed_marker(sealed: SealedL2Artifact) -> SealedL2Artifact:
    refs = tuple(getattr(sealed, "gate_verdict_refs", ()) or ())
    if GOVERNED_EXIT_SPINE_MARKER in refs:
        return sealed
    updated_refs = refs + (GOVERNED_EXIT_SPINE_MARKER,)
    try:
        object.__setattr__(sealed, "gate_verdict_refs", updated_refs)
        return sealed
    except (AttributeError, TypeError):
        from dataclasses import replace

        return replace(sealed, gate_verdict_refs=updated_refs)


def governed_l2_seal_integrated(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Integrated L2 — core executor (package-driven or v4 envelope) + L5 packet."""
    from apps_rg.runtime.bindings.l2_binding_adapter import _l2_execute_apps_rg_core
    from apps_rg.runtime.l5.packet_builder import (
        attach_l5_packet_to_sealed,
        build_l5_certification_packet,
    )

    sealed = _l2_execute_apps_rg_core(prompt)
    sealed = _stamp_sealed_governed_marker(sealed)
    packet_result = build_l5_certification_packet(
        sealed=sealed,
        prompt_artifact=prompt,
        allow_test_l5_cert_ref=bool(getattr(prompt, "allow_test_l5_cert_ref", False)),
    )
    return attach_l5_packet_to_sealed(sealed, packet_result)


def _x3_code_from_eval(eval_result: Any) -> str:
    packet = getattr(eval_result, "x3_packet", None)
    if packet is not None:
        code = getattr(packet, "x3_code", None) or getattr(packet, "disposition_code", None)
        if code:
            return str(code)
    disp = getattr(eval_result, "disposition", None)
    if disp is not None:
        return str(getattr(disp, "value", disp))
    return "UNKNOWN"


def _build_exit_eval_receipts(
    sealed: SealedL2Artifact,
    *,
    fec: Optional[FinalEvidenceContract],
    exit_result: Any,
    target_company: str = "",
    target_role: str = "",
) -> dict[str, Any]:
    disp = exit_result.disposition
    return {
        "request_id": getattr(sealed, "request_id", "") or "",
        "run_id": getattr(sealed, "run_id", "") or "",
        "trace_id": getattr(sealed, "trace_id", "") or "",
        "app_name": "apps_rg",
        "spine_mode": GOVERNED_L2_EXIT_MODE_INTEGRATED,
        "target_company": target_company,
        "target_role": target_role,
        "outcome_authorized": bool(getattr(disp, "outcome_authorized", False)),
        "c0_blocking": bool(getattr(disp, "c0_blocking", False)),
        "terminal_class": "success" if getattr(disp, "outcome_authorized", False) else "failure",
        "compilation_hash": str(getattr(sealed, "compilation_hash", "") or ""),
        "l5_certification_ref": str(getattr(sealed, "l5_certification_ref", "") or ""),
        "l5_certification_packet_ref": str(
            getattr(sealed, "l5_certification_packet_ref", "") or ""
        ),
        "l5_certification_packet_digest": str(
            getattr(sealed, "l5_certification_packet_digest", "") or ""
        ),
        "l5_certification_status": str(
            getattr(sealed, "l5_certification_status", "") or ""
        ),
        "fec_support_status": str(getattr(fec, "support_status", "") or "") if fec else "",
    }


@dataclass(frozen=True)
class GovernedIntegratedExitBundle:
    """Integrated Exit outcome — exactly one spine eval disposition + exhaust for L6."""

    exit_result: Any
    spine_eval: Any
    exhaust_bundle: Any
    x3_code: str
    governed_mode: str = GOVERNED_L2_EXIT_MODE_INTEGRATED


def governed_exit_finalize_integrated(
    sealed: SealedL2Artifact,
    *,
    fec: Optional[FinalEvidenceContract] = None,
    target_company: str = "",
    target_role: str = "",
    prompt_artifact: Any = None,
) -> GovernedIntegratedExitBundle:
    """Integrated Exit — apps_rg gates + ``ExitEvalPipeline`` + ``RuntimeExhaustBundle``."""
    from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline
    from apps_rg.runtime.bindings.exit_binding import (
        _exit_finalize_apps_rg_impl,
        build_exhaust_bundle_from_exit,
    )

    exit_result = _exit_finalize_apps_rg_impl(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        target_company=target_company,
        target_role=target_role,
    )
    receipts = _build_exit_eval_receipts(
        sealed,
        fec=fec,
        exit_result=exit_result,
        target_company=target_company,
        target_role=target_role,
    )
    spine_eval = ExitEvalPipeline().run(receipts)
    x3_code = _x3_code_from_eval(spine_eval)
    exit_ref = f"spine_exit_eval:{x3_code}"
    exhaust = build_exhaust_bundle_from_exit(
        exit_result,
        sealed,
        exit_disposition_ref=exit_ref,
    )
    return GovernedIntegratedExitBundle(
        exit_result=exit_result,
        spine_eval=spine_eval,
        exhaust_bundle=exhaust,
        x3_code=x3_code,
    )


__all__ = [
    "GOVERNED_EXIT_SPINE_MARKER",
    "GOVERNED_L2_EXIT_MODE_INTEGRATED",
    "GovernedIntegratedExitBundle",
    "governed_exit_finalize_integrated",
    "governed_l2_exit_enabled",
    "governed_l2_seal_integrated",
]
