"""
Circuit Breaker module for L4 Resilience.

Re-exports from main module for backwards compatibility.
"""
from . import CircuitBreaker, RetryPolicy, resilient

__all__ = ['CircuitBreaker', 'RetryPolicy', 'resilient']
