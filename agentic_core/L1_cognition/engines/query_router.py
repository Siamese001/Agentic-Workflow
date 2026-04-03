"""
Query Router for L1 Cognition
Intelligent query routing to relevant ChromaDB collections.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query types for routing decisions."""
    CODE_KNOWLEDGE = "code_knowledge"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    EXECUTION_INTELLIGENCE = "execution_intelligence"
    HISTORICAL_ANALYSIS = "historical_analysis"
    BLAST_RADIUS = "blast_radius"
    FAILURE_ANALYSIS = "failure_analysis"
    GENERAL_QUERY = "general_query"


@dataclass
class RoutingDecision:
    """Routing decision for a query."""
    query_type: QueryType
    primary_collections: List[str]
    secondary_collections: List[str]
    confidence: float
    reasoning: str


class QueryRouter:
    """
    Intelligent query router for L1 Cognition.

    Determines which ChromaDB collections are relevant for a given query
    based on keyword analysis, semantic patterns, and query intent.
    """

    def __init__(self):
        """Initialize query router with routing rules."""
        self.collection_mappings = {
            # Code knowledge collections
            QueryType.CODE_KNOWLEDGE: {
                "primary": ["repo_code_chunks", "repo_symbols", "repo_arch_docs"],
                "secondary": []
            },

            # Structural analysis collections
            QueryType.STRUCTURAL_ANALYSIS: {
                "primary": ["repo_adg_graph", "repo_symbols"],
                "secondary": ["repo_code_chunks", "repo_tests_guardrails"]
            },

            # Execution intelligence collections
            QueryType.EXECUTION_INTELLIGENCE: {
                "primary": ["repo_runtime_evidence"],
                "secondary": ["repo_adg_graph", "repo_symbols"]
            },

            # Historical analysis collections
            QueryType.HISTORICAL_ANALYSIS: {
                "primary": ["repo_git_history", "repo_incidents_rca"],
                "secondary": ["repo_runtime_evidence"]
            },

            # Blast radius analysis collections
            QueryType.BLAST_RADIUS: {
                "primary": ["repo_adg_graph", "repo_symbols"],
                "secondary": ["repo_code_chunks", "repo_tests_guardrails", "repo_runtime_evidence"]
            },

            # Failure analysis collections
            QueryType.FAILURE_ANALYSIS: {
                "primary": ["repo_incidents_rca", "repo_runtime_evidence"],
                "secondary": ["repo_adg_graph", "repo_tests_guardrails"]
            },

            # General query collections
            QueryType.GENERAL_QUERY: {
                "primary": ["repo_code_chunks", "repo_symbols", "repo_arch_docs"],
                "secondary": ["repo_adg_graph", "repo_tests_guardrails"]
            }
        }

        # Keyword patterns for query type detection
        self.query_patterns = {
            QueryType.CODE_KNOWLEDGE: [
                "what does", "how does", "explain", "describe", "what is", "implementation",
                "function", "class", "method", "module", "code", "algorithm"
            ],

            QueryType.STRUCTURAL_ANALYSIS: [
                "dependencies", "structure", "architecture", "design", "pattern", "relationship",
                "graph", "coupling", "cohesion", "hierarchy", "components", "layers"
            ],

            QueryType.EXECUTION_INTELLIGENCE: [
                "execution", "runtime", "performance", "trace", "execute", "run", "process",
                "workflow", "pipeline", "operation", "activity", "behavior"
            ],

            QueryType.HISTORICAL_ANALYSIS: [
                "history", "when", "commit", "change", "evolution", "timeline", "previously",
                "past", "version", "git", "incident", "rca", "root cause"
            ],

            QueryType.BLAST_RADIUS: [
                "impact", "affect", "blast radius", "depend", "require", "consequence",
                "ripple", "cascade", "side effect", "influence", "scope", "reach"
            ],

            QueryType.FAILURE_ANALYSIS: [
                "failure", "error", "bug", "issue", "problem", "crash", "exception",
                "incident", "fault", "break", "fail", "malfunction", "defect"
            ]
        }

        # Layer-specific keywords
        self.layer_keywords = {
            "L0": ["routing", "router", "gateway", "dispatch"],
            "L1": ["cognition", "retriever", "semantic", "reasoning"],
            "L2": ["execution", "uWG", "write", "gateway", "universal"],
            "L3": ["orchestration", "orchestrator", "coordination", "workflow"],
            "L4": ["state", "storage", "database", "memory", "persist"],
            "L5": ["safety", "guardrail", "validation", "security", "policy"],
            "L6": ["observability", "monitoring", "metrics", "logging", "trace"]
        }

        # Component-specific keywords
        self.component_keywords = {
            "UWG": ["universal write gateway", "UWG", "write operation"],
            "ADG": ["adg", "static scanner", "graph", "dependency"],
            "Scanner": ["scanner", "scan", "analyze", "inspect"],
            "Router": ["router", "routing", "dispatch", "route"],
            "ChromaDB": ["chroma", "vector", "embedding", "semantic"],
            "Agent": ["agent", "ai", "llm", "model"]
        }

    def route_query(self, query: str, available_collections: List[str]) -> RoutingDecision:
        """
        Route a query to appropriate collections.

        Args:
            query: The query string to route
            available_collections: List of available collections

        Returns:
            RoutingDecision with selected collections and reasoning
        """
        query_lower = query.lower()

        # Detect query type
        query_type = self._detect_query_type(query_lower)

        # Get base routing decision
        base_routing = self.collection_mappings[query_type]

        # Filter to available collections
        primary = [c for c in base_routing["primary"] if c in available_collections]
        secondary = [c for c in base_routing["secondary"] if c in available_collections]

        # Add layer-specific collections if detected
        layer_collections = self._detect_layer_collections(query_lower, available_collections)
        primary.extend(layer_collections)

        # Remove duplicates while preserving order
        primary = list(dict.fromkeys(primary))
        secondary = list(dict.fromkeys(secondary))

        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, query_type)

        # Generate reasoning
        reasoning = self._generate_reasoning(query_lower, query_type, primary, secondary)

        return RoutingDecision(
            query_type=query_type,
            primary_collections=primary,
            secondary_collections=secondary,
            confidence=confidence,
            reasoning=reasoning
        )

    def _detect_query_type(self, query: str) -> QueryType:
        """Detect query type based on keyword patterns."""
        scores = {}

        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query:
                    score += 1
                # Partial matches
                elif any(word in query for word in pattern.split()):
                    score += 0.5
            scores[query_type] = score

        # Return type with highest score
        if max(scores.values()) == 0:
            return QueryType.GENERAL_QUERY

        return max(scores, key=scores.get)

    def _detect_layer_collections(self, query: str, available_collections: List[str]) -> List[str]:
        """Detect layer-specific collections to include."""
        layer_collections = []

        for layer, keywords in self.layer_keywords.items():
            if any(keyword in query for keyword in keywords):
                # Look for layer-specific collections
                layer_specific = [c for c in available_collections if layer.lower() in c.lower()]
                layer_collections.extend(layer_specific)

        return layer_collections

    def _calculate_confidence(self, query: str, query_type: QueryType) -> float:
        """Calculate confidence in routing decision."""
        # Base confidence
        confidence = 0.5

        # Boost confidence based on keyword matches
        patterns = self.query_patterns.get(query_type, [])
        matches = sum(1 for pattern in patterns if pattern in query)

        if matches > 0:
            confidence = min(0.9, 0.5 + (matches * 0.1))

        # Boost confidence for specific indicators
        if any(word in query for word in ["what", "how", "why", "explain"]):
            confidence += 0.1

        # Boost confidence for technical terms
        if any(word in query for word in ["function", "class", "method", "module", "component"]):
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_reasoning(self, query: str, query_type: QueryType,
                          primary: List[str], secondary: List[str]) -> str:
        """Generate reasoning for routing decision."""
        reasoning_parts = []

        # Query type reasoning
        reasoning_parts.append(f"Detected query type: {query_type.value}")

        # Collection reasoning
        if primary:
            reasoning_parts.append(f"Primary collections: {', '.join(primary)}")
        if secondary:
            reasoning_parts.append(f"Secondary collections: {', '.join(secondary)}")

        # Keyword reasoning
        matched_keywords = []
        patterns = self.query_patterns.get(query_type, [])
        for pattern in patterns:
            if pattern in query:
                matched_keywords.append(pattern)

        if matched_keywords:
            reasoning_parts.append(f"Matched keywords: {', '.join(matched_keywords)}")

        return "; ".join(reasoning_parts)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and configuration."""
        return {
            "query_types": [qt.value for qt in QueryType],
            "collection_mappings": {
                qt.value: mapping for qt, mapping in self.collection_mappings.items()
            },
            "pattern_count": sum(len(patterns) for patterns in self.query_patterns.values()),
            "layer_count": len(self.layer_keywords),
            "component_count": len(self.component_keywords)
        }


# Example usage and testing
def main():
    """Test the query router."""
    router = QueryRouter()

    # Test queries
    test_queries = [
        "What does the UniversalWriteGateway do?",
        "Show me the blast radius for ADG scanner changes",
        "Find failures related to memory leaks in L1 cognition",
        "How does the routing between L0 and L2 work?",
        "What were the recent commits affecting safety layer?"
    ]

    available_collections = [
        "repo_code_chunks", "repo_symbols", "repo_arch_docs",
        "repo_adg_graph", "repo_tests_guardrails",
        "repo_runtime_evidence", "repo_git_history", "repo_incidents_rca"
    ]

    print("Query Router Test:")
    for query in test_queries:
        decision = router.route_query(query, available_collections)
        print(f"\nQuery: {query}")
        print(f"Type: {decision.query_type.value}")
        print(f"Primary: {decision.primary_collections}")
        print(f"Secondary: {decision.secondary_collections}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Reasoning: {decision.reasoning}")


if __name__ == "__main__":
    main()
