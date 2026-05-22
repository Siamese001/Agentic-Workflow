"""Competencies v3 contract — categories[] SSOT with legacy competencies[] sync."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apps_rg.runtime.sections.competencies_term_phrase import term_phrase

_REPO_ROOT: Path | None = None
_TAXONOMY_CACHE: dict[str, Any] | None = None

SUPPORT_CLASS_FACT_AND_SKILL_GRAPH = "FACT_AND_SKILL_GRAPH"
SUPPORT_CLASS_FACT_ONLY = "FACT_ONLY"
SUPPORT_CLASS_SKILL_GRAPH_ONLY = "SKILL_GRAPH_ONLY"


def _repo_root() -> Path:
    global _REPO_ROOT
    if _REPO_ROOT is not None:
        return _REPO_ROOT
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "config" / "competencies" / "executive_capability_taxonomy.yaml").is_file():
            _REPO_ROOT = parent
            return parent
    raise FileNotFoundError("executive_capability_taxonomy.yaml not found")


def load_executive_capability_taxonomy() -> dict[str, Any]:
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is not None:
        return _TAXONOMY_CACHE
    path = _repo_root() / "apps_rg" / "config" / "competencies" / "executive_capability_taxonomy.yaml"
    _TAXONOMY_CACHE = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return _TAXONOMY_CACHE


def approved_category_labels() -> frozenset[str]:
    tax = load_executive_capability_taxonomy()
    labels: set[str] = set()
    for row in tax.get("categories") or []:
        if isinstance(row, dict):
            lab = str(row.get("category_label") or "").strip()
            if lab:
                labels.add(lab)
    return frozenset(labels)


def approved_category_id_by_label() -> dict[str, str]:
    tax = load_executive_capability_taxonomy()
    out: dict[str, str] = {}
    for row in tax.get("categories") or []:
        if not isinstance(row, dict):
            continue
        lab = str(row.get("category_label") or "").strip()
        cid = str(row.get("category_id") or "").strip()
        if lab and cid:
            out[lab.lower()] = cid
        for alias in row.get("aliases") or []:
            al = str(alias or "").strip()
            if al and cid:
                out[al.lower()] = cid
    return out


def label_for_category_id(category_id: str) -> str | None:
    tax = load_executive_capability_taxonomy()
    for row in tax.get("categories") or []:
        if isinstance(row, dict) and str(row.get("category_id") or "") == category_id:
            return str(row.get("category_label") or "").strip() or None
    return None


def resolve_approved_category_label(raw_label: str) -> str | None:
    """Map legacy/alias labels to approved taxonomy label."""
    low = str(raw_label or "").strip().lower()
    if not low:
        return None
    id_map = approved_category_id_by_label()
    cid = id_map.get(low)
    if cid:
        return label_for_category_id(cid)
    if low in {x.lower() for x in approved_category_labels()}:
        for lab in approved_category_labels():
            if lab.lower() == low:
                return lab
    return None


def v3_term_from_legacy(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        phrase = term_phrase(raw)
        sids = list(raw.get("source_fact_ids") or [])
        sid = str(raw.get("source_fact_id") or "").strip()
        if sid and sid not in sids:
            sids = [sid, *sids]
        skill_ids = list(raw.get("source_skill_ids") or [])
        support = str(raw.get("support_class") or "").strip()
        if not support:
            if skill_ids and sids:
                support = SUPPORT_CLASS_FACT_AND_SKILL_GRAPH
            elif skill_ids:
                support = SUPPORT_CLASS_SKILL_GRAPH_ONLY
            else:
                support = SUPPORT_CLASS_FACT_ONLY
        return {
            "term": phrase,
            "source_fact_ids": [str(x) for x in sids if str(x).strip()],
            "source_skill_ids": [str(x) for x in skill_ids if str(x).strip()],
            "support_class": support,
        }
    phrase = str(raw or "").strip()
    return {
        "term": phrase,
        "source_fact_ids": [],
        "source_skill_ids": [],
        "support_class": SUPPORT_CLASS_FACT_ONLY,
    }


def legacy_term_from_v3(term: dict[str, Any]) -> dict[str, Any]:
    phrase = term_phrase(term)
    sids = list(term.get("source_fact_ids") or [])
    sid = sids[0] if sids else ""
    out: dict[str, Any] = {
        "text": phrase,
        "term": phrase,
        "source_fact_id": sid,
        "source_fact_ids": sids,
    }
    if term.get("source_skill_ids"):
        out["source_skill_ids"] = list(term.get("source_skill_ids") or [])
    if term.get("support_class"):
        out["support_class"] = term.get("support_class")
    return out


def category_v3_from_legacy(cat: dict[str, Any]) -> dict[str, Any]:
    label = str(cat.get("category_label") or "").strip()
    resolved = resolve_approved_category_label(label) or label
    id_map = approved_category_id_by_label()
    cid = id_map.get(resolved.lower()) or str(cat.get("category_id") or "").strip()
    terms_raw = cat.get("terms") or []
    terms = [v3_term_from_legacy(t) for t in terms_raw if term_phrase(t) or isinstance(t, dict)]
    return {
        "category_id": cid or resolved.lower().replace(" ", "_")[:48],
        "category_label": resolved,
        "terms": terms,
        "source_fact_ids": list(cat.get("source_fact_ids") or []),
    }


def legacy_category_from_v3(cat: dict[str, Any]) -> dict[str, Any]:
    label = str(cat.get("category_label") or "").strip()
    terms = [legacy_term_from_v3(t) for t in (cat.get("terms") or []) if isinstance(t, dict)]
    out: dict[str, Any] = {
        "category_label": label,
        "terms": terms,
    }
    if cat.get("category_id"):
        out["category_id"] = cat.get("category_id")
    if cat.get("source_fact_ids"):
        out["source_fact_ids"] = list(cat.get("source_fact_ids") or [])
    return out


def extract_categories(parsed: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not parsed or not isinstance(parsed, dict):
        return []
    raw = parsed.get("categories")
    if isinstance(raw, list) and raw:
        out: list[dict[str, Any]] = []
        for cat in raw:
            if not isinstance(cat, dict):
                continue
            terms0 = cat.get("terms") or []
            if (
                terms0
                and isinstance(terms0[0], dict)
                and ("term" in terms0[0] or terms0[0].get("support_class"))
            ):
                out.append(cat)
            else:
                out.append(category_v3_from_legacy(cat))
        return out
    legacy = parsed.get("competencies")
    if isinstance(legacy, list):
        return [category_v3_from_legacy(c) for c in legacy if isinstance(c, dict)]
    return []


def sync_categories_competencies(parsed: dict[str, Any]) -> None:
    cats = extract_categories(parsed)
    parsed["categories"] = cats
    parsed["competencies"] = [legacy_category_from_v3(c) for c in cats]
    parsed["section_id"] = "competencies"


__all__ = [
    "SUPPORT_CLASS_FACT_AND_SKILL_GRAPH",
    "SUPPORT_CLASS_FACT_ONLY",
    "SUPPORT_CLASS_SKILL_GRAPH_ONLY",
    "approved_category_labels",
    "approved_category_id_by_label",
    "extract_categories",
    "legacy_category_from_v3",
    "legacy_term_from_v3",
    "load_executive_capability_taxonomy",
    "resolve_approved_category_label",
    "sync_categories_competencies",
    "v3_term_from_legacy",
]
