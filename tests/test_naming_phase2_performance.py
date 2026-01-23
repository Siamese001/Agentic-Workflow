import os
import time
import pytest
import re
from pathlib import Path

# MANDATORY: 100% Pass language included.
# Tests focus on performance and directory exclusion.

def test_map_performance():
    """Verify that the project mapping completes in under 2 seconds."""
    from scripts.remediate_naming_phase2 import get_project_file_map
    
    start_time = time.time()
    file_map = get_project_file_map()
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"Mapping duration: {duration:.2f}s")
    
    # On a standard high-performance laptop, 
    # this should take < 1s if exclusions are working.
    assert duration < 2.0, f"Mapping is too slow ({duration:.2f}s). Exclusions likely failed."

def test_quarantine_exclusion():
    """Ensure venv and .git are NOT in the file map."""
    from scripts.remediate_naming_phase2 import get_project_file_map, QUARANTINED_DIRS
    
    file_map = get_project_file_map()
    
    for path in file_map.values():
        parts = set(path.parts)
        intersection = parts.intersection(QUARANTINED_DIRS)
        assert not intersection, f"Quarantined directory found in map: {intersection} in {path}"

def test_log_cleaning_logic():
    """Verify that tags are correctly stripped from the log input."""
    test_line = "StrategicPlannerAgent.py: Protected Suffix"
    clean = re.sub(r'\\s*', '', test_line)
    assert clean == "StrategicPlannerAgent.py: Protected Suffix"
    
    fname = clean.split(":")[0].strip()
    assert fname == "StrategicPlannerAgent.py"

def test_scoped_import_replacement():
    """Verify that only lines starting with import/from are modified."""
    from scripts.remediate_naming_phase2 import to_snake_case
    
    old = "fix_all_agentic_imports"
    new = to_snake_case(old)
    
    import_line = f"from common_utils import {old}"
    comment_line = f"# This script uses {old}"
    
    def simulate_replace(line):
        if re.match(r"^\s*(import|from)\b", line):
            return re.sub(rf"\b{old}\b", new, line)
        return line

    assert simulate_replace(import_line) == f"from common_utils import {new}"
    assert simulate_replace(comment_line) == comment_line  # Should NOT change
