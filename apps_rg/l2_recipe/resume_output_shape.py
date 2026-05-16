"""Classify apps_rg structured résumé model output (post-parse).

Fail-closed gate: a JSON object whose only key is ``raw_text`` is not a
structured résumé artifact — it is a malformed model-output wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "BLOCKED_PROVIDER_LANE",
    "BLOCKED_STUB_PROVIDER",
    "FAILED_ARTIFACT_GATE",
    "FAILED_PROVIDER",
    "INCOMPLETE_STRUCTURE",
    "MALFORMED_MODEL_OUTPUT",
    "NO_RESUME_PAYLOAD",
    "REAL_RESUME",
    "ResumeShapeReport",
    "STUB_RECEIPT",
    "STRUCTURED_RESUME_OK",
    "classify_resume_payload",
    "is_raw_text_only_wrapper",
    "is_real_resume_shape_report",
]

# W2: canonical full-résumé product token; legacy alias for STRUCTURED_RESUME_OK.
REAL_RESUME = "REAL_RESUME"
STRUCTURED_RESUME_OK = REAL_RESUME
MALFORMED_MODEL_OUTPUT = "MALFORMED_MODEL_OUTPUT"
INCOMPLETE_STRUCTURE = "INCOMPLETE_STRUCTURE"
NO_RESUME_PAYLOAD = "NO_RESUME_PAYLOAD"
BLOCKED_STUB_PROVIDER = "BLOCKED_STUB_PROVIDER"
BLOCKED_PROVIDER_LANE = "BLOCKED_PROVIDER_LANE"
FAILED_PROVIDER = "FAILED_PROVIDER"
FAILED_ARTIFACT_GATE = "FAILED_ARTIFACT_GATE"
STUB_RECEIPT = "STUB_RECEIPT"

_REQUIRED_FIELDS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "competencies",
    "professional_experience",
    "education",
    "certifications",
)


def is_raw_text_only_wrapper(payload: dict[str, Any] | None) -> bool:
    """True when *payload* is exactly ``{\"raw_text\": ...}`` (single key)."""
    if not payload:
        return False
    return set(payload.keys()) == {"raw_text"}


def _skills_to_competencies(skills_block: Any) -> list[Any]:
    """``sections.skills`` may be a list (legacy) or ``{\"categories\": [...]}`` (rg_output_schema)."""
    if isinstance(skills_block, list):
        return skills_block
    if isinstance(skills_block, dict):
        cats = skills_block.get("categories")
        if not isinstance(cats, list):
            return []
        out: list[str] = []
        for c in cats:
            if isinstance(c, dict):
                for x in c.get("items") or []:
                    if x:
                        out.append(str(x))
            elif c:
                out.append(str(c))
        return out
    return []


def _normalize_classifier_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """If payload follows ``rg_output_schema`` (nested ``sections``), map to flat classifier fields."""
    sec = payload.get("sections")
    if not isinstance(sec, dict):
        return payload

    summary = sec.get("summary")
    summary_text = ""
    if isinstance(summary, dict):
        summary_text = str(summary.get("text", "") or "")

    exp_raw = sec.get("experience")
    exp_list = exp_raw if isinstance(exp_raw, list) else []
    prof: list[dict[str, Any]] = []
    for role in exp_list:
        if not isinstance(role, dict):
            continue
        prof.append(
            {
                "company": str(role.get("company", "") or ""),
                "title": str(role.get("title", "") or ""),
                "location": str(role.get("location", "") or ""),
                "dates": str(role.get("dates", "") or ""),
                "summary": "",
                "bullets": list(role.get("bullets") or [])
                if isinstance(role.get("bullets"), list)
                else [],
            }
        )

    comps = _skills_to_competencies(sec.get("skills"))
    edu_raw = sec.get("education")
    edu = list(edu_raw) if isinstance(edu_raw, list) else []
    cert_raw = sec.get("certifications")
    certs = list(cert_raw) if isinstance(cert_raw, list) else []

    headline = str(payload.get("target_role") or payload.get("headline") or "").strip()
    return {
        "headline": headline,
        "executive_summary": summary_text,
        "competencies": comps,
        "professional_experience": prof,
        "education": edu,
        "certifications": certs,
    }


@dataclass(frozen=True, slots=True)
class ResumeShapeReport:
    generation_status: str
    full_resume_generated: bool
    resume_shape: str


def is_real_resume_shape_report(rep: ResumeShapeReport) -> bool:
    """True only for bounded REAL_RESUME (W2) — stub/provider failure tokens excluded."""
    return (
        rep.generation_status == REAL_RESUME
        and rep.full_resume_generated is True
        and rep.resume_shape == REAL_RESUME
    )


def classify_resume_payload(payload: dict[str, Any] | None) -> ResumeShapeReport:
    """Return generation / shape signals for exit and telemetry.

    ``MALFORMED_MODEL_OUTPUT`` + ``RAW_TEXT_ONLY`` applies to the strict
    single-key ``raw_text`` wrapper (parsed JSON or normalized dict).
    """
    if not payload:
        return ResumeShapeReport(
            generation_status=NO_RESUME_PAYLOAD,
            full_resume_generated=False,
            resume_shape="EMPTY",
        )
    if payload.get("stub_response") is True:
        return ResumeShapeReport(
            generation_status=STUB_RECEIPT,
            full_resume_generated=False,
            resume_shape=STUB_RECEIPT,
        )
    if is_raw_text_only_wrapper(payload):
        return ResumeShapeReport(
            generation_status=MALFORMED_MODEL_OUTPUT,
            full_resume_generated=False,
            resume_shape="RAW_TEXT_ONLY",
        )
    effective = _normalize_classifier_payload(payload)
    missing = [k for k in _REQUIRED_FIELDS if k not in effective]
    if missing:
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    headline = effective.get("headline")
    summary = effective.get("executive_summary")
    comps = effective.get("competencies")
    roles = effective.get("professional_experience")
    edu = effective.get("education")
    certs = effective.get("certifications")

    if not isinstance(headline, str) or not headline.strip():
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    if not isinstance(summary, str) or not summary.strip():
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    if not isinstance(comps, list) or not comps:
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    if not isinstance(roles, list) or not roles:
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    if not isinstance(edu, list):
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    if not isinstance(certs, list):
        return ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        )
    return ResumeShapeReport(
        generation_status=REAL_RESUME,
        full_resume_generated=True,
        resume_shape=REAL_RESUME,
    )
