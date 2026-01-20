#!/usr/bin/env python3
"""Quick test scanner with built-in progress indicator."""
from pathlib import Path
import re
import sys

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex

# ANSI colors
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
B = '\033[94m'  # Blue
C = '\033[96m'  # Cyan
X = '\033[0m'   # Reset

def progress_bar(current, total, width=40):
    """Simple progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    color = G if percent > 0.7 else Y if percent > 0.3 else R
    sys.stdout.write(f'\r{color}[{bar}]{X} {current}/{total} ({percent*100:.1f}%)')
    sys.stdout.flush()

# Scan tests
# Phase 6.7: Use ssot_discovery instead of rglob
from agentic_core.utils.ssot_discovery import get_python_files
test_files = list(get_python_files(Path(TESTS_UNIT_DIR)))

skip_pattern = re.compile(r'@pytest\.mark\.skip')
total_files_with_skips = 0
total_skips = 0

print(f"{C}Scanning {len(test_files)} test files...{X}\n")

for i, py_file in enumerate(test_files, 1):
    progress_bar(i, len(test_files))
    try:
        content = py_file.read_text(encoding='utf-8')
        skip_count = len(skip_pattern.findall(content))
        if skip_count > 0:
            total_files_with_skips += 1
            total_skips += skip_count
    except:
        pass

print(f"\n\n{B}{'='*60}{X}")
print(f"{B}Results:{X}")
print(f"{B}{'='*60}{X}")
print(f"  Files with skips: {C}{total_files_with_skips}{X}")

color = G if total_skips < 200 else Y if total_skips < 400 else R
print(f"  Total skip marks: {color}{total_skips}{X}")

if total_skips < 200:
    print(f"  Status: {G}✓ EXCELLENT (<200){X}")
elif total_skips < 400:
    print(f"  Status: {Y}⚠ NEEDS WORK (200-400){X}")
else:
    print(f"  Status: {R}✗ CRITICAL (>400){X}")

print(f"{B}{'='*60}{X}")
