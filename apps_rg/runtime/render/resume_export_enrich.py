"""Enrich LLM-generated resume JSON before DOCX export using the static profile.

The profile is a static identity spine only. It may supply contact, name, location, current title,
and certifications. It must not supply skills, bullets, summaries, accomplishments, metrics, or
role claims.
"""
from __future__ import annotations

import copy
import json
from typing import Any


def parse_static_profile_json(blob: str | None) -> dict[str, Any] | None:
    if not blob or not str(blob).strip():
        return None
    s = str(blob).strip()
    if not s.startswith("{"):
        return None
    try:
        d = json.loads(s)
    except json.JSONDecodeError:  # guardian: allow-return-none-swallow -- fail-soft optional boundary
        return None
    return d if isinstance(d, dict) else None


def contact_from_static_profile(profile: dict[str, Any]) -> dict[str, str]:
    """Phone, email, linkedin, github, and location from the static profile."""
    out: dict[str, str] = {}
    for k in ("phone", "email", "linkedin", "github", "location"):
        raw = profile.get(k)
        if raw is None:
            continue
        v = str(raw).strip()
        if v:
            out[k] = v
    return out


def verbatim_identity_from_static_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Name + contact fields copied verbatim from the static profile."""
    name = str(profile.get("name") or "").strip()
    out: dict[str, Any] = {"candidate_name": name}
    contact = contact_from_static_profile(profile)
    if contact:
        out["header_contact"] = contact
    return out


def skills_categories_from_static_profile(profile: dict[str, Any]) -> None:
    """Static profile is not a skills authority; skills must come from graph-backed payloads."""
    return None


def certifications_from_static_profile(profile: dict[str, Any]) -> list[dict[str, Any]]:
    raw = profile.get("certifications")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for cert in raw:
        if not isinstance(cert, dict):
            continue
        name = str(cert.get("name") or "").strip()
        if not name:
            continue
        row: dict[str, Any] = {"name": name}
        issuer = str(cert.get("issuer") or cert.get("issuing_organization") or "").strip()
        if issuer:
            row["issuer"] = issuer
        year = cert.get("year") or cert.get("date")
        if year is not None and str(year).strip():
            row["date"] = str(year).strip()
        out.append(row)
    return out


def _candidate_name_tokens(name: str) -> list[str]:
    parts = []
    for p in name.split():
        x = p.strip(".,'\"")
        if len(x) >= 3:
            parts.append(x.lower())
    return parts


def repair_headline_name_leak(headline_line: str, profile: dict[str, Any] | None) -> str:
    """If headline contains given/family name tokens, replace segment 1 with current role title."""
    h = (headline_line or "").strip()
    if not h or not profile:
        return h
    name = str(profile.get("name") or "").strip()
    if not name:
        return h
    tokens = _candidate_name_tokens(name)
    hl_low = h.lower()
    if not any(t in hl_low for t in tokens):
        return h
    emp = list(profile.get("employment_identity") or [])
    title = ""
    for e in emp:
        if isinstance(e, dict) and str(e.get("end_date") or "").strip().lower() in {"present", "current"}:
            title = str(e.get("title") or "").strip()
            break
    if not title and emp and isinstance(emp[0], dict):
        title = str(emp[0].get("title") or "").strip()
    if not title:
        return h
    parts = [p.strip() for p in h.split("|")]
    if len(parts) != 3:
        return h
    parts[0] = title
    return " | ".join(parts)


def enrich_generated_resume_for_docx(payload: dict[str, Any], static_profile_json: str | None) -> dict[str, Any]:
    """Return deep copy of ``payload`` merged with static profile fields for export."""
    out = copy.deepcopy(payload)
    profile = parse_static_profile_json(static_profile_json)
    if not profile:
        return out
    ident = verbatim_identity_from_static_profile(profile)
    cname = str(ident.get("candidate_name") or "").strip()
    if cname:
        out["candidate_name"] = cname
    hc = ident.get("header_contact") if isinstance(ident.get("header_contact"), dict) else {}
    existing = out.get("contact_info") if isinstance(out.get("contact_info"), dict) else {}
    merged_ci: dict[str, str] = {**{k: str(v) for k, v in existing.items() if v}}
    for k, v in hc.items():
        merged_ci[str(k)] = str(v).strip()
    if merged_ci:
        out["contact_info"] = merged_ci
    hl = str(out.get("headline_line") or "").strip()
    if hl:
        out["headline_line"] = repair_headline_name_leak(hl, profile)
    sec = out.get("sections")
    if not isinstance(sec, dict):
        return out
    c0 = sec.get("certifications")
    if not isinstance(c0, list) or len(c0) == 0:
        nc = certifications_from_static_profile(profile)
        if nc:
            sec["certifications"] = nc
    return out


# Backward-compatible aliases for older callers; active runtime callers use static-profile names.
parse_base_resume_json = parse_static_profile_json
contact_from_base_resume = contact_from_static_profile
verbatim_identity_from_base_resume = verbatim_identity_from_static_profile
skills_categories_from_base_resume = skills_categories_from_static_profile

__all__ = [
    "certifications_from_static_profile",
    "contact_from_static_profile",
    "enrich_generated_resume_for_docx",
    "parse_static_profile_json",
    "repair_headline_name_leak",
    "skills_categories_from_static_profile",
    "verbatim_identity_from_static_profile",
]
