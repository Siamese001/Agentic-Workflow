# Ownership: agentic_core / L2_execution
# -*- coding: utf-8 -*-
"""Validate execution - atomic wrapper for validation logic."""

from __future__ import annotations

from typing import Any, Dict, List

from shared.models import ValidationResult, ValidationSeverity


def validate(data: Dict[str, Any]) -> List[ValidationResult]:
    """Validate execution data and return results."""
    results = []
    
    if not data:
        results.append(ValidationResult(
            rule_id="EMPTY_DATA",
            passed=False,
            severity=ValidationSeverity.HIGH,
            message="Data is empty",
        ))
    else:
        results.append(ValidationResult(
            rule_id="DATA_PRESENT",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Data is present",
        ))
    
    return results
