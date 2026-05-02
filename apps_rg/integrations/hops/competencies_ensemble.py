"""HOP-4C-COMPETENCIES — Ensemble+Judge at the SET level.

Locked spec (D6 + Author-Gate W4.3 tentative): 3 generators each propose all
6 categories; judge picks best set. Set-level scoring rewards coherent
6 categories with no overlap, JD+company language coverage, and category-name
mirroring of company terminology.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P4.3).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Callable, Iterable, List, Optional

from apps_rg.integrations.hops._ensemble_runner import EnsembleResult, run_ensemble
from apps_rg.integrations.length_budget import budget_for_section

_log = logging.getLogger(__name__)

SECTION_ID = "hop_4c_competencies"
TIER = "critical"

_TARGET_CATEGORIES = 6

# LLM meta-prompt detector — bullets/headlines should never start with these
# patterns. If the LLM asks a question back instead of producing output, we
# reject that candidate (replaced with seed) so the question never lands in
# the resume.
_META_PROMPT_PATTERNS = (
    re.compile(r"^\s*(?:I\s+(?:need|would\s+need|can(?:not|'t)|am\s+unable))", re.IGNORECASE),
    re.compile(r"^\s*(?:please\s+provide|please\s+share|could\s+you\s+(?:provide|share))", re.IGNORECASE),
    re.compile(r"^\s*(?:to\s+(?:create|generate|produce|write)\s+(?:a|an|the)\s+\w+\s*,?\s+(?:I|you))", re.IGNORECASE),
    re.compile(r"\?\s*$"),  # ends with a question mark
    re.compile(r"^\s*(?:it\s+(?:looks\s+like|seems|appears))", re.IGNORECASE),
)


def is_meta_prompt(text: str) -> bool:
    """True if the text looks like an LLM clarification-request rather than output."""
    if not text or len(text.strip()) < 10:
        return True
    stripped = text.strip()
    # A single-line response that ends with '?' is always a meta-prompt.
    first_line = stripped.splitlines()[0] if stripped else ""
    for pat in _META_PROMPT_PATTERNS:
        if pat.search(first_line):
            return True
    # Multi-paragraph "let me help you..." responses — look for list-marker
    # prompts like "1. The candidate's..." which indicate the LLM is asking
    # FOR information rather than producing output.
    if re.search(r"^\s*\d+\.\s+(?:The\s+candidate'?s?|Which|What|How|Please)", stripped, re.IGNORECASE | re.MULTILINE):
        return True
    return False


def generate_competencies(
    *,
    company: str,
    jd_facets: Iterable[str],
    company_facets: Iterable[str],
    mirror_terms: Iterable[str],
    seed_text: str = "",
    archive_dir: Optional[Path] = None,
) -> EnsembleResult:
    # 6 lines, ~12 words each = ~72 words target.
    budget = budget_for_section(
        "competencies", target_words=72, target_sentences=None, tolerance=0.30
    )

    jd_list = [f for f in jd_facets if f]
    company_list = [f for f in company_facets if f]
    mirror_list = [m for m in mirror_terms if m]

    seed_lines = [ln.strip() for ln in (seed_text or "").splitlines() if ln.strip()]
    if not seed_lines:
        seed_lines = _stub_seed_lines(jd_list or company_list)
    seed = "\n".join(seed_lines[:_TARGET_CATEGORIES])

    prompt_variants = [
        ("set_strategy_first", _prompt_set("strategy_first", company, jd_list, company_list, seed_lines)),
        ("set_delivery_first", _prompt_set("delivery_first", company, jd_list, company_list, seed_lines)),
        ("set_governance_first", _prompt_set("governance_first", company, jd_list, company_list, seed_lines)),
    ]

    result = run_ensemble(
        section_id=SECTION_ID,
        seed_text=seed,
        prompt_variants=prompt_variants,
        budget=budget,
        mirror_terms=mirror_list,
        jd_facets=jd_list,
        company_facets=company_list,
        archive_dir=archive_dir,
    )

    # Meta-prompt defense: if the winner or any candidate text is a
    # clarification request, overwrite with the seed so it never lands in the
    # resume. This is belt-and-suspenders behind the narrative gates.
    for cand in result.candidates:
        if is_meta_prompt(cand.text):
            _log.warning("[hop_4c] candidate %s returned meta-prompt — replacing with seed", cand.candidate_id)
            cand.text = seed
            if cand.verdict is not None:
                cand.verdict.accepted = False
                cand.verdict.first_failed_gate = "meta_prompt_leak"
    if is_meta_prompt(result.winner.text):
        result.winner.text = seed
        result.accepted = False
        if result.fail_reason is None:
            result.fail_reason = "meta_prompt_leak"
    return result


def _prompt_set(
    ordering: str,
    company: str,
    jd_facets: List[str],
    company_facets: List[str],
    seed_lines: List[str],
) -> str:
    """Build a self-contained prompt that never requires clarification.

    Key discipline:
      - Always carry the seed skeleton IN the prompt (not just as run_ensemble seed_text).
      - Provide an explicit example output so format ambiguity is zero.
      - Forbid meta-questions in the output.
    """
    jd_str = ", ".join(jd_facets[:20]) if jd_facets else "(no JD facets supplied)"
    co_str = ", ".join(company_facets[:15]) if company_facets else "(no company facets supplied)"
    seed_block = "\n".join(f"  {ln}" for ln in seed_lines[:_TARGET_CATEGORIES])

    return (
        f"Produce exactly 6 core competency categories for a resume targeting {company}. "
        f"Ordering heuristic: {ordering}.\n\n"
        f"Each line MUST follow the shape: 'Category Name: 3-5 supporting capability phrases.'\n\n"
        "STRICT RULES:\n"
        "  - Return ONLY 6 newline-separated lines. No preamble. No closing remarks.\n"
        "  - Do NOT ask clarifying questions. Do NOT say 'I need...' or 'Please provide...'.\n"
        "  - If input is sparse, produce categories anchored to the seed skeleton below.\n"
        "  - Weave in JD and company mirror terms, but do not keyword-stuff.\n"
        "  - No filler intensifiers (leading, world-class, cutting-edge, synergy, leveraging).\n"
        f"  - Total under 80 words.\n\n"
        f"JD mirror terms: {jd_str}\n"
        f"Company mirror terms: {co_str}\n\n"
        "SEED SKELETON (rewrite and re-order; preserve technical substance):\n"
        f"{seed_block}\n\n"
        "EXAMPLE SHAPE (do not copy — illustrates formatting only):\n"
        "  Agentic AI Platform Architecture: multi-agent orchestration, governed autonomy, sandboxed execution, replayable traces\n"
        "  AI Runtime Governance: policy gating, validation controls, auditability, release gating\n\n"
        "Now produce the 6 lines."
    )


def _stub_seed_lines(facets: List[str]) -> List[str]:
    """Fallback skeleton when no master-resume competencies are available."""
    default = [
        "Agentic AI Platform Architecture: multi-agent orchestration, governed autonomy, sandboxed execution",
        "Enterprise AI Delivery: production deployment, evaluation pipelines, rollback controls, observability",
        "Data Platform Strategy: graph retrieval, context engineering, metadata-aware ranking",
        "AI Runtime Governance: policy enforcement, validation gates, auditability, human-in-the-loop escalation",
        "Cross-Functional Leadership: partner enablement, field motion, security and compliance alignment",
        "Outcome-Driven Consulting: commercial packaging, platform productization, enterprise adoption",
    ]
    if not facets:
        return default
    # If we have JD facets, prepend them as category hints but keep the
    # supporting text from the defaults so the LLM has concrete material.
    hints = [f.strip().title() for f in facets[:_TARGET_CATEGORIES] if f.strip()]
    out: List[str] = []
    for i, hint in enumerate(hints):
        tail = default[i].split(":", 1)[1].strip() if ":" in default[i] else default[i]
        out.append(f"{hint}: {tail}")
    while len(out) < _TARGET_CATEGORIES:
        out.append(default[len(out)])
    return out


__all__ = ["SECTION_ID", "TIER", "generate_competencies", "is_meta_prompt"]
