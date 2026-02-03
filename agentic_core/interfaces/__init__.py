"""
Interfaces module for agentic_core.

Provides Protocol definitions to decouple base agents from concrete L5 implementations,
preventing circular dependencies while maintaining type safety.
"""

from .verification_protocol import (
    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)
from .detection_protocol import (
    DetectionSignalProtocol,
    DetectionRequest,
    DetectionResult,
    Severity,
)
from .review_protocol import (
    HumanReviewProtocol,
    ReviewRequest,
    ReviewResult,
    ReviewStatus,
)
from .meta_learning_protocol import (
    MetaLearningProtocol,
    LearningContext,
    LearningResult,
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
