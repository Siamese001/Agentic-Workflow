#!/usr/bin/env python3
"""Quick test scanner with built-in progress indicator."""
from pathlib import Path
import re
import sys

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
test_files = list(Path('tests/unit').rglob('*.py'))
test_files = [f for f in test_files if '__pycache__' not in str(f)]

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
