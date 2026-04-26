"""Extended Retrieval Benchmark — full eval axis coverage for G8.

Extends the existing ``retrieval_benchmark.py`` with missing eval axes:
  - Citation precision: fraction of cited chunks that are relevant
  - Abstain correctness: fraction of abstain decisions that were correct
  - Per-sentence support rate: fraction of output sentences with support

These axes are required by the C0 Context Engine exit criteria.

Design:
  - ``CitationPrecisionResult`` captures per-query citation precision.
  - ``AbstainCorrectnessResult`` captures per-query abstain correctness.
  - ``ExtendedRetrievalBenchmark`` wraps an existing retrieval engine and
    computes all axes including the legacy ones from ``RetrievalBenchmark``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CitationPrecisionResult
# ---------------------------------------------------------------------------


@dataclass
class CitationPrecisionResult:
    """Citation precision for a single query.

    Attributes
    ----------
    query : str
        The query string.
    cited_chunk_ids : list[str]
        Chunk IDs cited in the output.
    relevant_chunk_ids : set[str]
        Chunk IDs that are actually relevant (ground truth).
    precision : float
        |cited ∩ relevant| / |cited| (0–1, or 1.0 if no citations).
    false_citations : list[str]
        Cited IDs that are not in the relevant set.
    """

    query: str
    cited_chunk_ids: list[str]
    relevant_chunk_ids: set[str]
    precision: float = 1.0
    false_citations: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# AbstainCorrectnessResult
# ---------------------------------------------------------------------------


@dataclass
class AbstainCorrectnessResult:
    """Abstain correctness for a single query.

    Attributes
    ----------
    query : str
        The query string.
    should_abstain : bool
        Ground truth: whether the system should have abstained.
    did_abstain : bool
        Whether the system actually abstained.
    correct : bool
        True if should_abstain == did_abstain.
    """

    query: str
    should_abstain: bool
    did_abstain: bool
    correct: bool = True


# ---------------------------------------------------------------------------
# ExtendedRetrievalBenchmark
# ---------------------------------------------------------------------------


class ExtendedRetrievalBenchmark:
    """Extended retrieval benchmark covering all G8 eval axes.

    Computes citation precision, abstain correctness, and per-sentence
    support rate in addition to the legacy recall/precision/MRR/NDCG
    metrics from ``RetrievalBenchmark``.

    Args:
        engine : Any
            A retrieval engine with a ``search()`` method.
    """

    def __init__(self, engine: Any) -> None:
        self._engine = engine

    def compute_citation_precision(
        self,
        query: str,
        cited_chunk_ids: list[str],
        relevant_chunk_ids: set[str],
    ) -> CitationPrecisionResult:
        """Compute citation precision for a single query.

        Args:
            query: The query string.
            cited_chunk_ids: Chunk IDs cited in the output.
            relevant_chunk_ids: Ground-truth relevant chunk IDs.

        Returns:
            ``CitationPrecisionResult``.

        Raises:
            TypeError: If cited_chunk_ids is not a list or relevant_chunk_ids is not a set.
        """
        if not isinstance(cited_chunk_ids, list):
            raise TypeError(f"cited_chunk_ids must be list, got {type(cited_chunk_ids).__name__}")
        if not isinstance(relevant_chunk_ids, (set, frozenset)):
            raise TypeError(f"relevant_chunk_ids must be set, got {type(relevant_chunk_ids).__name__}")
        if not cited_chunk_ids:
            return CitationPrecisionResult(
                query=query,
                cited_chunk_ids=cited_chunk_ids,
                relevant_chunk_ids=relevant_chunk_ids,
                precision=1.0,
            )

        cited_set = set(cited_chunk_ids)
        true_positives = cited_set & relevant_chunk_ids
        precision = len(true_positives) / len(cited_set)
        false_citations = sorted(cited_set - relevant_chunk_ids)

        return CitationPrecisionResult(
            query=query,
            cited_chunk_ids=cited_chunk_ids,
            relevant_chunk_ids=relevant_chunk_ids,
            precision=precision,
            false_citations=false_citations,
        )

    def compute_abstain_correctness(
        self,
        query: str,
        should_abstain: bool,
        did_abstain: bool,
    ) -> AbstainCorrectnessResult:
        """Compute abstain correctness for a single query.

        Args:
            query: The query string.
            should_abstain: Ground truth — should the system have abstained?
            did_abstain: Did the system actually abstain?

        Returns:
            ``AbstainCorrectnessResult``.
        """
        correct = should_abstain == did_abstain
        return AbstainCorrectnessResult(
            query=query,
            should_abstain=should_abstain,
            did_abstain=did_abstain,
            correct=correct,
        )

    def compute_abstain_report(
        self,
        results: list[AbstainCorrectnessResult],
    ) -> dict[str, Any]:
        """Aggregate abstain correctness across queries.

        Returns:
            Dict with total, correct_count, correctness_rate,
            false_abstains, false_answers.
        """
        if not results:
            return {"total": 0, "correctness_rate": 1.0}

        total = len(results)
        correct_count = sum(1 for r in results if r.correct)
        false_abstains = sum(1 for r in results if r.did_abstain and not r.should_abstain)
        false_answers = sum(1 for r in results if not r.did_abstain and r.should_abstain)

        return {
            "total": total,
            "correct_count": correct_count,
            "correctness_rate": correct_count / total,
            "false_abstains": false_abstains,
            "false_answers": false_answers,
        }

    def compute_citation_report(
        self,
        results: list[CitationPrecisionResult],
    ) -> dict[str, Any]:
        """Aggregate citation precision across queries.

        Returns:
            Dict with total, avg_precision, min_precision,
            total_false_citations.
        """
        if not results:
            return {"total": 0, "avg_precision": 1.0}

        n = len(results)
        avg_prec = sum(r.precision for r in results) / n
        min_prec = min(r.precision for r in results)
        total_false = sum(len(r.false_citations) for r in results)

        return {
            "total": n,
            "avg_precision": avg_prec,
            "min_precision": min_prec,
            "total_false_citations": total_false,
        }

    def compute_support_rate(
        self,
        sentence_supports: list[bool],
    ) -> float:
        """Compute per-sentence support rate.

        Args:
            sentence_supports: List of booleans, one per output sentence,
                indicating whether the sentence has supporting evidence.

        Returns:
            Fraction of sentences with support (0–1).

        Raises:
            TypeError: If sentence_supports is not a list.
        """
        if not isinstance(sentence_supports, list):
            raise TypeError(f"sentence_supports must be list, got {type(sentence_supports).__name__}")
        if not sentence_supports:
            return 1.0
        return sum(sentence_supports) / len(sentence_supports)
