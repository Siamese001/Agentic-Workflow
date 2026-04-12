#!/usr/bin/env python3
"""Analyze the guardian:allow-silent-swallow pattern across test files."""

import re
from collections import Counter
from pathlib import Path

pattern_files = []
for p in sorted(Path("tests").rglob("*.py")):
    try:
        content = p.read_text("utf-8")
        if "guardian: allow-silent-swallow" in content:
            blocks = content.count("guardian: allow-silent-swallow")
            has_mod_none = "_mod = None" in content or "= None  # type: ignore" in content
            skip_count = len(re.findall(r"pytest\.skip\(", content))
            pattern_files.append(
                {
                    "file": str(p).replace("\\", "/"),
                    "swallow_blocks": blocks,
                    "has_mod_none": has_mod_none,
                    "skip_count": skip_count,
                    "lines": len(content.splitlines()),
                }
            )
    except Exception:
        pass

total_swallow = sum(f["swallow_blocks"] for f in pattern_files)
total_mod_none = sum(1 for f in pattern_files if f["has_mod_none"])
total_skips = sum(f["skip_count"] for f in pattern_files)

print(f"Files with guardian:allow-silent-swallow: {len(pattern_files)}")
print(f"Total swallow blocks: {total_swallow}")
print(f"Files with _mod=None: {total_mod_none}")
print(f"Total skip calls in these files: {total_skips}")
print()

# Categorize by test directory
dir_counter = Counter()
for f in pattern_files:
    parts = f["file"].split("/")
    if len(parts) >= 2:
        dir_counter[parts[1]] += 1
    else:
        dir_counter["root"] += 1

print("By directory:")
for d, c in dir_counter.most_common():
    print(f"  {d}: {c}")

# Now check the ADG stub pattern specifically
# Pattern: try: import X except: X = None; then test_module_importable with pass
adg_stub_files = []
for p in sorted(Path("tests").rglob("*_adg.py")):
    try:
        content = p.read_text("utf-8")
        if "guardian: allow-silent-swallow" in content:
            adg_stub_files.append(str(p).replace("\\", "/"))
    except Exception:
        pass

print(f"\n_adg.py files with swallow pattern: {len(adg_stub_files)}")

# Non-ADG files with swallow pattern
non_adg_swallow = [f for f in pattern_files if not f["file"].endswith("_adg.py")]
print(f"Non-_adg.py files with swallow pattern: {len(non_adg_swallow)}")
for f in non_adg_swallow[:15]:
    print(f"  {f['file']} (skips={f['skip_count']}, swallows={f['swallow_blocks']})")
if len(non_adg_swallow) > 15:
    print(f"  ... and {len(non_adg_swallow) - 15} more")
