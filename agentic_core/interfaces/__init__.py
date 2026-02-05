"""
Interfaces module for agentic_core.

Provides Protocol definitions to decouple base agents from concrete L5 implementations,
preventing circular dependencies while maintaining type safety.
"""

from .detection_protocol import (
    DetectionRequest,
    DetectionResult,
    DetectionSignalProtocol,
    Severity,
)
from .meta_learning_protocol import (
    LearningContext,
    LearningResult,
    MetaLearningProtocol,
)
from .review_protocol import (
    HumanReviewProtocol,
    ReviewRequest,
    ReviewResult,
    ReviewStatus,
)
from .verification_protocol import (
    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)

__all__ = [
    # Verification
    "VerificationGateProtocol",
    "VerificationRequest",
    "VerificationResult",
    # Detection
    "DetectionSignalProtocol",
    "DetectionRequest",
    "DetectionResult",
    "Severity",
    # Review
    "HumanReviewProtocol",
    "ReviewRequest",
    "ReviewResult",
    "ReviewStatus",
    # Meta Learning
    "MetaLearningProtocol",
    "LearningContext",
    "LearningResult",
]
