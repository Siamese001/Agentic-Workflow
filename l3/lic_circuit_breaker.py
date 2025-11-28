"""LIC Circuit Breaker - L3 orchestration for preventing retry storms.

Implements nuclear prompt requirements for deterministic, async-safe circuit breaking:
- Sliding failure window with configurable thresholds
- Auto-open on failure threshold, auto-close after cooldown
- Concurrency safety with asyncio.Lock()
- Integration with LIC meta-loop and orchestrators
- L3-pure implementation (no L1/L2/L4/L5 logic)
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# TYPE_CHECKING imports to avoid circular dependencies
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from l3.lic_meta_loop import OutreachContext
    from l5.types import SafetyResult

logger = logging.getLogger(__name__)


@dataclass
class LICBreakerConfig:
    """Configuration for LIC circuit breaker."""
    failure_window: int = 10                # sliding window size (N most recent attempts)
    failure_threshold: int = 5              # breaker opens if failures ≥ threshold
    cooldown_seconds: float = 60.0          # after opening, how long until automatic reset
    max_blocked_attempts: int = 20          # limit for blocking before forced reset


@dataclass
class LICBreakerStatus:
    """Current status of LIC circuit breaker."""
    is_open: bool
    failure_count: int
    total_attempts: int
    last_failure_type: Optional[str]
    last_open_timestamp: Optional[float]
    blocked_attempts: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _AttemptRecord:
    """Internal record for attempt tracking."""
    success: bool
    failure_type: Optional[str]
    timestamp: float


class LICCircuitBreaker:
    """LIC circuit breaker implementing sliding window and cooldown logic.
    
    Prevents infinite retry storms and runaway meta-loops by tracking
    failure patterns and temporarily blocking attempts when thresholds
    are exceeded.
    """
    
    def __init__(
        self,
        *,
        config: Optional[LICBreakerConfig] = None,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC circuit breaker with configuration."""
        self.config = config or LICBreakerConfig()
        self.telemetry_bus = telemetry_bus
        
        # Sliding window of recent attempts (deque with maxlen for O(1) operations)
        self._attempts_window: deque[_AttemptRecord] = deque(
            maxlen=self.config.failure_window
        )
        
        # Breaker state
        self._is_open: bool = False
        self._last_open_timestamp: Optional[float] = None
        self._blocked_attempts: int = 0
        self._total_attempts: int = 0
        self._last_failure_type: Optional[str] = None
        
        # Concurrency safety
        self._lock = asyncio.Lock()
        
        logger.debug(f"LIC Circuit Breaker initialized: {self.config}")
    
    async def check_can_attempt(
        self,
        outreach_context: OutreachContext,
        attempts_total: int,
        archetype: str,
    ) -> bool:
        """Check if a new attempt is allowed (breaker not open).
        
        Args:
            outreach_context: Context for the outreach attempt
            attempts_total: Total attempts made so far in meta-loop
            archetype: Current archetype being attempted
            
        Returns:
            True if attempt is allowed, False if breaker is blocking
        """
        async with self._lock:
            self._safe_record_telemetry("lic_circuit_breaker_check", {
                "archetype": archetype,
                "attempts_total": attempts_total,
                "is_open": self._is_open,
                "failure_count": self._get_failure_count(),
            })
            
            # If breaker is closed, attempt is allowed
            if not self._is_open:
                return True
            
            # Check if cooldown period has expired for auto-close
            now = time.time()
            if (self._last_open_timestamp and 
                now - self._last_open_timestamp >= self.config.cooldown_seconds):
                
                logger.info("LIC Circuit Breaker auto-closing after cooldown")
                await self._reset_internal()
                self._safe_record_telemetry("lic_circuit_breaker_auto_close", {
                    "cooldown_seconds": self.config.cooldown_seconds,
                    "open_duration": now - (self._last_open_timestamp or now),
                })
                return True
            
            # Breaker is still open, block the attempt
            self._blocked_attempts += 1
            
            # Forced reset if too many blocked attempts
            if self._blocked_attempts >= self.config.max_blocked_attempts:
                logger.warning(
                    f"LIC Circuit Breaker forced reset after "
                    f"{self._blocked_attempts} blocked attempts"
                )
                await self._reset_internal()
                self._safe_record_telemetry("lic_circuit_breaker_forced_reset", {
                    "blocked_attempts": self._blocked_attempts,
                    "max_blocked": self.config.max_blocked_attempts,
                })
                return True
            
            self._safe_record_telemetry("lic_circuit_breaker_block", {
                "archetype": archetype,
                "blocked_attempts": self._blocked_attempts,
                "remaining_cooldown": (
                    self.config.cooldown_seconds - 
                    (now - (self._last_open_timestamp or now))
                ),
            })
            
            return False
    
    async def record_attempt(
        self,
        *,
        outreach_context: OutreachContext,
        archetype: str,
        success: bool,
        safety_result: Optional[SafetyResult],
        failure_type: Optional[str],
    ) -> None:
        """Record an attempt outcome for circuit breaker evaluation.
        
        Args:
            outreach_context: Context for the outreach attempt
            archetype: Archetype that was attempted
            success: Whether the attempt succeeded
            safety_result: Safety validation result (if available)
            failure_type: Type of failure (if any)
        """
        async with self._lock:
            now = time.time()
            
            # Create attempt record
            record = _AttemptRecord(
                success=success,
                failure_type=failure_type,
                timestamp=now,
            )
            
            # Add to sliding window (automatically trims to maxlen)
            self._attempts_window.append(record)
            self._total_attempts += 1
            
            if not success and failure_type:
                self._last_failure_type = failure_type
            
            self._safe_record_telemetry("lic_circuit_breaker_record", {
                "archetype": archetype,
                "success": success,
                "failure_type": failure_type,
                "window_size": len(self._attempts_window),
                "failure_count": self._get_failure_count(),
                "is_open": self._is_open,
            })
            
            # Check if we need to open the breaker
            if not self._is_open:
                failure_count = self._get_failure_count()
                if failure_count >= self.config.failure_threshold:
                    await self._open_breaker(failure_count, failure_type)
    
    def get_status(self) -> LICBreakerStatus:
        """Get current breaker status (synchronous, thread-safe for reads).
        
        Returns:
            Current status of the circuit breaker
        """
        # Note: This is intentionally synchronous for status queries
        # The internal state is protected by the lock in async methods
        return LICBreakerStatus(
            is_open=self._is_open,
            failure_count=self._get_failure_count(),
            total_attempts=self._total_attempts,
            last_failure_type=self._last_failure_type,
            last_open_timestamp=self._last_open_timestamp,
            blocked_attempts=self._blocked_attempts,
            metadata={
                "window_size": len(self._attempts_window),
                "config": {
                    "failure_window": self.config.failure_window,
                    "failure_threshold": self.config.failure_threshold,
                    "cooldown_seconds": self.config.cooldown_seconds,
                    "max_blocked_attempts": self.config.max_blocked_attempts,
                }
            },
        )
    
    async def reset(self) -> None:
        """Manually reset the circuit breaker to closed state.
        
        Clears all counters, sliding window, and closes the breaker.
        """
        async with self._lock:
            logger.info("LIC Circuit Breaker manual reset")
            await self._reset_internal()
            self._safe_record_telemetry("lic_circuit_breaker_manual_reset", {})
    
    async def _open_breaker(self, failure_count: int, failure_type: Optional[str]) -> None:
        """Open the circuit breaker due to failure threshold exceeded.
        
        Args:
            failure_count: Current failure count that triggered opening
            failure_type: Type of failure that triggered opening
        """
        self._is_open = True
        self._last_open_timestamp = time.time()
        self._blocked_attempts = 0
        
        logger.warning(
            f"LIC Circuit Breaker OPENED: {failure_count}/{self.config.failure_threshold} "
            f"failures in window, type: {failure_type}"
        )
        
        self._safe_record_telemetry("lic_circuit_breaker_open", {
            "failure_count": failure_count,
            "failure_threshold": self.config.failure_threshold,
            "failure_type": failure_type,
            "window_size": len(self._attempts_window),
        })
    
    async def _reset_internal(self) -> None:
        """Internal reset method (assumes lock is held)."""
        self._is_open = False
        self._last_open_timestamp = None
        self._blocked_attempts = 0
        self._total_attempts = 0
        self._last_failure_type = None
        self._attempts_window.clear()
    
    def _get_failure_count(self) -> int:
        """Get current failure count from sliding window.
        
        Returns:
            Number of failed attempts in the current window
        """
        return sum(1 for record in self._attempts_window if not record.success)
    
    def _safe_record_telemetry(self, event: str, payload: Dict[str, Any]) -> None:
        """Record telemetry event safely without breaking control flow.
        
        Args:
            event: Telemetry event name
            payload: Event payload data
        """
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(event, "L3", payload)
        except Exception:
            # Telemetry failures should never break circuit breaker logic
            logger.debug(f"Failed to record telemetry event {event}")
