# File: utils_LIC.py
# Description: General-purpose utilities for the LIC workflow.
# REFACTOR: v13.0 - This file has been slimmed down.
# - AdaptiveTemperatureController: Removed. Logic moved to agent_specs_LIC.json and HOPOrchestrator.
# - ContextManager: Removed. No longer needed in v13.0 HOP architecture.
# - ValidationHelper: Removed. Replaced by tools_LIC.py (ValidationToolkit).

__version__ = "13.0"

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict

# Import models needed for CircuitBreaker
from models_LIC import CircuitState, CircuitBreakerOpenError

# ============================================================================
# KEPT FOR v13.0: CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """
    Circuit breaker for API calls - prevents cascade failures.
    This is a core utility and remains in v13.0.
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are blocked
    - HALF_OPEN: Testing if service has recovered
    
    After failure_threshold consecutive failures, the circuit opens.
    After timeout_seconds, it transitions to HALF_OPEN to test recovery.
    A successful request in HALF_OPEN closes the circuit.
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 60
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening
            timeout_seconds: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
        
        Returns:
            Result from func
        
        Raises:
            CircuitBreakerOpenError: If circuit is OPEN
            Exception: Any exception raised by func
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
                print(f"[CircuitBreaker] Transitioning to HALF_OPEN for recovery test")
            else:
                raise CircuitBreakerOpenError(
                    f"API circuit breaker is OPEN - waiting for recovery "
                    f"(failed {self.failure_count} times, will retry after {self.timeout_seconds}s)"
                )
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                # Test request succeeded, close circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print(f"[CircuitBreaker] Recovery successful, circuit CLOSED")
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"[CircuitBreaker] Circuit OPEN after {self.failure_count} failures")
            else:
                print(f"[CircuitBreaker] Failure {self.failure_count}/{self.failure_threshold}")
            
            raise

# ============================================================================
# REMOVED v13.0: CONTEXT MANAGER
# Rationale: Replaced by explicit state-based I/O. Not needed in HOP architecture.
# ============================================================================

# ============================================================================
# REMOVED v13.0: ADAPTIVE TEMPERATURE CONTROLLER
# Rationale: Logic externalized to agent_specs_LIC.json and handled
#            directly by HOPOrchestrator in workflow_LIC_v13.py.
# ============================================================================

# ============================================================================
# KEPT FOR v13.0: TEXT PROCESSING UTILITIES
# ============================================================================

class TextProcessor:
    """
    Utility functions for text processing and analysis.
    Kept in v13.0 as these are generic, stateless helpers.
    """
    
    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
        
        Returns:
            Word count
        """
        return len(text.split())
    
    @staticmethod
    def count_chars(text: str) -> int:
        """
        Count characters in text.
        
        Args:
            text: Input text
        
        Returns:
            Character count
        """
        return len(text)
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        # Simple sentence splitting on period, exclamation, question mark
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_metrics(text: str) -> List[str]:
        """
        Extract quantitative metrics from text.
        
        Args:
            text: Input text
        
        Returns:
            List of metrics (percentages, multipliers, large numbers)
        """
        metric_pattern = r'\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand|k)\b'
        return re.findall(metric_pattern, text, re.IGNORECASE)
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """
        Remove extra whitespace from text.
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_chars: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum character length.
        
        Args:
            text: Input text
            max_chars: Maximum characters
            suffix: Suffix to add if truncated
        
        Returns:
            Truncated text
        """
        if len(text) <= max_chars:
            return text
        return text[:max_chars - len(suffix)] + suffix

# ============================================================================
# REMOVED v13.0: VALIDATION HELPERS
# Rationale: Replaced by the dedicated tools_LIC.py (ValidationToolkit)
#            and externalized rules in validator_rules_LIC.json.
# ============================================================================

# ============================================================================
# KEPT FOR v13.0: TIMING UTILITIES
# ============================================================================

class Timer:
    """
    Simple timer for measuring execution time.
    Kept in v13.0 as a generic, stateless helper.
    """
    
    def __init__(self):
        """Initialize timer"""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start(self):
        """Start timer"""
        self.start_time = datetime.now()
    
    def stop(self) -> float:
        """
        Stop timer and return elapsed seconds.
        
        Returns:
            Elapsed time in seconds
        """
        self.end_time = datetime.now()
        if self.start_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    def elapsed(self) -> float:
        """
        Get elapsed time without stopping timer.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()