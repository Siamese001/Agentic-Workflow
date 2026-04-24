"""Pairwise + reference-based judge protocols with bias mitigation.

Two judge protocols beyond the pointwise :class:`LLMJudge`:

1. :class:`PairwiseJudge` — compare two candidate answers A and B given
   the same query + context, return the winner and a confidence. Applies
   **position-swap bias mitigation**: if ``swap_on_disagreement`` is
   True and the first pass disagrees with itself after swapping A/B
   positions, the verdict is TIE (because the judge revealed position
   bias).

2. :class:`ReferenceJudge` — grade a candidate answer against a known
   gold reference answer. Returns a :class:`JudgeScore` where each
   dimension is graded against the reference rather than open-ended.

Both protocols rely on the same CoT-first, Unknown-escape prompt
structure as the pointwise rubrics in ``llm_judge.py``.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Protocol, cast, runtime_checkable

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    UNKNOWN,
    JudgeScore,
    _clean_raw,
    _extract_reasoning,
)

_log = logging.getLogger(__name__)


PAIRWISE_RUBRIC = """\
You are comparing TWO candidate answers (A and B) for the same query and
context. Decide which answer is better — or call TIE if they are of
equal quality.

Criteria (in priority order):
  1. Faithfulness to the provided context (no fabrication).
  2. Directness and completeness with respect to the query.
  3. Groundedness of factual claims.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
     Compare A and B claim-by-claim against the context.
  2. If you cannot confidently pick a winner, respond "TIE".
  3. If the inputs are insufficient to grade, respond with winner
     "Unknown" and an ``unknown_reason``.
  4. After the reasoning, output exactly one JSON object on the final
     line:
     {"winner": "A"|"B"|"TIE"|"Unknown",
      "confidence": <0.0-1.0>,
      "unknown_reason": "<string-or-null>"}

Respond with ONLY the reasoning block followed by the JSON line.
"""


REFERENCE_RUBRIC = """\
You are grading a candidate answer against a known gold reference
answer. Score each dimension 1-5 against how closely the candidate
matches the reference's factual content (not necessarily its wording).

Dimensions:
  - factual_equivalence: Does the candidate convey the same facts as
    the reference? 1=entirely different, 5=fully equivalent.
  - coverage: Does the candidate cover all the information in the
    reference? 1=covers almost nothing, 5=covers everything.
  - no_extraneous_claims: Does the candidate avoid introducing claims
    not present in the reference or context? 1=many fabrications,
    5=no fabrications.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
  2. For each dimension, if you cannot grade from the given inputs,
     respond "Unknown" for that dimension.
  3. After the reasoning, output exactly one JSON object on the final
     line:
     {"factual_equivalence": <1-5|"Unknown">,
      "coverage": <1-5|"Unknown">,
      "no_extraneous_claims": <1-5|"Unknown">,
      "unknown_reasons": {"<dim>": "<reason>"}}

Respond with ONLY the reasoning block followed by the JSON line.
"""


_REASONING_BLOCK_RE = re.compile(r"<reasoning>.*?</reasoning>", re.DOTALL | re.IGNORECASE)


def _extract_balanced_json(text: str) -> str | None:
    """Return the last balanced ``{...}`` block in ``text`` or None.

    Walks the string right-to-left counting braces so nested objects
    inside the payload (``unknown_reasons``) do not confuse the parser.
    """
    for end in range(len(text) - 1, -1, -1):
        if text[end] != "}":
            continue
        depth = 0
        for start in range(end, -1, -1):
            char = text[start]
            if char == "}":
                depth += 1
            elif char == "{":
                depth -= 1
                if depth == 0:
                    return text[start : end + 1]
    return None


def _parse_final_json(raw: str) -> dict[str, Any]:
    """Parse the trailing JSON object from a CoT-first response body."""
    # Strip reasoning block so it cannot interfere with balanced-brace scan.
    stripped = _REASONING_BLOCK_RE.sub("", raw).strip()
    cleaned = _clean_raw(stripped)
    candidate = _extract_balanced_json(cleaned)
    if candidate is not None:
        try:
            return cast(dict[str, Any], json.loads(candidate))
        except json.JSONDecodeError:  # guardian: allow-silent-swallow -- balanced-JSON parse is a best-effort first pass; falls through to raw-cleaned parse below
            pass
    try:
        return cast(dict[str, Any], json.loads(cleaned))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Missing final JSON in response: {raw!r}") from exc


# ---------------------------------------------------------------------------
# Generator protocol — any callable that turns a prompt into a string.
# Keeps this module agnostic of Gemini / Claude / mock backends.
# ---------------------------------------------------------------------------


@runtime_checkable
class PromptGenerator(Protocol):
    def __call__(self, prompt: str) -> str: ...


# ---------------------------------------------------------------------------
# Pairwise
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PairwiseVerdict:
    """Outcome of a pairwise comparison."""

    winner: str  # "A", "B", "TIE", or "Unknown"
    confidence: float
    reasoning: str
    judge_model: str
    position_swap_applied: bool
    position_swap_agreed: bool | None  # None if swap not run
    unknown_reason: str | None = None


def _coerce_pairwise_payload(payload: dict[str, Any]) -> tuple[str, float, str | None]:
    winner = str(payload.get("winner", "Unknown")).strip().upper()
    if winner not in {"A", "B", "TIE", "UNKNOWN"}:
        raise ValueError(f"Invalid winner {winner!r}")
    winner = "Unknown" if winner == "UNKNOWN" else winner
    confidence = payload.get("confidence", 0.0)
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.0
    conf = max(0.0, min(1.0, conf))
    reason_val = payload.get("unknown_reason")
    reason = str(reason_val) if reason_val not in (None, "", "null") else None
    return winner, conf, reason


class PairwiseJudge:
    """Pairwise A-vs-B judge with position-swap bias mitigation."""

    def __init__(
        self,
        generate: PromptGenerator,
        judge_model: str,
        swap_on_disagreement: bool = True,
    ) -> None:
        self._generate = generate
        self._model = judge_model
        self._swap = swap_on_disagreement

    @property
    def judge_model(self) -> str:
        return self._model

    def _build_prompt(self, query: str, context: str, answer_a: str, answer_b: str) -> str:
        return (
            f"{PAIRWISE_RUBRIC}\n\n"
            f"Query:\n{query}\n\n"
            f"Context:\n{context}\n\n"
            f"Answer A:\n{answer_a}\n\n"
            f"Answer B:\n{answer_b}"
        )

    def _one_pass(
        self,
        query: str,
        context: str,
        answer_a: str,
        answer_b: str,
    ) -> tuple[str, float, str, str | None]:
        raw = self._generate(self._build_prompt(query, context, answer_a, answer_b))
        reasoning = _extract_reasoning(raw)
        try:
            payload = _parse_final_json(raw)
            winner, conf, reason = _coerce_pairwise_payload(payload)
        except ValueError as exc:
            return "Unknown", 0.0, reasoning, f"parse_error: {exc}"
        return winner, conf, reasoning, reason

    def compare(
        self,
        query: str,
        context: str,
        answer_a: str,
        answer_b: str,
    ) -> PairwiseVerdict:
        winner, conf, reasoning, reason = self._one_pass(
            query,
            context,
            answer_a,
            answer_b,
        )

        if not self._swap or winner in {"TIE", "Unknown"}:
            return PairwiseVerdict(
                winner=winner,
                confidence=conf,
                reasoning=reasoning,
                judge_model=self._model,
                position_swap_applied=False,
                position_swap_agreed=None,
                unknown_reason=reason,
            )

        # Swap positions: original A becomes B and vice versa. Expected
        # winner should FLIP ("A" -> "B" or vice versa). If it doesn't,
        # the judge exhibited position bias on this pair.
        swap_winner, swap_conf, swap_reasoning, swap_reason = self._one_pass(
            query,
            context,
            answer_b,
            answer_a,
        )
        expected_flip = {"A": "B", "B": "A"}.get(winner, winner)
        agreed = swap_winner == expected_flip
        if not agreed:
            # Position bias revealed — degrade to TIE with lowered
            # confidence and a note on the bias in reasoning.
            return PairwiseVerdict(
                winner="TIE",
                confidence=min(conf, swap_conf),
                reasoning=(
                    f"{reasoning} || swap: {swap_reasoning} "
                    f"(position bias: original winner={winner}, swap winner={swap_winner})"
                ),
                judge_model=self._model,
                position_swap_applied=True,
                position_swap_agreed=False,
                unknown_reason=reason or swap_reason,
            )

        # Swap agreed with the flipped expectation → real preference.
        return PairwiseVerdict(
            winner=winner,
            confidence=(conf + swap_conf) / 2.0,
            reasoning=f"{reasoning} || swap: {swap_reasoning}",
            judge_model=self._model,
            position_swap_applied=True,
            position_swap_agreed=True,
            unknown_reason=reason,
        )


# ---------------------------------------------------------------------------
# Reference-based
# ---------------------------------------------------------------------------


REFERENCE_DIMENSIONS: tuple[str, ...] = (
    "factual_equivalence",
    "coverage",
    "no_extraneous_claims",
)


@dataclass(frozen=True)
class ReferenceVerdict:
    """Outcome of a reference-based grade."""

    scores: dict[str, float]  # dimension -> score or NaN
    unknown_reasons: dict[str, str]
    reasoning: str
    judge_model: str


class ReferenceJudge:
    """Grade a candidate answer against a gold reference answer."""

    def __init__(self, generate: PromptGenerator, judge_model: str) -> None:
        self._generate = generate
        self._model = judge_model

    @property
    def judge_model(self) -> str:
        return self._model

    def _build_prompt(
        self,
        query: str,
        context: str,
        candidate: str,
        reference: str,
    ) -> str:
        return (
            f"{REFERENCE_RUBRIC}\n\n"
            f"Query:\n{query}\n\n"
            f"Context:\n{context}\n\n"
            f"Reference (gold) answer:\n{reference}\n\n"
            f"Candidate answer:\n{candidate}"
        )

    def grade(
        self,
        query: str,
        context: str,
        candidate: str,
        reference: str,
    ) -> ReferenceVerdict:
        raw = self._generate(self._build_prompt(query, context, candidate, reference))
        reasoning = _extract_reasoning(raw)
        try:
            payload = _parse_final_json(raw)
        except ValueError as exc:
            return ReferenceVerdict(
                scores={dim: UNKNOWN for dim in REFERENCE_DIMENSIONS},
                unknown_reasons={dim: f"parse_error: {exc}" for dim in REFERENCE_DIMENSIONS},
                reasoning=reasoning,
                judge_model=self._model,
            )

        scores: dict[str, float] = {}
        unknown: dict[str, str] = {}
        payload_reasons = payload.get("unknown_reasons") or {}
        if not isinstance(payload_reasons, dict):
            payload_reasons = {}

        for dim in REFERENCE_DIMENSIONS:
            raw_score = payload.get(dim)
            if isinstance(raw_score, str) and raw_score.strip().lower() == "unknown":
                scores[dim] = UNKNOWN
                unknown[dim] = str(payload_reasons.get(dim) or "judge returned Unknown")
                continue
            try:
                numeric = float(raw_score)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                scores[dim] = UNKNOWN
                unknown[dim] = f"non-numeric {raw_score!r}"
                continue
            if not 1.0 <= numeric <= 5.0:
                scores[dim] = UNKNOWN
                unknown[dim] = f"out-of-range {numeric}"
                continue
            scores[dim] = numeric

        return ReferenceVerdict(
            scores=scores,
            unknown_reasons=unknown,
            reasoning=reasoning,
            judge_model=self._model,
        )


__all__ = [
    "PAIRWISE_RUBRIC",
    "REFERENCE_DIMENSIONS",
    "REFERENCE_RUBRIC",
    "PairwiseJudge",
    "PairwiseVerdict",
    "PromptGenerator",
    "ReferenceJudge",
    "ReferenceVerdict",
]


# Re-export DIMENSIONS so callers that consume pointwise scores through
# this module don't need a second import.
_ = DIMENSIONS
