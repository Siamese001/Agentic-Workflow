"""
L6 Feature Extractor

Extracts features for L6 anomaly detection model including
latency z-scores, error rate spikes, token deviations, path divergences,
policy hash changes, replay mismatches, escalation frequencies,
healing success rates, and semantic drift scores.
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import Any

from ..config.feature_schemas import FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor
from tqdm import tqdm


class L6FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for L6 anomaly detection.

    Extracts deterministic features for anomaly detection:
    - Performance metrics (latency, error rates, token usage)
    - Behavioral patterns (path selection, escalations)
    - System integrity (policy changes, replay mismatches)
    - Recovery metrics (healing success, rollback rates)
    - Semantic analysis (drift detection)
    - Operational health indicators
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("l6_anomaly_detector")
        if not schema:
            raise ValueError("L6 anomaly detector schema not found")
        super().__init__(schema)

    def _register_extraction_functions(self) -> None:
        """Register L6-specific feature extraction functions."""
        self.register_extraction_function("latency_z_score", self._extract_latency_z_score)
        self.register_extraction_function("error_rate_spike", self._extract_error_rate_spike)
        self.register_extraction_function("token_deviation", self._extract_token_deviation)
        self.register_extraction_function("path_divergence", self._extract_path_divergence)
        self.register_extraction_function("policy_hash_changes", self._extract_policy_hash_changes)
        self.register_extraction_function("replay_mismatch_count", self._extract_replay_mismatch_count)
        self.register_extraction_function("escalation_frequency", self._extract_escalation_frequency)
        self.register_extraction_function("healing_success_rate", self._extract_healing_success_rate)
        self.register_extraction_function("semantic_drift_score", self._extract_semantic_drift_score)

    def _extract_latency_z_score(self, context: dict[str, Any]) -> float:
        """Extract latency z-score from baseline."""
        metrics = context.get("metrics", {})
        latency_data = metrics.get("latency", {})

        # Direct z-score if provided
        if "z_score" in latency_data:
            return float(latency_data["z_score"])

        # Calculate from current latency and baseline
        current_latency = latency_data.get("current_ms")
        baseline_mean = latency_data.get("baseline_mean_ms")
        baseline_std = latency_data.get("baseline_std_ms")

        if current_latency is None or baseline_mean is None or baseline_std is None:
            return 0.0  # Default if insufficient data

        if baseline_std == 0:
            return 0.0  # No variation

        # Calculate z-score
        z_score = (current_latency - baseline_mean) / baseline_std

        # Cap extreme values for stability
        z_score = max(-5.0, min(5.0, z_score))

        return round(z_score, 3)

    def _extract_error_rate_spike(self, context: dict[str, Any]) -> float:
        """Extract error rate spike factor."""
        metrics = context.get("metrics", {})
        error_data = metrics.get("error_rate", {})

        # Direct spike factor if provided
        if "spike_factor" in error_data:
            return float(error_data["spike_factor"])

        # Calculate from current and baseline error rates
        current_rate = error_data.get("current_rate", 0.0)
        baseline_rate = error_data.get("baseline_rate", 0.0)

        if baseline_rate == 0:
            # If baseline is zero, any error is a spike
            return float(current_rate) if current_rate > 0 else 1.0

        # Calculate spike factor
        spike_factor = current_rate / baseline_rate

        # Cap extreme values
        spike_factor = max(0.0, min(10.0, spike_factor))

        return round(spike_factor, 3)

    def _extract_token_deviation(self, context: dict[str, Any]) -> float:
        """Extract token count deviation from baseline."""
        metrics = context.get("metrics", {})
        token_data = metrics.get("tokens", {})

        # Direct deviation if provided
        if "deviation" in token_data:
            return float(token_data["deviation"])

        # Calculate from current and baseline token counts
        current_tokens = token_data.get("current_count", 0)
        baseline_tokens = token_data.get("baseline_count", 0)

        if baseline_tokens == 0:
            return 0.0  # No baseline, no deviation

        # Calculate percentage deviation
        deviation = (current_tokens - baseline_tokens) / baseline_tokens

        # Cap extreme values
        deviation = max(-2.0, min(2.0, deviation))

        return round(deviation, 3)

    def _extract_path_divergence(self, context: dict[str, Any]) -> float:
        """Extract path selection divergence from expected."""
        routing = context.get("routing", {})
        path_data = routing.get("path_analysis", {})

        # Direct divergence if provided
        if "divergence" in path_data:
            return float(path_data["divergence"])

        # Calculate from path distribution
        current_path = routing.get("current_path")
        expected_paths = path_data.get("expected_distribution", {})
        actual_paths = path_data.get("actual_distribution", {})

        if not current_path or not expected_paths:
            return 0.0

        # Expected probability for current path
        expected_prob = expected_paths.get(current_path, 0.0)

        # Actual probability for current path
        actual_prob = actual_paths.get(current_path, 0.0)

        # Calculate divergence
        if expected_prob == 0:
            # Unexpected path
            divergence = 1.0
        else:
            # Relative difference from expected
            divergence = abs(actual_prob - expected_prob) / expected_prob

        return round(min(1.0, divergence), 3)

    def _extract_policy_hash_changes(self, context: dict[str, Any]) -> float:
        """Extract number of policy hash changes."""
        policy = context.get("policy", {})

        # Direct count if provided
        if "hash_changes_count" in policy:
            return float(policy["hash_changes_count"])

        # Calculate from policy history
        policy_history = policy.get("history", [])
        current_hash = policy.get("current_hash", "")

        # Count changes in recent time window
        recent_changes = 0
        time_window = timedelta(hours=24)  # Last 24 hours

        now = datetime.now()

        for i, change in tqdm(enumerate(policy_history), desc="Processing", unit="item"):
            if i == 0:
                continue  # Skip first entry (no previous to compare)

            change_time = change.get("timestamp")
            if change_time:
                try:
                    if isinstance(change_time, str):
                        change_time = datetime.fromisoformat(change_time.replace("Z", "+00:00"))

                    if now - change_time <= time_window:
                        # Check if hash actually changed
                        prev_hash = policy_history[i - 1].get("hash", "")
                        curr_hash = change.get("hash", "")
                        if prev_hash != curr_hash:
                            recent_changes += 1
                except ValueError:
                    continue

        return float(recent_changes)

    def _extract_replay_mismatch_count(self, context: dict[str, Any]) -> float:
        """Extract replay mismatch count."""
        replay = context.get("replay", {})

        # Direct count if provided
        if "mismatch_count" in replay:
            return float(replay["mismatch_count"])

        # Calculate from replay results
        replay_results = replay.get("results", [])

        mismatch_count = 0
        for result in replay_results:
            if result.get("status") == "mismatch":
                mismatch_count += 1

        return float(mismatch_count)

    def _extract_escalation_frequency(self, context: dict[str, Any]) -> float:
        """Extract escalation frequency."""
        escalation = context.get("escalation", {})

        # Direct frequency if provided
        if "frequency" in escalation:
            return float(escalation["frequency"])

        # Calculate from escalation events
        escalation_events = escalation.get("events", [])
        time_window = timedelta(hours=1)  # Last hour

        now = datetime.now()
        recent_escalations = 0

        for event in tqdm(escalation_events, desc="Processing", unit="item"):
            event_time = event.get("timestamp")
            if event_time:
                try:
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time.replace("Z", "+00:00"))

                    if now - event_time <= time_window:
                        recent_escalations += 1
                except ValueError:
                    continue

        return float(recent_escalations)

    def _extract_healing_success_rate(self, context: dict[str, Any]) -> float:
        """Extract healing success rate."""
        healing = context.get("healing", {})

        # Direct rate if provided
        if "success_rate" in healing:
            return float(healing["success_rate"])

        # Calculate from healing attempts
        healing_attempts = healing.get("attempts", [])

        if not healing_attempts:
            return 1.0  # Default to perfect if no attempts

        successful_attempts = sum(1 for attempt in healing_attempts if attempt.get("success", False))
        success_rate = successful_attempts / len(healing_attempts)

        return round(success_rate, 3)

    def _extract_semantic_drift_score(self, context: dict[str, Any]) -> float:
        """Extract semantic drift score."""
        semantic = context.get("semantic", {})

        # Direct drift score if provided
        if "drift_score" in semantic:
            return float(semantic["drift_score"])

        # Calculate from semantic analysis
        current_embeddings = semantic.get("current_embeddings", [])
        baseline_embeddings = semantic.get("baseline_embeddings", [])

        if not current_embeddings or not baseline_embeddings:
            return 0.0

        # Calculate average cosine similarity
        similarities = []

        for current_emb in tqdm(current_embeddings, desc="Processing", unit="item"):
            best_similarity = 0.0

            for baseline_emb in baseline_embeddings:
                if len(current_emb) == len(baseline_emb):
                    # Cosine similarity
                    dot_product = sum(c * b for c, b in zip(current_emb, baseline_emb))
                    current_norm = math.sqrt(sum(c * c for c in current_emb))
                    baseline_norm = math.sqrt(sum(b * b for b in baseline_emb))

                    if current_norm > 0 and baseline_norm > 0:
                        similarity = dot_product / (current_norm * baseline_norm)
                        best_similarity = max(best_similarity, similarity)

            similarities.append(best_similarity)

        if not similarities:
            return 0.0

        # Drift is inverse of similarity
        avg_similarity = statistics.mean(similarities)
        drift_score = 1.0 - avg_similarity

        return round(max(0.0, drift_score), 3)

    def extract_batch_features(
        self,
        contexts: list[dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        semantic_clock: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extract features for multiple contexts efficiently.

        Args:
            contexts: List of contexts to extract features from
            trace_id: Base trace ID
            replay_key: Replay key
            policy_hash: Policy hash
            semantic_clock: Semantic clock

        Returns:
            List of feature dictionaries
        """
        batch_features = []

        for i, context in tqdm(enumerate(contexts), desc="Processing", unit="item"):
            # Generate unique trace ID for this context
            context_trace_id = f"{trace_id}_batch_{i}"

            # Extract features
            extraction_result = self.extract_features(
                context=context,
                trace_id=context_trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
                semantic_clock=semantic_clock,
            )

            if extraction_result.success:
                batch_features.append(extraction_result.features)
            else:
                # Add default features for failed extraction
                batch_features.append(
                    {
                        "latency_z_score": 0.0,
                        "error_rate_spike": 1.0,
                        "token_deviation": 0.0,
                        "path_divergence": 0.0,
                        "policy_hash_changes": 0.0,
                        "replay_mismatch_count": 0.0,
                        "escalation_frequency": 0.0,
                        "healing_success_rate": 1.0,
                        "semantic_drift_score": 0.0,
                    }
                )

        return batch_features

    def get_anomaly_indicators_summary(self, features: dict[str, Any]) -> dict[str, str]:
        """
        Get human-readable anomaly indicators summary.

        Args:
            features: Extracted features

        Returns:
            Dictionary mapping feature names to indicator descriptions
        """
        indicators = {}

        # Latency z-score
        latency_z = features.get("latency_z_score", 0.0)
        if abs(latency_z) > 2.0:
            indicators["latency_z_score"] = f"High latency deviation ({latency_z:.2f}σ)"
        elif abs(latency_z) > 1.0:
            indicators["latency_z_score"] = f"Moderate latency deviation ({latency_z:.2f}σ)"
        else:
            indicators["latency_z_score"] = "Normal latency"

        # Error rate spike
        error_spike = features.get("error_rate_spike", 1.0)
        if error_spike > 3.0:
            indicators["error_rate_spike"] = f"Severe error spike ({error_spike:.1f}x)"
        elif error_spike > 1.5:
            indicators["error_rate_spike"] = f"Moderate error spike ({error_spike:.1f}x)"
        else:
            indicators["error_rate_spike"] = "Normal error rate"

        # Token deviation
        token_dev = features.get("token_deviation", 0.0)
        if abs(token_dev) > 0.5:
            indicators["token_deviation"] = f"High token deviation ({token_dev:.1%})"
        elif abs(token_dev) > 0.2:
            indicators["token_deviation"] = f"Moderate token deviation ({token_dev:.1%})"
        else:
            indicators["token_deviation"] = "Normal token usage"

        # Path divergence
        path_div = features.get("path_divergence", 0.0)
        if path_div > 0.5:
            indicators["path_divergence"] = f"High path divergence ({path_div:.1%})"
        elif path_div > 0.2:
            indicators["path_divergence"] = f"Moderate path divergence ({path_div:.1%})"
        else:
            indicators["path_divergence"] = "Normal path selection"

        # Policy changes
        policy_changes = features.get("policy_hash_changes", 0.0)
        if policy_changes > 5.0:
            indicators["policy_hash_changes"] = f"High policy activity ({int(policy_changes)} changes)"
        elif policy_changes > 2.0:
            indicators["policy_hash_changes"] = f"Moderate policy activity ({int(policy_changes)} changes)"
        else:
            indicators["policy_hash_changes"] = "Normal policy activity"

        # Replay mismatches
        replay_mismatches = features.get("replay_mismatch_count", 0.0)
        if replay_mismatches > 10.0:
            indicators["replay_mismatch_count"] = f"High replay mismatches ({int(replay_mismatches)})"
        elif replay_mismatches > 5.0:
            indicators["replay_mismatch_count"] = f"Moderate replay mismatches ({int(replay_mismatches)})"
        else:
            indicators["replay_mismatch_count"] = "Normal replay consistency"

        # Escalation frequency
        escalation_freq = features.get("escalation_frequency", 0.0)
        if escalation_freq > 5.0:
            indicators["escalation_frequency"] = f"High escalation rate ({int(escalation_freq)}/hour)"
        elif escalation_freq > 2.0:
            indicators["escalation_frequency"] = f"Moderate escalation rate ({int(escalation_freq)}/hour)"
        else:
            indicators["escalation_frequency"] = "Normal escalation rate"

        # Healing success rate
        healing_success = features.get("healing_success_rate", 1.0)
        if healing_success < 0.5:
            indicators["healing_success_rate"] = f"Poor healing success ({healing_success:.1%})"
        elif healing_success < 0.8:
            indicators["healing_success_rate"] = f"Moderate healing success ({healing_success:.1%})"
        else:
            indicators["healing_success_rate"] = f"Good healing success ({healing_success:.1%})"

        # Semantic drift
        semantic_drift = features.get("semantic_drift_score", 0.0)
        if semantic_drift > 0.3:
            indicators["semantic_drift_score"] = f"High semantic drift ({semantic_drift:.1%})"
        elif semantic_drift > 0.1:
            indicators["semantic_drift_score"] = f"Moderate semantic drift ({semantic_drift:.1%})"
        else:
            indicators["semantic_drift_score"] = "Low semantic drift"

        return indicators
