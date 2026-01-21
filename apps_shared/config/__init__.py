from __future__ import annotations

"""Shared configuration for operational agents."""

from apps_shared.config.operational_config import (
    OPERATIONAL_ALLOWED_DUPLICATES,
    OPERATIONAL_EXCLUDED_DIRS,
    OPERATIONAL_SCAN_TARGETS,
    is_allowed_duplicate,
    is_excluded_path,
    should_scan_directory,
)

__all__ = [
    "OPERATIONAL_EXCLUDED_DIRS",
    "OPERATIONAL_SCAN_TARGETS",
    "OPERATIONAL_ALLOWED_DUPLICATES",
    "is_excluded_path",
    "is_allowed_duplicate",
    "should_scan_directory",
]
