"""Query Tagger.

Tagging for query attribution and analysis.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class QueryTags:
    """Tags for a query."""

    intent: str = "unknown"
    domain: str = "general"
    complexity: str = "medium"
    urgency: str = "normal"
    topic_tags: list[str] = field(default_factory=list)
    user_segments: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class QueryTagger:
    """Tags queries for attribution and analysis.

    The QueryTagger analyzes queries and assigns relevant tags
    for categorization and performance attribution.
    """

    def __init__(self):
        """Initialize the query tagger."""
        self._setup_patterns()
        log.info("QueryTagger initialized")

    def _setup_patterns(self):
        """Setup detection patterns."""
        self.intent_patterns = {
            "how_to": [r"\bhow\s+(?:do|can|should)\s+i", r"\bsteps?\s+(?:to|for)"],
            "what_is": [r"\bwhat\s+(?:is|are|does)"],
            "troubleshoot": [r"\berror|issue|problem|broken|fail"],
            "compare": [r"\bcompare|versus|vs|difference"],
        }

        self.domain_patterns = {
            "technical": [r"\b(?:code|api|function|class|bug)"],
            "policy": [r"\b(?:policy|procedure|compliance|guideline)"],
            "operational": [r"\b(?:runbook|playbook|process|workflow)"],
        }

    def tag(self, query: str, context: dict[str, Any] | None = None) -> QueryTags:
        """Tag a query.

        Args:
            query: Query string
            context: Optional context

        Returns:
            QueryTags with assigned tags
        """
        trace_id = f"tag_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "QueryTagger.tag",
        )

        query_lower = query.lower()

        # Detect intent
        intent = self._detect_intent(query_lower)

        # Detect domain
        domain = self._detect_domain(query_lower)

        # Assess complexity
        complexity = self._assess_complexity(query)

        # Assess urgency
        urgency = self._assess_urgency(query_lower)

        # Extract topic tags
        topics = self._extract_topics(query_lower)

        tags = QueryTags(
            intent=intent,
            domain=domain,
            complexity=complexity,
            urgency=urgency,
            topic_tags=topics,
            user_segments=context.get("user_segments", []) if context else [],
        )

        log.debug(f"Tagged query: intent={intent}, domain={domain}")
        return tags

    def _detect_intent(self, query: str) -> str:
        """Detect query intent."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        return "general"

    def _detect_domain(self, query: str) -> str:
        """Detect query domain."""
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return domain
        return "general"

    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        word_count = len(query.split())

        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "medium"
        else:
            return "complex"

    def _assess_urgency(self, query: str) -> str:
        """Assess query urgency."""
        urgent_terms = ["urgent", "asap", "emergency", "critical", "blocker"]

        if any(term in query for term in urgent_terms):
            return "high"
        return "normal"

    def _extract_topics(self, query: str) -> list[str]:
        """Extract topic keywords."""
        # Simple keyword extraction
        stop_words = {"the", "a", "an", "is", "are", "was", "were"}
        words = re.findall(r"\b[a-z]{4,}\b", query)
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords
        seen = set()
        unique = []
        for kw in keywords[:10]:  # Limit to top 10
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return unique


# Global instance
_global_tagger: QueryTagger | None = None


def get_query_tagger() -> QueryTagger:
    """Get or create the global query tagger."""
    global _global_tagger
    if _global_tagger is None:
        _global_tagger = QueryTagger()
    return _global_tagger


def tag_query(query: str, context: dict[str, Any] | None = None) -> QueryTags:
    """Convenience function to tag a query."""
    return get_query_tagger().tag(query, context)
