"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging

from agentic_core.config.core.injection_layer_config import InjectionLayer, InstructionalPattern

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    # YAML-only path (no fallback)
    from agentic_core.config.core.yaml_injection_loader import get_yaml_loader

    yaml_loader = get_yaml_loader()
    all_patterns = yaml_loader.load_all_patterns()

    # Convert to flat list
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

    # Check for explicitly required patterns
    required_patterns = [pattern for pattern in all_patterns if pattern.required]

    if required_patterns:
        # Found explicitly required patterns
        logger.info(f"Identified {len(required_patterns)} explicitly required instructional patterns")
        return required_patterns
    else:
        # No explicitly required patterns - fallback to FRAMING layer deterministically
        framing_patterns = [pattern for pattern in all_patterns if pattern.layer == InjectionLayer.FRAMING]
        logger.info(
            f"No explicit required patterns found; using FRAMING layer fallback: {len(framing_patterns)} patterns"
        )
        return framing_patterns
