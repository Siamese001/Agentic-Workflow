# Ownership: agentic_core / L2_execution
# -*- coding: utf-8 -*-
"""Format execution output - atomic execution layer for shared types."""


from typing import Dict, List

from shared.models import ValidationResult


def format_execution_output(result: Dict[str, object]) -> str:
    """Format execution result for output."""
    status = result.get("status", "unknown")
    return f"Execution completed with status: {status}"


def format_validation_summary(results: List[ValidationResult]) -> str:
    """Format validation results as summary string."""
    passed = sum(1 for r in results if r.passed)
    return f"Validation: {passed}/{len(results)} passed"


def format_workflow_item(item: object) -> str:
    """Format a workflow item (checkpoint or decision) for logging."""
    if hasattr(item, 'hop_id'):
        return f"[{item.hop_id}] Status: {item.status.name}"
    if hasattr(item, 'name'):
        return f"Decision: {item.name}"
    return str(item)
