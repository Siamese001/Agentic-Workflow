"""Enrich LLM-generated résumé JSON before DOCX export using canonical base resume.

Legacy monolithic envelope output often omits ``contact_info``, strips ``sections.skills``
categories, or drops certifications. Modular lanes can still gap when a lane is thin.
This module merges **non-semantic** parity fields from the same base JSON used for PA/C0
so exports match ``amit_ayer_base_resume_v1``-class quality for header and competency tables.
"""
from __future__ import annotations

import copy
import json
import re
from typing import Any

from apps_rg.l2_recipe.modular_rg_output_builder import _certs_from_base


def _facts_blob(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("facts", data) if isinstance(data.get("facts"), dict) else data


def parse_base_resume_json(blob: str | None) -> dict[str, Any] | None:
    if not blob or not str(blob).strip():
        return None
    s = str(blob).strip()
    if not s.startswith("{"):
        return None
    try:
        d = json.loads(s)
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) else None


def contact_from_base_resume(base: dict[str, Any]) -> dict[str, str]:
    """Phone, email, linkedin, github from base ``header`` (top-level or under ``facts``)."""
    facts = _facts_blob(base)
    hdr_top = base.get("header") if isinstance(base.get("header"), dict) else {}
    hdr_facts = facts.get("header") if isinstance(facts.get("header"), dict) else {}
    merged: dict[str, Any] = {**hdr_facts, **hdr_top}
    out: dict[str, str] = {}
    for k in ("phone", "email", "linkedin", "github"):
        raw = merged.get(k)
        if raw is None:
            continue
        v = str(raw).strip()
        if v:
            out[k] = v
    return out


def verbatim_identity_from_base_resume(base: dict[str, Any]) -> dict[str, Any]:
    """Name + header contact fields copied verbatim from canonical base JSON (no rewriting).

    Used by DOCX assembly/export so the emitted document header matches SSOT base resume strings.
    """
    facts = _facts_blob(base)
    hdr_top = base.get("header") if isinstance(base.get("header"), dict) else {}
    hdr_facts = facts.get("header") if isinstance(facts.get("header"), dict) else {}
    merged: dict[str, Any] = {**hdr_facts, **hdr_top}

    name = ""
    if isinstance(base.get("candidate_name"), str) and base["candidate_name"].strip():
        name = base["candidate_name"].strip()
    else:
        n = str(merged.get("name") or "").strip()
        if n:
            name = n

    out: dict[str, Any] = {"candidate_name": name}
    contact: dict[str, str] = {}
    for k in ("phone", "email", "linkedin", "github", "location"):
        raw = merged.get(k)
        if raw is None:
            continue
        v = str(raw).strip()
        if v:
            contact[k] = v
    if contact:
        out["header_contact"] = contact
    return out


def skills_categories_from_base_resume(base: dict[str, Any]) -> dict[str, Any] | None:
    """Map ``facts.skills[]`` (category + terms) → ``sections.skills`` categories shape."""
    facts = _facts_blob(base)
    raw = facts.get("skills")
    if not isinstance(raw, list) or not raw:
        return None
    categories: list[dict[str, Any]] = []
    for row in raw[:12]:
        if not isinstance(row, dict):
            continue
        cat = str(row.get("category") or "").strip()
        terms = row.get("terms") or []
        if not isinstance(terms, list):
            continue
        items = [str(t).strip() for t in terms if str(t).strip()]
        if not cat or not items:
            continue
        categories.append({"name": cat, "items": items[:16]})
    if not categories:
        return None
    return {"categories": categories}


def _candidate_name_tokens(name: str) -> list[str]:
    parts = []
    for p in name.split():
        x = p.strip(".,'\"")
        if len(x) >= 3:
            parts.append(x.lower())
    return parts


def repair_headline_name_leak(headline_line: str, base: dict[str, Any] | None) -> str:
    """If headline contains given/family name tokens, replace segment 1 with current role title."""
    h = (headline_line or "").strip()
    if not h or not base:
        return h
    name = str(base.get("candidate_name") or "").strip()
    hdr = base.get("header") if isinstance(base.get("header"), dict) else {}
    if not name:
        name = str(hdr.get("name") or "").strip()
    if not name:
        return h
    tokens = _candidate_name_tokens(name)
    hl_low = h.lower()
    if not any(t in hl_low for t in tokens):
        return h
    facts = _facts_blob(base)
    emp = list(facts.get("employment") or [])
    title = ""
    for e in emp:
        if isinstance(e, dict) and e.get("is_current"):
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


def enrich_generated_resume_for_docx(payload: dict[str, Any], master_resume_json: str | None) -> dict[str, Any]:
    """Return deep copy of ``payload`` merged with base parity fields for export."""
    out = copy.deepcopy(payload)
    base = parse_base_resume_json(master_resume_json)
    if not base:
        return out
    ident = verbatim_identity_from_base_resume(base)
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
        out["headline_line"] = repair_headline_name_leak(hl, base)
    sec = out.get("sections")
    if not isinstance(sec, dict):
        return out
    sk = sec.get("skills")
    need_skills = False
    if sk is None:
        need_skills = True
    elif isinstance(sk, list) and len(sk) == 0:
        need_skills = True
    elif isinstance(sk, dict):
        cats = sk.get("categories")
        if not isinstance(cats, list) or len(cats) == 0:
            need_skills = True
    if need_skills:
        rep = skills_categories_from_base_resume(base)
        if rep:
            sec["skills"] = rep
    c0 = sec.get("certifications")
    if not isinstance(c0, list) or len(c0) == 0:
        nc = _certs_from_base(base)
        if nc:
            sec["certifications"] = nc
    return out


__all__ = [
    "contact_from_base_resume",
    "enrich_generated_resume_for_docx",
    "parse_base_resume_json",
    "repair_headline_name_leak",
    "skills_categories_from_base_resume",
    "verbatim_identity_from_base_resume",
]
