"""
Interfaces module for agentic_core.

Provides Protocol definitions to decouple base agents from concrete L5 implementations,
preventing circular dependencies while maintaining type safety.

RE-EXPORT: All protocol files are in agentic_core.utils - this module re-exports for API stability.
"""

# Sovereign Protocols (Zero-Ambiguity Standard)
from agentic_core.interfaces.IHealerProtocol import IHealerProtocol
from agentic_core.interfaces.IMemoryStoreProtocol import IMemoryStoreProtocol
from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol
from agentic_core.utils.detection_protocol_util import (
    DetectionRequest,
    DetectionResult,
    DetectionSignalProtocol,
    Severity,
)
from agentic_core.utils.meta_learning_types_util import (
    LearningContext,
    LearningResult,
    MetaLearningProtocol,
)
from agentic_core.utils.review_protocol_util import (
    HumanReviewProtocol,
    ReviewRequest,
    ReviewResult,
    ReviewStatus,
)
from agentic_core.utils.verification_types_util import (
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
    # Sovereign Protocols (Zero-Ambiguity Standard)
    "IHealerProtocol",
    "IOrchestratorProtocol",
    "IMemoryStoreProtocol",
]
