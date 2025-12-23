#!/usr/bin/env python3
"""
Root-level void_compliance.py - Symlink to agentic_core/runtime/void_compliance.py
This file exists to allow direct imports from the root level.
"""

# Import everything from the actual implementation
from agentic_core.runtime.P1_core.void_compliance import (
    # Constants
    ALLOWED_ROOT_FOLDERS,
    FORBIDDEN_ROOT_FOLDERS,
    CANONICAL_HIERARCHY,
    KEY_TO_FOLDER_MAP,
    STDLIB_MODULES,
    FORBIDDEN_FILE_PATTERNS,
    HIGH_SIGNAL_KEYWORDS,
    
    # Functions
    validate_file_location,
    validate_file_naming,
    validate_import_conventions,
    enforce_void_compliance,
    get_applicable_keys_for_file,
    get_folder_scope_summary,
    generate_ascii_tree,
    check_span_of_two_violations,
    check_span_of_two_violation,
    validate_canonical_hierarchy,
    check_import_waterfall_violations,
    get_placement_guidance,
)
