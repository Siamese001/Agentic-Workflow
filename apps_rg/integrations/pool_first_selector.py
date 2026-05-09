"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\pool_first_selector.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\pool_first_selector is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\pool_first_selector.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """Pool-first selector — for each bullet, try `bullet_pool` variants first;
# fall through to LLM regen only when no pool variant clears hard gates AND
# composite >= 0.85.
# 
# Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P5.1).
# """
# 
# from __future__ import annotations
# 
# from dataclasses import dataclass
# from typing import Iterable, Optional, Sequence
# 
# from apps_eval.engines.narrative_judge_scorer import JudgeVerdict, NarrativeJudgeScorer
# from apps_rg.integrations.length_budget import LengthBudget
# 
# 
# @dataclass
# class PoolChoice:
#     text: str
#     verdict: JudgeVerdict
# 
# 
# def pool_first_select(
#     *,
#     seed: str,
#     variants: Sequence[str],
#     scorer: NarrativeJudgeScorer,
#     budget: Optional[LengthBudget],
#     mirror_terms: Iterable[str] = (),
#     jd_facets: Iterable[str] = (),
#     company_facets: Iterable[str] = (),
#     adjacent_bullets: Optional[Sequence[str]] = None,
#     threshold: float = 0.85,
# ) -> Optional[PoolChoice]:
#     """Score every variant; return the best that passes hard gates and
#     composite >= threshold. Returns None if no variant qualifies.
# 
#     The seed text is implicitly included in the candidate pool so that an
#     untouched master_resume bullet can win (avoids needless rewrites).
#     """
#     candidates: list[str] = []
#     seen: set[str] = set()
#     for v in [seed, *variants]:
#         if not v:
#             continue
#         norm = v.strip()
#         if norm in seen:
#             continue
#         seen.add(norm)
#         candidates.append(norm)
# 
#     best: Optional[PoolChoice] = None
#     for cand in candidates:
#         verdict = scorer.score_candidate(
#             cand,
#             budget=budget,
#             mirror_terms=mirror_terms,
#             adjacent_bullets=adjacent_bullets,
#             jd_facets=jd_facets,
#             company_facets=company_facets,
#         )
#         if not verdict.accepted:
#             continue
#         if verdict.composite < threshold:
#             continue
#         if best is None or verdict.composite > best.verdict.composite:
#             best = PoolChoice(text=cand, verdict=verdict)
#     return best
# 
# 
# __all__ = ["PoolChoice", "pool_first_select"]
# 