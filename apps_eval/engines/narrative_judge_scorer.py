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

import json
import logging
import math
import time
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
    gate_pipe_format,
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
        gates.append(gate_pipe_format(text, section_id=section_id))

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

        # Wave 2 P2.1 (plan apps-eval-qwen32b-rollout-b7c4d9): prefer local
        # Qwen-32B vLLM judge. Same-process, effectively free per call,
        # deterministic at temperature=0, emits JUDGE_DECISION marker for
        # the calibration ledger. Falls through to the Anthropic/OpenAI
        # cloud judge when the local server is unavailable.
        qwen_scores = _qwen_soft_scores(prompt)
        if qwen_scores:
            return qwen_scores

        try:
            from apps_rg.integrations.hops._llm_client import call_judge
        except ImportError:
            return {}

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


def _qwen_soft_scores(prompt: str) -> Dict[str, float]:
    """Run the judge prompt against the local Qwen vLLM server.

    Wave 2 P2.1 (plan apps-eval-qwen32b-rollout-b7c4d9). Uses the
    OpenAI-compatible sync SDK pointed at ``VLLM_BASE_URL`` so this
    synchronous scorer stays synchronous. Preflights via
    :func:`is_qwen_available`; returns an empty dict when the server is
    down, the SDK is missing, the call fails, or the response is not
    parseable JSON. The empty-dict return triggers the cloud fallback in
    :meth:`NarrativeJudgeScorer._llm_soft_scores`.

    Emits a ``JUDGE_DECISION`` marker per call so the judge-calibration
    harness (``ops_scripts/calibration/judge_calibration.py``) can track
    acceptance rate, composite drift, and fallback ratio per app.
    """
    try:
        from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
            is_qwen_available,
        )
    except ImportError:
        return {}
    if not is_qwen_available():
        _emit_narrative_judge_marker(
            accepted=False,
            scores={},
            model_used="deterministic_fallback",
            fallback_reason="preflight_failed",
        )
        return {}

    try:
        import openai  # type: ignore  # noqa: PLC0415
    except ImportError:
        return {}

    try:
        from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
            QWEN_LOCAL_MODEL_ID,
            VLLM_BASE_URL,
        )
    except ImportError:
        return {}

    started = time.time()
    try:
        client = openai.OpenAI(
            base_url=VLLM_BASE_URL,
            api_key="not-needed",
            timeout=30.0,
        )
        resp = client.chat.completions.create(
            model=QWEN_LOCAL_MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior recruiter scoring resume narrative. "
                        "Respond ONLY with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=256,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-SDK-over-vLLM raises heterogeneous (APIError/Connection/Timeout); fail-soft preserves cloud fallback
        _log.info("[narrative_judge] qwen call failed, falling back: %s", exc)
        _emit_narrative_judge_marker(
            accepted=False,
            scores={},
            model_used=QWEN_LOCAL_MODEL_ID,
            fallback_reason="gateway_exception",
            latency_ms=(time.time() - started) * 1000.0,
        )
        return {}

    try:
        raw = (resp.choices[0].message.content or "") if resp.choices else ""
        first = raw.find("{")
        last = raw.rfind("}")
        if first < 0 or last <= first:
            _emit_narrative_judge_marker(
                accepted=False,
                scores={},
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="parse_failure",
                latency_ms=(time.time() - started) * 1000.0,
            )
            return {}
        parsed = json.loads(raw[first : last + 1])
        scores: Dict[str, float] = {
            "tone_executive_register": float(parsed.get("tone_executive_register", 0.0)),
            "naturalness": float(parsed.get("naturalness", 0.0)),
        }
    except (ValueError, TypeError, KeyError) as exc:
        _log.info("[narrative_judge] qwen parse failed: %s", exc)
        _emit_narrative_judge_marker(
            accepted=False,
            scores={},
            model_used=QWEN_LOCAL_MODEL_ID,
            fallback_reason="parse_failure",
            latency_ms=(time.time() - started) * 1000.0,
        )
        return {}

    _emit_narrative_judge_marker(
        accepted=True,
        scores=scores,
        model_used=QWEN_LOCAL_MODEL_ID,
        fallback_reason="none",
        latency_ms=(time.time() - started) * 1000.0,
    )
    return scores


def _emit_narrative_judge_marker(
    *,
    accepted: bool,
    scores: Dict[str, float],
    model_used: str,
    fallback_reason: str,
    latency_ms: float = 0.0,
) -> None:
    """Best-effort ``JUDGE_DECISION`` emission; never raises."""
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415
    except ImportError:
        return
    composite = 0.0
    if scores:
        composite = (
            0.4 * float(scores.get("tone_executive_register", 0.0))
            + 0.6 * float(scores.get("naturalness", 0.0))
        )
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_eval.narrative_judge, "
        "rubric_id=narrative_judge_v1, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        f"composite={composite:.4f}, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        f"latency_ms={latency_ms:.1f}"
    )
    try:
        append_marker(payload, session_hint="apps_eval.narrative_judge")
    except (OSError, PermissionError):
        pass


__all__ = ["JudgeVerdict", "NarrativeJudgeScorer"]
