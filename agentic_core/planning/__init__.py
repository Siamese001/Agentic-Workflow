"""
Planning Module for Token Budget Management
# Layer: L3

This module provides deterministic token budget estimation and enforcement
for Kimi 2.5 planning phases and waves.

Components:
- ContextWindowEstimator: Core token estimation engine
- PlanningPreflightHook: Integration layer with budget enforcement
- TokenBudget: Configuration for token limits and thresholds

Usage:
    from agentic_core.planning import ContextWindowEstimator, PlanningPreflightHook

    # Initialize hook
    hook = PlanningPreflightHook()

    # Check budget before step
    estimate = hook.preflight_check(
        plan_step="my_step",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        files=file_contents,
        diffs=diff_contents,
        logs=log_outputs,
        retrieved_context=retrieved_chunks,
        prior_steps=prior_contents
    )

    # Proceed based on estimate.action
"""

from .preflight_hook import PlanningPreflightHook, TokenBudgetExceededError, require_token_budget
from .token_estimator import ContextSource, ContextWindowEstimator, TokenBudget, TokenEstimate

__all__ = [
    # Core estimator
    "ContextWindowEstimator",
    "TokenBudget",
    "TokenEstimate",
    "ContextSource",
    # Integration layer
    "PlanningPreflightHook",
    "TokenBudgetExceededError",
    "require_token_budget",
]

# Version information
__version__ = "1.0.0"
__author__ = "Agentic Workflow Team"
__description__ = "Token budget management for Kimi 2.5 planning"
