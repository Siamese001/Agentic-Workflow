"""Query Intent Expansion - Query Preprocessing

Implements spec-compliant query intent expansion from Agentic Retrieval Models v9:
- Query understanding and analysis
- Intent classification (factual, exploratory, comparative)
- Query expansion with synonyms and related terms
- Query reformulation for better retrieval
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)


@dataclass
class QueryIntent:
    """Parsed query intent."""
    original_query: str
    intent_type: str  # factual, exploratory, comparative, procedural
    expanded_query: str
    expansion_terms: list[str] = field(default_factory=list)
    reformulated_queries: list[str] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    complexity_score: float = 0.5


class QueryIntentExpander:
    """Query intent expansion and preprocessing.

    Analyzes queries and expands them for better retrieval.
    """

    # Common synonyms for technical terms
    SYNONYMS = {
        "adg": ["dependency graph", "architecture graph", "code graph"],
        "embedding": ["vector", "encoding", "representation"],
        "cache": ["store", "buffer", "memory"],
        "retrieval": ["search", "fetch", "query", "lookup"],
        "chunk": ["segment", "piece", "block", "unit"],
        "pipeline": ["workflow", "process", "sequence"],
        "agent": ["worker", "process", "executor"],
    }

    # Intent patterns
    INTENT_PATTERNS = {
        "factual": [
            r"what is",
            r"what are",
            r"how does",
            r"define",
            r"explain",
        ],
        "comparative": [
            r"vs",
            r"versus",
            r"compare",
            r"difference between",
            r"better than",
        ],
        "procedural": [
            r"how to",
            r"how do i",
            r"steps to",
            r"guide",
            r"tutorial",
        ],
        "exploratory": [
            r"why",
            r"when",
            r"where",
            r"which",
            r"best",
        ],
    }

    def __init__(self, enable_llm_expansion: bool = False):
        """Initialize query expander.

        Args:
            enable_llm_expansion: Use LLM for advanced expansion
        """
        self.enable_llm_expansion = enable_llm_expansion
        self._expansion_count = 0

    def expand(self, query: str) -> QueryIntent:
        """Expand query with intent understanding.

        Args:
            query: Original user query

        Returns:
            QueryIntent with expansions
        """
        _emit_records_execution_trace(
            f"expand_{self._expansion_count}",
            LayerSegment.L1_COGNITION,
            "QueryIntentExpander.expand"
        )

        # Clean query
        cleaned = self._clean_query(query)

        # Detect intent
        intent_type = self._detect_intent(cleaned)

        # Extract entities
        entities = self._extract_entities(cleaned)

        # Expand terms
        expansion_terms = self._expand_terms(cleaned)

        # Build expanded query
        expanded = self._build_expanded_query(cleaned, expansion_terms)

        # Reformulate for retrieval
        reformulated = self._reformulate_queries(cleaned, intent_type)

        # Calculate complexity
        complexity = self._calculate_complexity(cleaned)

        intent = QueryIntent(
            original_query=query,
            intent_type=intent_type,
            expanded_query=expanded,
            expansion_terms=expansion_terms,
            reformulated_queries=reformulated,
            entities=entities,
            complexity_score=complexity,
        )

        self._expansion_count += 1

        return intent

    def _clean_query(self, query: str) -> str:
        """Clean and normalize query."""
        # Remove extra whitespace
        cleaned = " ".join(query.split())
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\-\'\?\.]', ' ', cleaned)
        return cleaned.strip().lower()

    def _detect_intent(self, query: str) -> str:
        """Detect query intent type."""
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent_type

        # Default based on query structure
        if query.endswith("?"):
            return "exploratory"

        if any(word in query for word in ["implement", "create", "build"]):
            return "procedural"

        return "factual"

    def _extract_entities(self, query: str) -> list[dict[str, Any]]:
        """Extract entities from query."""
        entities = []

        # Technical terms (camelCase, snake_case, kebab-case)
        patterns = [
            r'\b[a-z]+(?:[A-Z][a-z]+)+\b',  # camelCase
            r'\b[a-z]+(?:_[a-z]+)+\b',       # snake_case
            r'\b[a-z]+(?:-[a-z]+)+\b',       # kebab-case
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, query):
                entities.append({
                    "text": match.group(),
                    "type": "technical_term",
                    "position": match.start(),
                })

        # Layer references (L0, L1, etc.)
        for match in re.finditer(r'\bL[0-6]\b', query, re.IGNORECASE):
            entities.append({
                "text": match.group(),
                "type": "architecture_layer",
                "position": match.start(),
            })

        return entities

    def _expand_terms(self, query: str) -> list[str]:
        """Expand query with synonyms."""
        expansion_terms = []
        query_words = set(query.split())

        for term, synonyms in self.SYNONYMS.items():
            if term in query or any(word in query_words for word in term.split()):
                expansion_terms.extend(synonyms)

        # Remove duplicates and terms already in query
        expansion_terms = [
            t for t in set(expansion_terms)
            if t.lower() not in query
        ]

        return expansion_terms[:5]  # Limit expansions

    def _build_expanded_query(self, query: str, expansion_terms: list[str]) -> str:
        """Build expanded query string."""
        if not expansion_terms:
            return query

        # Add expansion terms in parentheses for OR search
        expansion_str = " OR ".join(expansion_terms)
        return f"({query}) OR ({expansion_str})"

    def _reformulate_queries(self, query: str, intent_type: str) -> list[str]:
        """Generate reformulated queries for better retrieval."""
        reformulated = []

        if intent_type == "comparative":
            # Split comparisons
            parts = re.split(r'\s+(?:vs|versus|compared to)\s+', query, flags=re.IGNORECASE)
            if len(parts) == 2:
                reformulated.append(f"what is {parts[0]}")
                reformulated.append(f"what is {parts[1]}")
                reformulated.append(f"{parts[0]} features")
                reformulated.append(f"{parts[1]} features")

        elif intent_type == "procedural":
            # Add implementation-focused variants
            reformulated.append(f"how to implement {query}")
            reformulated.append(query.replace("how to ", "").replace("how do i ", ""))

        elif intent_type == "factual":
            # Add definition and explanation variants
            if "what is" in query:
                base = query.replace("what is ", "").replace("what are ", "")
                reformulated.append(f"{base} definition")
                reformulated.append(f"{base} explained")

        # Remove duplicates
        seen = {query.lower()}
        unique = []
        for r in reformulated:
            if r.lower() not in seen:
                unique.append(r)
                seen.add(r.lower())

        return unique[:3]  # Limit reformulations

    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score (0-1)."""
        complexity = 0.3

        # Length factor
        word_count = len(query.split())
        if word_count > 10:
            complexity += 0.1
        if word_count > 20:
            complexity += 0.1

        # Structural complexity
        if " and " in query:
            complexity += 0.1
        if any(word in query for word in ["compare", "versus", "vs"]):
            complexity += 0.15

        # Question complexity
        if query.count("?") > 1:
            complexity += 0.1

        return min(complexity, 1.0)


class QueryPreprocessor:
    """Main query preprocessing pipeline."""

    def __init__(self):
        """Initialize query preprocessor."""
        self.expander = QueryIntentExpander()
        self._process_count = 0

    def process(self, query: str) -> QueryIntent:
        """Process query through full pipeline.

        Args:
            query: Raw user query

        Returns:
            Processed QueryIntent
        """
        _emit_records_execution_trace(
            f"preprocess_{self._process_count}",
            LayerSegment.L1_COGNITION,
            "QueryPreprocessor.process"
        )

        intent = self.expander.expand(query)
        self._process_count += 1

        return intent

    def get_stats(self) -> dict[str, Any]:
        """Get preprocessor statistics."""
        return {
            "processed_count": self._process_count,
        }


# Global instance
_global_preprocessor: QueryPreprocessor | None = None


def get_global_preprocessor() -> QueryPreprocessor:
    """Get or create global preprocessor."""
    global _global_preprocessor
    if _global_preprocessor is None:
        _global_preprocessor = QueryPreprocessor()
    return _global_preprocessor


def preprocess_query(query: str) -> QueryIntent:
    """Convenience function to preprocess query."""
    return get_global_preprocessor().process(query)
