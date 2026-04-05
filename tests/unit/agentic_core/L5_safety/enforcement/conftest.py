"""conftest.py for L5_safety/enforcement tests - ensures tools/fix is on path."""
import sys
from pathlib import Path

def _find_repo_root():
    """Find repo root by looking for pytest.ini or .git."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pytest.ini").exists() or (parent / ".git").exists():
            return parent
    return current.parents[5]  # Fallback

# Add tools/fix to path for importing fix_high_severity_silent_swallowers
_repo_root = _find_repo_root()
_tools_fix = _repo_root / "tools" / "fix"
if str(_tools_fix) not in sys.path:
    sys.path.insert(0, str(_tools_fix))
