"""Red-path proof: expired waiver makes W5 gate fail."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WAIVER = REPO_ROOT / "config" / "wiring_gate_waivers.yaml"

# Snapshot current waiver file, overwrite with expired entry, run gate, restore.
backup = WAIVER.read_text(encoding="utf-8")
try:
    WAIVER.write_text(
        """
waivers:
  - gate: J1_canonical_pipeline_wiring
    scope: C0_context_engine::C01_plan
    reason: Test — intentionally expired
    owner: w5-test
    expires_on: 2020-01-01
  - gate: J1_canonical_pipeline_wiring
    scope: C0_context_engine::C01_acl_gate
    reason: Test — still valid
    owner: w5-test
    expires_on: 2099-01-01
""".lstrip(),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_waiver_expiry.py"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
    )
    print(f"exit_code: {proc.returncode}")
    print("stdout:")
    print(proc.stdout)
    print("stderr:", proc.stderr, end="")
finally:
    WAIVER.write_text(backup, encoding="utf-8")
    print(f"restored: {WAIVER.relative_to(REPO_ROOT).as_posix()}")
