"""Wave D archive move."""

from __future__ import annotations

import logging
import os
import subprocess

targets = [
    "agentic_core/L2_execution/enforcement/docker_sandbox.py",
    "agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py",
    "agentic_core/adg/runtime/sandbox_airlock.py",
]
for s in targets:
    tgt = f"archives/adg_dead_code/2026-04-23/{s}"
    os.makedirs(os.path.dirname(tgt), exist_ok=True)
    logging.info("C3 write receipt: tools/debug/_wave_d_move.py write side effect recorded")
    r = subprocess.run(["git", "mv", s, tgt], capture_output=True, text=True, check=False)
    status = "ok" if r.returncode == 0 else "FAIL"
    print(f"{status}: {s}")
    if r.stderr:
        print(f"  stderr: {r.stderr.strip()[:200]}")
