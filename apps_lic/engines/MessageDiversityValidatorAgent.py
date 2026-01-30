from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

"""
MessageDiversityValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: ContentCleanlinessValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


# STUBS: Legacy mixins (use LICAgentBase instead)
class MCPHardenedMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


class HealerMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


@dataclass
class MessageDiversityValidatorAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Prevent repetitive messages using cosine similarity
    FEATURE 1.3 from SUPREME_SPELL
    """

    MIN_DIVERSITY_THRESHOLD = 0.85  # Messages must be <85% similar

    def __init__(self) -> None:
        """
        Initialize message diversity validator.

        Sets up TF-IDF vectorizer for similarity analysis and initializes
        message history tracking.
        """
        self.message_history: list[str] = []
        self.vectorizer = TfidfVectorizer()

    def check_diversity(self, new_message: str) -> tuple[bool, float, str]:
        """
        Check if new message is sufficiently different from history

        Returns:
            (is_diverse, max_similarity, most_similar_message)
        """
        if not self.message_history:
            return True, 0.0, ""

        all_messages = self.message_history + [new_message]

        try:
            vectors = self.vectorizer.fit_transform(all_messages)
            new_vector = vectors[-1]
            history_vectors = vectors[:-1]

            similarities = cosine_similarity(new_vector, history_vectors)[0]
            max_similarity = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))

            is_diverse = max_similarity < self.MIN_DIVERSITY_THRESHOLD
            most_similar = (
                self.message_history[max_idx] if max_idx < len(self.message_history) else ""
            )

            return is_diverse, max_similarity, most_similar

        except (ValueError, TypeError, KeyError):
            # If vectorization fails, assume diverse
            return True, 0.0, ""

    def add_to_history(self, message: str) -> None:
        """
        Add message to history for future diversity checks.

        Args:
            message: Message text to add to history
        """
        self.message_history.append(message)

    def heal_repository(self) -> dict:
        """
        Invoke healing chain via super().

        Returns:
            Dictionary with healing results including violations, fixed, errors, skipped
        """
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by MessageDiversityValidatorAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"MessageDiversityValidatorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"MessageDiversityValidatorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
