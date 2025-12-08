# Ownership: agentic_core / L2_execution
# -*- coding: utf-8 -*-
"""Format execution output - atomic wrapper for shared types."""

from __future__ import annotations

from typing import Any, Dict, List

from shared.workflow_types import HopStatus, GateDecision, HopCheckpoint
from shared.models import ValidationResult, ValidationSeverity


def format_execution_output(result: Dict[str, Any]) -> str:
    """Format execution result for output."""
    status = result.get("status", "unknown")
    return f"Execution completed with status: {status}"


def format_validation_summary(results: List[ValidationResult]) -> str:
    """Format validation results as summary string."""
    passed = sum(1 for r in results if r.passed)
    return f"Validation: {passed}/{len(results)} passed"


def format_hop_checkpoint(checkpoint: HopCheckpoint) -> str:
    """Format a hop checkpoint for logging."""
    return f"[{checkpoint.hop_id}] Status: {checkpoint.status.name}"


def format_gate_decision(decision: GateDecision) -> str:
    """Format a gate decision for logging."""
    return f"Gate decision: {decision.name}"
