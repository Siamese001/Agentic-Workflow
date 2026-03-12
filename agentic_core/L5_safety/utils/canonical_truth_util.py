"""
CANONICAL TRUTH: Sovereign Single Source of Truth Utilities
=========================================================

This module provides pure utility functions for SSOT calculations.

CRITICAL CONSTRAINTS:
- ZERO internal project imports (no agentic_core.* imports)
- Only stdlib imports allowed (pathlib, re, typing)
- Can be imported from anywhere without circular dependencies
- All functions are pure and deterministic

PURPOSE:
Resolves SSOT violations by providing canonical implementations for:
1. Health score calculation (Violation 4)
2. Layer inference from paths (Violation 2)
3. Agent categorization, territory mapping, etc.

USAGE:
    from agentic_core.utils.canonical_truth_validator import (
        calculate_health_score,
        get_canonical_layer
    )
"""
import re
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def calculate_health_score(violations: list[dict[str, Any]], weights: dict[str, float] | None=None) -> float:
    """
    Calculate a normalized health score (0-100) from violation data.

    Args:
        violations: List of violation dictionaries with 'severity' and 'count' keys
        weights: Optional weights for different severity levels

    Returns:
        Health score from 0 (worst) to 100 (best)
    """
    if not violations:
        return 100.0
    default_weights = {'critical': 10.0, 'high': 5.0, 'medium': 2.0, 'low': 1.0}
    weights = weights or default_weights
    total_penalty = 0.0
    max_possible_penalty = 0.0
    for violation in violations:
        severity = violation.get('severity', 'medium').lower()
        count = violation.get('count', 1)
        penalty = weights.get(severity, 2.0) * count
        total_penalty += penalty
        max_possible_penalty += default_weights['critical'] * count
    if max_possible_penalty == 0:
        return 100.0
    health_score = max(0, 100 - total_penalty / max_possible_penalty * 100)
    return round(health_score, 2)

def get_canonical_layer(file_path: str | Path) -> str:
    """
    Infer the canonical layer from a file path.

    Args:
        file_path: Path to the file

    Returns:
        Canonical layer string (L0-L6, Apps, Utils, Tests, or 'unknown')
    """
    path_str = str(file_path)
    layer_patterns = {'/L0_routing/': 'L0', '/L1_cognition/': 'L1', '/L2_execution/': 'L2', '/L3_orchestration/': 'L3', '/L4_state/': 'L4', '/L5_safety/': 'L5', '/L6_observability/': 'L6', '/apps_': 'Apps', '/apps_shared/': 'Apps', '/agentic_core/utils/': 'Utils', '/tests/': 'Tests', '/test_': 'Tests'}
    for pattern, layer in layer_patterns.items():
        if re.search(pattern, path_str):
            return layer
    return 'unknown'

def validate_health_components(components: dict[str, Any]) -> dict[str, Any]:
    """
    Validate health components and return validation results.

    Args:
        components: Dictionary of health components to validate

    Returns:
        Validation results with valid/invalid components
    """
    results = {'valid': [], 'invalid': [], 'missing_required': [], 'overall_valid': True}
    required_components = ['violations', 'weights', 'thresholds']
    for component in required_components:
        if component not in components:
            results['missing_required'].append(component)
            results['overall_valid'] = False
    if 'violations' in components:
        violations = components['violations']
        if isinstance(violations, list):
            results['valid'].append('violations')
        else:
            results['invalid'].append('violations')
            results['overall_valid'] = False
    if 'weights' in components:
        weights = components['weights']
        if isinstance(weights, dict) and all((isinstance(k, str) and isinstance(v, int | float) for k, v in weights.items())):
            results['valid'].append('weights')
        else:
            results['invalid'].append('weights')
            results['overall_valid'] = False
    return results

def get_health_weights() -> dict[str, float]:
    """
    Get default health calculation weights.

    Returns:
        Dictionary of weights for different violation severities
    """
    return {'critical': 10.0, 'high': 5.0, 'medium': 2.0, 'low': 1.0, 'info': 0.5}

def categorize_agent(class_name: str, base_classes: list | None=None, docstring: str | None=None) -> str:
    """
    Categorize an agent based on its name, inheritance, and documentation.

    Args:
        class_name: Name of the agent class (e.g., "BaseClassEnforcerAgent")
        base_classes: List of base class names (e.g., ["L5Agent", "MCPHardenedMixin"])
        docstring: Optional docstring content

    Returns:
        Agent category string
    """
    base_classes = base_classes or []
    search_string = class_name + ' ' + ' '.join(base_classes) + ' ' + (docstring or '')
    categories = {'Validator': 'validator|check|enforce|validate|audit', 'Orchestrator': 'orchestrat|workflow|coordination|meta', 'Guardrail': 'guardrail|safety|security|protect', 'Memory': 'memory|storage|cache|persist', 'L1': 'cognition|thought|intent|analysis', 'L2': 'execution|tool|action|mcp', 'L3': 'orchestrat|workflow|coordination|meta', 'L4': 'state|validation|ledger|memory', 'L5': 'safety|guardrail|validator|audit', 'L6': 'observability|logging|telemetry|metrics', 'GenericAgent': 'agent|base|sovereign'}
    for category, pattern in categories.items():
        if re.search(pattern, search_string, re.IGNORECASE):
            return category
    return 'Unknown'

def get_agent_categories() -> list[str]:
    """
    Get list of all valid agent categories.

    Returns:
        List of category strings
    """
    return ['Validator', 'Orchestrator', 'Guardrail', 'Memory', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'GenericAgent', 'Unknown']
