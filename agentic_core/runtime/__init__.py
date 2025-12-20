"""
L6 Runtime: Self-Maintenance Layer
Enforces project structure integrity and automated cleanup.
"""

from agentic_core.runtime.void_compliance import (
    ALLOWED_ROOT_FOLDERS,
    FORBIDDEN_ROOT_FOLDERS,
    KEY_TO_FOLDER_MAP,
    check_import_waterfall_violations,
    check_single_child_violations,
    enforce_void_compliance,
    get_applicable_keys_for_file,
    get_folder_scope_summary,
    validate_file_location,
)

__all__ = [
    "ALLOWED_ROOT_FOLDERS",
    "FORBIDDEN_ROOT_FOLDERS",
    "KEY_TO_FOLDER_MAP",
    "check_import_waterfall_violations",
    "check_single_child_violations",
    "enforce_void_compliance",
    "get_applicable_keys_for_file",
    "get_folder_scope_summary",
    "validate_file_location",
]
