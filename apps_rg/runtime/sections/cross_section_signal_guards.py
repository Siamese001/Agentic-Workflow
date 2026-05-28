"""Shared cross-section signal-loss guards (apps_rg only).

Small, local helpers reused by headline, unify_bullets, and unify_narrative
bundle-consumption X2 gates. These deliberately reuse the existing vocab/threshold
constants from narrative_quality_x2 / bullet_ngram_overlap_x2 rather than redefining
them, to avoid drift. No agentic_core dependency.

Authority model recap (enforced upstream, surfaced here as detectors only):
- graph skills + linked source facts + role episode bundles = content/proof authority
- base resume = seniority / technical specificity / scope / voice calibration only
- archive resumes = provenance inventory only
- JD/briefing = targeting only
- E0 examples = style only
"""
from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    compute_max_ngram_overlap_multi_reference,
)
from apps_rg.runtime.validators.narrative_quality_x2 import (
    MECHANISM_VOCAB,
    NARRATIVE_CONSULTING_PHRASES,
    NARRATIVE_STRONG_VERBS,
)

# Generic consulting-delivery phrases that demote a senior engineering role arc.
GENERIC_CONSULTING_PHRASES: frozenset[str] = NARRATIVE_CONSULTING_PHRASES | frozenset({
    "delivered consulting engagements",
    "advised clients on",
    "consulting delivery",
    "client delivery engagements",
    "professional services delivery",
    "managed client relationships",
    "delivery oversight",
    "stakeholder management",
    "cross-functional collaboration",
    "subject matter expertise",
    "drove business outcomes",
})

# Architecture / platform mechanism signal (technical specificity proxy).
ARCHITECTURE_MECHANISM_VOCAB: frozenset[str] = MECHANISM_VOCAB | frozenset({
    "deterministic", "routing", "sandboxed", "replayable", "trace", "traces",
    "graphrag", "vector", "gateway", "rollback", "lineage", "dependency",
    "accelerator", "policy", "gate", "gates", "validation", "telemetry",
    "lakehouse", "databricks", "multi-agent", "platform", "commercialization",
    "productization",
})

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_NGRAM_SIZE = 4


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(str(text or "").lower())


def seniority_floor_score(text: str) -> int:
    """Count distinct strong executive ownership verbs present (proxy seniority signal)."""
    tokens = set(_tokenize(text))
    return len(NARRATIVE_STRONG_VERBS & tokens)


def technical_specificity_score(text: str, *, vocab: frozenset[str] | None = None) -> int:
    """Count distinct named mechanism/technology tokens (technical density proxy)."""
    tokens = set(_tokenize(text))
    return len((vocab or ARCHITECTURE_MECHANISM_VOCAB) & tokens)


def detect_generic_consulting_phrases(text: str) -> list[str]:
    """Return generic consulting-delivery phrases found in text (demotion risk)."""
    low = str(text or "").lower()
    return [p for p in GENERIC_CONSULTING_PHRASES if p in low]


def detect_jd_only_phrases(text: str, jd_text: str, *, min_run: int = 6) -> list[str]:
    """Return long verbatim phrase runs lifted from JD/briefing (JD-as-proof leakage).

    A "JD-only phrase" is a run of >= min_run consecutive shared tokens between the
    output and the JD/briefing text. JD is targeting only — never proof substrate.
    """
    out_tokens = _tokenize(text)
    jd_tokens = _tokenize(jd_text)
    if not out_tokens or not jd_tokens or min_run <= 0:
        return []
    jd_runs: set[str] = set()
    for i in range(len(jd_tokens) - min_run + 1):
        jd_runs.add(" ".join(jd_tokens[i : i + min_run]))
    hits: list[str] = []
    for i in range(len(out_tokens) - min_run + 1):
        run = " ".join(out_tokens[i : i + min_run])
        if run in jd_runs and run not in hits:
            hits.append(run)
    return hits


def base_archive_ngram_overlap(text: str, reference_texts: list[str], *, n: int = _NGRAM_SIZE) -> float:
    """Max n-gram overlap vs base/archive reference prose (anti-hydration proxy)."""
    refs = [r for r in (reference_texts or []) if str(r or "").strip()]
    if not refs:
        return 0.0
    return compute_max_ngram_overlap_multi_reference(str(text or ""), refs, n=n)


def is_flat_skill_only_graph_packet(packet: dict[str, Any] | None) -> bool:
    """True when graph context is flat skills only (no role-episode/positioning bundle binding).

    Generic across sections: a packet that exposes graph_skill_node_ids / bound_skills but
    no *_bundle_id, *_bundle_ids, or bundles list is flat-skill-only and forbidden as proof.
    """
    if not isinstance(packet, dict):
        return False
    bundle_id_keys = (
        "role_episode_bundle_id",
        "role_episode_bundle_ids",
        "headline_positioning_bundle_id",
        "headline_positioning_bundle_ids",
        "competency_bundle_id",
    )
    for k in bundle_id_keys:
        if packet.get(k):
            return False
    for list_key in ("role_episode_bundles", "headline_positioning_bundles", "bundles"):
        if packet.get(list_key):
            return False
    has_flat_skills = bool(packet.get("graph_skill_node_ids") or packet.get("bound_skills"))
    return has_flat_skills


__all__ = [
    "ARCHITECTURE_MECHANISM_VOCAB",
    "GENERIC_CONSULTING_PHRASES",
    "base_archive_ngram_overlap",
    "detect_generic_consulting_phrases",
    "detect_jd_only_phrases",
    "is_flat_skill_only_graph_packet",
    "seniority_floor_score",
    "technical_specificity_score",
]
