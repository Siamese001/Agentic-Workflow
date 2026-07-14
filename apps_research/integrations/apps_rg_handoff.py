"""apps_research -> apps_rg targeting-brief handoff v2 contract.

The producer atomically publishes a digest-bound v2 manifest only after the
generic package-driven Exit binding emits exact ``X3D_ALLOW_FINISH``. Runtime
GateVerdicts are evidence; they never mint X3.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.dimension import Dimension, GraderClass
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges.google_judge import GoogleJudge
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

APPS_RG_HANDOFF_GENERATION_PROVIDER = "external_openai"
APPS_RG_HANDOFF_JUDGE_NAME = "gemini_pro"
APPS_RG_HANDOFF_JUDGE_PROVIDER = "gemini_pro"
APPS_RG_HANDOFF_JUDGE_MODEL = "gemini-3.1-pro-preview"
APPS_RG_HANDOFF_X2_THRESHOLD = 0.75
APPS_RG_HANDOFF_JUDGE_MAX_TOKENS = 4096
APPS_RG_HANDOFF_X2_MAX_ATTEMPTS = 2
APPS_RG_HANDOFF_EXIT_PROFILE_ID = "apps_research.apps_rg_handoff.exit.v1"
APPS_RG_HANDOFF_GATE_MESH_SCHEMA = "apps_research.apps_rg_handoff_gate_mesh.v1"
_RETRYABLE_JUDGE_PARSE_MARKERS = (
    "no JSON object",
    "incomplete JSON object",
    "judge JSON parse failed",
    "judge response was not JSON",
    "response had no text part",
)
_HANDOFF_REQUIRED_GATE_IDS = (
    "G5_ANSWER_PRESENT",
    "G6_ANSWER_RELEVANT",
    "G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
    "G21_OUTPUT_SCHEMA",
    "G24_REPLAY_ELIGIBLE",
    "G26_EXIT_ELIGIBILITY",
)


@dataclasses.dataclass(frozen=True, slots=True)
class AppsRgHandoffExitAuthorization:
    """Canonical Exit artifacts required before publishing the handoff."""

    gate_mesh_result: GateMeshResult
    sealed_workflow_package: SealedWorkflowPackage
    exit_review_packet: ExitReviewPacket
    exit_disposition_receipt: ExitDispositionReceipt
    runtime_exhaust_bundle: RuntimeExhaustBundle

    @property
    def allows_finish(self) -> bool:
        return self.exit_disposition_receipt.x3_code == X3D_ALLOW_FINISH


@dataclasses.dataclass(frozen=True, slots=True)
class AppsRgTargetingArtifactBundle:
    """Producer-owned durable artifacts required for apps_rg handoff."""

    run_id: str
    run_dir: Path
    briefing_path: Path
    company_brief_path: Path
    envelope_path: Path
    metadata_path: Path
    envelope: dict[str, Any]
    gate_mesh_path: Path | None = None
    sealed_workflow_path: Path | None = None
    exit_review_path: Path | None = None
    exit_disposition_path: Path | None = None
    runtime_exhaust_path: Path | None = None
    handoff_v2_path: Path | None = None
    commit_manifest_path: Path | None = None
    u0_receipt_path: Path | None = None
    raw_input_path: Path | None = None
    normalized_input_path: Path | None = None
    brief_sha256: str = ""
    result_metadata_digest: str = ""
    bundle_manifest_digest: str = ""


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(payload: Any, *, pretty: bool = True) -> bytes:
    options: dict[str, Any] = {
        "ensure_ascii": False,
        "sort_keys": True,
        "default": str,
    }
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(payload, **options) + "\n").encode("utf-8")


def _write_fsync(path: Path, payload: bytes) -> None:
    """Create one staged artifact and force its bytes to stable storage."""
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def looks_like_stub_company_brief(text: str) -> bool:
    blob = str(text or "").lower()
    stub_markers = (
        "stub company",
        "stub executive summary",
        "stub business description",
        "stub research gap",
        "finding 1",
        "product a",
        "service b",
    )
    return any(re.search(rf"\b{re.escape(marker)}\b", blob) for marker in stub_markers)


def _mapping_from(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return dumped
    return {}


def find_apps_rg_targeting_sidecar(value: Any, *, _depth: int = 0) -> dict[str, Any]:
    """Find an apps_rg targeting sidecar in nested run/FEC payloads."""
    if _depth > 6:
        return {}
    mapping = _mapping_from(value)
    if mapping:
        sidecar = mapping.get("apps_rg_targeting_brief_sidecar")
        if isinstance(sidecar, dict):
            return dict(sidecar)
        for child in mapping.values():
            found = find_apps_rg_targeting_sidecar(child, _depth=_depth + 1)
            if found:
                return found
        return {}
    if isinstance(value, (list, tuple)):
        for child in value:
            found = find_apps_rg_targeting_sidecar(child, _depth=_depth + 1)
            if found:
                return found
    return {}


def _retryable_judge_serialization_error(exc: BaseException) -> bool:
    if not isinstance(exc, GraderError):
        return False
    message = str(exc).lower()
    return any(marker.lower() in message for marker in _RETRYABLE_JUDGE_PARSE_MARKERS)


def run_apps_rg_handoff_x2_judge(
    *,
    brief_text: str,
    jd_text: str,
    research_notes: str,
    source_register: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    judge: Any | None = None,
) -> dict[str, Any]:
    """Run the model-backed X2 semantic judge and return a sealed receipt."""
    dimension = Dimension(
        name="faithfulness",
        grader_class=GraderClass.MODEL_BASED,
        threshold=APPS_RG_HANDOFF_X2_THRESHOLD,
        is_hard_gate=True,
        abstain_allowed=True,
    )
    context = {
        "reference": (
            f"JD CONTEXT:\n{jd_text or '(not provided)'}\n\n"
            f"RESEARCH NOTES:\n{research_notes or '(not provided)'}\n\n"
            "SOURCE REGISTER:\n"
            + json.dumps(list(source_register), ensure_ascii=False, sort_keys=True)
        ),
        "agent_output": brief_text,
        "question": (
            "Does this apps_rg targeting briefing faithfully reflect the JD/research "
            "context and contain enough role-relevant evidence to hand off to apps_rg?"
        ),
    }
    resolved_judge = judge or GoogleJudge(
        model=APPS_RG_HANDOFF_JUDGE_MODEL,
        timeout=30.0,
        max_tokens=APPS_RG_HANDOFF_JUDGE_MAX_TOKENS,
    )
    base = {
        "schema_version": "apps_research.apps_rg_handoff_x2_judge_receipt.v1",
        "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
        "judge_name": APPS_RG_HANDOFF_JUDGE_NAME,
        "judge_provider": APPS_RG_HANDOFF_JUDGE_PROVIDER,
        "judge_model": APPS_RG_HANDOFF_JUDGE_MODEL,
        "threshold": APPS_RG_HANDOFF_X2_THRESHOLD,
        "model_backed": True,
    }
    response = None
    attempt = 0
    retryable_error = False
    for attempt in range(1, APPS_RG_HANDOFF_X2_MAX_ATTEMPTS + 1):
        try:
            response = resolved_judge.judge(dimension, context)
            break
        except (GraderError, TimeoutError, KeyError, ValueError, RuntimeError, OSError) as exc:
            retryable_error = _retryable_judge_serialization_error(exc)
            if retryable_error and attempt < APPS_RG_HANDOFF_X2_MAX_ATTEMPTS:
                continue
            return {
                **base,
                "status": "FAIL",
                "score": 0.0,
                "verdict": "FAIL",
                "provider_status": "JUDGE_PROVIDER_ERROR",
                "model_backed": False,
                "attempt_count": attempt,
                "retry_count": max(0, attempt - 1),
                "retryable_provider_error": retryable_error,
                "reason": f"{type(exc).__name__}: {exc}",
            }

    score = float(getattr(response, "score", 0.0) or 0.0)
    abstain = bool(getattr(response, "abstain", False))
    status = "UNKNOWN" if abstain else "PASS" if score >= APPS_RG_HANDOFF_X2_THRESHOLD else "FAIL"
    return {
        **base,
        "status": status,
        "score": score,
        "verdict": status,
        "provider_status": f"MODEL_BACKED_{status}",
        "attempt_count": attempt,
        "retry_count": max(0, attempt - 1),
        "retryable_provider_error": retryable_error,
        "reason": str(getattr(response, "reasoning", "") or ""),
    }


def x2_judge_receipt_passes(receipt: Mapping[str, Any] | None) -> bool:
    if not isinstance(receipt, Mapping):
        return False
    if receipt.get("status") != "PASS":
        return False
    if receipt.get("model_backed") is not True:
        return False
    if not str(receipt.get("judge_model") or "").strip():
        return False
    if not str(receipt.get("judge_provider") or receipt.get("judge_name") or "").strip():
        return False
    try:
        score = float(receipt.get("score"))
        threshold = float(receipt.get("threshold"))
    except (TypeError, ValueError):
        return False
    return score >= threshold


def validate_apps_rg_handoff_sidecar(
    sidecar: Mapping[str, Any] | None,
    *,
    expected_brief_sha: str,
) -> tuple[bool, str]:
    if not isinstance(sidecar, Mapping) or not sidecar:
        return False, "missing_apps_rg_handoff_sidecar"
    sidecar_sha = str(sidecar.get("brief_text_sha256") or "").strip()
    if sidecar_sha and sidecar_sha != expected_brief_sha:
        return False, "apps_rg_handoff_sidecar_digest_mismatch"
    if sidecar.get("generation_provider") != APPS_RG_HANDOFF_GENERATION_PROVIDER:
        return False, "generation_provider_not_external_openai"
    if not str(sidecar.get("generation_model") or "").strip():
        return False, "missing_generation_model"
    if not bool(sidecar.get("handoff_eligible")):
        return False, str(sidecar.get("reason") or "handoff_not_eligible")
    if not x2_judge_receipt_passes(sidecar.get("x2_judge_receipt")):
        return False, "x2_model_backed_judge_not_pass"
    return True, "ok"


def _verdict(
    *,
    gate_id: str,
    result: str,
    run_id: str,
    request_id: str,
    trace_root: str,
    packet_ref: str,
    reason_code: str,
    score: float = 0.0,
    threshold: float = 0.0,
    evidence_refs: tuple[str, ...] = (),
) -> GateVerdict:
    evaluated_at = datetime.now(timezone.utc).isoformat()
    severity = "hard_fail" if result == "FAIL" else "warn" if result == "WARN" else "advisory"
    payload = {
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
        confidence=score if score else (1.0 if result == "PASS" else 0.0),
        deterministic_digest=_sha256_json(payload),
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        evidence_digest=_sha256_json(
            {
                "packet_ref": packet_ref,
                "evidence_refs": list(evidence_refs),
                "reason_code": reason_code,
            }
        ),
        evaluator_version=APPS_RG_HANDOFF_GATE_MESH_SCHEMA,
        evaluated_at=evaluated_at,
        unknown_reason=reason_code if result == "UNKNOWN" else "",
        created_at=evaluated_at,
    )


def build_apps_rg_handoff_gate_mesh(
    *,
    run_id: str,
    request_id: str = "",
    trace_root: str,
    briefing_text: str,
    jd_text: str,
    sidecar: Mapping[str, Any] | None,
) -> GateMeshResult:
    """Build current-run GateVerdicts; Exit remains the sole X3 authority."""
    request_id = str(request_id or run_id)
    brief_sha = sha256_text(briefing_text)
    jd_sha = sha256_text(jd_text) if jd_text else ""
    sidecar_map = dict(sidecar or {})
    x2 = sidecar_map.get("x2_judge_receipt")
    x2_map = dict(x2) if isinstance(x2, Mapping) else {}

    answer_present = bool(briefing_text.strip()) and not looks_like_stub_company_brief(briefing_text)
    validation = validate_targeting_brief_text(
        briefing_text,
        jd_text=jd_text,
        profile="apps_rg",
    )
    source_register = sidecar_map.get("source_register")
    source_rows = list(source_register) if isinstance(source_register, (list, tuple)) else []
    evidence_present = any(
        isinstance(row, Mapping) and bool(row.get("has_content"))
        for row in source_rows
    )
    sidecar_sha = str(sidecar_map.get("brief_text_sha256") or "").strip()
    replay_ok = bool(run_id and brief_sha and (not sidecar_sha or sidecar_sha == brief_sha))
    sidecar_eligible, sidecar_reason = validate_apps_rg_handoff_sidecar(
        sidecar_map,
        expected_brief_sha=brief_sha,
    )

    x2_status = str(x2_map.get("status") or "UNKNOWN").upper()
    if x2_judge_receipt_passes(x2_map):
        x2_result = "PASS"
        x2_reason = "model_backed_x2_pass"
    elif x2_status == "UNKNOWN":
        x2_result = "UNKNOWN"
        x2_reason = "model_backed_x2_unknown"
    else:
        x2_result = "FAIL"
        x2_reason = str(x2_map.get("reason") or "model_backed_x2_fail")
    try:
        x2_score = float(x2_map.get("score") or 0.0)
        x2_threshold = float(x2_map.get("threshold") or APPS_RG_HANDOFF_X2_THRESHOLD)
    except (TypeError, ValueError):
        x2_score = 0.0
        x2_threshold = APPS_RG_HANDOFF_X2_THRESHOLD

    verdicts = (
        _verdict(
            gate_id="G5_ANSWER_PRESENT",
            result="PASS" if answer_present else "FAIL",
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code="brief_present_non_stub" if answer_present else "brief_missing_or_stub",
            evidence_refs=(brief_sha,),
        ),
        _verdict(
            gate_id="G6_ANSWER_RELEVANT",
            result=x2_result,
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code=x2_reason,
            score=x2_score,
            threshold=x2_threshold,
            evidence_refs=(str(x2_map.get("judge_model") or ""),),
        ),
        _verdict(
            gate_id="G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
            result="PASS" if evidence_present else "FAIL",
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code="source_register_present" if evidence_present else "source_register_empty",
            evidence_refs=tuple(
                str(row.get("family") or "")
                for row in source_rows
                if isinstance(row, Mapping) and row.get("has_content")
            ),
        ),
        _verdict(
            gate_id="G21_OUTPUT_SCHEMA",
            result="PASS" if validation.valid else "FAIL",
            run_id=run_id,
            request_id=request_id,
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
        _verdict(
            gate_id="G24_REPLAY_ELIGIBLE",
            result="PASS" if replay_ok else "FAIL",
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code="digest_lineage_bound" if replay_ok else "digest_lineage_mismatch",
            evidence_refs=tuple(ref for ref in (brief_sha, jd_sha, sidecar_sha) if ref),
        ),
        _verdict(
            gate_id="G26_EXIT_ELIGIBILITY",
            result="PASS" if sidecar_eligible else "FAIL",
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            packet_ref=brief_sha,
            reason_code="handoff_sidecar_eligible" if sidecar_eligible else sidecar_reason,
            evidence_refs=(brief_sha,),
        ),
    )
    return build_gate_mesh_result(
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_id="apps_research.company_brief_v1",
        evaluated_surface="apps_rg_targeting_brief",
        evaluated_packet_ref=brief_sha,
        required_gate_ids=_HANDOFF_REQUIRED_GATE_IDS,
        verdicts=verdicts,
    )


def _seal_exit_receipt(
    *,
    receipt: ExitDispositionReceipt,
    output_artifact_digest: str,
) -> ExitDispositionReceipt:
    seed = receipt.as_dict()
    seed["deterministic_digest"] = ""
    seed["output_artifact_digest"] = output_artifact_digest
    digest = _sha256_json(seed)
    return dataclasses.replace(
        receipt,
        output_artifact_digest=output_artifact_digest,
        deterministic_digest=digest,
    )


class _ExitGateMeshProxy:
    """Compatibility proxy for generic Exit bindings expecting ``summarize``."""

    def __init__(self, mesh: GateMeshResult) -> None:
        self._mesh = mesh

    def __getattr__(self, name: str) -> Any:
        return getattr(self._mesh, name)

    def summarize(self) -> dict[str, Any]:
        return self._mesh.as_dict()


def run_apps_rg_handoff_exit_authorization(
    *,
    run_id: str,
    request_id: str = "",
    trace_root: str,
    briefing_text: str,
    jd_text: str,
    sidecar: Mapping[str, Any] | None,
) -> AppsRgHandoffExitAuthorization:
    """Run GateMesh -> package-driven Exit and return the canonical X3 artifacts."""
    brief_sha = sha256_text(briefing_text)
    mesh = build_apps_rg_handoff_gate_mesh(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        briefing_text=briefing_text,
        jd_text=jd_text,
        sidecar=sidecar,
    )
    sealed = SealedWorkflowPackage(
        package_id=f"apps_research:{run_id}:apps_rg_targeting_brief",
        route_contract_ref="apps_research.company_brief_v1",
        workflow_ref="apps_research.single_step.targeting_brief",
        workflow_id=run_id,
        run_id=run_id,
        app_context="apps_research",
        trace_root=trace_root,
        completed_at=datetime.now(timezone.utc).isoformat(),
        merged_content=briefing_text,
        merged_content_digest=brief_sha,
        merged_payload_digest=brief_sha,
        runtime_gate_refs=(mesh.deterministic_digest,),
        terminal_class="success" if briefing_text.strip() else "failed",
        decisive_reason="targeting_brief_candidate_sealed_for_exit",
        replay_manifest=json.dumps(
            {
                "run_id": run_id,
                "trace_root": trace_root,
                "brief_sha256": brief_sha,
                "jd_sha256": sha256_text(jd_text) if jd_text else "",
                "gate_mesh_digest": mesh.deterministic_digest,
            },
            sort_keys=True,
        ),
    )
    gate_profile = GateProfile(
        profile_id=APPS_RG_HANDOFF_EXIT_PROFILE_ID,
        app_id="apps_research",
        task_class="company_brief",
        version="1",
        required_exit_gates=_HANDOFF_REQUIRED_GATE_IDS,
        gate_definitions={
            gate_id: {"required": "always"} for gate_id in _HANDOFF_REQUIRED_GATE_IDS
        },
    )
    review, receipt, exhaust = exit_bind_and_finalize_apps_research(
        gate_profile=gate_profile,
        exit_policy=ExitPolicy(),
        exit_input=ExitInput(
            sealed_l2_artifact=sealed,
            gate_mesh_result=_ExitGateMeshProxy(mesh),
            evidence={
                "brief_sha256": brief_sha,
                "jd_sha256": sha256_text(jd_text) if jd_text else "",
            },
        ),
        request_id=str(request_id or run_id),
        run_id=run_id,
        trace_root=trace_root,
        route_id="apps_research.company_brief_v1",
        commit_requested=False,
    )
    receipt = _seal_exit_receipt(
        receipt=receipt,
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


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _default_apps_research_runs_root() -> Path:
    return Path(__file__).resolve().parents[2] / "artifacts" / "apps_research" / "runs"


def _validated_u0_receipt(
    *,
    record: Any,
    run_id: str,
    trace_root: str,
    target_company: str,
    target_role: str,
) -> dict[str, Any]:
    """Return a real U0 receipt, running the shared validator if needed.

    Production records arrive through ``run_research_via_spine`` and already
    carry this receipt.  Direct library callers still traverse the same U0
    validator here; there is no fixture/test bypass.
    """
    existing = getattr(record, "apps_research_u0_receipt", None)
    if isinstance(existing, Mapping) and existing.get("status") == "PASS":
        receipt = dict(existing)
        authority = receipt.get("authority_validation_receipt")
        reflection = receipt.get("reflection_receipt")
        expected_digest = str(
            getattr(record, "apps_research_u0_receipt_digest", "") or ""
        )
        actual_digest = _sha256_bytes(
            json.dumps(
                receipt,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        )
        if (
            receipt.get("schema_version") != "apps_research.u0_receipt.v1"
            or receipt.get("authority_contract_id")
            != "apps_research_rg_e2e_authority"
            or not isinstance(authority, Mapping)
            or authority.get("passed") is not True
            or authority.get("allowed") is not True
            or not isinstance(reflection, Mapping)
            or reflection.get("legacy_authority_scan_passed") is not True
            or not expected_digest
            or expected_digest != actual_digest
        ):
            raise RuntimeError("apps_research record carries an invalid U0 receipt")
        return receipt

    from apps_research.runtime.profile_builder_adapter import parse_payload
    from apps_research.runtime.u0.binding import (
        u0_validate_apps_research,
    )

    parent_run_id = str(getattr(record, "parent_run_id", "") or run_id)
    request_id = str(getattr(record, "request_id", "") or run_id)
    tenant_id = str(getattr(record, "tenant_id", "") or "apps_research")
    envelope = parse_payload(
        {
            "target_company": target_company,
            "target_role": target_role,
            "topic": target_company,
            "request_id": request_id,
            "run_id": parent_run_id,
            "trace_id": trace_root,
            "tenant_id": tenant_id,
        }
    )
    if envelope is None:
        raise RuntimeError("apps_research U0 could not build handoff envelope")
    validated = u0_validate_apps_research(envelope)
    authority = getattr(validated, "authority_validation_receipt", None)
    reflection = getattr(validated, "reflection_receipt", None)
    normalized = _canonical_json_bytes(validated.app_payload, pretty=False)
    return {
        "schema_version": "apps_research.u0_receipt.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "request_id": validated.request_id,
        "parent_run_id": validated.run_id,
        "child_run_id": run_id,
        "trace_root": validated.trace_id,
        "tenant_id": validated.tenant_id,
        "raw_input_sha256": _sha256_bytes(normalized),
        "normalized_input_sha256": _sha256_bytes(normalized),
        "authority_validation_receipt": (
            dataclasses.asdict(authority) if dataclasses.is_dataclass(authority) else {}
        ),
        "reflection_receipt": (
            dataclasses.asdict(reflection) if dataclasses.is_dataclass(reflection) else {}
        ),
        "status": "PASS",
    }


def persist_apps_rg_targeting_brief_artifacts(
    *,
    record: Any,
    target_company: str,
    target_role: str,
    jd_text: str,
    runs_root: Path | None = None,
    generated_at_utc: str | None = None,
    mode: str = "brief",
    depth_profile: str = "",
) -> AppsRgTargetingArtifactBundle:
    """Authorize, stage, fsync, and atomically publish the v2 handoff bundle."""
    run_id = str(getattr(record, "run_id", "") or "").strip()
    if not run_id:
        raise RuntimeError("apps_research targeting run missing run_id")
    record_trace_root = str(
        getattr(record, "trace_root", "")
        or getattr(record, "trace_id", "")
        or run_id
    ).strip()
    company = str(target_company or getattr(record, "topic", "") or "").strip()
    role = str(target_role or "").strip()
    if not company or not role:
        raise RuntimeError("apps_research targeting run missing target company or role")
    briefing_text = str(getattr(record, "company_brief_text", "") or "").strip()
    if not briefing_text or looks_like_stub_company_brief(briefing_text):
        raise RuntimeError(
            "apps_research targeting run produced no usable company_brief_text; "
            f"terminal_error={getattr(record, 'hop_terminal_error', '')!r}"
        )
    sidecar = find_apps_rg_targeting_sidecar(
        getattr(record, "fec_run_context", {}) or {}
    )
    if not sidecar:
        raise RuntimeError("apps_research targeting run missing apps_rg handoff sidecar")

    u0_receipt = _validated_u0_receipt(
        record=record,
        run_id=run_id,
        trace_root=record_trace_root,
        target_company=company,
        target_role=role,
    )
    trace_root = str(u0_receipt.get("trace_root") or record_trace_root).strip()
    authorization = run_apps_rg_handoff_exit_authorization(
        run_id=run_id,
        request_id=str(u0_receipt.get("request_id") or run_id),
        trace_root=trace_root,
        briefing_text=briefing_text,
        jd_text=str(jd_text or ""),
        sidecar=sidecar,
    )
    if not authorization.allows_finish:
        receipt = authorization.exit_disposition_receipt
        raise RuntimeError(
            "apps_research targeting handoff blocked by canonical Exit: "
            f"x3={receipt.x3_code} reason={receipt.decisive_reason}"
        )

    safe_run_id = "".join(
        char if char.isalnum() or char in "._-" else "_" for char in run_id
    ).strip("._-")
    if not safe_run_id:
        raise RuntimeError("apps_research targeting run_id cannot form an artifact path")
    root = (runs_root or _default_apps_research_runs_root()).resolve()
    run_dir = root / safe_run_id
    briefing_path = run_dir / "briefing.md"
    company_brief_path = run_dir / "company_brief.json"
    metadata_path = run_dir / "run_metadata.json"
    gate_mesh_path = run_dir / "apps_research_gate_mesh_result.json"
    sealed_workflow_path = run_dir / "sealed_workflow_package.json"
    exit_review_path = run_dir / "exit_review_packet.json"
    exit_disposition_path = run_dir / "exit_disposition_receipt.json"
    runtime_exhaust_path = run_dir / "runtime_exhaust_bundle.json"
    handoff_v2_path = run_dir / "apps_research_apps_rg_handoff_v2.json"
    envelope_path = handoff_v2_path
    commit_manifest_path = run_dir / "bundle_commit_manifest.json"
    u0_receipt_path = run_dir / "apps_research_u0_receipt.json"
    raw_input_path = run_dir / "job_description.raw.txt"
    normalized_input_path = run_dir / "job_description.normalized.txt"
    emitted_at = generated_at_utc or datetime.now(timezone.utc).isoformat()
    briefing_bytes = (briefing_text + "\n").encode("utf-8")
    raw_input_bytes = str(jd_text or "").encode("utf-8") or b"\n"
    normalized_jd = str(jd_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized_input_bytes = (normalized_jd + "\n").encode("utf-8")
    exact_brief_sha256 = _sha256_bytes(briefing_bytes)
    exact_jd_sha256 = _sha256_bytes(normalized_input_bytes)
    payload = {
        "schema_version": "apps_research.company_brief_artifact.v3",
        "company": company,
        "run_id": run_id,
        "generated_at_utc": emitted_at,
        "targeting_format": "apps_rg_targeting_brief_v1",
        "company_brief_text": briefing_text,
        "brief_sha256": exact_brief_sha256,
        "exit_disposition_receipt_digest": (
            authorization.exit_disposition_receipt.deterministic_digest
        ),
        "x3_code": authorization.exit_disposition_receipt.x3_code,
        "apps_research_u0_receipt_digest": _sha256_bytes(
            _canonical_json_bytes(u0_receipt)
        ),
        "confidence_score": float(getattr(record, "confidence_score", 0.0) or 0.0),
        "support_coverage": float(getattr(record, "support_coverage", 0.0) or 0.0),
        "hop_terminal_error": str(getattr(record, "hop_terminal_error", "") or ""),
        "fec_run_context": _jsonable(getattr(record, "fec_run_context", {}) or {}),
    }
    metadata = {
        "run_id": run_id,
        "topic": company,
        "mode": str(mode or "brief"),
        "depth_profile": str(depth_profile or ""),
        "targeting_format": payload["targeting_format"],
        "company_brief_path": str(company_brief_path.resolve()),
        "briefing_path": str(briefing_path.resolve()),
        "gate_mesh_result_path": str(gate_mesh_path.resolve()),
        "sealed_workflow_package_path": str(sealed_workflow_path.resolve()),
        "exit_review_packet_path": str(exit_review_path.resolve()),
        "exit_disposition_receipt_path": str(exit_disposition_path.resolve()),
        "runtime_exhaust_bundle_path": str(runtime_exhaust_path.resolve()),
        "apps_research_apps_rg_handoff_v2_path": str(handoff_v2_path),
        "bundle_commit_manifest_path": str(commit_manifest_path),
        "apps_research_u0_receipt_path": str(u0_receipt_path),
        "brief_sha256": exact_brief_sha256,
        "jd_sha256": exact_jd_sha256,
        "exit_disposition_receipt_digest": (
            authorization.exit_disposition_receipt.deterministic_digest
        ),
        "x3_code": authorization.exit_disposition_receipt.x3_code,
    }

    root.mkdir(parents=True, exist_ok=True)
    if run_dir.exists():
        raise RuntimeError(f"apps_research committed run directory already exists: {run_dir}")
    stage_dir = root / f".{safe_run_id}.staging-{uuid.uuid4().hex}"

    artifact_payloads: dict[str, bytes] = {
        "job_description.raw.txt": raw_input_bytes,
        "job_description.normalized.txt": normalized_input_bytes,
        "apps_research_u0_receipt.json": _canonical_json_bytes(u0_receipt),
        "apps_research_gate_mesh_result.json": _canonical_json_bytes(
            authorization.gate_mesh_result.as_dict()
        ),
        "sealed_workflow_package.json": _canonical_json_bytes(
            authorization.sealed_workflow_package.as_dict()
        ),
        "exit_review_packet.json": _canonical_json_bytes(
            authorization.exit_review_packet.as_dict()
        ),
        "exit_disposition_receipt.json": _canonical_json_bytes(
            authorization.exit_disposition_receipt.as_dict()
        ),
        "runtime_exhaust_bundle.json": _canonical_json_bytes(
            authorization.runtime_exhaust_bundle.as_dict()
        ),
        "company_brief.json": _canonical_json_bytes(payload),
        "briefing.md": briefing_bytes,
        "run_metadata.json": _canonical_json_bytes(metadata),
    }
    media_types = {
        "briefing.md": "text/markdown; charset=utf-8",
        "job_description.raw.txt": "text/plain; charset=utf-8",
        "job_description.normalized.txt": "text/plain; charset=utf-8",
    }
    artifact_rows = [
        {
            "artifact_id": name.replace(".", "_").replace("-", "_"),
            "artifact_ref": str(run_dir / name),
            "sha256": _sha256_bytes(content),
            "byte_length": len(content),
            "media_type": media_types.get(name, "application/json"),
            "required": True,
        }
        for name, content in sorted(artifact_payloads.items())
    ]
    artifact_manifest_sha = _sha256_bytes(
        _canonical_json_bytes(artifact_rows, pretty=False)
    )
    handoff_id = f"apps-research-rg:{run_id}"
    marker = {
        "schema_version": "apps_research.apps_rg_bundle_commit_manifest.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "handoff_id": handoff_id,
        "artifact_manifest_sha256": artifact_manifest_sha,
        "artifact_count": len(artifact_rows),
        "status": "COMMITTED",
        "created_at_utc": emitted_at,
    }
    marker_bytes = _canonical_json_bytes(marker)

    repo_root = Path(__file__).resolve().parents[2]
    policy_path = repo_root / "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
    blueprint_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.json"
    policy_bytes = policy_path.read_bytes() if policy_path.is_file() else b"apps_research_rg_e2e_authority"
    blueprint_bytes = blueprint_path.read_bytes() if blueprint_path.is_file() else b"apps_research.company_brief.v1"
    identity = {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "parent_run_id": str(u0_receipt.get("parent_run_id") or run_id),
        "child_run_id": run_id,
        "request_id": str(u0_receipt.get("request_id") or run_id),
        "trace_root": trace_root,
        "tenant_id": str(u0_receipt.get("tenant_id") or "apps_research"),
        "target_company": company,
        "target_role": role,
        "jd_sha256": exact_jd_sha256,
        "brief_sha256": exact_brief_sha256,
        "policy_hash": _sha256_bytes(policy_bytes),
        "blueprint_hash": _sha256_bytes(blueprint_bytes),
        "schema_version": "apps_research_rg_run_identity.v1",
    }
    gate_mesh_sha = _sha256_bytes(artifact_payloads["apps_research_gate_mesh_result.json"])
    gate_map = {
        "G5": "G5_ANSWER_PRESENT",
        "G6": "G6_ANSWER_RELEVANT",
        "G7": "G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
        "G21": "G21_OUTPUT_SCHEMA",
        "G24": "G24_REPLAY_ELIGIBLE",
        "G26": "G26_EXIT_ELIGIBILITY",
    }
    passed_gates = {
        str(row.get("gate_id") or "")
        for row in authorization.gate_mesh_result.as_dict().get("verdicts", [])
        if isinstance(row, Mapping) and row.get("result") == "PASS"
    }
    if passed_gates != set(gate_map.values()):
        raise RuntimeError("apps_research handoff GateMesh is not the exact mandatory gate set")
    mandatory_gate_receipts = {
        short_id: {
            "gate_id": short_id,
            "status": "PASS",
            "receipt_ref": str(gate_mesh_path),
            "receipt_sha256": gate_mesh_sha,
            "schema_version": APPS_RG_HANDOFF_GATE_MESH_SCHEMA,
        }
        for short_id in gate_map
    }
    u0_receipt_sha = _sha256_bytes(artifact_payloads["apps_research_u0_receipt.json"])
    attestation_seed = {
        "identity": identity,
        "u0_receipt_sha256": u0_receipt_sha,
        "exit_receipt_sha256": _sha256_bytes(
            artifact_payloads["exit_disposition_receipt.json"]
        ),
    }
    handoff_v2 = {
        "schema_version": "apps_research.apps_rg_handoff.v2",
        "handoff_id": handoff_id,
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity": identity,
        "producer": {
            "producer_app_id": "apps_research",
            "producer_run_id": run_id,
            "attestation_sha256": _sha256_bytes(
                _canonical_json_bytes(attestation_seed, pretty=False)
            ),
        },
        "raw_input": {
            "artifact_ref": str(raw_input_path),
            "sha256": _sha256_bytes(raw_input_bytes),
            "byte_length": len(raw_input_bytes),
        },
        "normalized_input": {
            "artifact_ref": str(normalized_input_path),
            "sha256": exact_jd_sha256,
            "byte_length": len(normalized_input_bytes),
            "normalization_profile_hash": _sha256_bytes(
                b"apps_research.apps_rg.jd_normalization.v1"
            ),
            "raw_input_sha256": _sha256_bytes(raw_input_bytes),
        },
        "mandatory_gate_receipts": mandatory_gate_receipts,
        "exit_authorization": {
            "x3_code": X3D_ALLOW_FINISH,
            "receipt_ref": str(exit_disposition_path),
            "receipt_sha256": _sha256_bytes(
                artifact_payloads["exit_disposition_receipt.json"]
            ),
            "output_artifact_sha256": exact_brief_sha256,
        },
        "artifact_manifest": {
            "artifacts": artifact_rows,
            "artifact_count": len(artifact_rows),
            "manifest_sha256": artifact_manifest_sha,
        },
        "commit_protocol": {
            "protocol": "write_fsync_atomic_rename_marker.v1",
            "temporary_bundle_ref": str(stage_dir),
            "committed_bundle_ref": str(run_dir),
            "commit_marker_ref": str(commit_manifest_path),
            "commit_marker_sha256": _sha256_bytes(marker_bytes),
            "consumer_validation_receipt_name": "apps_research_handoff_validation_receipt.json",
        },
        "created_at_utc": emitted_at,
    }
    handoff_v2_bytes = _canonical_json_bytes(handoff_v2)

    stage_dir.mkdir(mode=0o700)
    try:
        for name, content in artifact_payloads.items():
            _write_fsync(stage_dir / name, content)
        _write_fsync(stage_dir / handoff_v2_path.name, handoff_v2_bytes)
        # Commit marker is intentionally the final file written in staging.
        _write_fsync(stage_dir / commit_manifest_path.name, marker_bytes)
        _fsync_directory(stage_dir)
        os.replace(stage_dir, run_dir)
        _fsync_directory(root)
    except BaseException:  # guardian: allow-broad-exception -- atomic publisher cleanup boundary; always re-raises
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        raise

    for required in (
        *[run_dir / name for name in artifact_payloads],
        handoff_v2_path,
        commit_manifest_path,
    ):
        if not required.is_file() or required.stat().st_size <= 0:
            raise RuntimeError(f"apps_research failed to publish required artifact: {required}")
    return AppsRgTargetingArtifactBundle(
        run_id=run_id,
        run_dir=run_dir.resolve(),
        briefing_path=briefing_path.resolve(),
        company_brief_path=company_brief_path.resolve(),
        envelope_path=envelope_path.resolve(),
        metadata_path=metadata_path.resolve(),
        envelope=handoff_v2,
        gate_mesh_path=gate_mesh_path.resolve(),
        sealed_workflow_path=sealed_workflow_path.resolve(),
        exit_review_path=exit_review_path.resolve(),
        exit_disposition_path=exit_disposition_path.resolve(),
        runtime_exhaust_path=runtime_exhaust_path.resolve(),
        handoff_v2_path=handoff_v2_path.resolve(),
        commit_manifest_path=commit_manifest_path.resolve(),
        u0_receipt_path=u0_receipt_path.resolve(),
        raw_input_path=raw_input_path.resolve(),
        normalized_input_path=normalized_input_path.resolve(),
        brief_sha256=exact_brief_sha256,
        result_metadata_digest=_sha256_bytes(artifact_payloads["run_metadata.json"]),
        bundle_manifest_digest=_sha256_bytes(handoff_v2_bytes),
    )


__all__ = [
    "APPS_RG_HANDOFF_EXIT_PROFILE_ID",
    "APPS_RG_HANDOFF_GENERATION_PROVIDER",
    "APPS_RG_HANDOFF_JUDGE_MODEL",
    "APPS_RG_HANDOFF_JUDGE_NAME",
    "APPS_RG_HANDOFF_JUDGE_PROVIDER",
    "APPS_RG_HANDOFF_X2_THRESHOLD",
    "AppsRgHandoffExitAuthorization",
    "AppsRgTargetingArtifactBundle",
    "build_apps_rg_handoff_gate_mesh",
    "find_apps_rg_targeting_sidecar",
    "looks_like_stub_company_brief",
    "persist_apps_rg_targeting_brief_artifacts",
    "run_apps_rg_handoff_exit_authorization",
    "run_apps_rg_handoff_x2_judge",
    "sha256_text",
    "validate_apps_rg_handoff_sidecar",
    "x2_judge_receipt_passes",
]
