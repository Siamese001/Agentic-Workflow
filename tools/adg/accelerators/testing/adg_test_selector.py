"""Test selector proxy - imports from actual location."""
# This file proxies to the actual adg_test_selector.py location

import sys
from pathlib import Path

# Add parent of parent to path
tools_adg_dir = Path(__file__).parent.parent.parent / "adg"
if str(tools_adg_dir.parent) not in sys.path:
    sys.path.insert(0, str(tools_adg_dir.parent))

# Import and re-export from tools.adg.adg_test_selector
from tools.adg.adg_test_selector import (
    ADGTestSelector,
    TestImpactAnalyzer,
    main,
    select_tests_for_changes,
)

__all__ = [
    "ADGTestSelector",
    "TestImpactAnalyzer",
    "main",
    "select_tests_for_changes",
]
