"""
L0 Feature Extractor

Extracts features for L0 routing recommendation model including
token count, tool complexity, latency budget, user confidence,
path success history, system load, semantic similarity, and policy metadata.
"""

import hashlib
from typing import Any

from ..config.feature_schemas import FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class L0FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L0 routing decisions.

    Extracts deterministic features for route recommendation:
    - Request characteristics (tokens, complexity, latency)
    - User context (confidence, preferences)
    - System state (load, availability)
    - Historical performance (success rates, patterns)
    - Policy and governance metadata
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l0_route_recommender")
        if not schema:
            raise ValueError("L0 route recommender schema not found")
        super().__init__(schema)

    def _register_extraction_functions(self) -> None:
        """Register L0-specific feature extraction functions."""
        self.register_extraction_function("token_count", self._extract_token_count)
        self.register_extraction_function("tool_complexity_score", self._extract_tool_complexity_score)
        self.register_extraction_function("latency_budget_ms", self._extract_latency_budget_ms)
        self.register_extraction_function("user_confidence_score", self._extract_user_confidence_score)
        self.register_extraction_function("path_success_history", self._extract_path_success_history)
        self.register_extraction_function("current_load_ratio", self._extract_current_load_ratio)
        self.register_extraction_function("semantic_similarity_score", self._extract_semantic_similarity_score)
        self.register_extraction_function("policy_hash_version", self._extract_policy_hash_version)
        self.register_extraction_function("trace_id_hash", self._extract_trace_id_hash)

    def _extract_token_count(self, context: dict[str, Any]) -> int:
        """Extract token count from request."""
        request = context.get("request", {})

        # Try different token count sources
        if "token_count" in request:
            return int(request["token_count"])
        elif "input" in request and "token_count" in request["input"]:
            return int(request["input"]["token_count"])
        elif "message" in request:
            # Simple token estimation (rough approximation)
            message = str(request["message"])
            # Approximate: 1 token ≈ 4 characters for English
            return max(1, len(message) // 4)
        else:
            # Fallback: estimate from context size
            context_str = str(context)
            return max(1, len(context_str) // 4)

    def _extract_tool_complexity_score(self, context: dict[str, Any]) -> float:
        """Extract tool complexity score (0.0-1.0)."""
        request = context.get("request", {})
        tools = request.get("tools", [])

        if not tools:
            return 0.0

        # Base complexity per tool type
        complexity_map = {
            "simple": 0.1,
            "moderate": 0.3,
            "complex": 0.6,
            "expert": 0.9,
            "external": 0.7,
            "database": 0.5,
            "api": 0.4,
        }

        total_complexity = 0.0
        for tool in tools:
            tool_type = tool.get("type", "simple").lower()
            tool_complexity = complexity_map.get(tool_type, 0.3)

            # Adjust for tool count and dependencies
            dependencies = len(tool.get("dependencies", []))
            dependency_factor = 1.0 + (dependencies * 0.1)

            total_complexity += tool_complexity * dependency_factor

        # Normalize to 0-1 range
        max_complexity = len(tools) * 1.0  # Maximum possible complexity
        normalized_complexity = min(1.0, total_complexity / max_complexity) if max_complexity > 0 else 0.0

        return round(normalized_complexity, 3)

    def _extract_latency_budget_ms(self, context: dict[str, Any]) -> int:
        """Extract latency budget in milliseconds."""
        request = context.get("request", {})
        constraints = request.get("constraints", {})

        # Direct latency budget
        if "latency_budget_ms" in constraints:
            return int(constraints["latency_budget_ms"])
        elif "latency_budget" in constraints:
            # Convert seconds to milliseconds
            return int(constraints["latency_budget"] * 1000)

        # Infer from user preferences
        user_prefs = context.get("user_preferences", {})
        if "response_time_preference" in user_prefs:
            pref = user_prefs["response_time_preference"].lower()
            if pref == "fast":
                return 1000  # 1 second
            elif pref == "normal":
                return 5000  # 5 seconds
            elif pref == "slow":
                return 30000  # 30 seconds

        # Default budget based on request type
        request_type = request.get("type", "general")
        default_budgets = {
            "simple_query": 2000,
            "complex_analysis": 10000,
            "batch_processing": 60000,
            "real_time": 500,
            "general": 5000,
        }

        return default_budgets.get(request_type, 5000)

    def _extract_user_confidence_score(self, context: dict[str, Any]) -> float:
        """Extract user confidence score (0.0-1.0)."""
        request = context.get("request", {})
        user = context.get("user", {})

        # Direct confidence score
        if "confidence_score" in request:
            return float(request["confidence_score"])
        elif "confidence" in user:
            return float(user["confidence"])

        # Infer from user behavior
        confidence_indicators = {
            "explicit_instructions": 0.2,
            "examples_provided": 0.1,
            "constraints_specified": 0.15,
            "domain_specific_terms": 0.1,
            "follow_up_questions": 0.05,
        }

        score = 0.5  # Base confidence

        message = str(request.get("message", ""))

        # Check for confidence indicators
        if len(message) > 100:  # Detailed request
            score += confidence_indicators["explicit_instructions"]

        if "for example" in message.lower() or "e.g." in message.lower():
            score += confidence_indicators["examples_provided"]

        if "constraints" in request or "requirements" in request:
            score += confidence_indicators["constraints_specified"]

        # Check user history
        user_history = context.get("user_history", {})
        if "success_rate" in user_history:
            score += (user_history["success_rate"] - 0.5) * 0.2

        return round(min(1.0, max(0.0, score)), 3)

    def _extract_path_success_history(self, context: dict[str, Any]) -> float:
        """Extract historical path success rate (0.0-1.0)."""
        history = context.get("history", {})
        path_stats = history.get("path_statistics", {})

        # Get success rates for different paths
        path_success_rates = {}
        for path_name, stats in path_stats.items():
            if isinstance(stats, dict) and "success_count" in stats and "total_count" in stats:
                success_rate = stats["success_count"] / max(1, stats["total_count"])
                path_success_rates[path_name] = success_rate

        if not path_success_rates:
            return 0.5  # Default if no history

        # Return weighted average success rate
        total_weight = 0
        weighted_sum = 0

        for path, rate in path_success_rates.items():
            # Weight by recent activity
            recent_activity = path_stats.get(path, {}).get("recent_count", 1)
            weight = recent_activity
            weighted_sum += rate * weight
            total_weight += weight

        return round(weighted_sum / total_weight if total_weight > 0 else 0.5, 3)

    def _extract_current_load_ratio(self, context: dict[str, Any]) -> float:
        """Extract current system load ratio (0.0-1.0)."""
        system = context.get("system", {})
        load_metrics = system.get("load_metrics", {})

        # Direct load ratio
        if "current_ratio" in load_metrics:
            return float(load_metrics["current_ratio"])

        # Calculate from individual load metrics
        cpu_load = load_metrics.get("cpu_utilization", 0.0)
        memory_load = load_metrics.get("memory_utilization", 0.0)
        active_requests = load_metrics.get("active_requests", 0)
        max_requests = load_metrics.get("max_requests", 100)

        request_load = active_requests / max_requests if max_requests > 0 else 0.0

        # Combine different load types
        combined_load = (cpu_load * 0.4) + (memory_load * 0.3) + (request_load * 0.3)

        return round(min(1.0, max(0.0, combined_load)), 3)

    def _extract_semantic_similarity_score(self, context: dict[str, Any]) -> float:
        """Extract semantic similarity to historical requests (0.0-1.0)."""
        request = context.get("request", {})
        semantic_analysis = context.get("semantic_analysis", {})

        # Direct similarity score
        if "similarity_score" in semantic_analysis:
            return float(semantic_analysis["similarity_score"])

        # Simple similarity based on text overlap
        current_message = str(request.get("message", ""))
        historical_requests = context.get("historical_requests", [])

        if not historical_requests or not current_message:
            return 0.0

        # Calculate Jaccard similarity with most similar historical request
        max_similarity = 0.0
        current_words = set(current_message.lower().split())

        for hist_request in historical_requests[:10]:  # Check top 10
            hist_message = str(hist_request.get("message", ""))
            hist_words = set(hist_message.lower().split())

            # Jaccard similarity
            intersection = len(current_words & hist_words)
            union = len(current_words | hist_words)
            similarity = intersection / union if union > 0 else 0.0

            max_similarity = max(max_similarity, similarity)

        return round(max_similarity, 3)

    def _extract_policy_hash_version(self, context: dict[str, Any]) -> str:
        """Extract policy hash version."""
        policy = context.get("policy", {})

        # Direct version
        if "hash_version" in policy:
            return str(policy["hash_version"])
        elif "version" in policy:
            return str(policy["version"])

        # Extract from policy hash
        policy_hash = policy.get("hash", "")
        if policy_hash:
            # Simple version extraction from hash
            if "v1.0" in policy_hash:
                return "v1.0"
            elif "v1.1" in policy_hash:
                return "v1.1"
            elif "v2.0" in policy_hash:
                return "v2.0"

        # Default version
        return "v1.0"

    def _extract_trace_id_hash(self, context: dict[str, Any]) -> str:
        """Extract hash of trace ID for determinism."""
        trace_id = context.get("trace_id", "")
        if not trace_id:
            # Generate from context
            context_str = str(context)
            trace_id = hashlib.md5(context_str.encode()).hexdigest()

        # Return first 32 characters of SHA-256
        return hashlib.sha256(trace_id.encode()).hexdigest()[:32]
