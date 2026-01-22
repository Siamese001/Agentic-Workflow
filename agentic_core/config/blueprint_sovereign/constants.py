"""
Blueprint Sovereign Constants - SSOT for Configuration Constants

This module provides centralized configuration constants used across the codebase.
All feature flags, default values, and configuration constants should be defined here.

SSOT Location: agentic_core/config/blueprint_sovereign/constants.py
"""
import os

# =============================================================================
# Redis Cache Configuration
# =============================================================================

# Feature flag to enable/disable Redis caching
USE_REDIS_CACHE: bool = os.getenv("USE_REDIS_CACHE", "false").lower() == "true"

# Enable graceful degradation to local dict when Redis is unavailable
GRACEFUL_DEGRADATION: bool = os.getenv("GRACEFUL_DEGRADATION", "true").lower() == "true"

# Enable cache metrics collection for dashboard visibility
CACHE_METRICS_ENABLED: bool = os.getenv("CACHE_METRICS_ENABLED", "false").lower() == "true"


# =============================================================================
# File Discovery Configuration
# =============================================================================

# Default directories to exclude from file discovery
# This is a frozenset for immutability and hashability
DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset({
    ".sovereign_healing_backup",
    "archives",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".tox",
    "build",
    "dist",
    "*.egg-info",
    ".coverage",
    "htmlcov",
    ".hypothesis",
})


# =============================================================================
# Agent Configuration
# =============================================================================

# Default timeout for agent operations (in seconds)
AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))

# Default timeout for mission operations (in seconds)
MISSION_TIMEOUT_SECONDS: int = int(os.getenv("MISSION_TIMEOUT_SECONDS", "3600"))


# =============================================================================
# Healing Configuration
# =============================================================================

# Maximum healing attempts per file per violation type
MAX_HEALING_ATTEMPTS: int = 3

# Enable auto-archive before destructive operations
AUTO_ARCHIVE_ENABLED: bool = True


# =============================================================================
# Exports
# =============================================================================

__all__ = [
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
