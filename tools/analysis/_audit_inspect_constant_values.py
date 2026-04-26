"""Inspect actual values of SSOT magic constants to determine consolidation strategy."""
import re
from pathlib import Path

CONSTANTS = ["BATCH_SIZE", "BUFFER_SIZE", "THRESHOLD", "MAX_RETRIES", "DEFAULT_SLEEP", "MAX_DEPTH", "MAX_FILES", "DEFAULT_TIMEOUT"]

REPO = Path(".")
results = {c: [] for c in CONSTANTS}

# Scan key directories for assignment patterns
roots = ["agentic_core", "apps_eval", "apps_exec", "apps_lic", "apps_research", "apps_rfp", "apps_rg", "apps_shared", "apps_underwriting_ai"]
for root in roots:
    rp = REPO / root
    if not rp.exists():
        continue
    for py in rp.rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for c in CONSTANTS:
            # Match "BATCH_SIZE = <value>" at module level (no leading whitespace)
            for m in re.finditer(rf"^{c}\s*[:=]\s*([^\n#]+?)(?:\s*#|$)", text, re.MULTILINE):
                value = m.group(1).strip()
                results[c].append((str(py), value))

print("=" * 80)
print("ACTUAL VALUES OF SSOT MAGIC CONSTANTS")
print("=" * 80)
for c in CONSTANTS:
    print(f"\n{c}:  {len(results[c])} definitions")
    # Group by value
    from collections import Counter
    val_counter = Counter(v for _, v in results[c])
    for val, cnt in val_counter.most_common():
        print(f"   {cnt:>3d}x  value=`{val[:60]}`")
    if len(val_counter) >= 2:
        print(f"   *** DIVERGENT — {len(val_counter)} distinct values ***")
        # Show file→value pairs for divergent constants
        for path, val in results[c][:8]:
            print(f"      {path}  ::  {val[:50]}")
    else:
        print(f"   ✓ all {len(results[c])} occurrences share the same value")
