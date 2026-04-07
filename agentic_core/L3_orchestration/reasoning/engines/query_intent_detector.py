"""Query Intent Detection for Hybrid Search.

Determines whether a query is semantic (intent-based) or structural (graph-based).
"""

import logging
import re
from typing import Literal

Logger = logging.getLogger(__name__)


class QueryIntent:
    """Query intent classification."""

    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"


class QueryIntentDetector:
    """Detects query intent based on patterns and keywords."""

    # Structural query patterns
    STRUCTURAL_PATTERNS = [
        r"calls?\s+\w+",  # "calls X", "call function"
        r"import(s|ed)?\s+\w+",  # "imports X", "imported from"
        r"depend(s|encies)?\s+on",  # "depends on", "dependencies of"
        r"parent\s+of",  # "parent of"
        r"child\s+of",  # "child of"
        r"caller(s)?\s+of",  # "callers of"
        r"callee(s)?\s+of",  # "callees of"
        r"violat(es|ions)?",  # "violates", "violations"
        r"layer\s+\w+",  # "layer L2"
        r"inherits?\s+from",  # "inherits from"
        r"extends?",  # "extends"
    ]

    # Semantic query patterns
    SEMANTIC_PATTERNS = [
        r"how\s+to\s+\w+",  # "how to do X"
        r"what\s+is",  # "what is X"
        r"explain\s+\w+",  # "explain X"
        r"describe\s+\w+",  # "describe X"
        r"why\s+does",  # "why does X"
        r"when\s+to\s+use",  # "when to use X"
    ]

    def __init__(self):
        self._structural_regex = re.compile("|".join(self.STRUCTURAL_PATTERNS), re.IGNORECASE)
        self._semantic_regex = re.compile("|".join(self.SEMANTIC_PATTERNS), re.IGNORECASE)

    def detect_intent(self, query: str) -> Literal["semantic", "structural", "hybrid"]:
        """Detect query intent.

        Args:
            query: Query string

        Returns:
            Intent classification: semantic, structural, or hybrid
        """
        if not query or not isinstance(query, str):
            return QueryIntent.SEMANTIC

        # Check for structural patterns
        structural_matches = self._structural_regex.findall(query)
        has_structural = len(structural_matches) > 0

        # Check for semantic patterns
        semantic_matches = self._semantic_regex.findall(query)
        has_semantic = len(semantic_matches) > 0

        # Determine intent
        if has_structural and has_semantic:
            return QueryIntent.HYBRID
        elif has_structural:
            return QueryIntent.STRUCTURAL
        elif has_semantic:
            return QueryIntent.SEMANTIC
        else:
            # Default to semantic for unknown patterns
            return QueryIntent.SEMANTIC

    def get_confidence(self, query: str) -> float:
        """Get confidence score for intent detection.

        Args:
            query: Query string

        Returns:
            Confidence score between 0.0 and 1.0
        """
        structural_matches = len(self._structural_regex.findall(query))
        semantic_matches = len(self._semantic_regex.findall(query))

        total_matches = structural_matches + semantic_matches
        if total_matches == 0:
            return 0.3  # Low confidence for no matches

        # Higher confidence with more matches
        confidence = min(total_matches * 0.2, 1.0)
        return confidence
