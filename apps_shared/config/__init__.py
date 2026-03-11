"""Shared configuration for operational agents."""

from __future__ import annotations

from apps_shared.config.operational_config import (
    OPERATIONAL_ALLOWED_DUPLICATES,
    OPERATIONAL_EXCLUDED_DIRS,
    OPERATIONAL_SCAN_TARGETS,
    is_allowed_duplicate,
    is_excluded_path,
    should_scan_directory,
)
from apps_shared.utils.config_loader_util import (
    ConfigLoader,
    ConfigLoadResult,
    get_config_loader,
    load_agent_config,
)

__all__ = [
    "OPERATIONAL_EXCLUDED_DIRS",
    "OPERATIONAL_SCAN_TARGETS",
    "OPERATIONAL_ALLOWED_DUPLICATES",
    "is_excluded_path",
    "is_allowed_duplicate",
    "should_scan_directory",
    "ConfigLoader",
    "ConfigLoadResult",
    "get_config_loader",
    "load_agent_config",
]
