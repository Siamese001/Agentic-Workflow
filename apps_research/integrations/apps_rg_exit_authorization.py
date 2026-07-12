"""Canonical runtime-gate and Exit authorization for apps_research -> apps_rg.

GateVerdicts are current-run evidence only. The generic package-driven Exit
binding is the sole authority that emits X3. Callers may publish ``briefing.md``
only when this module returns ``X3D_ALLOW_FINISH``.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
from agentic_core.runtime.exit.apps_research_exit_binding import (
    exit_bind_and_finalize_apps_research,
)
from agentic_core.runtime.exit.exit_disposition import (
    X3D_ALLOW_FINISH,
    ExitDispositionReceipt,
    ExitReviewPacket,
    RuntimeExhaustBundle,
)
from agentic_core.runtime.exit.exit_package_driven_binding import ExitInput, ExitPolicy
from agentic_core.runtime.gates.gate_profile_resolver import GateProfile
from agentic_core.runtime.gates.gate_types import (
    GateMeshResult,
    GateVerdict,
    build_gate_mesh_result,
)
from apps_research.types.apps_rg_targeting_brief_contract import (
    validate_targeting_brief_text,
)

HANDOFF_EXIT_PROFILE_ID = "apps_research.apps_rg_handoff.exit.v1"
HANDOFF_GATE_EVALUATOR_VERSION = "apps_research.apps_rg_handoff_gate_mesh.v1"
HANDOFF_ROUTE_ID = "apps_research.company_brief_v1"
HANDOFF_REQUIRED_GATE_IDS: tuple[str, ...] = (
    "G5_ANSWER_PRESENT",
    "G6_ANSWER_RELEVANT",
    "G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
    "G21_OUTPUT_SCHEMA",
    "G24_REPLAY_ELIGIBLE",
    "G26_EXIT_ELIGIBILITY",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class _ExitGateMeshAdapter:
    """Compatibility adapter for the generic Exit binding's summary surface."""

    def __init__(self, mesh: GateMeshResult) -> None:
        self._mesh = mesh

    def __getattr__(self, name: str) -> Any:
        return getattr(self._mesh, name)

    def summarize(self) -> dict[str, Any]:
        return self._mesh.as_dict()


@dataclass(frozen=True, slots=True)
class AppsRgHandoffExitAuthorization:
    """Canonical proof bundle produced before briefing publication."""

    gate_mesh_result: GateMeshResult
    sealed_workflow_package: SealedWorkflowPackage
    exit_review_packet: ExitReviewPacket
    exit_disposition_receipt: ExitDispositionReceipt
    runtime_exhaust_bundle: RuntimeExhaustBundle

    @property
    def allows_finish(self) -> bool:
        return self.exit_disposition_receipt.x3_code == X3D_ALLOW_FINISH

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_mesh_result": self.gate_mesh_result.as_dict(),
            "sealed_workflow_package": self.sealed_workflow_package.as_dict(),
            "exit_review_packet": self.exit_review_packet.as_dict(),
            "exit_disposition_receipt": self.exit_disposition_receipt.as_dict(),
            "runtime_exhaust_bundle": self.runtime_exhaust_bundle.as_dict(),
        }


def _build_verdict(
    *,
    gate_id: str,
    result: str,
    run_id: str,
    trace_root: str,
    packet_ref: str,
    reason_code: str,
    score: float = 0.0,
    threshold: float = 0.0,
    evidence_refs: tuple[str, ...] = (),
) -> GateVerdict:
    evaluated_at = datetime.now(timezone.utc).isoformat()
    severity = (
        "hard_fail"
        if result == "FAIL"
        else "warn"
        if result in {"WARN", "UNKNOWN"}
        else "advisory"
    )
    digest_payload = {
        "gate_id": gate_id,
        "result": result,
        "run_id": run_id,
        "trace_root": trace_root,
        "packet_ref": packet_ref,
        "reason_code": reason_code,
        "score": score,
        "threshold": threshold,
        "evidence_refs": list(evidence_refs),
        "evaluated_at": evaluated_at,
    }
    return GateVerdict(
        gate_id=gate_id,
        gate_family="apps_research_apps_rg_handoff",
        evaluated_stage="Exit",
        evaluated_surface="apps_rg_targeting_brief",
        evaluated_packet_ref=packet_ref,
        result=result,
        severity=severity,
        reason_codes=(reason_code,),
        score=score,
        threshold=threshold,
        evidence_refs=evidence_refs,
        replay_refs=(packet_ref,),
        confidence=score if score else (1.0 if result == "PASS" else 0.0),
        deterministic_digest=_sha256_json(digest_payload),
        request_id=run_id,
        run_id=run_id,
        trace_root=trace_root,
        replay_key=run_id,
        evidence_digest=_sha256_json(
            {
                "packet_ref": packet_ref,
                "evidence_refs": list(evidence_refs),
                "reason_code": reason_code,
            }
        ),
        evaluator_version=HANDOFF_GATE_EVALUATOR_VERSION,
        evaluated_at=evaluated_at,
        unknown_reason=reason_code if result == "UNKNOWN" else "",
        created_at=evaluated_at,
    )


def _x2_result(receipt: Mapping[str, Any]) -> tuple[str, str, float, float]:
    status = str(receipt.get("status") or "UNKNOWN").upper()
    model_backed = receipt.get("model_backed") is True
    provider = str(receipt.get("judge_provider") or receipt.get("judge_name") or "").strip()
    model = str(receipt.get("judge_model") or "").strip()
    try:
        score = float(receipt.get("score") or 0.0)
        threshold = float(receipt.get("threshold") or 0.75)
    except (TypeError, ValueError):
        return "FAIL", "x2_score_or_threshold_invalid", 0.0, 0.75

    if (
        status == "PASS"
        and model_backed
        and provider
        and model
        and score >= threshold
    ):
        return "PASS", "model_backed_x2_pass", score, threshold
    if status == "UNKNOWN":
        return "UNKNOWN", "model_backed_x2_unknown", score, threshold
    return (
        "FAIL",
        str(receipt.get("reason") or "model_backed_x2_not_pass"),
        score,
        threshold,
    )


def build_apps_rg_handoff_gate_mesh(
    *,
    run_id: str,
    trace_root: str,
    briefing_text: str,
    jd_text: str,
    sidecar: Mapping[str, Any] | None,
) -> GateMeshResult:
    """Evaluate the current handoff candidate without emitting X3."""

    brief_text = str(briefing_text or "").strip()
    brief_sha = _sha256_text(brief_text)
    jd_sha = _sha256_text(jd_text) if jd_text else ""
    sidecar_map = dict(sidecar or {})
    x2_raw = sidecar_map.get("x2_judge_receipt")
    x2_receipt = dict(x2_raw) if isinstance(x2_raw, Mapping) else {}
    x2_result, x2_reason, x2_score, x2_threshold = _x2_result(x2_receipt)

    stub_markers = (
        "stub company",
        "stub executive summary",
        "stub business description",
        "stub research gap",
        "finding 1",
        "product a",
        "service b",
    )
    lower_brief = brief_text.lower()
    answer_present = bool(brief_text) and not any(
        marker in lower_brief for marker in stub_markers
    )

    validation = validate_targeting_brief_text(
        brief_text,
        jd_text=str(jd_text or ""),
        profile="apps_rg",
    )

    register_raw = sidecar_map.get("source_register")
    register = list(register_raw) if isinstance(register_raw, (list, tuple)) else []
    evidence_families = tuple(
        str(row.get("family") or "")
        for row in register
        if isinstance(row, Mapping) and bool(row.get("has_content"))
    )
    evidence_present = bool(evidence_families)

    sidecar_sha = str(sidecar_map.get("brief_text_sha256") or "").strip()
    replay_ok = bool(run_id and brief_sha) and (
        not sidecar_sha or sidecar_sha == brief_sha
    )

    provider_ok = (
        sidecar_map.get("generation_provider") == "external_openai"
        and bool(str(sidecar_map.get("generation_model") or "").strip())
        and bool(sidecar_map.get("provider_call_attempted", True))
    )

    verdicts = (
        _build_verdict(
            gate_id="G5_ANSWER_PRESENT",
            result="PASS" if answer_present else "FAIL",
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=(
                "brief_present_non_stub" if answer_present else "brief_missing_or_stub"
            ),
            evidence_refs=(brief_sha,),
        ),
        _build_verdict(
            gate_id="G6_ANSWER_RELEVANT",
            result=x2_result,
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=x2_reason,
            score=x2_score,
            threshold=x2_threshold,
            evidence_refs=tuple(
                value
                for value in (
                    str(x2_receipt.get("judge_provider") or ""),
                    str(x2_receipt.get("judge_model") or ""),
                )
                if value
            ),
        ),
        _build_verdict(
            gate_id="G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
            result="PASS" if evidence_present else "FAIL",
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=(
                "source_register_present" if evidence_present else "source_register_empty"
            ),
            evidence_refs=evidence_families,
        ),
        _build_verdict(
            gate_id="G21_OUTPUT_SCHEMA",
            result="PASS" if validation.valid else "FAIL",
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=(
                "targeting_brief_contract_valid"
                if validation.valid
                else "targeting_brief_contract_invalid:"
                + ",".join(validation.violations[:8])
            ),
            evidence_refs=(brief_sha,),
        ),
        _build_verdict(
            gate_id="G24_REPLAY_ELIGIBLE",
            result="PASS" if replay_ok else "FAIL",
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=(
                "digest_lineage_bound" if replay_ok else "digest_lineage_mismatch"
            ),
            evidence_refs=tuple(
                value for value in (brief_sha, jd_sha, sidecar_sha) if value
            ),
        ),
        _build_verdict(
            gate_id="G26_EXIT_ELIGIBILITY",
            result="PASS" if provider_ok else "FAIL",
            run_id=run_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=(
                "provider_lane_and_model_bound"
                if provider_ok
                else "generation_provider_or_model_not_authorized"
            ),
            evidence_refs=tuple(
                value
                for value in (
                    str(sidecar_map.get("generation_provider") or ""),
                    str(sidecar_map.get("generation_model") or ""),
                )
                if value
            ),
        ),
    )
    return build_gate_mesh_result(
        request_id=run_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=HANDOFF_ROUTE_ID,
        evaluated_surface="apps_rg_targeting_brief",
        evaluated_packet_ref=brief_sha,
        required_gate_ids=HANDOFF_REQUIRED_GATE_IDS,
        verdicts=verdicts,
    )


def _seal_receipt(
    receipt: ExitDispositionReceipt,
    *,
    output_artifact_digest: str,
) -> ExitDispositionReceipt:
    seed = receipt.as_dict()
    seed["output_artifact_digest"] = output_artifact_digest
    seed["deterministic_digest"] = ""
    digest = _sha256_json(seed)
    return dataclasses.replace(
        receipt,
        output_artifact_digest=output_artifact_digest,
        deterministic_digest=digest,
    )


def run_apps_rg_handoff_exit_authorization(
    *,
    run_id: str,
    trace_root: str,
    briefing_text: str,
    jd_text: str,
    sidecar: Mapping[str, Any] | None,
) -> AppsRgHandoffExitAuthorization:
    """Run the GateMesh and generic Exit binding exactly once."""

    brief_text = str(briefing_text or "").strip()
    brief_sha = _sha256_text(brief_text)
    mesh = build_apps_rg_handoff_gate_mesh(
        run_id=run_id,
        trace_root=trace_root,
        briefing_text=brief_text,
        jd_text=str(jd_text or ""),
        sidecar=sidecar,
    )
    sealed = SealedWorkflowPackage(
        package_id=f"apps_research:{run_id}:apps_rg_targeting_brief",
        route_contract_ref=HANDOFF_ROUTE_ID,
        workflow_ref="apps_research.single_step.targeting_brief",
        workflow_id=run_id,
        run_id=run_id,
        app_context="apps_research",
        trace_root=trace_root,
        completed_at=datetime.now(timezone.utc).isoformat(),
        merged_content=brief_text,
        merged_content_digest=brief_sha,
        merged_payload_digest=brief_sha,
        runtime_gate_refs=(mesh.deterministic_digest,),
        terminal_class="success" if brief_text else "failed",
        decisive_reason="targeting_brief_candidate_sealed_for_exit",
        replay_manifest=json.dumps(
            {
                "run_id": run_id,
                "trace_root": trace_root,
                "brief_sha256": brief_sha,
                "jd_sha256": _sha256_text(jd_text) if jd_text else "",
                "gate_mesh_digest": mesh.deterministic_digest,
            },
            sort_keys=True,
        ),
    )
    profile = GateProfile(
        profile_id=HANDOFF_EXIT_PROFILE_ID,
        app_id="apps_research",
        task_class="company_brief",
        version="1",
        required_exit_gates=HANDOFF_REQUIRED_GATE_IDS,
        gate_definitions={
            gate_id: {"required": "always"}
            for gate_id in HANDOFF_REQUIRED_GATE_IDS
        },
    )
    review, receipt, exhaust = exit_bind_and_finalize_apps_research(
        gate_profile=profile,
        exit_policy=ExitPolicy(),
        exit_input=ExitInput(
            sealed_l2_artifact=sealed,
            gate_mesh_result=_ExitGateMeshAdapter(mesh),  # type: ignore[arg-type]
            evidence={
                "brief_sha256": brief_sha,
                "jd_sha256": _sha256_text(jd_text) if jd_text else "",
            },
        ),
        request_id=run_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id=HANDOFF_ROUTE_ID,
        commit_requested=False,
    )
    receipt = _seal_receipt(
        receipt,
        output_artifact_digest=brief_sha,
    )
    exhaust = dataclasses.replace(
        exhaust,
        exit_disposition_ref=receipt.deterministic_digest,
    )
    return AppsRgHandoffExitAuthorization(
        gate_mesh_result=mesh,
        sealed_workflow_package=sealed,
        exit_review_packet=review,
        exit_disposition_receipt=receipt,
        runtime_exhaust_bundle=exhaust,
    )


__all__ = [
    "AppsRgHandoffExitAuthorization",
    "HANDOFF_EXIT_PROFILE_ID",
    "HANDOFF_REQUIRED_GATE_IDS",
    "build_apps_rg_handoff_gate_mesh",
    "run_apps_rg_handoff_exit_authorization",
]
