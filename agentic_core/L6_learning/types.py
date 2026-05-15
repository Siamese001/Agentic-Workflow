"""agentic_core.L6_learning.types — re-export alias for L6 learning types.

W1 delivery gap fix: downstream consumers (e.g. Phase 12 cross-plan tests)
import types from `agentic_core.L6_learning.types`. All types are defined in
`agentic_core.L6_learning.__init__`. This module is a pure re-export alias —
no new logic, no new types.
"""
from agentic_core.L6_learning import (  # noqa: F401
    CompletedEvalRecord,
    FutureRunPromotionRequest,
    L6GauntletResult,
    ObserverLawReceipt,
    ProofType,
    ProposalPacket,
    ProposalType,
    RCAPacket,
)
from agentic_core.L6_learning.promotion_gauntlet import (  # noqa: F401
    PromotionGauntlet,
)

__all__ = [
    "CompletedEvalRecord",
    "FutureRunPromotionRequest",
    "L6GauntletResult",
    "ObserverLawReceipt",
    "ProofType",
    "ProposalPacket",
    "ProposalType",
    "PromotionGauntlet",
    "RCAPacket",
]
