"""
Qwen Circuit Breaker - Deterministic Circuit Breaker with Replay Safety

Provides failure detection and automatic tier disabling with deterministic
behavior during replay mode.
"""
from __future__ import annotations
import logging
import time
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class QwenCircuitBreaker:
    """Deterministic circuit breaker with replay safety."""

    def __init__(self, replay_mode: bool=False):
        self.replay_mode = replay_mode
        self.failure_count = 0
        self.failure_timestamps: list[int] = []
        self.circuit_open = False
        self.circuit_open_timestamp: int | None = None
        self.last_failure_timestamp: int | None = None

    def record_failure(self, timestamp: int | None=None) -> bool:
        """Record failure with deterministic replay behavior."""
        if self.replay_mode:
            return False
        now = timestamp or int(time.time())
        self.last_failure_timestamp = now
        self.failure_timestamps = [t for t in self.failure_timestamps if now - t <= 60]
        self.failure_timestamps.append(now)
        self.failure_count = len(self.failure_timestamps)
        if self.failure_count >= 3:
            self.circuit_open = True
            self.circuit_open_timestamp = now
            logger.warning('Qwen circuit breaker OPEN - disabling for 5 minutes')
            return True
        return False

    def is_circuit_open(self, timestamp: int | None=None) -> bool:
        """Check circuit state with deterministic replay behavior."""
        if self.replay_mode:
            return False
        if not self.circuit_open:
            return False
        now = timestamp or int(time.time())
        if now - self.circuit_open_timestamp > 300:
            self.circuit_open = False
            self.failure_count = 0
            self.failure_timestamps.clear()
            logger.info('Qwen circuit breaker CLOSED - re-enabling tier')
            return False
        return True

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status for health endpoint."""
        return {'circuit_open': self.is_circuit_open(), 'failure_count': self.failure_count, 'last_failure': self.last_failure_timestamp, 'replay_mode': self.replay_mode}
circuit_breaker = QwenCircuitBreaker()
__all__ = ['QwenCircuitBreaker', 'circuit_breaker']
