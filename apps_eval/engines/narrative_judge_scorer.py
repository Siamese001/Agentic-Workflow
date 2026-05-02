"""NarrativeJudgeScorer — applies hard gates + soft dimensions to a candidate
piece of resume narrative. Used by HOP-4A through HOP-4G.

Hard gates fail the candidate immediately. Soft dimensions are weighted into
a composite [0..1]. The candidate ACCEPTs when all hard gates pass AND
composite >= rubric_threshold (default 0.85, tuned per HOP).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P3.2).

The judge LLM call is best-effort — when no gateway is wired, soft dimensions
fall back to deterministic heuristics so the pipeline stays green.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import yaml

from apps_rg.integrations.anti_overfitting import (
    AntiOverfittingConfig,
    GateResult,
    gate_adjacent_repetition,
    gate_buzzword_soup,
    gate_filler_intensifiers,
    gate_mirror_density,
)
from apps_rg.integrations.length_budget import LengthBudget

_log = logging.getLogger(__name__)

_DEFAULT_RUBRIC_PATH = Path("apps_eval/config/rubrics/narrative_judge.yaml")


@dataclass
class JudgeVerdict:
    accepted: bool
    composite: float
    hard_gates: List[GateResult] = field(default_factory=list)
    soft_scores: Dict[str, float] = field(default_factory=dict)
    rationale: str = ""

    @property
    def first_failed_gate(self) -> Optional[str]:
        for g in self.hard_gates:
            if not g.passed:
                return g.gate_id
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "composite": round(self.composite, 4),
            "hard_gates": [g.as_dict() for g in self.hard_gates],
            "soft_scores": {k: round(v, 4) for k, v in self.soft_scores.items()},
            "rationale": self.rationale,
            "first_failed_gate": self.first_failed_gate,
        }


@dataclass
class NarrativeJudgeScorer:
    rubric_path: Path = _DEFAULT_RUBRIC_PATH
    use_llm: bool = True
    rubric: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rubric = _load_rubric(self.rubric_path)

    # ------------------------------------------------------------------ public

    def score_candidate(
        self,
        text: str,
        *,
        budget: Optional[LengthBudget] = None,
        provenance_ok: bool = True,
        mirror_terms: Iterable[str] = (),
        adjacent_bullets: Optional[Sequence[str]] = None,
        jd_facets: Iterable[str] = (),
        company_facets: Iterable[str] = (),
        anti_cfg: Optional[AntiOverfittingConfig] = None,
        section_id: str = "",
    ) -> JudgeVerdict:
        anti_cfg = anti_cfg or _anti_cfg_from_rubric(self.rubric)
        gates: List[GateResult] = []

        gates.append(GateResult("provenance", provenance_ok, "caller-supplied" if provenance_ok else "missing source trace"))
        if budget is not None:
            gates.append(_gate_length(text, budget))
        gates.append(gate_buzzword_soup(text, anti_cfg, section_id=section_id))
        gates.append(gate_mirror_density(text, mirror_terms, anti_cfg))
        if adjacent_bullets:
            gates.append(gate_adjacent_repetition(list(adjacent_bullets) + [text], mirror_terms))
        gates.append(gate_filler_intensifiers(text, anti_cfg))

        soft: Dict[str, float] = {
            "jd_facet_coverage": _facet_coverage(text, jd_facets),
            "company_facet_coverage": _facet_coverage(text, company_facets),
            "tone_executive_register": _heuristic_tone(text),
            "naturalness": _heuristic_naturalness(text, mirror_terms),
        }

        if self.use_llm:
            try:
                soft.update(self._llm_soft_scores(text, jd_facets, company_facets) or {})
            except Exception as exc:  # guardian: allow-broad-exception -- LLM judge call paths heterogeneous (HTTP/timeout/parse); fall back to heuristic scores
                _log.info("[narrative_judge] LLM scoring unavailable, using heuristics: %s", exc)

        composite = self._compose(soft)
        accepted = all(g.passed for g in gates) and composite >= float(
            self.rubric.get("composite_threshold", 0.85)
        )
        return JudgeVerdict(
            accepted=accepted,
            composite=composite,
            hard_gates=gates,
            soft_scores=soft,
            rationale=_build_rationale(gates, soft, composite),
        )

    # --------------------------------------------------------------- internals

    def _compose(self, soft: Dict[str, float]) -> float:
        total_weight = 0.0
        running = 0.0
        for dim in self.rubric.get("soft_dimensions", []) or []:
            dim_id = dim.get("dimension_id")
            weight = float(dim.get("weight", 0.0))
            min_score = float(dim.get("min_score", 0.0))
            score = soft.get(dim_id, 0.0)
            if score < min_score:
                # Below the dim minimum collapses composite, like a soft veto.
                return 0.0
            running += weight * score
            total_weight += weight
        if total_weight <= 0:
            return 0.0
        return min(1.0, running / total_weight)

    def _llm_soft_scores(
        self,
        text: str,
        jd_facets: Iterable[str],
        company_facets: Iterable[str],
    ) -> Dict[str, float]:
        try:
            from apps_rg.integrations.hops._llm_client import call_judge
        except ImportError:
            return {}

        prompt = (
            "You are a senior recruiter judging a single piece of resume narrative.\n"
            "Score on a 0.0-1.0 scale and return strict JSON with EXACTLY these keys:\n"
            '  {"tone_executive_register": <float 0-1>, "naturalness": <float 0-1>}\n\n'
            "tone_executive_register: penalize corporate-speak, jargon without substance, breathless framing.\n"
            "naturalness: penalize keyword stuffing, template-rigid structure, verbatim JD language.\n\n"
            f"Job-description facets: {list(jd_facets)[:25]}\n"
            f"Company facets: {list(company_facets)[:25]}\n\n"
            f"Candidate:\n{text}\n\nReturn JSON now."
        )
        result = call_judge(prompt)
        return result or {}


# ----------------------------------------------------------------------- utils


def _load_rubric(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}


def _anti_cfg_from_rubric(rubric: Dict[str, Any]) -> AntiOverfittingConfig:
    cfg = AntiOverfittingConfig()
    for gate in rubric.get("hard_gates") or []:
        gid = gate.get("gate_id")
        c = gate.get("config") or {}
        if gid == "buzzword_soup":
            cfg.buzzwords = list(c.get("buzzwords", cfg.buzzwords))
            cfg.max_buzzwords = int(c.get("max_count", cfg.max_buzzwords))
        elif gid == "filler_intensifiers":
            cfg.filler = list(c.get("forbidden", cfg.filler))
        elif gid == "mirror_density":
            cfg.mirror_min = float(c.get("min", cfg.mirror_min))
            cfg.mirror_max = float(c.get("max", cfg.mirror_max))
    return cfg


def _gate_length(text: str, budget: LengthBudget) -> GateResult:
    diag = budget.diagnostic(text)
    return GateResult(
        "length_parity",
        bool(diag["fits"]),
        f"n={diag['n_words']} target={diag['target']} range=[{diag['min']},{diag['max']}]",
    )


def _facet_coverage(text: str, facets: Iterable[str]) -> float:
    facets = [f for f in facets if f]
    if not facets:
        return 0.0
    lower = (text or "").lower()
    hits = sum(1 for f in facets if f.lower() in lower)
    return hits / len(facets)


def _heuristic_tone(text: str) -> float:
    if not text:
        return 0.0
    n_words = len(text.split())
    # Reward concise sentences; penalize exclamation and breathless framing.
    score = 0.85 if n_words >= 6 else 0.65
    if "!" in text:
        score -= 0.2
    if any(t in text.lower() for t in ("amazing", "incredible", "transformative")):
        score -= 0.2
    return max(0.0, min(1.0, score))


def _heuristic_naturalness(text: str, mirror_terms: Iterable[str]) -> float:
    if not text:
        return 0.0
    lower = text.lower()
    mirror_hits = sum(1 for m in mirror_terms if m and m.lower() in lower)
    n_words = max(1, len(text.split()))
    density = mirror_hits / n_words
    # Optimum density ~0.10; score falls off either side via simple Gaussian.
    score = math.exp(-((density - 0.10) ** 2) / (2 * 0.05 ** 2))
    return max(0.0, min(1.0, score))


def _build_rationale(
    gates: List[GateResult], soft: Dict[str, float], composite: float
) -> str:
    failed = [g for g in gates if not g.passed]
    if failed:
        return "; ".join(f"{g.gate_id}: {g.detail}" for g in failed)
    return f"composite={composite:.3f} soft={ {k: round(v, 3) for k, v in soft.items()} }"


__all__ = ["JudgeVerdict", "NarrativeJudgeScorer"]
