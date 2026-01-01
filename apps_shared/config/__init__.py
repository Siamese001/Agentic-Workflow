"""Shared configuration for operational agents."""

from apps_shared.config.operational_config import (
    OPERATIONAL_EXCLUDED_DIRS,
    OPERATIONAL_SCAN_TARGETS,
    OPERATIONAL_ALLOWED_DUPLICATES,
    is_excluded_path,
    is_allowed_duplicate,
    should_scan_directory,
)

__all__ = [
    'OPERATIONAL_EXCLUDED_DIRS',
    'OPERATIONAL_SCAN_TARGETS',
    'OPERATIONAL_ALLOWED_DUPLICATES',
    'is_excluded_path',
    'is_allowed_duplicate',
    'should_scan_directory',
]
