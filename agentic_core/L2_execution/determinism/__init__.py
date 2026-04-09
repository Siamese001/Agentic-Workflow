"""C1 Deterministic Replay Execution Integrity.

Implements 10C GAP-10C-004:
- C1.1: Replay Envelope Build - replay_key, policy_hash, capability_token, run_id
- C1.2: Replay Mode Propagation - Freeze signal across L0->L3->L5->L2
- C1.3: Determinism Surface - Run Clock Only, Seeded Only, Stable IDs Only
- C1.4: Replay Guard - Wrap tool/model invocations
- C1.5: Seal Determinism Digest - Stable proof for audit
"""

from .replay_envelope import ReplayEnvelope, EnvelopeBuilder
from .freeze_propagator import FreezePropagator, FreezeSignal
from .determinism_surface import DeterminismSurface, ClockMode, RandomMode
from .replay_guard import ReplayGuard, InvocationWrapper
from .determinism_digest import DeterminismDigest, DigestSealer

__all__ = [
    "ReplayEnvelope",
    "EnvelopeBuilder",
    "FreezePropagator",
    "FreezeSignal",
    "DeterminismSurface",
    "ClockMode",
    "RandomMode",
    "ReplayGuard",
    "InvocationWrapper",
    "DeterminismDigest",
    "DigestSealer",
]
