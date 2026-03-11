"""
W4-F Retrieval Profile Invariant Checker

Validates RetrievalProfile invariants before activation.
"""

from dataclasses import dataclass

from system_learning.engines.retrieval_profile import RetrievalProfile


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True, slots=True)
class InvariantViolation:
    """Represents an invariant violation."""

    field: str
    expected: str
    actual: str
    message: str


class RetrievalProfileInvariantChecker:
    """Validates RetrievalProfile invariants."""

    def __init__(self, min_top_k: int = 1, max_top_k: int = 200):
        """Initialize checker with bounds.

        Args:
            min_top_k: Minimum allowed top_k value
            max_top_k: Maximum allowed top_k value
        """
        self.min_top_k = min_top_k
        self.max_top_k = max_top_k

    def validate(
        self, *, profile: RetrievalProfile, reference_profile: RetrievalProfile | None = None
    ) -> None:
        """Validate profile invariants.

        Args:
            profile: Profile to validate
            reference_profile: Optional reference profile for embedding_dim comparison

        Raises:
            ValueError: If any invariant is violated
        """
        violations = []

        # Check similarity_cutoff bounds
        if not (0.0 < profile.similarity_cutoff <= 1.0):
            violations.append(
                InvariantViolation(
                    field="similarity_cutoff",
                    expected="0.0 < similarity_cutoff <= 1.0",
                    actual=str(profile.similarity_cutoff),
                    message="Similarity cutoff must be between 0 and 1 (exclusive of 0)",
                )
            )

        # Check top_k bounds
        if not (self.min_top_k <= profile.top_k <= self.max_top_k):
            violations.append(
                InvariantViolation(
                    field="top_k",
                    expected=f"{self.min_top_k} <= top_k <= {self.max_top_k}",
                    actual=str(profile.top_k),
                    message=f"Top_k must be between {self.min_top_k} and {self.max_top_k}",
                )
            )

        # Check influence_cap bounds
        if not (0.0 <= profile.influence_cap <= 1.0):
            violations.append(
                InvariantViolation(
                    field="influence_cap",
                    expected="0.0 <= influence_cap <= 1.0",
                    actual=str(profile.influence_cap),
                    message="Influence cap must be between 0 and 1 (inclusive)",
                )
            )

        # Check embedding_dim matches reference if provided
        if reference_profile is not None:
            if profile.embedding_dim != reference_profile.embedding_dim:
                violations.append(
                    InvariantViolation(
                        field="embedding_dim",
                        expected=str(reference_profile.embedding_dim),
                        actual=str(profile.embedding_dim),
                        message="Embedding dimension must match reference profile",
                    )
                )

        # Check primary_embedder_id is not empty
        if not profile.primary_embedder_id or not profile.primary_embedder_id.strip():
            violations.append(
                InvariantViolation(
                    field="primary_embedder_id",
                    expected="non-empty string",
                    actual=str(profile.primary_embedder_id),
                    message="Primary embedder ID must be a non-empty string",
                )
            )

        # If any violations found, raise with detailed message
        if violations:
            error_messages = []
            for violation in violations:
                error_messages.append(
                    f"{violation.field}: {violation.message} "
                    f"(expected: {violation.expected}, actual: {violation.actual})"
                )
            raise ValueError(f"Invariant violations found: {'; '.join(error_messages)}")


# Export public interface
__all__ = [
    "RetrievalProfileInvariantChecker",
    "InvariantViolation",
]
