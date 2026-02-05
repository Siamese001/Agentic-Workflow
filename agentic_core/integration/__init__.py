"""
Integration module for agentic_core.

Provides factory functions and utilities for creating protocol-compliant
components with proper feature flag integration across all core layers.
"""

from .component_factory import (
    ComponentFactory,
    get_detection_emitter,
    get_human_review_queue,
    get_meta_learning_service,
    get_verification_gate,
)
from .migration_helper import (
    MigrationHelper,
    check_agent_compliance,
    get_migration_status,
)

__all__ = [
    # Factory
    "ComponentFactory",
    "get_verification_gate",
    "get_human_review_queue",
    "get_detection_emitter",
    "get_meta_learning_service",
    # Migration
    "MigrationHelper",
    "check_agent_compliance",
    "get_migration_status",
]
