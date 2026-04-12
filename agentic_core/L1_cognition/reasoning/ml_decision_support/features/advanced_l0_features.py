"""
Advanced L0 Feature Extractor

Extracts enhanced features for L0 advanced routing model including
semantic understanding, context awareness, user behavior patterns,
and routing optimization signals.
"""

import math
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class AdvancedL0FeatureExtractor(DeterministicFeatureExtractor):
    """
    Advanced feature extractor for L0 neural network routing.

    Extracts enhanced deterministic features for advanced routing:
    - Semantic query understanding and intent classification
    - Context-aware routing signals and environmental factors
    - User behavior patterns and preference learning
    - Historical routing performance and success metrics
    - Resource availability and system state indicators
    - Routing optimization signals and efficiency metrics
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("advanced_l0_router")
        if not schema:
            # Create schema for advanced L0 router
            schema = self._create_advanced_l0_schema()
        super().__init__(schema)

    def _create_advanced_l0_schema(self) -> FeatureSchema:
        """Create feature schema for advanced L0 router."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="semantic_similarity_score",
                feature_type=FeatureType.NUMERIC,
                description="Semantic similarity between query and routing options",
                provenance="routing.semantic.similarity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="intent_confidence",
                feature_type=FeatureType.NUMERIC,
                description="Confidence in query intent classification",
                provenance="routing.intent.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="context_relevance",
                feature_type=FeatureType.NUMERIC,
                description="Relevance of current context to routing decision",
                provenance="routing.context.relevance",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="user_preference_score",
                feature_type=FeatureType.NUMERIC,
                description="User preference score for routing option",
                provenance="routing.user.preference",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="historical_success_rate",
                feature_type=FeatureType.NUMERIC,
                description="Historical success rate for similar routing decisions",
                provenance="routing.historical.success_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="resource_availability",
                feature_type=FeatureType.NUMERIC,
                description="Current resource availability for routing",
                provenance="routing.resource.availability",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="routing_efficiency",
                feature_type=FeatureType.NUMERIC,
                description="Efficiency score of routing option",
                provenance="routing.efficiency.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="system_load_factor",
                feature_type=FeatureType.NUMERIC,
                description="Current system load affecting routing",
                provenance="routing.system.load_factor",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="query_complexity",
                feature_type=FeatureType.NUMERIC,
                description="Complexity of the query being routed",
                provenance="routing.query.complexity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="routing_confidence",
                feature_type=FeatureType.NUMERIC,
                description="Overall confidence in routing decision",
                provenance="routing.overall.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
        ]

        return FeatureSchema(
            schema_name="advanced_l0_router",
            schema_version="1.0",
            description="Enhanced features for L0 neural network routing model",
            features=features,
        )

    def _register_extraction_functions(self) -> None:
        """Register advanced L0-specific feature extraction functions."""
        self.register_extraction_function(
            "semantic_similarity_score", self._extract_semantic_similarity_score
        )
        self.register_extraction_function("intent_confidence", self._extract_intent_confidence)
        self.register_extraction_function("context_relevance", self._extract_context_relevance)
        self.register_extraction_function("user_preference_score", self._extract_user_preference_score)
        self.register_extraction_function("historical_success_rate", self._extract_historical_success_rate)
        self.register_extraction_function("resource_availability", self._extract_resource_availability)
        self.register_extraction_function("routing_efficiency", self._extract_routing_efficiency)
        self.register_extraction_function("system_load_factor", self._extract_system_load_factor)
        self.register_extraction_function("query_complexity", self._extract_query_complexity)
        self.register_extraction_function("routing_confidence", self._extract_routing_confidence)

    def _extract_semantic_similarity_score(self, context: dict[str, Any]) -> float:
        """Extract semantic similarity score (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct semantic similarity if provided
        if "semantic_similarity" in routing:
            return float(routing["semantic_similarity"])

        # Calculate from query embedding similarities
        query_embedding = routing.get("query_embedding", [])
        option_embeddings = routing.get("option_embeddings", [])

        if not query_embedding or not option_embeddings:
            return 0.5  # Default if no embeddings

        # Calculate cosine similarity with best matching option
        max_similarity = 0.0

        for option_embedding in option_embeddings:
            if len(option_embedding) == len(query_embedding):
                # Cosine similarity
                dot_product = sum(q * o for q, o in zip(query_embedding, option_embedding))
                query_norm = math.sqrt(sum(q * q for q in query_embedding))
                option_norm = math.sqrt(sum(o * o for o in option_embedding))

                if query_norm > 0 and option_norm > 0:
                    similarity = dot_product / (query_norm * option_norm)
                    max_similarity = max(max_similarity, similarity)

        return round(max(0.0, min(1.0, max_similarity)), 3)

    def _extract_intent_confidence(self, context: dict[str, Any]) -> float:
        """Extract intent confidence (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct intent confidence if provided
        if "intent_confidence" in routing:
            return float(routing["intent_confidence"])

        # Calculate from intent classification probabilities
        intent_probabilities = routing.get("intent_probabilities", {})

        if not intent_probabilities:
            return 0.5  # Default if no probabilities

        # Use max probability as confidence
        max_probability = max(intent_probabilities.values())

        # Adjust for entropy (more confident if distribution is peaked)
        if len(intent_probabilities) > 1:
            entropy = -sum(p * math.log(p + 1e-10) for p in intent_probabilities.values())
            max_entropy = math.log(len(intent_probabilities))

            if max_entropy > 0:
                entropy_normalized = entropy / max_entropy
                confidence_adjustment = 1.0 - entropy_normalized
            else:
                confidence_adjustment = 1.0
        else:
            confidence_adjustment = 1.0

        confidence = max_probability * confidence_adjustment
        return round(max(0.0, min(1.0, confidence)), 3)

    def _extract_context_relevance(self, context: dict[str, Any]) -> float:
        """Extract context relevance (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct context relevance if provided
        if "context_relevance" in routing:
            return float(routing["context_relevance"])

        # Calculate from context features
        context_features = routing.get("context_features", {})

        if not context_features:
            return 0.5  # Default if no context

        relevance_factors = {
            "session_continuity": 0.3,
            "recent_interactions": 0.25,
            "user_state": 0.2,
            "environmental_factors": 0.15,
            "temporal_relevance": 0.1,
        }

        relevance_score = 0.0

        # Session continuity
        session_continuity = context_features.get("session_continuity", 0.5)
        relevance_score += relevance_factors["session_continuity"] * session_continuity

        # Recent interactions
        recent_interactions = context_features.get("recent_interactions", 0.5)
        relevance_score += relevance_factors["recent_interactions"] * recent_interactions

        # User state
        user_state = context_features.get("user_state", 0.5)
        relevance_score += relevance_factors["user_state"] * user_state

        # Environmental factors
        environmental_factors = context_features.get("environmental_factors", 0.5)
        relevance_score += relevance_factors["environmental_factors"] * environmental_factors

        # Temporal relevance
        temporal_relevance = context_features.get("temporal_relevance", 0.5)
        relevance_score += relevance_factors["temporal_relevance"] * temporal_relevance

        return round(max(0.0, min(1.0, relevance_score)), 3)

    def _extract_user_preference_score(self, context: dict[str, Any]) -> float:
        """Extract user preference score (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct user preference if provided
        if "user_preference" in routing:
            return float(routing["user_preference"])

        # Calculate from user history and preferences
        user_history = routing.get("user_history", {})
        user_preferences = routing.get("user_preferences", {})

        if not user_history and not user_preferences:
            return 0.5  # Default if no user data

        preference_score = 0.0

        # Historical preference patterns
        if user_history:
            successful_routes = user_history.get("successful_routes", {})
            total_routes = user_history.get("total_routes", 1)

            if total_routes > 0:
                success_rate = successful_routes.get("current_option", 0) / total_routes
                preference_score += 0.6 * success_rate

        # Explicit user preferences
        if user_preferences:
            option_preference = user_preferences.get("current_option", 0.5)
            preference_score += 0.4 * option_preference

        return round(max(0.0, min(1.0, preference_score)), 3)

    def _extract_historical_success_rate(self, context: dict[str, Any]) -> float:
        """Extract historical success rate (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct success rate if provided
        if "historical_success_rate" in routing:
            return float(routing["historical_success_rate"])

        # Calculate from historical performance data
        historical_data = routing.get("historical_data", {})

        if not historical_data:
            return 0.5  # Default if no historical data

        total_attempts = historical_data.get("total_attempts", 1)
        successful_attempts = historical_data.get("successful_attempts", 0)

        if total_attempts > 0:
            success_rate = successful_attempts / total_attempts
        else:
            success_rate = 0.0

        return round(max(0.0, min(1.0, success_rate)), 3)

    def _extract_resource_availability(self, context: dict[str, Any]) -> float:
        """Extract resource availability (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct resource availability if provided
        if "resource_availability" in routing:
            return float(routing["resource_availability"])

        # Calculate from system resource metrics
        system_resources = routing.get("system_resources", {})

        if not system_resources:
            return 0.5  # Default if no resource data

        # CPU availability
        cpu_usage = system_resources.get("cpu_usage", 50)
        cpu_availability = max(0.0, (100 - cpu_usage) / 100)

        # Memory availability
        memory_usage = system_resources.get("memory_usage", 50)
        memory_availability = max(0.0, (100 - memory_usage) / 100)

        # Network availability
        network_usage = system_resources.get("network_usage", 50)
        network_availability = max(0.0, (100 - network_usage) / 100)

        # Weighted average
        resource_availability = (
            (cpu_availability * 0.4) + (memory_availability * 0.4) + (network_availability * 0.2)
        )

        return round(resource_availability, 3)

    def _extract_routing_efficiency(self, context: dict[str, Any]) -> float:
        """Extract routing efficiency (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct routing efficiency if provided
        if "routing_efficiency" in routing:
            return float(routing["routing_efficiency"])

        # Calculate from routing performance metrics
        performance_metrics = routing.get("performance_metrics", {})

        if not performance_metrics:
            return 0.5  # Default if no performance data

        efficiency_factors = {
            "response_time": 0.3,
            "throughput": 0.25,
            "error_rate": 0.2,
            "resource_utilization": 0.15,
            "latency": 0.1,
        }

        efficiency_score = 0.0

        # Response time (lower is better)
        response_time = performance_metrics.get("response_time", 1000)
        target_response_time = performance_metrics.get("target_response_time", 500)
        response_efficiency = min(1.0, target_response_time / max(1, response_time))
        efficiency_score += efficiency_factors["response_time"] * response_efficiency

        # Throughput (higher is better)
        throughput = performance_metrics.get("throughput", 100)
        target_throughput = performance_metrics.get("target_throughput", 200)
        throughput_efficiency = min(1.0, throughput / max(1, target_throughput))
        efficiency_score += efficiency_factors["throughput"] * throughput_efficiency

        # Error rate (lower is better)
        error_rate = performance_metrics.get("error_rate", 0.05)
        error_efficiency = max(0.0, 1.0 - error_rate * 10)  # Scale error rate impact
        efficiency_score += efficiency_factors["error_rate"] * error_efficiency

        # Resource utilization (optimal range)
        resource_util = performance_metrics.get("resource_utilization", 0.7)
        optimal_util = 0.8
        util_efficiency = 1.0 - abs(resource_util - optimal_util)
        efficiency_score += efficiency_factors["resource_utilization"] * util_efficiency

        # Latency (lower is better)
        latency = performance_metrics.get("latency", 100)
        target_latency = performance_metrics.get("target_latency", 50)
        latency_efficiency = min(1.0, target_latency / max(1, latency))
        efficiency_score += efficiency_factors["latency"] * latency_efficiency

        return round(max(0.0, min(1.0, efficiency_score)), 3)

    def _extract_system_load_factor(self, context: dict[str, Any]) -> float:
        """Extract system load factor (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct system load if provided
        if "system_load_factor" in routing:
            return float(routing["system_load_factor"])

        # Calculate from system load metrics
        system_metrics = routing.get("system_metrics", {})

        if not system_metrics:
            return 0.5  # Default if no system metrics

        load_indicators = {
            "cpu_load": 0.3,
            "memory_load": 0.25,
            "disk_io": 0.2,
            "network_io": 0.15,
            "active_connections": 0.1,
        }

        load_score = 0.0

        # CPU load
        cpu_load = system_metrics.get("cpu_load", 50)
        load_score += load_indicators["cpu_load"] * (cpu_load / 100)

        # Memory load
        memory_load = system_metrics.get("memory_load", 50)
        load_score += load_indicators["memory_load"] * (memory_load / 100)

        # Disk I/O
        disk_io = system_metrics.get("disk_io", 50)
        load_score += load_indicators["disk_io"] * (disk_io / 100)

        # Network I/O
        network_io = system_metrics.get("network_io", 50)
        load_score += load_indicators["network_io"] * (network_io / 100)

        # Active connections
        active_connections = system_metrics.get("active_connections", 50)
        max_connections = system_metrics.get("max_connections", 100)
        connection_load = active_connections / max(1, max_connections)
        load_score += load_indicators["active_connections"] * connection_load

        return round(max(0.0, min(1.0, load_score)), 3)

    def _extract_query_complexity(self, context: dict[str, Any]) -> float:
        """Extract query complexity (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct query complexity if provided
        if "query_complexity" in routing:
            return float(routing["query_complexity"])

        # Calculate from query characteristics
        query_info = routing.get("query_info", {})

        if not query_info:
            return 0.5  # Default if no query info

        complexity_indicators = {
            "token_count": 0.25,
            "entity_count": 0.2,
            "intent_complexity": 0.2,
            "context_requirements": 0.15,
            "nested_queries": 0.1,
            "special_operations": 0.1,
        }

        complexity_score = 0.0

        # Token count
        token_count = query_info.get("token_count", 100)
        token_complexity = min(1.0, token_count / 1000)  # Normalize to 1000 tokens
        complexity_score += complexity_indicators["token_count"] * token_complexity

        # Entity count
        entity_count = query_info.get("entity_count", 5)
        entity_complexity = min(1.0, entity_count / 20)  # Normalize to 20 entities
        complexity_score += complexity_indicators["entity_count"] * entity_complexity

        # Intent complexity
        intent_complexity = query_info.get("intent_complexity", 0.5)
        complexity_score += complexity_indicators["intent_complexity"] * intent_complexity

        # Context requirements
        context_requirements = query_info.get("context_requirements", 0.5)
        complexity_score += complexity_indicators["context_requirements"] * context_requirements

        # Nested queries
        nested_queries = query_info.get("nested_queries", 0)
        nested_complexity = min(1.0, nested_queries / 5)  # Normalize to 5 nested queries
        complexity_score += complexity_indicators["nested_queries"] * nested_complexity

        # Special operations
        special_operations = query_info.get("special_operations", 0)
        special_complexity = min(1.0, special_operations / 3)  # Normalize to 3 special ops
        complexity_score += complexity_indicators["special_operations"] * special_complexity

        return round(max(0.0, min(1.0, complexity_score)), 3)

    def _extract_routing_confidence(self, context: dict[str, Any]) -> float:
        """Extract overall routing confidence (0.0 to 1.0)."""
        routing = context.get("routing", {})

        # Direct routing confidence if provided
        if "routing_confidence" in routing:
            return float(routing["routing_confidence"])

        # Calculate from individual confidence factors
        confidence_factors = {
            "semantic_similarity": 0.25,
            "intent_confidence": 0.2,
            "context_relevance": 0.15,
            "user_preference": 0.15,
            "historical_success": 0.15,
            "resource_availability": 0.1,
        }

        # Extract individual confidences
        semantic_confidence = self._extract_semantic_similarity_score(context)
        intent_confidence = self._extract_intent_confidence(context)
        context_confidence = self._extract_context_relevance(context)
        user_confidence = self._extract_user_preference_score(context)
        historical_confidence = self._extract_historical_success_rate(context)
        resource_confidence = self._extract_resource_availability(context)

        # Weighted combination
        routing_confidence = (
            confidence_factors["semantic_similarity"] * semantic_confidence
            + confidence_factors["intent_confidence"] * intent_confidence
            + confidence_factors["context_relevance"] * context_confidence
            + confidence_factors["user_preference"] * user_confidence
            + confidence_factors["historical_success"] * historical_confidence
            + confidence_factors["resource_availability"] * resource_confidence
        )

        return round(max(0.0, min(1.0, routing_confidence)), 3)
