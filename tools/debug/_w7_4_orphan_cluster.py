"""W7.4 — cluster G_REACH archival orphans by folder pattern to design anchors.

The D7/G_REACH_archival gate is flagging 1583 modules as archival_orphans.
Many are false positives (subsystems dispatched via capability registries,
strategy loaders, or importlib). This script clusters orphans by top 3 path
segments so we can design compact anchor patterns that cover the legit
dynamic-dispatch subsystems without hand-listing every file.
"""

from __future__ import annotations

import subprocess
import re
from collections import Counter


def run_gate() -> list[str]:
    proc = subprocess.run(
        ["python", "ops_scripts/ci/check_graph_reach_archival.py"],
        capture_output=True,
        text=True,
        timeout=120,
        shell=False,
    )
    output = proc.stdout + proc.stderr
    orphans: list[str] = []
    pattern = re.compile(r"FAIL\s+(\S+\.py)\s+::\s+archival_orphan")
    for line in output.splitlines():
        m = pattern.search(line)
        if m:
            orphans.append(m.group(1).replace("\\", "/"))
    return orphans


def cluster(orphans: list[str]) -> None:
    # Cluster by first 2 segments
    c2: Counter[str] = Counter()
    # Cluster by first 3 segments
    c3: Counter[str] = Counter()
    for p in orphans:
        parts = p.split("/")
        if len(parts) >= 2:
            c2["/".join(parts[:2])] += 1
        if len(parts) >= 3:
            c3["/".join(parts[:3])] += 1

    print(f"TOTAL ORPHANS: {len(orphans)}\n")
    print("=== TOP 20 BY 2-SEGMENT PREFIX ===")
    for k, v in c2.most_common(20):
        print(f"  {v:4d}  {k}/")
    print()
    print("=== TOP 40 BY 3-SEGMENT PREFIX ===")
    for k, v in c3.most_common(40):
        print(f"  {v:4d}  {k}/")


if __name__ == "__main__":
    orphans = run_gate()
    cluster(orphans)
