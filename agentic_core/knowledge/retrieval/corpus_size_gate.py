"""Corpus-size gate — skip RAG when long-context + caching would be better.

Per Anthropic's guidance (https://www.anthropic.com/research/contextual-retrieval),
when the entire relevant corpus fits within the model's context window AND
prompt caching is available, full-context retrieval-augmented prompting is
simpler and often more accurate than chunk-level RAG. Break-even is model- and
workflow-specific, but Anthropic cites ~200k tokens as a reasonable default
threshold for Claude Sonnet / Opus (context window is 200k; leave headroom
for output and conversation state).

This module is a PURE gate: it answers "given this corpus size, should we skip
the RAG pipeline?" It does NOT itself fetch the corpus, call the model, or
modify any retrieval state. Callers integrate it before invoking their
adaptive-retrieval gate so that small corpora short-circuit to a full-context
code path when the workflow supports it.

Design invariants:
- Pure functions. No I/O, no caller mutation.
- Anthropic-tokenizer-parity caveat: exact token counts require the
  `anthropic.count_tokens(...)` endpoint (live API call). This module offers
  a deterministic char-based heuristic (~4 chars/token) so callers can gate
  WITHOUT a live API round-trip; the heuristic ERRS ON THE SIDE OF KEEPING
  RAG (overestimates tokens), so false negatives (unnecessary full-context
  path) are rare and false positives (skipping RAG when the corpus is too
  big) are effectively zero at the default threshold.
- Model-specific headroom: callers can tune the threshold per target model.

References:
- Anthropic (2024-09). Contextual Retrieval in AI Systems.
- Anthropic API Docs. Prompt caching.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

# Claude Sonnet / Opus context window at time of writing. The threshold for
# "skip RAG, use full-context + caching" is set lower than the raw window to
# leave room for output, conversation history, and a grounding preamble.
#
# 160k tokens is a conservative default: it preserves ~40k tokens of headroom
# below the 200k window for response generation, tool outputs, and safety
# framing. Callers with explicit budget can pass a different threshold.
DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS = 160_000

# Per Anthropic's own tokenizer, English prose ranges ~3.5–4.5 chars/token.
# We use 4.0 as a round number — this slightly OVERESTIMATES tokens for prose
# (Claude's actual tokenizer produces ~3.7 chars/token on typical docs) and
# UNDERESTIMATES for code (~3.2 chars/token is typical for Python). The net
# effect: the heuristic is biased toward KEEPING RAG (safer default) when
# the corpus size is ambiguous near the threshold.
_CHARS_PER_TOKEN_HEURISTIC = 4.0


@dataclass(frozen=True)
class CorpusSizeGateResult:
    """Outcome of the corpus-size gate.

    Attributes
    ----------
    skip_rag:
        True when the caller should bypass retrieval and feed the full corpus
        (typically with prompt caching) to the model. False when the corpus
        is too large to fit.
    estimated_tokens:
        Heuristic token count used for the decision. Not model-authoritative;
        pass through `anthropic.count_tokens(...)` for exact counts.
    threshold_tokens:
        The threshold the decision was made against.
    reason:
        Short human-readable rationale suitable for logging and telemetry.
    """

    skip_rag: bool
    estimated_tokens: int
    threshold_tokens: int
    reason: str


def estimate_corpus_tokens(
    texts: Iterable[str],
    *,
    chars_per_token: float = _CHARS_PER_TOKEN_HEURISTIC,
) -> int:
    """Rough token count across many text chunks using char-based heuristic.

    Parameters
    ----------
    texts:
        Iterable of chunk/document text strings.
    chars_per_token:
        Characters per token ratio. Defaults to 4.0 which errs toward RAG.

    Returns
    -------
    Estimated total token count. Always ≥ 0.
    """
    if chars_per_token <= 0:
        raise ValueError(f"chars_per_token must be positive, got {chars_per_token}")
    total_chars = sum(len(t) for t in texts if t)
    return int(total_chars / chars_per_token)


def should_skip_rag(
    corpus_token_count: int,
    *,
    threshold_tokens: int = DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS,
) -> CorpusSizeGateResult:
    """Decide whether to skip the RAG pipeline in favor of full-context.

    Parameters
    ----------
    corpus_token_count:
        Estimated total tokens the corpus would occupy. Typically from
        `estimate_corpus_tokens(...)` or the exact Anthropic tokenizer.
    threshold_tokens:
        Skip RAG when the corpus ≤ this threshold. Default 160k (Claude
        Sonnet window with ~40k headroom for output).

    Returns
    -------
    CorpusSizeGateResult with decision, rationale, and the numbers that
    justified it.
    """
    if corpus_token_count < 0:
        raise ValueError(f"corpus_token_count must be ≥ 0, got {corpus_token_count}")

    if corpus_token_count <= threshold_tokens:
        return CorpusSizeGateResult(
            skip_rag=True,
            estimated_tokens=corpus_token_count,
            threshold_tokens=threshold_tokens,
            reason=(
                f"corpus {corpus_token_count} tokens ≤ threshold {threshold_tokens}; "
                "full-context + prompt caching is simpler and typically more accurate"
            ),
        )

    return CorpusSizeGateResult(
        skip_rag=False,
        estimated_tokens=corpus_token_count,
        threshold_tokens=threshold_tokens,
        reason=(
            f"corpus {corpus_token_count} tokens > threshold {threshold_tokens}; "
            "use RAG pipeline (retrieve + rerank + grounded prompt)"
        ),
    )


def should_skip_rag_from_texts(
    texts: Iterable[str],
    *,
    threshold_tokens: int = DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS,
    chars_per_token: float = _CHARS_PER_TOKEN_HEURISTIC,
) -> CorpusSizeGateResult:
    """Convenience: estimate corpus size from texts then gate.

    Use when the caller has the chunk text already assembled but does not
    want to count tokens itself. For production paths that repeatedly check
    the same corpus, cache the token count and call `should_skip_rag` directly.
    """
    tokens = estimate_corpus_tokens(texts, chars_per_token=chars_per_token)
    return should_skip_rag(tokens, threshold_tokens=threshold_tokens)


__all__ = [
    "CorpusSizeGateResult",
    "DEFAULT_FULL_CONTEXT_THRESHOLD_TOKENS",
    "estimate_corpus_tokens",
    "should_skip_rag",
    "should_skip_rag_from_texts",
]
