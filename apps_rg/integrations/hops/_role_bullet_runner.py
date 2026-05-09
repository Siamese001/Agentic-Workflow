"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime hop runners (def generate_* / def run_*).

Original: apps_rg/integrations/hops/_role_bullet_runner.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Contains run_role_bullets method (runtime hop runner)

Importing this module raises RuntimeError immediately.
Core L2/L3 owns all runtime execution. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.hops._role_bullet_runner is QUARANTINED. "
    "apps_rg may NOT contain runtime hop runners. "
    "Core L2/L3 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to:
# archives/apps_rg/quarantine_w4_20260509/integrations/hops/_role_bullet_runner.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
"""Shared per-bullet runner - ORIGINAL (QUARANTINED)"""
# from __future__ import annotations
# import logging
# from dataclasses import dataclass, field
# from pathlib import Path
# from typing import Iterable, List, Optional, Sequence
# from apps_eval.engines.narrative_judge_scorer import JudgeVerdict, NarrativeJudgeScorer
# from apps_rg.integrations.hops._ensemble_runner import EnsembleResult, run_ensemble
# from apps_rg.integrations.length_budget import LengthBudget, budget_from_text
# from apps_rg.integrations.pool_first_selector import pool_first_select

_log = logging.getLogger(__name__)


class NarrativeQualityError(RuntimeError):
    """Raised when a critical-tier section has no acceptable candidate."""


@dataclass
class BulletResult:
    bullet_index: int
    chosen_text: str
    source: str  # "pool" | "ensemble" | "judge_only" | "fallback"
    accepted: bool
    verdict: Optional[JudgeVerdict] = None
    candidates_archive: List[Path] = field(default_factory=list)


@dataclass
class RoleBulletPlan:
    role_id: str
    bullets: List[dict]  # list of {"text": ..., "pool_variants": [...]}


def run_role_bullets(
    *,
    role_id: str,
    bullets: Sequence[dict],
    jd_facets: Iterable[str],
    company_facets: Iterable[str],
    mirror_terms: Iterable[str],
    archive_dir: Optional[Path] = None,
    tier: str = "critical",  # "critical" or "medium"
    n_candidates: int = 3,
    scorer: Optional[NarrativeJudgeScorer] = None,
) -> List[BulletResult]:
    scorer = scorer or NarrativeJudgeScorer()
    results: List[BulletResult] = []
    prior_chosen: List[str] = []

    for idx, bullet in enumerate(bullets):
        seed_text = str(bullet.get("text") or "").strip()
        pool_variants = [str(v) for v in (bullet.get("pool_variants") or [])]
        budget = budget_from_text(f"{role_id}::{idx}", seed_text or "x x x x x", tolerance=0.65)

        # 1. Pool-first
        pool_choice = pool_first_select(
            seed=seed_text,
            variants=pool_variants,
            scorer=scorer,
            budget=budget,
            mirror_terms=mirror_terms,
            jd_facets=jd_facets,
            company_facets=company_facets,
            adjacent_bullets=prior_chosen,
        )
        if pool_choice is not None and pool_choice.verdict and pool_choice.verdict.accepted:
            res = BulletResult(
                bullet_index=idx,
                chosen_text=pool_choice.text,
                source="pool",
                accepted=True,
                verdict=pool_choice.verdict,
            )
            results.append(res)
            prior_chosen.append(pool_choice.text)
            continue

        # 2. LLM ensemble (or judge-only, depending on tier)
        if tier == "critical" and n_candidates >= 2:
            ens = _run_ensemble_for_bullet(
                role_id=role_id,
                idx=idx,
                seed_text=seed_text,
                jd_facets=jd_facets,
                company_facets=company_facets,
                mirror_terms=mirror_terms,
                budget=budget,
                adjacent_bullets=prior_chosen,
                archive_dir=archive_dir,
                scorer=scorer,
                n_candidates=n_candidates,
            )
            chosen_text = ens.winner.text
            verdict = ens.winner.verdict
            accepted = ens.accepted
            source = "ensemble"
            archive = ens.archive_paths
        else:
            # Medium-tier: single regen + judge
            ens = _run_ensemble_for_bullet(
                role_id=role_id,
                idx=idx,
                seed_text=seed_text,
                jd_facets=jd_facets,
                company_facets=company_facets,
                mirror_terms=mirror_terms,
                budget=budget,
                adjacent_bullets=prior_chosen,
                archive_dir=archive_dir,
                scorer=scorer,
                n_candidates=1,
            )
            chosen_text = ens.winner.text
            verdict = ens.winner.verdict
            accepted = ens.accepted
            source = "judge_only"
            archive = ens.archive_paths

        if not accepted and tier == "critical":
            # Honor the lenient escape hatch from constitutional D8:
            #   NARRATIVE_LENIENT_CRITICAL=1 -> degrade-and-continue instead
            #   of aborting the run. Used for offline / stub-generator smoke
            #   runs and for early-iteration LLM tuning where gates are
            #   intentionally tight.
            import os
            if os.getenv("NARRATIVE_LENIENT_CRITICAL", "").strip() in {"1", "true", "yes"}:
                _log.warning(
                    "[role_bullets] role=%s bullet=%d critical-tier degrade (LENIENT mode): %s",
                    role_id, idx, ens.fail_reason,
                )
            else:
                raise NarrativeQualityError(
                    f"role={role_id} bullet={idx} failed all paths "
                    f"(reason: {ens.fail_reason})"
                )

        results.append(
            BulletResult(
                bullet_index=idx,
                chosen_text=chosen_text,
                source=source if accepted else "fallback",
                accepted=accepted,
                verdict=verdict,
                candidates_archive=archive,
            )
        )
        prior_chosen.append(chosen_text)

    return results


def _run_ensemble_for_bullet(
    *,
    role_id: str,
    idx: int,
    seed_text: str,
    jd_facets,
    company_facets,
    mirror_terms,
    budget: LengthBudget,
    adjacent_bullets: Sequence[str],
    archive_dir: Optional[Path],
    scorer: NarrativeJudgeScorer,
    n_candidates: int,
) -> EnsembleResult:
    section_id = f"role_bullets__{role_id}__{idx}"
    prompt_variants = [
        ("preserve_metrics", _prompt_preserve(seed_text, jd_facets)),
        ("compress_to_outcome", _prompt_compress(seed_text)),
        ("mirror_company_lang", _prompt_mirror(seed_text, company_facets)),
    ]
    return run_ensemble(
        section_id=section_id,
        seed_text=seed_text,
        prompt_variants=prompt_variants,
        budget=budget,
        mirror_terms=mirror_terms,
        jd_facets=jd_facets,
        company_facets=company_facets,
        adjacent_bullets=adjacent_bullets,
        archive_dir=archive_dir,
        scorer=scorer,
        n_candidates=max(1, n_candidates),
    )


def _prompt_preserve(seed: str, jd_facets) -> str:
    return (
        "Rewrite this resume bullet preserving every quantified metric "
        f"(%, $, multiples, scale figures). Stay within ±15% of the original "
        f"word count. Mirror at most 2 JD facets from {list(jd_facets)[:15]}. "
        "No filler intensifiers. Return only the rewritten bullet.\n\n"
        f"Original:\n{seed}"
    )


def _prompt_compress(seed: str) -> str:
    return (
        "Compress this resume bullet to its strongest single outcome+method. "
        "Stay within ±15% of original length. No filler. Return only the bullet.\n\n"
        f"Original:\n{seed}"
    )


def _prompt_mirror(seed: str, company_facets) -> str:
    return (
        f"Rewrite this resume bullet so it mirrors company language: "
        f"{list(company_facets)[:15]}. Stay within ±15% length. No filler. "
        f"Preserve all metrics. Return only the bullet.\n\nOriginal:\n{seed}"
    )


__all__ = [
    "BulletResult",
    "NarrativeQualityError",
    "RoleBulletPlan",
    "run_role_bullets",
]
