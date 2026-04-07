"""Routing Signal Detector.

Lightweight model for intent/domain assessment generating route_signal
for policy routing.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of query intent."""
    INFORMATIONAL = "informational"
    ACTION = "action"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    TROUBLESHOOTING = "troubleshooting"
    UNKNOWN = "unknown"


class DomainType(Enum):
    """Types of knowledge domain."""
    POLICY = "policy"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    GENERAL = "general"
    CODE = "code"
    INCIDENT = "incident"


@dataclass
class RoutingSignal:
    """Routing signal for policy routing decisions.

    The RoutingSignal provides lightweight intent and domain assessment
    to guide pre-retrieval gating and cache decisions.
    """
    intent: IntentType
    domain: DomainType
    confidence: float
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    urgency_score: float = 0.0
    complexity_score: float = 0.5
    requires_freshness: bool = False
    requires_authoritative: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class RoutingSignalDetector:
    """Detects routing signals from normalized queries.

    The RoutingSignalDetector provides lightweight analysis to generate
    routing signals for policy-based routing decisions.
    """

    def __init__(self):
        """Initialize the routing signal detector."""
        self._setup_patterns()
        log.info("RoutingSignalDetector initialized")

    def _setup_patterns(self):
        """Setup detection patterns."""
        # Intent patterns
        self.intent_patterns = {
            IntentType.ACTION: [
                r'\b(how\s+(do|can|should)\s+i|steps?\s+(to|for)|guide|tutorial|instructions?)\b',
                r'\b(create|make|build|setup|configure|install|deploy)\b',
            ],
            IntentType.ANALYTICAL: [
                r'\b(analyz(?:e|ing)|evaluat(?:e|ing)|assess(?:ing)?|compare|contrast)\b',
                r'\b(why|what\s+(is|are|causes?)|reason|explain)\b',
            ],
            IntentType.COMPARATIVE: [
                r'\b(compare|versus|vs|difference\s+between|better|best|alternatives?)\b',
                r'\b(pros?\s+and\s+cons?|advantages?|disadvantages?)\b',
            ],
            IntentType.TROUBLESHOOTING: [
                r'\b(error|issue|problem|bug|fail(?:ed|ure)?|broken|not\s+working)\b',
                r'\b(troubleshoot|debug|fix|resolve|solve)\b',
                r'\b(exception|crash|hang|freeze|timeout)\b',
            ],
            IntentType.PROCEDURAL: [
                r'\b(process|workflow|procedure|protocol|steps?)\b',
                r'\b(approv(?:al|e)|review|audit|compliance)\b',
            ],
        }

        # Domain patterns
        self.domain_patterns = {
            DomainType.POLICY: [
                r'\b(policy|procedure|guideline|standard|compliance|regulation|legal)\b',
                r'\b(approv(?:al|e)|authoriz(?:e|ation)|permission)\b',
            ],
            DomainType.CODE: [
                r'\b(code|function|class|method|api|library|module|package)\b',
                r'\b(python|javascript|java|cpp|go|rust|typescript|sql)\b',
                r'\b(git|commit|branch|merge|repository)\b',
            ],
            DomainType.INCIDENT: [
                r'\b(incident|outage|disruption|severity|impact|oncall)\b',
                r'\b(alert|page|escalat(?:e|ion)|war\s+room|postmortem)\b',
            ],
            DomainType.TECHNICAL: [
                r'\b(architecture|infrastructure|system|component|service)\b',
                r'\b(database|cache|queue|api|endpoint|microservice)\b',
                r'\b(performance|latency|throughput|capacity|scaling)\b',
            ],
            DomainType.OPERATIONAL: [
                r'\b(runbook|playbook|operation|maintenance|deployment)\b',
                r'\b(monitor(?:ing)?|metric|log|trace|observability)\b',
            ],
            DomainType.STRATEGIC: [
                r'\b(strategy|roadmap|planning|vision|goal|objective)\b',
                r'\b(priorit(?:y|ize)|quarter|yearly|annual|okr|kpi)\b',
            ],
        }

        # Urgency indicators
        self.urgency_patterns = [
            r'\b(urgent|asap|immediately|critical|emergency|p0|p1)\b',
            r'\b(blocking|broken|down|outage|sev[0-9])\b',
            r'\b(deadline|due\s+(today|tomorrow|soon))\b',
        ]

        # Authority indicators
        self.authority_patterns = [
            r'\b(official|authoritative|canonical|source\s+of\s+truth)\b',
            r'\b(documentation|manual|handbook|standard)\b',
        ]

    def detect(self, query: str) -> RoutingSignal:
        """Detect routing signal from query.

        Args:
            query: Normalized query string

        Returns:
            RoutingSignal with intent and domain assessment
        """
        trace_id = f"signal_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "RoutingSignalDetector.detect",
        )

        query_lower = query.lower()

        # Detect intent
        intent_scores = self._score_intents(query_lower)
        best_intent = max(intent_scores, key=intent_scores.get)
        intent_confidence = intent_scores[best_intent]

        # Detect domain
        domain_scores = self._score_domains(query_lower)
        best_domain = max(domain_scores, key=domain_scores.get)
        domain_confidence = domain_scores[best_domain]

        # Extract keywords
        keywords = self._extract_keywords(query_lower)

        # Detect entities (simple noun phrase extraction)
        entities = self._extract_entities(query)

        # Calculate urgency
        urgency = self._calculate_urgency(query_lower)

        # Calculate complexity
        complexity = self._calculate_complexity(query)

        # Check freshness requirement
        requires_freshness = urgency > 0.5 or best_domain == DomainType.INCIDENT

        # Check authoritative source requirement
        requires_authoritative = best_domain == DomainType.POLICY or urgency > 0.7

        signal = RoutingSignal(
            intent=best_intent,
            domain=best_domain,
            confidence=(intent_confidence + domain_confidence) / 2,
            keywords=keywords[:10],  # Top 10 keywords
            entities=entities[:5],   # Top 5 entities
            urgency_score=urgency,
            complexity_score=complexity,
            requires_freshness=requires_freshness,
            requires_authoritative=requires_authoritative,
            metadata={
                "intent_scores": intent_scores,
                "domain_scores": domain_scores,
                "query_length": len(query),
            },
        )

        _emit_records_telemetry_event(
            "routing_signal",
            f"{best_intent.value}_{best_domain.value}",
        )

        log.debug(f"Detected signal: intent={best_intent.value}, domain={best_domain.value}")
        return signal

    def detect_batch(self, queries: list[str]) -> list[RoutingSignal]:
        """Detect signals for multiple queries.

        Args:
            queries: List of normalized query strings

        Returns:
            List of RoutingSignal objects
        """
        return [self.detect(q) for q in queries]

    def _score_intents(self, query: str) -> dict[IntentType, float]:
        """Score query against intent patterns."""
        scores = dict.fromkeys(IntentType, 0.0)

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                scores[intent] += matches * 0.3

        # Default to informational if no strong match
        if all(s < 0.1 for s in scores.values()):
            scores[IntentType.INFORMATIONAL] = 0.5

        return scores

    def _score_domains(self, query: str) -> dict[DomainType, float]:
        """Score query against domain patterns."""
        scores = dict.fromkeys(DomainType, 0.0)

        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                scores[domain] += matches * 0.3

        # Default to general if no strong match
        if all(s < 0.1 for s in scores.values()):
            scores[DomainType.GENERAL] = 0.5

        return scores

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract significant keywords."""
        # Simple keyword extraction (could be enhanced with NLP)
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'and', 'but', 'or', 'yet', 'so',
        }

        words = re.findall(r'\b[a-z]{3,}\b', query.lower())
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return unique

    def _extract_entities(self, query: str) -> list[str]:
        """Extract potential entities (capitalized phrases)."""
        # Match capitalized phrases (potential proper nouns)
        pattern = r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b'
        matches = re.findall(pattern, query)

        # Filter out common words
        common = {'The', 'A', 'An', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been'}
        entities = [m for m in matches if m not in common and len(m) > 2]

        return list(set(entities))  # Deduplicate

    def _calculate_urgency(self, query: str) -> float:
        """Calculate urgency score."""
        score = 0.0

        for pattern in self.urgency_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            score += len(matches) * 0.3

        return min(score, 1.0)

    def _calculate_complexity(self, query: str) -> float:
        """Calculate complexity score."""
        # Based on query length, word complexity, and structure
        words = query.split()

        if not words:
            return 0.0

        # Length factor
        length_score = min(len(words) / 20, 0.5)

        # Word complexity (average word length)
        avg_len = sum(len(w) for w in words) / len(words)
        complexity_score = min(avg_len / 8, 0.5)

        return length_score + complexity_score


# Global instance
_global_detector: RoutingSignalDetector | None = None


def get_routing_signal_detector() -> RoutingSignalDetector:
    """Get or create the global routing signal detector."""
    global _global_detector
    if _global_detector is None:
        _global_detector = RoutingSignalDetector()
    return _global_detector


def detect_routing_signal(query: str) -> RoutingSignal:
    """Convenience function to detect routing signal."""
    return get_routing_signal_detector().detect(query)
