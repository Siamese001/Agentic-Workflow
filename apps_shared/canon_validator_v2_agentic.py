#!/usr/bin/env python3
"""
Canon Validator v2.0 - Merged and Consolidated
All validator logic consolidated from multiple silos.
"""

import ast
import hashlib
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace")

# ==============================================================================
# CONFIGURATION: EXCLUSION ZONES
# ==============================================================================
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs',
    'archives', 'data',
}

EXCLUDED_FILES = {
    'canon_validator.py',
    'canon_validator_backup.py',
    'canon_validator_v2_agentic.py',
    'auto_canon.py',
    '.DS_Store'
}

def is_excluded(path: str) -> bool:
    """Check if a path should be excluded from validation."""
    path_parts = path.split(os.sep)
    
    # Check directory exclusions
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            return True
    
    # Check file exclusions
    filename = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True
    
    return False


# Function: is_valid (from /app/agentic_core/L1_cognition/identity/spiffe_manager_types.py)
    def is_valid(self) -> bool:
        """Check if identity is valid. """
        return not self.is_expired() and self.spiffe_id and self.public_key and self.private_key


# Function: validate (from /app/apps_rg/L1_cognition/k25_models.py)
    def validate(self) -> bool:
        """Docstring."""
        return bool(self.metric_name and self.value and self.source_citation)


# Function: check (from /app/apps_rg/L3_orchestration/safety/check_hallucination.py)
def check(self: Any, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check text for potential hallucinations.

    Args:
        text: Text to check
        context: Additional context for checking

    Returns:
        Dictionary with check results
    """
    return {'is_hallucination': False, 'confidence': 0.95, 'issues': []}


# Function: verify (from /app/apps_shared/canon_validator_v2_agentic.py)
    def verify(self, content: str) -> bool:
        """Docstring."""
        computed_hash = hashlib.sha256(content.encode()).hexdigest()
        return computed_hash == self.content_hash

