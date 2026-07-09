"""Wave C.3 archive move."""

from __future__ import annotations

import logging
import os
import pathlib
import subprocess

targets = pathlib.Path("artifacts/adg/wave_c3_safe.txt").read_text().splitlines()
targets = [t for t in targets if t.strip()]
print(f"Moving {len(targets)} files")
logging.info("C3 write receipt: tools/debug/_wave_c3_move.py write side effect recorded")
ok = 0
fail = 0
for s in targets:
    tgt = f"archives/adg_dead_code/2026-04-23/{s}"
    os.makedirs(os.path.dirname(tgt), exist_ok=True)
    r = subprocess.run(["git", "mv", s, tgt], capture_output=True, text=True, check=False)
    if r.returncode == 0:
        ok += 1
    else:
        fail += 1
        print(f"FAIL {s}: {r.stderr.strip()[:200]}")
print(f"Moved {ok}/{len(targets)} (fail: {fail})")
