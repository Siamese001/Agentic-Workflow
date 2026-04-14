from __future__ import annotations

from enum import Enum
import re
from typing import Any


class QueryIntent(str, Enum):
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"


class QueryIntentDetector:
    """Heuristic intent classifier with stable defaults and bounded confidence."""

    _semantic_patterns = [
        r"\bhow\s+to\b",
        r"\bpurpose\b",
        r"\bexplain\b",
        r"\bimplementation\b",
        r"\bwhat\s+is\b",
        r"\bwhy\b",
        r"\bbehavior\b",
        r"\bsemantics?\b",
    ]
    _structural_patterns = [
        r"\bcalls?\b",
        r"\bimports?\b",
        r"\bcallers?\b",
        r"\bdepends?\s+on\b",
        r"\bfile\b",
        r"\bpath\b",
        r"\broute\b",
        r"\bedge\b",
    ]
    _path_tokens = ("/", "\\", ".py", "::", "->", "@")

    def __init__(self) -> None:
        self._semantic_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self._semantic_patterns]
        self._structural_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in self._structural_patterns
        ]

    @staticmethod
    def _normalize_query(query: Any) -> str:
        if query is None:
            return ""
        if isinstance(query, str):
            return query.strip()
        return str(query).strip()

    def _pattern_hits(self, text: str, regexes: list[re.Pattern[str]]) -> int:
        return sum(1 for regex in regexes if regex.search(text))

    def _structural_bonus(self, text: str) -> int:
        bonus = 0
        if any(token in text for token in self._path_tokens):
            bonus += 1
        if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\([^)]*\)", text):
            bonus += 1
        if re.search(r"\bline\s+\d+\b", text, re.IGNORECASE):
            bonus += 1
        return bonus

    def _semantic_bonus(self, text: str) -> int:
        bonus = 0
        if "?" in text:
            bonus += 1
        if re.search(r"\b(meaning|intent|goal|overview|summary)\b", text, re.IGNORECASE):
            bonus += 1
        return bonus

    def detect_intent(self, query: Any) -> QueryIntent:
        text = self._normalize_query(query)
        if not text:
            return QueryIntent.SEMANTIC

        semantic_hits = self._pattern_hits(text, self._semantic_regexes) + self._semantic_bonus(text)
        structural_hits = self._pattern_hits(text, self._structural_regexes) + self._structural_bonus(text)

        if semantic_hits > 0 and structural_hits > 0:
            return QueryIntent.HYBRID
        if structural_hits > semantic_hits:
            return QueryIntent.STRUCTURAL
        return QueryIntent.SEMANTIC

    def get_confidence(self, query: Any) -> float:
        text = self._normalize_query(query)
        if not text:
            return 0.3

        semantic_hits = self._pattern_hits(text, self._semantic_regexes) + self._semantic_bonus(text)
        structural_hits = self._pattern_hits(text, self._structural_regexes) + self._structural_bonus(text)
        total_hits = semantic_hits + structural_hits

        if total_hits == 0:
            return 0.3
        if semantic_hits > 0 and structural_hits > 0:
            return min(0.95, 0.55 + (min(semantic_hits, structural_hits) * 0.1))
        dominant_hits = max(semantic_hits, structural_hits)
        return min(0.95, 0.4 + (dominant_hits * 0.12))


__all__ = ["QueryIntent", "QueryIntentDetector"]
