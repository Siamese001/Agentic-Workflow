"""
Signal Bus - Blackboard Pattern for Inter-Agent Communication.

Implements the Canon Validator signal system for L5+ autonomy.
Enables agents to emit and consume signals for state coordination,
convergence detection, and human-in-the-loop intervention triggers.

Canon Validator Patterns Implemented:
- Signal emission and detection (CRITICAL_FAIL, TEST_FAILURE, HIGH_RISK, etc.)
- Blackboard pattern for shared state
- Listener registration for reactive behavior
- Signal history for debugging and reflection
- Async-safe operations with lock protection (Canon Validator compliance)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Standard signal types matching Canon Validator patterns."""
    
    # Critical signals - abort/escalate
    CRITICAL_FAIL = "CRITICAL_FAIL"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    SECURE_REBOOT = "SECURE_REBOOT"
    
    # Test/validation signals
    TEST_FAILURE = "TEST_FAILURE"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    QUALITY_BELOW_THRESHOLD = "QUALITY_BELOW_THRESHOLD"
    
    # Risk signals - may trigger human intervention
    HIGH_RISK = "HIGH_RISK"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
    
    # Human intervention signals
    VETOED = "VETOED"
    APPROVED = "APPROVED"
    
    # Convergence signals
    CONVERGED = "CONVERGED"
    CONVERGENCE_FAILED = "CONVERGENCE_FAILED"
    
    # Progress signals
    CYCLE_COMPLETE = "CYCLE_COMPLETE"
    PHASE_COMPLETE = "PHASE_COMPLETE"
    
    # Rollback signals
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    ROLLBACK_EXECUTED = "ROLLBACK_EXECUTED"
    
    # Performance signals
    PERFORMANCE_REGRESSION = "PERFORMANCE_REGRESSION"
    
    # LLM signals
    LLM_FAILURE = "LLM_FAILURE"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"


@dataclass
class Signal:
    """Individual signal with metadata."""
    
    signal_type: SignalType
    message: str = ""
    source: str = ""  # Agent/component that emitted
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "info"  # info, warning, error, critical


@dataclass
class SignalHistory:
    """Track signal history for reflection and debugging."""
    
    signals: List[Signal] = field(default_factory=list)
    max_history: int = 1000
    
    def add(self, signal: Signal) -> None:
        """Add signal to history with size limit."""
        self.signals.append(signal)
        if len(self.signals) > self.max_history:
            self.signals = self.signals[-self.max_history:]
    
    def get_by_type(self, signal_type: SignalType) -> List[Signal]:
        """Get all signals of a specific type."""
        return [s for s in self.signals if s.signal_type == signal_type]
    
    def get_recent(self, count: int = 10) -> List[Signal]:
        """Get most recent signals."""
        return self.signals[-count:]
    
    def get_by_cycle(self, cycle: int) -> List[Signal]:
        """Get signals from a specific cycle."""
        return [s for s in self.signals if s.payload.get("cycle") == cycle]


class SignalBus:
    """
    Central signal bus implementing the Canon Validator blackboard pattern.
    
    Provides:
    - Signal emission and detection
    - Listener registration for reactive behavior
    - Signal history for reflection
    - Cycle-aware signal management
    - Async-safe emit/clear with lock protection
    
    Usage:
        bus = SignalBus()
        await bus.emit(SignalType.TEST_FAILURE, "Unit tests failed", source="TestPilot")
        if bus.has(SignalType.CRITICAL_FAIL):
            break
    
    Sync Usage (backward compatible):
        bus.emit_sync(SignalType.TEST_FAILURE, "Unit tests failed", source="TestPilot")
    """
    
    def __init__(self) -> None:
        """Initialize the signal bus."""
        self.signals: Set[SignalType] = set()
        self.active_signals: Dict[SignalType, Signal] = {}
        self.listeners: Dict[SignalType, List[Callable[[Signal], None]]] = {}
        self.history = SignalHistory()
        self.current_cycle: int = 0
        self._lock = asyncio.Lock()
        
        logger.info("SignalBus initialized - Canon Validator blackboard pattern active")
    
    async def emit(
        self,
        signal_type: SignalType,
        message: str = "",
        source: str = "",
        payload: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> Signal:
        """
        Emit a signal to the bus (async, lock-protected).
        
        Args:
            signal_type: Type of signal to emit
            message: Human-readable message
            source: Agent/component emitting the signal
            payload: Additional data
            severity: Signal severity level
            
        Returns:
            The emitted Signal object
        """
        signal = Signal(
            signal_type=signal_type,
            message=message,
            source=source,
            payload=payload or {},
            severity=severity
        )
        signal.payload["cycle"] = self.current_cycle
        
        async with self._lock:
            self.signals.add(signal_type)
            self.active_signals[signal_type] = signal
            self.history.add(signal)
        
        # Log based on severity
        log_msg = f"[SIGNAL] {signal_type.value}: {message} (source={source})"
        if severity == "critical":
            logger.critical(log_msg)
        elif severity == "error":
            logger.error(log_msg)
        elif severity == "warning":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Notify listeners (async-aware)
        await self._notify_listeners_async(signal)
        
        return signal
    
    def emit_sync(
        self,
        signal_type: SignalType,
        message: str = "",
        source: str = "",
        payload: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> Signal:
        """
        Emit a signal to the bus (sync version for backward compatibility).
        
        WARNING: This method does not use async lock protection.
        Use `await emit()` in async contexts for full safety.
        
        Args:
            signal_type: Type of signal to emit
            message: Human-readable message
            source: Agent/component emitting the signal
            payload: Additional data
            severity: Signal severity level
            
        Returns:
            The emitted Signal object
        """
        signal = Signal(
            signal_type=signal_type,
            message=message,
            source=source,
            payload=payload or {},
            severity=severity
        )
        signal.payload["cycle"] = self.current_cycle
        
        self.signals.add(signal_type)
        self.active_signals[signal_type] = signal
        self.history.add(signal)
        
        # Log based on severity
        log_msg = f"[SIGNAL] {signal_type.value}: {message} (source={source})"
        if severity == "critical":
            logger.critical(log_msg)
        elif severity == "error":
            logger.error(log_msg)
        elif severity == "warning":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Notify listeners (sync only)
        self._notify_listeners_sync(signal)
        
        return signal
    
    async def _notify_listeners_async(self, signal: Signal) -> None:
        """Notify all registered listeners for this signal type (async-aware)."""
        listeners = self.listeners.get(signal.signal_type, [])
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    asyncio.create_task(listener(signal))
                else:
                    listener(signal)
            except Exception as e:
                logger.error(f"Signal listener error: {e}")
    
    def _notify_listeners_sync(self, signal: Signal) -> None:
        """Notify all registered listeners for this signal type (sync only)."""
        listeners = self.listeners.get(signal.signal_type, [])
        for listener in listeners:
            try:
                listener(signal)
            except Exception as e:
                logger.error(f"Signal listener error: {e}")
    
    def has(self, signal_type: SignalType) -> bool:
        """Check if a signal type is currently active."""
        return signal_type in self.signals
    
    def has_any(self, signal_types: List[SignalType]) -> bool:
        """Check if any of the given signal types are active."""
        return any(st in self.signals for st in signal_types)
    
    def has_all(self, signal_types: List[SignalType]) -> bool:
        """Check if all of the given signal types are active."""
        return all(st in self.signals for st in signal_types)
    
    def get(self, signal_type: SignalType) -> Optional[Signal]:
        """Get the active signal of a specific type."""
        return self.active_signals.get(signal_type)
    
    async def discard(self, signal_type: SignalType) -> None:
        """Remove a signal from active signals (async, lock-protected)."""
        async with self._lock:
            self.signals.discard(signal_type)
            self.active_signals.pop(signal_type, None)
            logger.debug(f"Signal discarded: {signal_type.value}")
    
    async def clear(self) -> None:
        """Clear all active signals (async, lock-protected)."""
        async with self._lock:
            self.signals.clear()
            self.active_signals.clear()
            logger.debug("All signals cleared")
    
    def clear_sync(self) -> None:
        """Clear all active signals (sync version for backward compatibility)."""
        self.signals.clear()
        self.active_signals.clear()
        logger.debug("All signals cleared (sync)")
    
    async def clear_cycle(self) -> None:
        """Clear signals and increment cycle counter (async, lock-protected)."""
        await self.clear()
        async with self._lock:
            self.current_cycle += 1
        logger.info(f"Cycle {self.current_cycle} started - signals cleared")
    
    def clear_cycle_sync(self) -> None:
        """Clear signals and increment cycle counter (sync version)."""
        self.clear_sync()
        self.current_cycle += 1
        logger.info(f"Cycle {self.current_cycle} started - signals cleared (sync)")
    
    def register_listener(
        self,
        signal_type: SignalType,
        callback: Callable[[Signal], None]
    ) -> None:
        """
        Register a listener for a specific signal type.
        
        Args:
            signal_type: Signal type to listen for
            callback: Function to call when signal is emitted (can be sync or async)
        """
        if signal_type not in self.listeners:
            self.listeners[signal_type] = []
        self.listeners[signal_type].append(callback)
        logger.debug(f"Listener registered for {signal_type.value}")
    
    def unregister_listener(
        self,
        signal_type: SignalType,
        callback: Callable[[Signal], None]
    ) -> None:
        """Unregister a listener."""
        if signal_type in self.listeners:
            try:
                self.listeners[signal_type].remove(callback)
            except ValueError:
                pass
    
    # Convenience methods matching Canon Validator API (async)
    async def signal_critical_failure(self, message: str, source: str = "") -> Signal:
        """Emit a critical failure signal (async)."""
        return await self.emit(
            SignalType.CRITICAL_FAIL,
            message,
            source,
            severity="critical"
        )
    
    async def signal_test_failure(self, message: str = "", source: str = "TestPilot") -> Signal:
        """Emit a test failure signal (async)."""
        return await self.emit(
            SignalType.TEST_FAILURE,
            message,
            source,
            severity="error"
        )
    
    async def signal_high_risk(self, message: str, source: str = "") -> Signal:
        """Emit a high risk signal (async, may trigger human intervention)."""
        return await self.emit(
            SignalType.HIGH_RISK,
            message,
            source,
            severity="warning"
        )
    
    async def signal_convergence(self, source: str = "") -> Signal:
        """Emit convergence signal (async)."""
        return await self.emit(
            SignalType.CONVERGED,
            "System converged successfully",
            source,
            severity="info"
        )
    
    async def signal_needs_human_review(self, message: str, source: str = "") -> Signal:
        """Emit signal requesting human review (async)."""
        return await self.emit(
            SignalType.NEEDS_HUMAN_REVIEW,
            message,
            source,
            severity="warning"
        )
    
    async def signal_rollback_required(self, message: str, source: str = "") -> Signal:
        """Emit rollback required signal (async)."""
        return await self.emit(
            SignalType.ROLLBACK_REQUIRED,
            message,
            source,
            severity="error"
        )
    
    async def signal_llm_failure(self, error: str, source: str = "") -> Signal:
        """Emit LLM failure signal (async)."""
        return await self.emit(
            SignalType.LLM_FAILURE,
            error,
            source,
            severity="error"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current signal state for reflection."""
        return {
            "current_cycle": self.current_cycle,
            "active_signals": [s.value for s in self.signals],
            "signal_count": len(self.signals),
            "history_count": len(self.history.signals),
            "recent_signals": [
                {
                    "type": s.signal_type.value,
                    "message": s.message,
                    "source": s.source,
                    "timestamp": s.timestamp.isoformat()
                }
                for s in self.history.get_recent(5)
            ]
        }
    
    def is_critical_state(self) -> bool:
        """Check if system is in a critical state requiring abort."""
        critical_signals = [
            SignalType.CRITICAL_FAIL,
            SignalType.SECURE_REBOOT,
            SignalType.VETOED
        ]
        return self.has_any(critical_signals)
    
    def needs_intervention(self) -> bool:
        """Check if human intervention is needed."""
        intervention_signals = [
            SignalType.HIGH_RISK,
            SignalType.NEEDS_HUMAN_REVIEW
        ]
        return self.has_any(intervention_signals)


# Global singleton instance
_signal_bus: Optional[SignalBus] = None


def get_signal_bus() -> SignalBus:
    """Get or create the global SignalBus instance."""
    global _signal_bus
    if _signal_bus is None:
        _signal_bus = SignalBus()
    return _signal_bus


def reset_signal_bus() -> SignalBus:
    """Reset the global SignalBus (for testing)."""
    global _signal_bus
    _signal_bus = SignalBus()
    return _signal_bus
