"""Debug _find_import_end for problem files."""

import sys

sys.path.insert(
    0, "tools"
)  # guardian: allow-global-mutation -- debug script requires tools/ on path before importing p0_microwave_wirer
from p0_microwave_wirer import _find_import_end

for fp_str in ["agentic_core/mixins/healing_mixin.py", "apps_rg/utils/enhanced_rg_flow_router_util.py"]:
    lines = open(fp_str, encoding="utf-8").read().split("\n")
    result = _find_import_end(lines)
    print(f"{fp_str}: import_end={result}")
    if result >= 0:
        print(f"  line {result}: {repr(lines[result][:80])}")
        nxt = lines[result + 1][:80] if result + 1 < len(lines) else "(end)"
        print(f"  line {result + 1}: {repr(nxt)}")
    else:
        print("  (no import block found — first 15 lines):")
        for i, l in enumerate(lines[:15]):
            print(f"  {i}: {repr(l[:80])}")
