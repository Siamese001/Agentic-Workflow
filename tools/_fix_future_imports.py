"""Fix __future__ import ordering: move lru_cache import after __future__."""

import pathlib

ROOT = pathlib.Path(r"c:\Git\Agentic-Workflow")

for rel in ["agentic_core/adg/schema_util.py", "agentic_core/adg/schema.py"]:
    p = ROOT / rel
    content = p.read_text(encoding="utf-8")

    # Swap: move lru_cache line to after __future__ line
    bad = "from functools import lru_cache\nfrom __future__ import annotations"
    good = "from __future__ import annotations\nfrom functools import lru_cache"

    if bad in content:
        content = content.replace(bad, good, 1)
        p.write_text(content, encoding="utf-8")
        print(f"[OK] {rel}: fixed __future__ ordering")
    else:
        print(f"[SKIP] {rel}: pattern not found")

    # Verify
    lines = p.read_text(encoding="utf-8").split("\n")
    for i, l in enumerate(lines):
        if "__future__" in l or "functools" in l:
            print(f"  line {i}: {l}")
