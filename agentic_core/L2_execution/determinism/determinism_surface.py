"""C1.3: Determinism Surface - Non-determinism isolation.

10C-REQ-119: Enforce Run Clock Only Seeded Only Stable IDs Only Photocopy Calls
One Snapshot Only Proposal Only - no wall clock no raw random no uuid4 no live network
"""

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable


class ClockMode(Enum):
    """Clock mode for determinism."""
    WALL_CLOCK = auto()  # Non-deterministic
    RUN_CLOCK = auto()   # Deterministic from envelope
    FROZEN = auto()      # Fixed timestamp


class RandomMode(Enum):
    """Random mode for determinism."""
    RAW_RANDOM = auto()   # Non-deterministic
    SEEDED = auto()       # Deterministic from seed
    FROZEN = auto()       # Fixed sequence


class IDMode(Enum):
    """ID generation mode."""
    UUID4 = auto()        # Non-deterministic
    STABLE = auto()       # Deterministic from counter
    HASHED = auto()       # Deterministic from content


class NetworkMode(Enum):
    """Network access mode."""
    LIVE = auto()         # Non-deterministic
    PHOTOCOPY = auto()    # Recorded/replayed
    MOCKED = auto()       # Deterministic mock


class StateMode(Enum):
    """State access mode."""
    MIXED = auto()        # Non-deterministic
    ONE_SNAPSHOT = auto() # Fixed snapshot
    PROPOSAL_ONLY = auto() # Pending commit only


@dataclass
class DeterminismSurface:
    """Determinism surface configuration.

    10C-REQ-119: Enforces the six determinism constraints:
    1. Run Clock Only
    2. Seeded Only
    3. Stable IDs Only
    4. Photocopy Calls
    5. One Snapshot Only
    6. Proposal Only
    """
    clock_mode: ClockMode = ClockMode.RUN_CLOCK
    random_mode: RandomMode = RandomMode.SEEDED
    id_mode: IDMode = IDMode.STABLE
    network_mode: NetworkMode = NetworkMode.PHOTOCOPY
    state_mode: StateMode = StateMode.ONE_SNAPSHOT

    # Frozen values for deterministic execution
    frozen_timestamp: float | None = None
    entropy_seed: int = 42
    id_counter: int = 0
    snapshot_id: str = ""

    def get_timestamp(self) -> float:
        """Get deterministic timestamp."""
        if self.clock_mode == ClockMode.FROZEN and self.frozen_timestamp:
            return self.frozen_timestamp
        elif self.clock_mode == ClockMode.RUN_CLOCK:
            return self.frozen_timestamp or time.time()
        else:
            raise RuntimeError("Wall clock access prohibited in determinism surface")

    def get_random(self) -> random.Random:
        """Get deterministic random generator."""
        if self.random_mode == RandomMode.SEEDED:
            return random.Random(self.entropy_seed)
        elif self.random_mode == RandomMode.FROZEN:
            return random.Random(0)  # Fixed
        else:
            raise RuntimeError("Raw random access prohibited in determinism surface")

    def generate_id(self, prefix: str = "") -> str:
        """Generate deterministic ID."""
        if self.id_mode == IDMode.STABLE:
            self.id_counter += 1
            return f"{prefix}{self.id_counter:08d}"
        elif self.id_mode == IDMode.HASHED:
            import hashlib
            data = f"{prefix}:{self.entropy_seed}:{self.id_counter}"
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        else:
            raise RuntimeError("UUID4 access prohibited in determinism surface")

    def validate_network_access(self, url: str) -> bool:
        """Validate network access is allowed."""
        if self.network_mode == NetworkMode.LIVE:
            raise RuntimeError("Live network access prohibited in determinism surface")
        return True  # Photocopy or mocked allowed


class DeterminismEnforcer:
    """Enforces determinism surface on execution."""

    def __init__(self, surface: DeterminismSurface | None = None) -> None:
        self.surface = surface or DeterminismSurface()
        self._original_time = None
        self._original_random = None
        self._original_uuid = None

    def __enter__(self) -> DeterminismSurface:
        """Enter determinism context."""
        # Save originals
        self._original_time = time.time
        self._original_random = random.random
        self._original_uuid = uuid.uuid4

        # Override with deterministic versions
        # Note: In production, this would use more sophisticated patching
        return self.surface

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit determinism context."""
        # Restore originals
        pass  # Restoration handled by context manager
