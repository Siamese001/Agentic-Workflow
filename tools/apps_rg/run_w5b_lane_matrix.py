#!/usr/bin/env python3
"""Run Wave 5B product-visible section lanes and print lane=artifact_dir lines."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

LANES = (
    "headline",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
    "executive_summary",
)

COMMON = [
    "python",
    "-m",
    "apps_rg",
    "--target-company",
    "Unify Consulting",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--jd",
    "apps_rg/config/default_jd_targeting.txt",
    "--manual-brief",
    "apps_rg/config/default_targeting_briefing.txt",
    "--allow-non-allow-exit-zero",
]

_ARTIFACT_RE = re.compile(r"artifact_dir_workspace=(\S+)")


def main() -> int:
    exits: dict[str, int] = {}
    for lane in LANES:
        cmd = [*COMMON, "--section", lane]
        print(f"\n=== RUN {lane} ===", flush=True)
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=600,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        print(out[-4000:] if len(out) > 4000 else out, flush=True)
        m = _ARTIFACT_RE.search(out)
        if m:
            rel = m.group(1).replace("\\", "/")
            abs_path = (REPO / rel).resolve()
            print(f"{lane}={abs_path}", flush=True)
            print(f"{lane}_exit={proc.returncode}", flush=True)
        else:
            print(f"{lane}=MISSING", flush=True)
            print(f"{lane}_exit={proc.returncode}", flush=True)
        exits[lane] = proc.returncode
    return 0 if all(v == 0 for v in exits.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
