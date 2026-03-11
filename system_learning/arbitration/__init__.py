"""Arbitration module for deterministic multi-agent proposal selection."""

from .engine import ArbitrationEngine
from .types import ArbitrationCandidate, ArbitrationDecision, ArbitrationPolicy

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = [
    "ArbitrationEngine",
    "ArbitrationCandidate",
    "ArbitrationDecision",
    "ArbitrationPolicy",
]
