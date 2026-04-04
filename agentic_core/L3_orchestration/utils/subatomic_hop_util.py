"""Subatomic Hop Utility - Deterministic cross-layer routing.

This module provides deterministic routing functionality previously
implemented in SubatomicHopAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 5).

Usage:
    from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
        validate_dependencies, create_hop_context, SubatomicHopResult
    )

    # Validate hop dependencies
    result = validate_dependencies(config, storage, genealogy)
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


class SovereignDependencyError(Exception):
    """Raised when a required dependency is not injected."""
    pass


@dataclass
class SubatomicHopResult:
    """Result of a subatomic hop operation."""

    success: bool
    hop_id: str
    role: str
    errors: list[str] = field(default_factory=list)


@dataclass
class HopContext:
    """Context for a subatomic hop."""

    role: str
    config: dict[str, Any]
    hop_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "role": self.role,
            "config": self.config,
            "hop_id": self.hop_id,
        }


def validate_dependencies(
    role: str,
    config: dict[str, Any],
    storage: Any | None = None,
    genealogy: Any | None = None,
    governor: Any | None = None,
    overseer: Any | None = None,
) -> SubatomicHopResult:
    """Validate that required dependencies are present.

    Args:
        role: Agent role identifier
        config: Configuration dictionary
        storage: Storage adapter (optional)
        genealogy: Genealogy registry (optional)
        governor: Cost governor (optional)
        overseer: Constitutional overseer (optional)

    Returns:
        SubatomicHopResult with validation status
    """
    errors = []

    # Validate required fields
    if not role:
        errors.append("Missing required: role")

    if not config:
        errors.append("Missing required: config")

    # Note: Optional dependencies are not required for basic operation
    # but may be needed for full functionality

    if errors:
        return SubatomicHopResult(
            success=False,
            hop_id=str(uuid.uuid4()),
            role=role or "unknown",
            errors=errors,
        )

    return SubatomicHopResult(
        success=True,
        hop_id=str(uuid.uuid4()),
        role=role,
        errors=[],
    )


def create_hop_context(role: str, config: dict[str, Any]) -> HopContext:
    """Create a hop context for routing.

    Args:
        role: Agent role identifier
        config: Configuration dictionary

    Returns:
        HopContext instance
    """
    return HopContext(role=role, config=config)


def run_self_tests(role: str, config: dict[str, Any]) -> bool:
    """Phase 1: Self-testing for L3 compliance.

    Args:
        role: Agent role identifier
        config: Configuration dictionary

    Returns:
        True if self-tests pass

    Raises:
        AssertionError: If required attributes are missing
    """
    assert role, "Missing role"
    assert config, "Missing config"
    return True


def ensure_dependency(dep: Any, name: str) -> Any:
    """Validate that a required dependency was injected.

    Args:
        dep: The dependency instance
        name: Human-readable name for error messages

    Returns:
        The validated dependency

    Raises:
        SovereignDependencyError: If dependency is None
    """
    if dep is None:
        raise SovereignDependencyError(f"Required dependency '{name}' was not injected")
    return dep
