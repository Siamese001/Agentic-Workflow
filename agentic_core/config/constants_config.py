"""
Blueprint Sovereign Constants - SSOT for configuration Constants

This module provides centralized configuration constants used across the codebase.
All feature flags, default values, and configuration constants should be defined here.

SSOT Location: agentic_core/config/core/constants.py
"""

import os
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_ROOT = Path(__file__).resolve().parents[3]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # guardian: allow-global-mutation


def _get_ssot_exclusions():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )

    return DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS


# =============================================================================
# Redis cache configuration
# =============================================================================

# Feature flag to enable/disable Redis caching
USE_REDIS_CACHE: bool = os.getenv("USE_REDIS_CACHE", "true").lower() == "true"

# Enable graceful degradation to local dict when Redis is unavailable
GRACEFUL_DEGRADATION: bool = os.getenv("GRACEFUL_DEGRADATION", "true").lower() == "true"

# Enable cache metrics collection for dashboard visibility
CACHE_METRICS_ENABLED: bool = os.getenv("CACHE_METRICS_ENABLED", "false").lower() == "true"


# =============================================================================
# File Discovery configuration
# =============================================================================

# Default directories to exclude from file discovery
# This is a frozenset for immutability and hashability
try:
    _DET, _GED, _SEF = _get_ssot_exclusions()
    DEFAULT_EXCLUDE_DIRS: frozenset[str] = _GED | _SEF | _DET
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
        {"__pycache__", ".git", "node_modules", "venv", ".venv", "archives"}
    )


# =============================================================================
# Agent configuration
# =============================================================================

# Default timeout for agent operations (in seconds)
AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))

# Default timeout for mission operations (in seconds)
MISSION_TIMEOUT_SECONDS: int = int(os.getenv("MISSION_TIMEOUT_SECONDS", "3600"))


# =============================================================================
# Healing configuration
# =============================================================================

# Maximum healing attempts per file per violation type
MAX_HEALING_ATTEMPTS: int = 3

# Enable auto-archive before destructive operations
AUTO_ARCHIVE_ENABLED: bool = True


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core Constants (SSOT)
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
    # Redis
    "USE_REDIS_CACHE",
    "GRACEFUL_DEGRADATION",
    "CACHE_METRICS_ENABLED",
    # File Discovery
    "DEFAULT_EXCLUDE_DIRS",
    # Agent
    "AGENT_TIMEOUT_SECONDS",
    "MISSION_TIMEOUT_SECONDS",
    # Healing
    "MAX_HEALING_ATTEMPTS",
    "AUTO_ARCHIVE_ENABLED",
]
