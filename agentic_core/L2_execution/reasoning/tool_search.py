"""
Tool Search Tool — W4-P4.1 (gap plan b7c4e2: G6).

Anthropic pattern: instead of binding every tool statically, the agent
queries a description-keyed index to retrieve the subset it needs, keeping
the active set ≤ 10-20 (Google guidance).

Implementation: TF-IDF-style lexical ranking over registered tool
descriptions. No external dependencies — stdlib only. Swappable with an
embedding-based retriever later; the ``ToolSearchResult`` contract stays
stable.

Design choices:
* Index is in-memory and keyed by ``tool_name``.
* Query ranking is case-insensitive word overlap with IDF weighting.
* ``search(query, k)`` caps the result at ``k`` (default 10) matching the
  "≤ 10-20 active tools" invariant from the plan.
* Tie-breaking uses registered insertion order for determinism in tests.
"""

from __future__ import annotations

import math
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import Iterable, Mapping

__all__ = [
    "ToolSearchEntry",
    "ToolSearchResult",
    "ToolSearchIndex",
]


_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text or "")]


@dataclass(frozen=True, slots=True)
class ToolSearchEntry:
    """Indexable record for a single tool."""

    tool_name: str
    description: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ToolSearchResult:
    """Ranked hit."""

    tool_name: str
    score: float
    description: str


class ToolSearchIndex:
    """Tiny TF-IDF index over tool names + descriptions + tags.

    Usage::

        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry(tool_name="orders.submit",
                                     description="Submit a customer order"))
        hits = idx.search("customer order", k=5)
    """

    def __init__(self) -> None:
        self._entries: OrderedDict[str, ToolSearchEntry] = OrderedDict()
        self._doc_freq: Counter[str] = Counter()
        self._term_freq: dict[str, Counter[str]] = {}

    def register(self, entry: ToolSearchEntry) -> None:
        if not entry.tool_name:
            raise ValueError("tool_name is required")
        if entry.tool_name in self._entries:
            # Re-registering overrides. Drop the previous doc freq first.
            prior = self._term_freq.pop(entry.tool_name, Counter())
            for term in prior:
                self._doc_freq[term] -= 1
                if self._doc_freq[term] <= 0:
                    del self._doc_freq[term]
        self._entries[entry.tool_name] = entry
        tokens = _tokenize(entry.tool_name) + _tokenize(entry.description) + [
            t.lower() for t in entry.tags
        ]
        tf = Counter(tokens)
        self._term_freq[entry.tool_name] = tf
        for term in tf:
            self._doc_freq[term] += 1

    def register_many(self, entries: Iterable[ToolSearchEntry]) -> None:
        for e in entries:
            self.register(e)

    def size(self) -> int:
        return len(self._entries)

    def has(self, tool_name: str) -> bool:
        return tool_name in self._entries

    def search(self, query: str, *, k: int = 10) -> list[ToolSearchResult]:
        """Return the top-``k`` matches by TF-IDF score. Stable across ties."""
        if k <= 0:
            raise ValueError("k must be positive")
        q_tokens = _tokenize(query)
        if not q_tokens or not self._entries:
            return []
        n_docs = len(self._entries)
        idf: Mapping[str, float] = {
            term: math.log(1 + n_docs / (1 + self._doc_freq[term])) for term in q_tokens
        }
        results: list[ToolSearchResult] = []
        for name, tf in self._term_freq.items():
            score = 0.0
            for term in q_tokens:
                if term in tf:
                    score += tf[term] * idf[term]
            if score > 0:
                entry = self._entries[name]
                results.append(
                    ToolSearchResult(
                        tool_name=name, score=score, description=entry.description
                    )
                )
        # Sort by score desc, then by registered insertion order (stable).
        order_index = {n: i for i, n in enumerate(self._entries.keys())}
        results.sort(key=lambda r: (-r.score, order_index[r.tool_name]))
        return results[:k]

    def clear(self) -> None:
        self._entries.clear()
        self._doc_freq.clear()
        self._term_freq.clear()
