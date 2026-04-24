"""Code-based claim extractor + hallucination metric (ADR-041).

Design:
- Extract claim-bearing sentences with a simple regex tokenizer.
- Classify each claim's support source against (a) the retrieved context
  text and (b) the canonical tool-call ledger from the sealed artifact.
- Emit a deterministic hallucination metric:

    {
      "score_0_1": 1.0 - unsupported / max(1, total),
      "unsupported_claim_count": int,
      "tool_grounded": bool,   # every tool claim matches ledger
    }

This is a deterministic baseline; an LLM-based extractor can drop in later
under the same interface.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Iterable, Literal, Sequence

SupportSource = Literal["context", "tool_output", "parametric", "unsupported"]

# Sentence splitter: breaks on ., !, ? followed by whitespace/EOL.
# Tolerates trailing quotes/parentheses.
_SENTENCE_SPLIT: Final[re.Pattern[str]] = re.compile(r"(?<=[.!?])[\"')\]]*\s+")

# Sentences that do not carry factual content; skipped before classification.
_NON_CLAIM_PREFIXES: Final[tuple[str, ...]] = (
    "for example",
    "in other words",
    "note that",
    "please ",
    "would you",
    "could you",
    "do you",
    "let me ",
    "i'll ",
    "i will ",
)

# A claim is "tool-grounded" when its text references any canonical tool
# name; matching is case-insensitive substring.
_TOOL_VERB_HINTS: Final[tuple[str, ...]] = (
    "called ",
    "invoked ",
    "ran ",
    "queried ",
    "fetched ",
    "retrieved ",
    "searched ",
    "wrote ",
    "computed ",
)


@dataclass(frozen=True)
class Claim:
    """A single extracted claim."""

    text: str
    support: SupportSource
    supporting_tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class HallucinationReport:
    """Output of claim_extractor.analyze."""

    score_0_1: float
    unsupported_claim_count: int
    total_claim_count: int
    tool_grounded: bool
    claims: tuple[Claim, ...]

    def as_exit_decision_payload(self) -> dict[str, object]:
        return {
            "score_0_1": self.score_0_1,
            "unsupported_claim_count": self.unsupported_claim_count,
            "tool_grounded": self.tool_grounded,
        }


def _split_sentences(text: str) -> list[str]:
    # Normalize newlines into spaces so the regex split sees a single sequence.
    flat = re.sub(r"\s+", " ", text.strip())
    if not flat:
        return []
    pieces = _SENTENCE_SPLIT.split(flat)
    return [piece.strip() for piece in pieces if piece.strip()]


def _is_claim(sentence: str) -> bool:
    lower = sentence.lower()
    if len(lower) < 8:
        return False
    if any(lower.startswith(prefix) for prefix in _NON_CLAIM_PREFIXES):
        return False
    if lower.endswith("?"):
        return False
    return True


def _context_supports(claim: str, context_text: str) -> bool:
    """Trivial substring overlap check — any 5+ char consecutive word matches."""
    if not context_text:
        return False
    claim_lower = claim.lower()
    context_lower = context_text.lower()
    words = re.findall(r"[a-zA-Z0-9_\-]{5,}", claim_lower)
    # If any notable word appears in context, count as supported for this
    # deterministic baseline. A smarter extractor would use semantic matching.
    for word in words:
        if word in context_lower:
            return True
    return False


def _claim_tool_refs(claim: str, tool_names: Sequence[str]) -> tuple[str, ...]:
    claim_lower = claim.lower()
    hits = tuple(name for name in tool_names if name and name.lower() in claim_lower)
    return hits


def _claim_mentions_tool_action(claim: str) -> bool:
    claim_lower = claim.lower()
    return any(hint in claim_lower for hint in _TOOL_VERB_HINTS)


def analyze(
    answer_text: str,
    *,
    context_text: str = "",
    tool_calls: Iterable[object] = (),
) -> HallucinationReport:
    """Classify claims in ``answer_text`` and return a HallucinationReport.

    Parameters
    ----------
    answer_text:
        The sealed final artifact text.
    context_text:
        Concatenated retrieved context (C0 bundle text). Optional.
    tool_calls:
        Iterable of canonical tool-call records OR objects with a ``tool``
        attribute. Used to classify tool_grounded support.
    """
    sentences = _split_sentences(answer_text)
    tool_names: list[str] = []
    for call in tool_calls:
        if isinstance(call, dict):
            name = call.get("tool")
        else:
            name = getattr(call, "tool", None)
        if isinstance(name, str) and name:
            tool_names.append(name)
    ledger_names = tuple(sorted(set(tool_names)))

    claims: list[Claim] = []
    for sentence in sentences:
        if not _is_claim(sentence):
            continue
        tool_refs = _claim_tool_refs(sentence, ledger_names)
        if tool_refs:
            claims.append(Claim(text=sentence, support="tool_output", supporting_tools=tool_refs))
            continue
        if _claim_mentions_tool_action(sentence) and not ledger_names:
            # Claim references a tool action but no tools were called — unsupported.
            claims.append(Claim(text=sentence, support="unsupported"))
            continue
        if _context_supports(sentence, context_text):
            claims.append(Claim(text=sentence, support="context"))
            continue
        # No context overlap, no tool ref → parametric or unsupported.
        # Conservative default: parametric (model knowledge) when context
        # was provided but no overlap found; unsupported when no context.
        if context_text:
            claims.append(Claim(text=sentence, support="parametric"))
        else:
            claims.append(Claim(text=sentence, support="unsupported"))

    total = len(claims)
    unsupported = sum(1 for claim in claims if claim.support == "unsupported")
    # tool_grounded: every claim that references a tool action AND names a tool
    # matches a real tool call. Failure modes:
    #   - claim mentions tool action but no tool was called → not grounded.
    #   - claim references tool name not in ledger → covered by tool_refs check.
    tool_grounded = True
    for claim in claims:
        if _claim_mentions_tool_action(claim.text) and not claim.supporting_tools:
            tool_grounded = False
            break

    score = 1.0 - (unsupported / total) if total > 0 else 1.0
    return HallucinationReport(
        score_0_1=score,
        unsupported_claim_count=unsupported,
        total_claim_count=total,
        tool_grounded=tool_grounded,
        claims=tuple(claims),
    )


__all__ = [
    "Claim",
    "HallucinationReport",
    "SupportSource",
    "analyze",
]
