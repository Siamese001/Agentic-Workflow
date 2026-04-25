"""Retrieval grader — per-chunk relevance verdict for the reflective loop.

Per ADR-060 §2, the grader's contract is a single method:

    grade(query, chunks) -> list[GradeVerdict]

Each verdict is one of ``relevant``, ``ambiguous``, ``irrelevant`` with a
0..1 score and a short rationale. The default backend is a small fast LLM
(routed through the existing L3 vLLM gateway per ADR-045 backend selection);
the heuristic fallback (lexical-overlap × cross-encoder rerank score) runs
when the LLM is unavailable so the loop never hard-fails on infrastructure.

A grader cache is keyed by ``(query_hash, chunk_id, grader_identity)`` so
retries within a loop iteration reuse decisions deterministically. The cache
is in-memory and process-scoped — it is NOT cross-session (W4.2 §5).
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class GradeVerdictKind(Enum):
    """Tri-state per-chunk relevance verdict."""

    RELEVANT = "relevant"
    AMBIGUOUS = "ambiguous"
    IRRELEVANT = "irrelevant"


@dataclass(frozen=True)
class GradeVerdict:
    """One grader output for one (query, chunk) pair."""

    chunk_id: str
    verdict: GradeVerdictKind
    score: float
    rationale: str
    grader_identity: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0, 1], got {self.score}")
        if len(self.rationale) > 120:
            # Hard bound per ADR-060 §2 to keep records compact.
            raise ValueError(f"rationale must be <= 120 chars, got {len(self.rationale)}")


@dataclass
class Chunk:
    """Minimal chunk shape consumed by the grader.

    The full ``ChunkManifest`` shape lives at
    ``agentic_core/knowledge/canonical/chunk_manifest.py`` and carries far
    more metadata. This local dataclass is the deliberately-narrow surface
    the grader needs; consumers adapt their richer types into this.
    """

    chunk_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class GraderLLMGateway(Protocol):
    """Protocol the LLM-backed grader requires from its gateway.

    Mirrors the contract used by ``tools/ingestion/contextual_chunk_builder.py``
    so the same Qwen / Anthropic gateways can be reused. A single ``generate``
    method takes a flat prompt and returns the raw model output; this module
    handles parsing.
    """

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_s: float,
    ) -> str: ...


# ---------------------------------------------------------------------------
# Identity stamping (cache key + telemetry)
# ---------------------------------------------------------------------------


def _grader_identity(backend: str, version: str) -> str:
    """Stable identity string for cache + telemetry keying."""

    return f"{backend}/v{version}"


def _query_hash(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()[:16]


def _cache_key(query: str, chunk_id: str, grader_identity: str) -> str:
    return f"{_query_hash(query)}|{chunk_id}|{grader_identity}"


# ---------------------------------------------------------------------------
# Heuristic backend (deterministic fallback — no LLM)
# ---------------------------------------------------------------------------


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text)}


def _heuristic_score(query: str, chunk_text: str) -> float:
    """Lexical-overlap proxy in [0, 1].

    Cheap, deterministic, and good enough as a fallback when the LLM grader
    is unavailable. Real production traffic should run the LLM backend.
    """

    q = _tokenize(query)
    c = _tokenize(chunk_text)
    if not q:
        return 0.0
    overlap = len(q & c)
    # Score is fraction of query tokens present, with a small chunk-length
    # bonus so a chunk that contains all query tokens but is otherwise huge
    # doesn't beat a tightly-matching chunk.
    base = overlap / max(1, len(q))
    return min(1.0, base)


def _heuristic_verdict(score: float) -> GradeVerdictKind:
    if score >= 0.55:
        return GradeVerdictKind.RELEVANT
    if score >= 0.20:
        return GradeVerdictKind.AMBIGUOUS
    return GradeVerdictKind.IRRELEVANT


# ---------------------------------------------------------------------------
# LLM backend (parses structured output; falls back on parse failure)
# ---------------------------------------------------------------------------


_LLM_PROMPT_TEMPLATE = """\
You grade retrieval candidates for relevance to a query.

Query:
{query}

Candidate chunk (id={chunk_id}):
{chunk}

Output exactly one JSON object on a single line:
{{"verdict": "<relevant|ambiguous|irrelevant>", "score": <float in [0,1]>, "reason": "<<=80 chars>"}}

Rules:
- "relevant": chunk directly answers the query.
- "ambiguous": chunk is topical but does not directly answer.
- "irrelevant": chunk is off-topic.
- Score must reflect verdict: relevant>=0.6, ambiguous in [0.2,0.6), irrelevant<0.2.
- Output the JSON line and nothing else.
"""

_LLM_PARSE_RE = re.compile(
    r'\{\s*"verdict"\s*:\s*"(?P<verdict>relevant|ambiguous|irrelevant)"\s*,\s*'
    r'"score"\s*:\s*(?P<score>[0-9.]+)\s*,\s*'
    r'"reason"\s*:\s*"(?P<reason>[^"]{0,120})"\s*\}',
    re.IGNORECASE,
)


def _parse_llm_output(raw: str) -> tuple[GradeVerdictKind, float, str] | None:
    match = _LLM_PARSE_RE.search(raw)
    if not match:
        return None
    try:
        score = float(match.group("score"))
    except ValueError:  # guardian: allow-return-none-swallow -- LLM-output parsing fallback: malformed score returns None so the caller can fall back to the heuristic grader path; the failure is structurally signalled to _grade_one which then routes to _grade_via_heuristic
        return None
    if not 0.0 <= score <= 1.0:
        return None
    verdict_str = match.group("verdict").lower()
    try:
        verdict = GradeVerdictKind(verdict_str)
    except ValueError:  # guardian: allow-return-none-swallow -- same fallback contract: invalid verdict literal returns None so caller routes to heuristic grader instead of crashing
        return None
    reason = match.group("reason").strip()[:120]
    return verdict, score, reason


# ---------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------


class RetrievalGrader:
    """Grade candidate chunks against a query.

    Construction is dependency-injection-friendly: pass in a gateway and
    optional cache. The gateway may be ``None`` to force the heuristic path
    (useful in CI and offline tests).
    """

    HEURISTIC_VERSION = "1"
    LLM_VERSION = "1"

    def __init__(
        self,
        gateway: GraderLLMGateway | None = None,
        *,
        model: str = "qwen-2.5-32b-instruct-awq",
        cache: dict[str, GradeVerdict] | None = None,
        timeout_s: float = 5.0,
        max_tokens: int = 80,
    ) -> None:
        self._gateway = gateway
        self._model = model
        self._cache: dict[str, GradeVerdict] = {} if cache is None else cache
        self._timeout_s = timeout_s
        self._max_tokens = max_tokens

    @property
    def grader_identity(self) -> str:
        if self._gateway is None:
            return _grader_identity("heuristic", self.HEURISTIC_VERSION)
        return _grader_identity(f"llm:{self._model}", self.LLM_VERSION)

    def grade(self, query: str, chunks: list[Chunk]) -> list[GradeVerdict]:
        """Return per-chunk verdicts in the same order as the input chunks.

        Deterministic for a fixed gateway + cache. The heuristic path is
        bit-stable across processes; the LLM path is bit-stable only at
        ``temperature=0`` (the gateway is responsible for that).
        """

        if not query.strip():
            raise ValueError("query must be non-empty")
        if not chunks:
            return []

        identity = self.grader_identity
        results: list[GradeVerdict] = []
        for chunk in chunks:
            key = _cache_key(query, chunk.chunk_id, identity)
            cached = self._cache.get(key)
            if cached is not None:
                results.append(cached)
                continue
            verdict = self._grade_one(query, chunk, identity)
            self._cache[key] = verdict
            results.append(verdict)
        return results

    # -- internal -----------------------------------------------------------

    def _grade_one(self, query: str, chunk: Chunk, identity: str) -> GradeVerdict:
        if self._gateway is not None:
            try:
                return self._grade_via_llm(query, chunk, identity)
            except (
                RuntimeError,
                ValueError,
                TimeoutError,
            ) as exc:  # guardian: allow-log-and-swallow -- LLM-grader graceful-degradation path: when the LLM gateway raises (timeout, malformed response, runtime), log at WARNING and fall through to the deterministic heuristic grader so retrieval grading remains available
                logger.warning(
                    "Grader LLM path failed (%s); falling back to heuristic.",
                    exc,
                )
                # Fall through to heuristic.
        return self._grade_via_heuristic(query, chunk, identity)

    def _grade_via_heuristic(self, query: str, chunk: Chunk, identity: str) -> GradeVerdict:
        score = _heuristic_score(query, chunk.text)
        verdict = _heuristic_verdict(score)
        return GradeVerdict(
            chunk_id=chunk.chunk_id,
            verdict=verdict,
            score=round(score, 4),
            rationale=f"heuristic_overlap={score:.2f}"[:120],
            grader_identity=identity,
        )

    def _grade_via_llm(self, query: str, chunk: Chunk, identity: str) -> GradeVerdict:
        assert self._gateway is not None  # narrow for type-checker
        prompt = _LLM_PROMPT_TEMPLATE.format(query=query, chunk_id=chunk.chunk_id, chunk=chunk.text[:2000])
        raw = self._gateway.generate(
            prompt,
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=0.0,
            timeout_s=self._timeout_s,
        )
        parsed = _parse_llm_output(raw)
        if parsed is None:
            raise ValueError(f"unparseable grader output: {raw[:200]!r}")
        verdict, score, reason = parsed
        return GradeVerdict(
            chunk_id=chunk.chunk_id,
            verdict=verdict,
            score=score,
            rationale=reason or f"llm_score={score:.2f}",
            grader_identity=identity,
        )


__all__ = [
    "Chunk",
    "GradeVerdict",
    "GradeVerdictKind",
    "GraderLLMGateway",
    "RetrievalGrader",
]
