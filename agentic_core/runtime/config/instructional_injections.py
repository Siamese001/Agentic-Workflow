"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging

from agentic_core.config.core.injection_layer_config import InjectionLayer, InstructionalPattern
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "instructional_injections")
_emit_applies_guardrail("p0", "instructional_injections", "p0_governance")
_emit_reads_policy_state("p0", "instructional_injections", "policy_binding")
_emit_snapshots_state("p0", "instructional_injections", "state_snapshot")
emit_replay_key("p0", "instructional_injections")
emit_determinism_digest("p0", "instructional_injections")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


def get_instructional_injections() -> list[InstructionalPattern]:
    """Get instructional injection patterns from YAML (mandatory).

    YAML-only enforcement: No markdown fallback.
    If YAML loading fails, raises typed exception.

    Returns:
        List of InstructionalPattern objects.

    Raises:
        ImportError: If YAML loader not available.
        FileNotFoundError: If YAML corpus not found.
        YamlValidationError: If YAML validation fails.
    """
    from agentic_core.config.core.yaml_injection_loader import get_yaml_loader

    yaml_loader = get_yaml_loader()
    all_patterns = yaml_loader.load_all_patterns()
    patterns = []
    for layer_patterns in all_patterns.values():
        patterns.extend(layer_patterns)
    logger.info(f"Loaded {len(patterns)} instructional patterns from YAML")
    return patterns


def get_required_injections() -> list[InstructionalPattern]:
    """Get required instructional injection patterns.

    Returns:
        List of required InstructionalPattern objects.
        Deterministic rule:
        1. If any patterns have required=True, return only those
        2. If no patterns have required=True, return all FRAMING layer patterns
    """
    all_patterns = get_instructional_injections()
    required_patterns = [pattern for pattern in all_patterns if pattern.required]
    if required_patterns:
        logger.info(f"Identified {len(required_patterns)} explicitly required instructional patterns")
        return required_patterns
    else:
        framing_patterns = [pattern for pattern in all_patterns if pattern.layer == InjectionLayer.FRAMING]
        logger.info(
            f"No explicit required patterns found; using FRAMING layer fallback: {len(framing_patterns)} patterns"
        )
        return framing_patterns
