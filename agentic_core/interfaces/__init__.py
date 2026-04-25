"""
Interfaces module for agentic_core.

Provides Protocol definitions to decouple base agents from concrete L5 implementations,
preventing circular dependencies while maintaining type safety.

Two flavors of Protocol live here:
  - Sovereign Protocols defined locally (`healer_protocol`,
    `memory_store_protocol`, `orchestrator_protocol`,
    `blackboard_lease_protocol`).
  - Re-exports of Protocols whose canonical home is `agentic_core.utils.*_util`
    (verification, detection, review, meta-learning).

The lowercase module filenames replace the legacy `I*Protocol.py` PascalCase
filenames; the public class names (`IHealerProtocol`, etc.) are unchanged.
"""

# Sovereign Protocols (Zero-Ambiguity Standard) — locally defined
from agentic_core.interfaces.healer_protocol import IHealerProtocol
from agentic_core.interfaces.memory_store_protocol import IMemoryStoreProtocol
from agentic_core.interfaces.orchestrator_protocol import IOrchestratorProtocol
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
