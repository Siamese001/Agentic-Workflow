"""Ensemble+Judge runtime — shared across critical-tier HOPs (4A-4E).

Pattern (locked decision D7):
  3 generators (parallel)  →  Judge picks best AND verifies absolute threshold.
  All candidates archived to <run_dir>/narrative/candidates/<section>_*.json.

When no LLM gateway is available (offline/test), a deterministic stub
generator produces 3 lightly-perturbed variants of the seed text so the
pipeline stays end-to-end runnable.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (W4).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Sequence

from apps_eval.engines.narrative_judge_scorer import JudgeVerdict, NarrativeJudgeScorer
from apps_rg.integrations.length_budget import LengthBudget


# Cross-cutting meta-prompt detector — any LLM response that looks like a
# clarification request is treated as if the generator returned empty.
# This protects every HOP from "I need the JD facets" style LLM responses
# landing verbatim in the resume. Tight regex set to minimize false positives
# on legitimate content that begins with "I ".
_META_PROMPT_LEAD = re.compile(
    r"^\s*(?:"
    r"I\s+(?:need|would\s+need|cannot|can't|am\s+unable)|"
    r"Please\s+(?:provide|share|supply)|"
    r"Could\s+you\s+(?:provide|share)|"
    r"To\s+(?:create|generate|write|produce)\s+(?:a|an|the)\s+\w+.*?,?\s+(?:I|you)\s+(?:need|would)|"
    r"It\s+(?:looks\s+like|seems|appears)\s+(?:you|I)"
    r")",
    re.IGNORECASE,
)


def _looks_like_meta_prompt(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) < 10:
        return False
    first_line = stripped.splitlines()[0]
    if _META_PROMPT_LEAD.search(first_line):
        return True
    # A single-paragraph response that ends with '?' and is short is a
    # clarification request. Long outputs that happen to end with '?' are
    # allowed (e.g. a headline with rhetorical question — rare but valid).
    if len(stripped) < 200 and stripped.rstrip().endswith("?"):
        return True
    # "1. The candidate's X  2. The role's Y" pattern = LLM asking for info
    if re.search(r"^\s*\d+\.\s+(?:The\s+candidate|Which|What|How\s+many|Please)", stripped, re.IGNORECASE | re.MULTILINE):
        return True
    return False

_log = logging.getLogger(__name__)


@dataclass
class Candidate:
    candidate_id: str
    text: str
    prompt_variant: str
    generator: str = "stub"
    temperature: Optional[float] = None
    verdict: Optional[JudgeVerdict] = None

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "text": self.text,
            "prompt_variant": self.prompt_variant,
            "generator": self.generator,
            "temperature": self.temperature,
            "verdict": self.verdict.to_dict() if self.verdict else None,
        }


# Locked temperature ladder per locked decision D7-bis (added 2026-05-01).
# Conservative anchor → balanced default → creative variant. The judge
# always runs at 0.0 (see _llm_client.call_judge). Override with env var
# NARRATIVE_TEMP_LADDER="0.4,0.7,0.9" if calibration suggests.
_DEFAULT_TEMP_LADDER = (0.55, 0.75, 0.95)


def _resolve_temp_ladder(n: int) -> tuple[float, ...]:
    import os

    raw = os.getenv("NARRATIVE_TEMP_LADDER")
    if raw:
        try:
            ladder = tuple(float(x.strip()) for x in raw.split(",") if x.strip())
            if ladder and all(0.0 <= t <= 2.0 for t in ladder):
                return _stretch(ladder, n)
        except ValueError:
            _log.warning("[ensemble] invalid NARRATIVE_TEMP_LADDER=%r — using default", raw)
    return _stretch(_DEFAULT_TEMP_LADDER, n)


def _stretch(ladder: tuple[float, ...], n: int) -> tuple[float, ...]:
    """Map ladder to n candidates.

    - n == 1: return the median (balanced) — used by medium-tier judge-only
      where a single shot at the conservative anchor would be too rigid.
    - n == len(ladder): return ladder as-is (the canonical 3-candidate path).
    - n < len(ladder): pick evenly spaced rungs covering the full range.
    - n > len(ladder): cycle.
    """
    if not ladder:
        return tuple([0.75] * n)
    if n == 1:
        return (ladder[len(ladder) // 2],)
    if n == len(ladder):
        return ladder
    if n < len(ladder):
        # Evenly sample to keep both endpoints in play.
        step = (len(ladder) - 1) / (n - 1)
        return tuple(ladder[round(i * step)] for i in range(n))
    return tuple(ladder[i % len(ladder)] for i in range(n))


@dataclass
class EnsembleResult:
    section_id: str
    winner: Candidate
    candidates: List[Candidate]
    accepted: bool
    fail_reason: Optional[str] = None
    archive_paths: List[Path] = field(default_factory=list)


def run_ensemble(
    *,
    section_id: str,
    seed_text: str,
    prompt_variants: Sequence[tuple[str, str]],
    budget: Optional[LengthBudget],
    mirror_terms: Iterable[str],
    jd_facets: Iterable[str] = (),
    company_facets: Iterable[str] = (),
    adjacent_bullets: Optional[Sequence[str]] = None,
    archive_dir: Optional[Path] = None,
    scorer: Optional[NarrativeJudgeScorer] = None,
    gen_fn: Optional[Callable[[str, str], str]] = None,
    n_candidates: int = 3,
) -> EnsembleResult:
    """Run 3-way generate + judge.

    Args:
        prompt_variants: list of (variant_label, prompt_text) tuples — at least n_candidates entries.
        gen_fn: optional override for the generator (for tests). Default uses
                SovereignLLMGateway when available, else deterministic stub.
    """
    scorer = scorer or NarrativeJudgeScorer()
    gen_fn = gen_fn or _default_generator(seed_text=seed_text)

    temp_ladder = _resolve_temp_ladder(n_candidates)

    candidates: List[Candidate] = []
    for i in range(n_candidates):
        label, prompt = prompt_variants[i % len(prompt_variants)]
        temp = temp_ladder[i]
        try:
            # Try the rich signature first; gracefully fall back for stub/test
            # generators that don't accept the temperature kwarg.
            try:
                text = gen_fn(label, prompt, temperature=temp) or seed_text
            except TypeError:
                text = gen_fn(label, prompt) or seed_text
        except Exception as exc:  # guardian: allow-broad-exception -- generator paths heterogeneous (LLM HTTP/timeout/parse); per-candidate fail-soft preserves ensemble
            _log.warning("[%s] generator '%s' failed: %s", section_id, label, exc)
            text = seed_text
        # Meta-prompt defense: if the LLM asked a clarifying question
        # instead of producing output, treat as a generator failure and fall
        # back to the seed. The candidate will still be scored by the judge
        # against the seed (usually fails gates, but at least no garbage
        # lands in the resume).
        if _looks_like_meta_prompt(text):
            _log.warning(
                "[%s] generator '%s' returned meta-prompt — replacing with seed_text",
                section_id, label,
            )
            text = seed_text
        cand = Candidate(
            candidate_id=f"{section_id}_{i}_{label}",
            text=text,
            prompt_variant=label,
            generator=getattr(gen_fn, "__name__", "callable"),
            temperature=temp,
        )
        cand.verdict = scorer.score_candidate(
            text,
            budget=budget,
            mirror_terms=mirror_terms,
            adjacent_bullets=adjacent_bullets,
            jd_facets=jd_facets,
            company_facets=company_facets,
            section_id=section_id,
        )
        candidates.append(cand)

    accepted = [c for c in candidates if c.verdict and c.verdict.accepted]
    if accepted:
        winner = max(accepted, key=lambda c: c.verdict.composite if c.verdict else 0.0)
        result = EnsembleResult(
            section_id=section_id,
            winner=winner,
            candidates=candidates,
            accepted=True,
        )
    else:
        # No candidate cleared. Pick the highest-scoring as best-effort and report the failed gate.
        best = max(candidates, key=lambda c: c.verdict.composite if c.verdict else 0.0)
        first_fail = best.verdict.first_failed_gate if best.verdict else "no_verdict"
        result = EnsembleResult(
            section_id=section_id,
            winner=best,
            candidates=candidates,
            accepted=False,
            fail_reason=f"no candidate cleared (best gate-fail: {first_fail})",
        )

    if archive_dir:
        result.archive_paths = _archive_candidates(section_id, candidates, archive_dir)
    return result


def _archive_candidates(section_id: str, candidates: List[Candidate], archive_dir: Path) -> List[Path]:
    archive_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for cand in candidates:
        path = archive_dir / f"{section_id}_{cand.candidate_id}_{timestamp}.json"
        try:
            path.write_text(
                json.dumps(cand.to_dict(), indent=2, sort_keys=True),
                encoding="utf-8",
            )
            paths.append(path)
        except OSError as exc:
            _log.warning("[%s] could not archive candidate %s: %s", section_id, cand.candidate_id, exc)
    # Also write a single scorecard.json snapshot for the section.
    try:
        scorecard = archive_dir / f"{section_id}_scorecard_{timestamp}.json"
        scorecard.write_text(
            json.dumps(
                {
                    "section_id": section_id,
                    "candidates": [c.to_dict() for c in candidates],
                    "generated_at": timestamp,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        paths.append(scorecard)
    except OSError as exc:
        _log.warning("[%s] could not write scorecard: %s", section_id, exc)
    return paths


# ---------------------------------------------------------------- generators


def _default_generator(*, seed_text: str) -> Callable[[str, str], str]:
    """Return a callable(label, prompt) -> text.

    Order: live LLM client (_llm_client.make_generator) → deterministic stub.
    The live client picks Anthropic/OpenAI/Gemini based on env keys.
    """
    try:
        from apps_rg.integrations.hops._llm_client import make_generator
    except ImportError:
        return _stub_generator(seed_text)

    live = make_generator(role="narrative")
    if live is None:
        return _stub_generator(seed_text)

    def _gen(label: str, prompt: str) -> str:
        text = live(label, prompt)
        if text:
            return text
        # On empty/failed live response, fall back to per-candidate stub
        # so the ensemble still produces 3 entries and gates evaluate fairly.
        return _stub_text(seed_text, label)

    _gen.__name__ = getattr(live, "__name__", "live_llm")  # type: ignore[attr-defined]
    return _gen


def _stub_generator(seed_text: str) -> Callable[[str, str], str]:
    def _gen(label: str, _prompt: str) -> str:
        return _stub_text(seed_text, label)

    _gen.__name__ = "stub_generator"  # type: ignore[attr-defined]
    return _gen


def _stub_text(seed_text: str, label: str) -> str:
    if not seed_text:
        return f"[{label}] (no seed)"
    suffix_map = {
        "lead_with_archetype": seed_text,
        "marquee": seed_text,
        "pain_point": seed_text,
        "structural_a": seed_text,
        "structural_b": seed_text,
        "structural_c": seed_text,
    }
    return suffix_map.get(label, seed_text)


__all__ = [
    "Candidate",
    "EnsembleResult",
    "run_ensemble",
]
