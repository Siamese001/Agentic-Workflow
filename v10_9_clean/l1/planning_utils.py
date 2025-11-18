# FILE: v10_9_clean/l1/planning_utils.py
"""
L1 Planning Utilities (v10_9)
Pure deterministic helpers for planning layers (Strategy, RAG, Draft).
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, List


def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}

    def _first(*keys: str) -> str:
        for key in keys:
            v = job.get(key)
            if v:
                return str(v)
        return ""

    raw_reqs = (
        job.get("top_requirements")
        or job.get("required_skills")
        or job.get("keywords")
        or job.get("skills")
        or []
    )

    if isinstance(raw_reqs, str):
        requirements = [r.strip() for r in raw_reqs.split(",") if r.strip()]
    elif isinstance(raw_reqs, Iterable):
        requirements = [str(r).strip() for r in raw_reqs if str(r).strip()]
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
    master = resume.get("master_resume") or {}

    summary = (
        master.get("summary")
        or master.get("professional_summary")
        or master.get("profile")
        or ""
    )

    exps = master.get("professional_experience")
    if not isinstance(exps, list):
        exps = []

    return {"summary": str(summary), "experiences": exps}


def describe_experience(exp: Dict[str, Any]) -> str:
    title = exp.get("title") or exp.get("role") or "Role"
    company = exp.get("company") or exp.get("employer") or "Company"
    scope = (
        exp.get("impact_summary")
        or exp.get("summary")
        or exp.get("description")
        or ""
    )

    s = f"{title} @ {company}"
    if scope:
        s = f"{s} – {scope}"
    return s.strip()


def detect_metrics(exps: List[Dict[str, Any]]) -> List[str]:
    metrics: List[str] = []
    for exp in exps:
        texts: List[str] = []
        for key in ("impact_summary", "summary", "description"):
            v = exp.get(key)
            if v:
                texts.append(str(v))

        bullets = exp.get("bullet_pool")
        if isinstance(bullets, list):
            texts.extend(str(b) for b in bullets)

        combined = " ".join(texts)
        if any(ch.isdigit() for ch in combined):
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


def missing_requirements(reqs: List[str], exps: List[Dict[str, Any]]) -> List[str]:
    if not reqs:
        return []

    combined = " ".join(
        str(exp.get("impact_summary") or exp.get("summary") or "")
        for exp in exps
    ).lower()

    return [r for r in reqs if r.lower() not in combined]
