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

    _architecture_patterns = [
        r"\barch(itecture)?\b",
        r"\badr\b",
        r"\bdesign\s+doc\b",
        r"\binvariant\b",
        r"\bcontract\b",
        r"\bspec(ification)?\b",
        r"\bstandard\b",
        r"\bprinciple\b",
        r"\bguideline\b",
        r"\blayer\b",
        r"\bL[0-6]\b",
        r"\bADR[-\s]\d+\b",
    ]
    _policy_patterns = [
        r"\bconstitu(tion|tional)\b",
        r"\bsafety\s+(rules?|constraints?|policy|policies|boundary|layer)\b",
        r"\bguardian\b",
        r"\binjection\s+control\b",
        r"\bhard\s+(rule|constraint|limit)\b",
        r"\btrust\s+boundary\b",
        r"\bpolicy\s+enforcement\b",
        r"\bagentic\s+(policy|rule|constraint)\b",
        r"\bbare\s+except\b",
        r"\bwithout\s+timeout\b",
    ]
    _best_practice_patterns = [
        r"\bbest\s+practice\b",
        r"\bpattern\b",
        r"\btutorial\b",
        r"\bhow\s+to\b",
        r"\bexample\b",
        r"\brecipe\b",
        r"\bplaybook\b",
        r"\bframework\b",
        r"\bblast.?radius\b",
        r"\bdependency\s+analysis\b",
        r"\bagent\s+pattern\b",
        r"\brag\b",
        r"\brag\s+pipeline\b",
        r"\blangchain\b",
        r"\banthrop(ic)?\b",
        r"\bopenai\b",
    ]
    _tool_patterns = [
        r"\bmcp\b",
        r"\bmodel\s+context\s+protocol\b",
        r"\btool\s+call\b",
        r"\btool\s+contracts?\b",
        r"\bfunction\s+tool\b",
        r"\bfastmcp\b",
        r"\bagent\s+tool\b",
    ]
    _code_patterns = [
        r"\bfunction\b",
        r"\bclass\b",
        r"\bmethod\b",
        r"\bmodule\b",
        r"\bimport\b",
        r"\.py\b",
        r"\bdef\s+\w+\b",
        r"\btest_\w+\b",
        r"\bcode\b",
        r"\bimplementation\b",
        r"\bbugs?\b",
        r"\berror\b",
    ]

    def detect_topic_domain(self, query: Any) -> str:
        """Classify query into topic domain.

        Returns the domain label for collection routing:
          - 'policy'        → route to curated_agent_docs (constitutional/safety/guardian)
          - 'architecture'  → route to arch_docs with canonical prefilter
          - 'best_practice' → route to curated_agent_docs
          - 'tool_contracts'→ route to curated_agent_docs
          - 'code'          → route to code_chunks / symbols
          - 'general'       → no collection restriction

        'policy' is checked before 'architecture' — constitutional/safety/guardian
        queries must never reach arch_docs.
        """
        text = self._normalize_query(query)
        if not text:
            return "general"

        policy_re = [re.compile(p, re.IGNORECASE) for p in self._policy_patterns]
        arch_re = [re.compile(p, re.IGNORECASE) for p in self._architecture_patterns]
        bp_re = [re.compile(p, re.IGNORECASE) for p in self._best_practice_patterns]
        code_re = [re.compile(p, re.IGNORECASE) for p in self._code_patterns]
        tool_re = [re.compile(p, re.IGNORECASE) for p in self._tool_patterns]

        policy_hits = self._pattern_hits(text, policy_re)
        arch_hits = self._pattern_hits(text, arch_re)
        bp_hits = self._pattern_hits(text, bp_re)
        code_hits = self._pattern_hits(text, code_re)
        tool_hits = self._pattern_hits(text, tool_re)

        # policy is first in dict so it wins ties with architecture
        scores = {
            "policy": policy_hits,
            "architecture": arch_hits,
            "best_practice": bp_hits,
            "code": code_hits,
            "tool_contracts": tool_hits,
        }
        best = max(scores, key=lambda k: scores[k])
        if scores[best] == 0:
            return "general"
        return best


__all__ = ["QueryIntent", "QueryIntentDetector"]
