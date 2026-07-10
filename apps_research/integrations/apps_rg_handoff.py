"""apps_research -> apps_rg targeting-brief handoff contract."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.dimension import Dimension, GraderClass
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges.google_judge import GoogleJudge

APPS_RG_HANDOFF_GENERATION_PROVIDER = "external_openai"
APPS_RG_HANDOFF_JUDGE_NAME = "gemini_pro"
APPS_RG_HANDOFF_JUDGE_PROVIDER = "gemini_pro"
APPS_RG_HANDOFF_JUDGE_MODEL = "gemini-3.1-pro-preview"
APPS_RG_HANDOFF_X2_THRESHOLD = 0.75
APPS_RG_HANDOFF_JUDGE_MAX_TOKENS = 4096
APPS_RG_HANDOFF_X2_MAX_ATTEMPTS = 2
_RETRYABLE_JUDGE_PARSE_MARKERS = (
    "no JSON object",
    "incomplete JSON object",
    "judge JSON parse failed",
    "judge response was not JSON",
    "response had no text part",
)


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


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


def build_apps_rg_handoff_envelope(
    *,
    sidecar: Mapping[str, Any],
    run_id: str,
    target_company: str,
    target_role: str,
    briefing_text: str,
    jd_text: str,
    generated_at_utc: str,
    briefing_path: str = "",
    company_brief_path: str = "",
) -> dict[str, Any]:
    """Build the authoritative apps_research handoff envelope."""
    expected_brief_sha = sha256_text(briefing_text)
    if looks_like_stub_company_brief(briefing_text):
        raise RuntimeError("apps_research targeting run produced stub-like handoff brief")
    eligible, reason = validate_apps_rg_handoff_sidecar(
        sidecar,
        expected_brief_sha=expected_brief_sha,
    )
    if not eligible:
        raise RuntimeError(f"apps_research targeting handoff not eligible: {reason}")

    emitted_at = datetime.fromisoformat(generated_at_utc.replace("Z", "+00:00"))
    expires_at = emitted_at + timedelta(days=7)
    jd_sha = sha256_text(jd_text) if jd_text else ""
    x2_receipt = dict(sidecar.get("x2_judge_receipt") or {})
    score = x2_receipt.get("score")
    threshold = x2_receipt.get("threshold")
    x1_x3_authorization = {
        "schema_version": "apps_research.apps_rg_handoff_x1_x3_authorization.v1",
        "run_id": run_id,
        "brief_sha256": expected_brief_sha,
        "jd_sha256": jd_sha,
        "x1": {
            "gate_id": "X1_TARGETING_BRIEF_CONTRACT",
            "status": "PASS",
            "evidence": "brief text present, non-stub, digest-bound",
        },
        "x2": {
            "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
            "status": "PASS",
            "score": score,
            "threshold": threshold,
            "judge_name": x2_receipt.get("judge_name"),
            "judge_provider": x2_receipt.get("judge_provider"),
            "judge_model": x2_receipt.get("judge_model"),
            "model_backed": True,
            "provider_status": x2_receipt.get("provider_status"),
        },
        "x3": {
            "gate_id": "X3_HANDOFF_AUTHORIZATION",
            "status": "PASS",
            "disposition": "ALLOW",
            "reason": "model_backed_x2_passed",
        },
    }
    return {
        "schema_version": "apps_research.apps_rg_briefing_envelope.v1",
        "producer_app": "apps_research",
        "consumer_app": "apps_rg",
        "run_id": run_id,
        "target_company": target_company,
        "target_role": target_role,
        "generated_at_utc": generated_at_utc,
        "expires_at_utc": expires_at.isoformat(),
        "dry_run": False,
        "stub_detected": False,
        "is_stale": False,
        "handoff_eligible": True,
        "generation_provider": sidecar.get("generation_provider"),
        "generation_model": sidecar.get("generation_model"),
        "provider_call_attempted": bool(sidecar.get("provider_call_attempted", True)),
        "brief_sha256": expected_brief_sha,
        "jd_sha256": jd_sha,
        "apps_research_x1_x3_authorization": x1_x3_authorization,
        "apps_research_x2_judge_receipt": x2_receipt,
        "briefing_path": briefing_path,
        "company_brief_path": company_brief_path,
        "semantic_assessment": {
            "score": score,
            "threshold": threshold,
            "judge_name": x2_receipt.get("judge_name"),
            "judge_provider": x2_receipt.get("judge_provider"),
            "judge_model": x2_receipt.get("judge_model"),
            "model_backed": True,
            "role_archetype": sidecar.get("role_archetype"),
            "required_sections_present": sidecar.get("required_sections_present", []),
            "missing_sections": sidecar.get("missing_sections", []),
            "source_families_present": sidecar.get("source_families_present", []),
            "source_families_missing": sidecar.get("source_families_missing", []),
            "signal_terms_present": sidecar.get("signal_terms_present", []),
            "signal_terms_missing": sidecar.get("signal_terms_missing", []),
        },
        "source_register": sidecar.get("source_register", []),
        "upstream_sidecar": dict(sidecar),
    }


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
    """Validate and persist the apps_research-owned handoff bundle.

    Both the direct apps_research CLI and the managed apps_rg bridge call this
    writer. A handoff is not product evidence until every returned path exists.
    """
    run_id = str(getattr(record, "run_id", "") or "").strip()
    if not run_id:
        raise RuntimeError("apps_research targeting run missing run_id")
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

    safe_run_id = "".join(
        char if char.isalnum() or char in "._-" else "_" for char in run_id
    ).strip("._-")
    if not safe_run_id:
        raise RuntimeError("apps_research targeting run_id cannot form an artifact path")
    run_dir = (runs_root or _default_apps_research_runs_root()) / safe_run_id
    briefing_path = run_dir / "briefing.md"
    company_brief_path = run_dir / "company_brief.json"
    envelope_path = run_dir / "apps_research_briefing_envelope.json"
    metadata_path = run_dir / "run_metadata.json"
    emitted_at = generated_at_utc or datetime.now(timezone.utc).isoformat()
    envelope = build_apps_rg_handoff_envelope(
        sidecar=sidecar,
        run_id=run_id,
        target_company=company,
        target_role=role,
        briefing_text=briefing_text,
        jd_text=str(jd_text or ""),
        generated_at_utc=emitted_at,
        briefing_path=str(briefing_path.resolve()),
        company_brief_path=str(company_brief_path.resolve()),
    )
    payload = {
        "schema_version": "apps_research.company_brief_artifact.v2",
        "company": company,
        "run_id": run_id,
        "generated_at_utc": emitted_at,
        "targeting_format": "apps_rg_targeting_brief_v1",
        "company_brief_text": briefing_text,
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
        "apps_research_briefing_envelope_path": str(envelope_path.resolve()),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    company_brief_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    briefing_path.write_text(briefing_text + "\n", encoding="utf-8")
    envelope_path.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for required in (
        briefing_path,
        company_brief_path,
        envelope_path,
        metadata_path,
    ):
        if not required.is_file() or required.stat().st_size <= 0:
            raise RuntimeError(f"apps_research failed to persist required artifact: {required}")
    return AppsRgTargetingArtifactBundle(
        run_id=run_id,
        run_dir=run_dir.resolve(),
        briefing_path=briefing_path.resolve(),
        company_brief_path=company_brief_path.resolve(),
        envelope_path=envelope_path.resolve(),
        metadata_path=metadata_path.resolve(),
        envelope=envelope,
    )


__all__ = [
    "APPS_RG_HANDOFF_GENERATION_PROVIDER",
    "APPS_RG_HANDOFF_JUDGE_MODEL",
    "APPS_RG_HANDOFF_JUDGE_NAME",
    "APPS_RG_HANDOFF_JUDGE_PROVIDER",
    "APPS_RG_HANDOFF_X2_THRESHOLD",
    "AppsRgTargetingArtifactBundle",
    "build_apps_rg_handoff_envelope",
    "find_apps_rg_targeting_sidecar",
    "looks_like_stub_company_brief",
    "persist_apps_rg_targeting_brief_artifacts",
    "run_apps_rg_handoff_x2_judge",
    "sha256_text",
    "validate_apps_rg_handoff_sidecar",
    "x2_judge_receipt_passes",
]
