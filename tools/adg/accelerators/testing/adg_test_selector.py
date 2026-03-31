"""Test selector proxy - imports from actual location."""
# This file proxies to the actual adg_test_selector.py location

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import and re-export from tools.adg.adg_test_selector
from tools.adg.adg_test_selector import (
    ADGTestSelector,
    TestImpactAnalyzer,
    _cli,
    select_tests_for_changes,
)

__all__ = [
    "ADGTestSelector",
    "TestImpactAnalyzer",
    "_cli",
    "select_tests_for_changes",
]
