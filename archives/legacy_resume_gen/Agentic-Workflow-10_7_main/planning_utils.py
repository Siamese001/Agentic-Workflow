"""Shared helpers for lightweight L1 planning stacks."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}

    def _first(*keys: str) -> str:
        for key in keys:
            value = job.get(key)
            if value:
                return str(value)
        return ""

    raw_requirements = (
        job.get("top_requirements")
        or job.get("required_skills")
        or job.get("keywords")
        or job.get("skills")
        or []
    )
    requirements: List[str]
    if isinstance(raw_requirements, str):
        requirements = [part.strip() for part in raw_requirements.split(",") if part.strip()]
    elif isinstance(raw_requirements, Iterable):
        requirements = [str(item).strip() for item in raw_requirements if str(item).strip()]
    else:
        requirements = []

    return {
        "title": _first("job_title", "title", "role"),
        "company": _first("company", "employer", "organization"),
        "summary": _first("summary", "description", "jd_excerpt", "jd"),
        "team": _first("team", "org_unit", "department"),
        "location": _first("location", "city"),
        "requirements": requirements,
    }


def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume") or {}
    master_resume = resume.get("master_resume") or {}
    summary = (
        master_resume.get("summary")
        or master_resume.get("professional_summary")
        or master_resume.get("profile")
        or ""
    )
    experiences = master_resume.get("professional_experience")
    if not isinstance(experiences, list):
        experiences = []
    return {"summary": str(summary), "experiences": experiences}


def describe_experience(experience: Dict[str, Any]) -> str:
    title = experience.get("title") or experience.get("role") or "Role"
    company = experience.get("company") or experience.get("employer") or "Company"
    scope = (
        experience.get("impact_summary")
        or experience.get("summary")
        or experience.get("description")
        or ""
    )
    description = f"{title} @ {company}".strip()
    if scope:
        description = f"{description} – {scope}".strip()
    return description


def detect_metrics(experiences: List[Dict[str, Any]]) -> List[str]:
    metrics: List[str] = []
    for exp in experiences:
        text_parts: List[str] = []
        for key in ("impact_summary", "summary", "description"):
            value = exp.get(key)
            if value:
                text_parts.append(str(value))
        bullet_pool = exp.get("bullet_pool")
        if isinstance(bullet_pool, list):
            text_parts.extend(str(item) for item in bullet_pool)
        combined = " ".join(text_parts)
        if any(char.isdigit() for char in combined):
            metrics.append(f"Quantify results from {describe_experience(exp)}")
    if not metrics:
        metrics.append("Quantify at least one outcome per bullet")
    return metrics


def collect_sections(state: Dict[str, Any]) -> List[str]:
    draft = state.get("draft") or {}
    sections = draft.get("sections")
    if isinstance(sections, dict) and sections:
        return list(sections.keys())
    return ["summary", "experience", "skills"]


def missing_requirements(requirements: List[str], experiences: List[Dict[str, Any]]) -> List[str]:
    if not requirements:
        return []
    combined = " ".join(
        str(exp.get("impact_summary") or exp.get("summary") or "") for exp in experiences
    ).lower()
    missing = [req for req in requirements if req.lower() not in combined]
    return missing
