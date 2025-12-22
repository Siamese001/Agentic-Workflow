"""
L2 RUNTIME BRIDGE: KEY 46 (THE LABOR)
=====================================
Exposes Void Compliance and ASCII visualization tools.
"""
import re
import time


from agentic_core.runtime.void_compliance import (
    ALLOWED_ROOT_FOLDERS,
    FORBIDDEN_ROOT_FOLDERS,
    KEY_TO_FOLDER_MAP,
    check_import_waterfall_violations,
    check_single_child_violations,
    enforce_void_compliance,
    generate_ascii_tree,
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
    "generate_ascii_tree",
    "get_applicable_keys_for_file",
    "get_folder_scope_summary",
    "validate_file_location",
]
