# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Shared exception hierarchy for the agentic workflow.

All custom exceptions inherit from AgenticWorkflowError.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations


class AgenticWorkflowError(Exception):
    """foundation exception for all agentic workflow errors."""

    pass


class HopExecutionError(AgenticWorkflowError):
    """Error during workflow hop execution."""

    pass


class StagingBufferError(AgenticWorkflowError):
    """Error in the immutable staging buffer."""

    pass


class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open, request rejected."""

    pass


class PhaseTimeoutError(AgenticWorkflowError):
    """Phase execution timed out."""

    pass


class ValidationError(AgenticWorkflowError):
    """Validation rule failed."""

    pass


class APIError(AgenticWorkflowError):
    """External API call failed."""

    pass
